import argparse
import json
import os
import platform
import threading
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

import numpy as np
import psutil
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# -----------------------------
# Resource monitoring (prediction-only window)
# -----------------------------
@dataclass
class ResourceSample:
    t: float
    cpu_percent: float
    rss_mb: float

class ResourceMonitor:
    def __init__(self, sample_interval_s: float = 0.2):
        self.sample_interval_s = sample_interval_s
        self.samples: List[ResourceSample] = []
        self._stop = threading.Event()
        self._thread = None
        self._proc = psutil.Process(os.getpid())

    def start(self):
        # Prime cpu_percent so first reading isn't 0.0 due to psutil behavior
        psutil.cpu_percent(interval=None)
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run(self):
        while not self._stop.is_set():
            cpu = psutil.cpu_percent(interval=None)
            rss = self._proc.memory_info().rss / (1024 ** 2)
            self.samples.append(ResourceSample(time.time(), cpu, rss))
            time.sleep(self.sample_interval_s)

    def summary(self) -> Dict[str, Any]:
        if not self.samples:
            return {"n_samples": 0}
        cpu_vals = [s.cpu_percent for s in self.samples]
        rss_vals = [s.rss_mb for s in self.samples]
        return {
            "n_samples": len(self.samples),
            "cpu_avg_percent": float(np.mean(cpu_vals)),
            "cpu_peak_percent": float(np.max(cpu_vals)),
            "rss_avg_mb": float(np.mean(rss_vals)),
            "rss_peak_mb": float(np.max(rss_vals)),
            "sample_interval_s": self.sample_interval_s,
        }

# -----------------------------
# Dummy image generation
# -----------------------------
def generate_images(n: int, shape=(224, 224, 3), seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # Generate uint8-like image values then cast to float32 for preprocess_input
    imgs = rng.integers(0, 256, size=(n, *shape), dtype=np.uint8).astype(np.float32)
    return imgs

# -----------------------------
# Main experiment
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", type=str, default="clientA",
                        help="Identifier used to vary seed in 'different' mode.")
    parser.add_argument("--mode", type=str, choices=["same", "different"], default="same",
                        help="'same' uses shared seed across clients. 'different' varies seed by client-id.")
    parser.add_argument("--n-images", type=int, default=100)
    parser.add_argument("--image-shape", type=str, default="224,224,3")
    parser.add_argument("--warmup", type=int, default=5, help="Warmup predictions (not timed).")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--monitor-interval", type=float, default=0.2)
    parser.add_argument("--out", type=str, default="results.json")
    args = parser.parse_args()

    h, w, c = [int(x.strip()) for x in args.image_shape.split(",")]

    # Decide seed:
    # - same: fixed seed for all clients
    # - different: seed derived from client-id (stable across runs for that client)
    if args.mode == "same":
        seed = 12345
    else:
        seed = (abs(hash(args.client_id)) % 1_000_000) + 1

    # System info (helpful for your report)
    sys_info = {
        "client_id": args.client_id,
        "mode": args.mode,
        "seed": seed,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "tensorflow_version": tf.__version__,
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "tf_devices": [d.name for d in tf.config.list_logical_devices()],
    }

    # 1) Initialize model
    model = MobileNetV2(weights="imagenet", include_top=True)

    # 2) Generate dummy images
    imgs = generate_images(args.n_images, shape=(h, w, c), seed=seed)
    imgs_pp = preprocess_input(imgs.copy())

    # 3) Warmup (not timed)
    for _ in range(args.warmup):
        _ = model.predict(imgs_pp[:args.batch_size], verbose=0)

    # 4) Timed prediction-only section + resource monitoring
    monitor = ResourceMonitor(sample_interval_s=args.monitor_interval)
    monitor.start()

    start_wall = time.time()
    start_perf = time.perf_counter()

    # Predict 100 images (batching supported)
    latencies_ms = []
    for i in range(0, args.n_images, args.batch_size):
        batch = imgs_pp[i:i + args.batch_size]
        t0 = time.perf_counter()
        _ = model.predict(batch, verbose=0)
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

    end_perf = time.perf_counter()
    end_wall = time.time()

    monitor.stop()

    total_s = end_perf - start_perf
    per_image_ms = (total_s / args.n_images) * 1000.0

    results = {
        "system": sys_info,
        "prediction_window": {
            "start_time_wall": start_wall,
            "end_time_wall": end_wall,
            "duration_s": total_s,
            "n_images": args.n_images,
            "batch_size": args.batch_size,
            "avg_per_image_ms": per_image_ms,
            "batch_latency_ms_avg": float(np.mean(latencies_ms)),
            "batch_latency_ms_p95": float(np.percentile(latencies_ms, 95)),
            "batch_latency_ms_peak": float(np.max(latencies_ms)),
        },
        "resources": monitor.summary(),
    }

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved: {args.out}")
    print("Summary:")
    print(json.dumps({
        "client_id": args.client_id,
        "mode": args.mode,
        "duration_s": round(total_s, 4),
        "avg_per_image_ms": round(per_image_ms, 3),
        "cpu_peak_percent": results["resources"].get("cpu_peak_percent", None),
        "rss_peak_mb": results["resources"].get("rss_peak_mb", None),
        "tf_devices": sys_info["tf_devices"],
    }, indent=2))

if __name__ == "__main__":
    main()
