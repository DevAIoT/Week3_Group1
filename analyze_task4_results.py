"""
Analysis Script for Task 4 Three-Tier Smart Routing Results
Analyzes JSON output and generates comprehensive text report
"""

import json
import numpy as np
import sys
import os
from datetime import datetime


def load_results(filepath):
    """Load results from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        sys.exit(1)


def analyze_distribution(results):
    """Analyze inference source distribution"""
    test = results['smart_routing_test']
    dist = test['distribution']

    print("=" * 60)
    print("INFERENCE SOURCE DISTRIBUTION")
    print("=" * 60)
    print(f"Total Requests: {test['num_successful']}")
    print(f"  Local (Edge):  {dist['num_local']:3d} requests ({dist['percent_local']:5.1f}%)")
    print(f"  Fog:           {dist['num_fog']:3d} requests ({dist['percent_fog']:5.1f}%)")
    print(f"  Cloud:         {dist['num_cloud']:3d} requests ({dist['percent_cloud']:5.1f}%)")
    print()


def analyze_latency(results):
    """Analyze latency statistics by tier"""
    test = results['smart_routing_test']
    individual = test['individual_requests']

    # Separate by inference source
    local_requests = [r for r in individual if r.get('inference_source') == 'local']
    fog_requests = [r for r in individual if r.get('inference_source') == 'fog']
    cloud_requests = [r for r in individual if r.get('inference_source') == 'cloud']

    print("=" * 60)
    print("LATENCY STATISTICS BY TIER")
    print("=" * 60)

    # Local statistics
    if local_requests:
        latencies = [r['latency_ms'] for r in local_requests]
        print(f"\nLocal (Edge) - {len(local_requests)} requests:")
        print(f"  Mean:      {np.mean(latencies):7.2f} ms")
        print(f"  Median:    {np.median(latencies):7.2f} ms")
        print(f"  Min:       {np.min(latencies):7.2f} ms")
        print(f"  Max:       {np.max(latencies):7.2f} ms")
        print(f"  Std Dev:   {np.std(latencies):7.2f} ms")
        print(f"  P50:       {np.percentile(latencies, 50):7.2f} ms")
        print(f"  P95:       {np.percentile(latencies, 95):7.2f} ms")
        print(f"  P99:       {np.percentile(latencies, 99):7.2f} ms")

    # Fog statistics
    if fog_requests:
        latencies = [r['latency_ms'] for r in fog_requests]
        print(f"\nFog - {len(fog_requests)} requests:")
        print(f"  Mean:      {np.mean(latencies):7.2f} ms")
        print(f"  Median:    {np.median(latencies):7.2f} ms")
        print(f"  Min:       {np.min(latencies):7.2f} ms")
        print(f"  Max:       {np.max(latencies):7.2f} ms")
        print(f"  Std Dev:   {np.std(latencies):7.2f} ms")
        print(f"  P50:       {np.percentile(latencies, 50):7.2f} ms")
        print(f"  P95:       {np.percentile(latencies, 95):7.2f} ms")
        print(f"  P99:       {np.percentile(latencies, 99):7.2f} ms")

    # Cloud statistics
    if cloud_requests:
        latencies = [r['latency_ms'] for r in cloud_requests]
        print(f"\nCloud - {len(cloud_requests)} requests:")
        print(f"  Mean:      {np.mean(latencies):7.2f} ms")
        print(f"  Median:    {np.median(latencies):7.2f} ms")
        print(f"  Min:       {np.min(latencies):7.2f} ms")
        print(f"  Max:       {np.max(latencies):7.2f} ms")
        print(f"  Std Dev:   {np.std(latencies):7.2f} ms")
        print(f"  P50:       {np.percentile(latencies, 50):7.2f} ms")
        print(f"  P95:       {np.percentile(latencies, 95):7.2f} ms")
        print(f"  P99:       {np.percentile(latencies, 99):7.2f} ms")

    print()


def analyze_complexity(results):
    """Analyze image complexity distribution"""
    test = results['smart_routing_test']
    individual = test['individual_requests']

    # Get all complexities
    complexities = [r['complexity'] for r in individual if 'complexity' in r]

    if not complexities:
        print("No complexity data available")
        return

    print("=" * 60)
    print("IMAGE COMPLEXITY STATISTICS")
    print("=" * 60)
    print(f"Total Images: {len(complexities)}")
    print(f"  Mean:        {np.mean(complexities):10.2f}")
    print(f"  Median:      {np.median(complexities):10.2f}")
    print(f"  Min:         {np.min(complexities):10.2f}")
    print(f"  Max:         {np.max(complexities):10.2f}")
    print(f"  Std Dev:     {np.std(complexities):10.2f}")
    print(f"  25th %ile:   {np.percentile(complexities, 25):10.2f}")
    print(f"  50th %ile:   {np.percentile(complexities, 50):10.2f}")
    print(f"  75th %ile:   {np.percentile(complexities, 75):10.2f}")
    print()

    # Complexity by tier
    local_requests = [r for r in individual if r.get('inference_source') == 'local']
    fog_requests = [r for r in individual if r.get('inference_source') == 'fog']
    cloud_requests = [r for r in individual if r.get('inference_source') == 'cloud']

    print("Complexity by Tier:")
    if local_requests:
        local_complexities = [r['complexity'] for r in local_requests]
        print(f"  Local:  Mean={np.mean(local_complexities):8.2f}, Range=[{np.min(local_complexities):8.2f}, {np.max(local_complexities):8.2f}]")

    if fog_requests:
        fog_complexities = [r['complexity'] for r in fog_requests]
        print(f"  Fog:    Mean={np.mean(fog_complexities):8.2f}, Range=[{np.min(fog_complexities):8.2f}, {np.max(fog_complexities):8.2f}]")

    if cloud_requests:
        cloud_complexities = [r['complexity'] for r in cloud_requests]
        print(f"  Cloud:  Mean={np.mean(cloud_complexities):8.2f}, Range=[{np.min(cloud_complexities):8.2f}, {np.max(cloud_complexities):8.2f}]")

    print()

    # Check threshold effectiveness
    config = results['routing_config']
    edge_threshold = config['edge_threshold']

    print(f"Threshold Analysis:")
    print(f"  Edge Threshold: {edge_threshold:.2f}")
    below_threshold = len([c for c in complexities if c < edge_threshold])
    above_threshold = len([c for c in complexities if c >= edge_threshold])
    print(f"  Below threshold: {below_threshold} images ({below_threshold/len(complexities)*100:.1f}%)")
    print(f"  Above threshold: {above_threshold} images ({above_threshold/len(complexities)*100:.1f}%)")
    print()


def analyze_performance(results):
    """Analyze overall performance metrics"""
    test = results['smart_routing_test']
    individual = test['individual_requests']

    print("=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)

    # Calculate throughput
    total_time = test['total_time_seconds']
    num_successful = test['num_successful']
    throughput = num_successful / total_time if total_time > 0 else 0

    print(f"Total Time:        {total_time:.3f} seconds")
    print(f"Successful Reqs:   {num_successful}")
    print(f"Throughput:        {throughput:.2f} requests/second")
    print()

    # Compare tier performance
    local_requests = [r for r in individual if r.get('inference_source') == 'local']
    fog_requests = [r for r in individual if r.get('inference_source') == 'fog']
    cloud_requests = [r for r in individual if r.get('inference_source') == 'cloud']

    print("Performance Comparison:")
    print(f"{'Tier':<10} {'Count':<10} {'Avg Latency':<15} {'Throughput':<15}")
    print("-" * 50)

    if local_requests:
        avg_latency = np.mean([r['latency_ms'] for r in local_requests])
        tput = len(local_requests) / total_time if total_time > 0 else 0
        print(f"{'Local':<10} {len(local_requests):<10} {avg_latency:<15.2f} {tput:<15.2f}")

    if fog_requests:
        avg_latency = np.mean([r['latency_ms'] for r in fog_requests])
        tput = len(fog_requests) / total_time if total_time > 0 else 0
        print(f"{'Fog':<10} {len(fog_requests):<10} {avg_latency:<15.2f} {tput:<15.2f}")

    if cloud_requests:
        avg_latency = np.mean([r['latency_ms'] for r in cloud_requests])
        tput = len(cloud_requests) / total_time if total_time > 0 else 0
        print(f"{'Cloud':<10} {len(cloud_requests):<10} {avg_latency:<15.2f} {tput:<15.2f}")

    print()

    # Resource usage
    resources = test['resources']
    print("Resource Usage:")
    print(f"  Avg CPU:     {resources['avg_during_test']['cpu_percent']:.1f}%")
    print(f"  Avg Memory:  {resources['avg_during_test']['memory_used_gb']:.2f} GB")
    print()


def generate_insights(results):
    """Generate insights and observations"""
    test = results['smart_routing_test']
    individual = test['individual_requests']
    dist = test['distribution']

    print("=" * 60)
    print("INSIGHTS AND OBSERVATIONS")
    print("=" * 60)

    # Distribution insight
    if dist['num_local'] > dist['num_fog'] + dist['num_cloud']:
        print("✓ Most requests processed locally - edge threshold is effective")
    elif dist['num_cloud'] > dist['num_local'] + dist['num_fog']:
        print("! Most requests forwarded to cloud - consider raising thresholds")
    else:
        print("✓ Good distribution across tiers - balanced workload")

    print()

    # Latency insight
    local_requests = [r for r in individual if r.get('inference_source') == 'local']
    fog_requests = [r for r in individual if r.get('inference_source') == 'fog']
    cloud_requests = [r for r in individual if r.get('inference_source') == 'cloud']

    if local_requests and (fog_requests or cloud_requests):
        local_avg = np.mean([r['latency_ms'] for r in local_requests])

        if fog_requests:
            fog_avg = np.mean([r['latency_ms'] for r in fog_requests])
            overhead = fog_avg - local_avg
            print(f"Network overhead (Fog):  {overhead:.2f} ms ({overhead/local_avg*100:.1f}% increase)")

        if cloud_requests:
            cloud_avg = np.mean([r['latency_ms'] for r in cloud_requests])
            overhead = cloud_avg - local_avg
            print(f"Network overhead (Cloud): {overhead:.2f} ms ({overhead/local_avg*100:.1f}% increase)")

    print()

    # Success rate
    if test['num_failed'] == 0:
        print("✓ All requests successful - system is stable")
    else:
        failure_rate = test['num_failed'] / test['num_images'] * 100
        print(f"! Failure rate: {failure_rate:.1f}% - investigate errors")

    print()


def save_text_report(results, output_path):
    """Save analysis as text report"""
    import sys
    from io import StringIO

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    # Run all analysis functions
    analyze_distribution(results)
    analyze_latency(results)
    analyze_complexity(results)
    analyze_performance(results)
    generate_insights(results)

    # Get captured output
    report_text = sys.stdout.getvalue()
    sys.stdout = old_stdout

    # Save to file
    with open(output_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("TASK 4: THREE-TIER SMART ROUTING ANALYSIS REPORT\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(report_text)

    print(f"Text report saved to: {output_path}")


def main():
    """Main analysis execution"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_task4_results.py <results_json_file>")
        print("\nExample:")
        print("  python analyze_task4_results.py output/task4_smart_routing_results_20260126_150000.json")
        sys.exit(1)

    # Load results
    results_file = sys.argv[1]
    print(f"Loading results from: {results_file}")
    results = load_results(results_file)

    print(f"\n{'=' * 60}")
    print("TASK 4: THREE-TIER SMART ROUTING ANALYSIS")
    print(f"{'=' * 60}\n")

    # Run analysis
    analyze_distribution(results)
    analyze_latency(results)
    analyze_complexity(results)
    analyze_performance(results)
    generate_insights(results)

    # Save text report
    output_dir = os.path.dirname(results_file)
    if not output_dir:
        output_dir = 'output'
    report_path = os.path.join(output_dir, 'task4_analysis_report.txt')
    save_text_report(results, report_path)


if __name__ == "__main__":
    main()
