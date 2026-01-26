"""
Local Testing Script for Task 4 Implementation
Tests all components on a single machine using different ports
"""

import subprocess
import time
import requests
import sys
import os


def test_router_utils():
    """Test router utilities"""
    print("\n" + "="*60)
    print("TEST 1: Router Utilities")
    print("="*60)

    try:
        from router_utils import ImageComplexityRouter
        import numpy as np

        # Create router
        router = ImageComplexityRouter(threshold=2000.0)
        print("✓ Router created successfully")

        # Test with simple image (low variance)
        simple_image = np.ones((1, 224, 224, 3)) * 128.0
        decision = router.get_routing_decision(simple_image)
        print(f"✓ Simple image complexity: {decision['complexity']:.2f}")
        print(f"  Process locally: {decision['process_locally']}")

        # Test with complex image (high variance)
        np.random.seed(42)
        complex_image = np.random.randint(0, 256, (1, 224, 224, 3)).astype(np.float32)
        decision = router.get_routing_decision(complex_image)
        print(f"✓ Complex image complexity: {decision['complexity']:.2f}")
        print(f"  Process locally: {decision['process_locally']}")

        print("\n✓ Router utilities test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Router utilities test FAILED: {str(e)}")
        return False


def test_config():
    """Test configuration"""
    print("\n" + "="*60)
    print("TEST 2: Configuration")
    print("="*60)

    try:
        from config_routing import (
            EDGE_COMPLEXITY_THRESHOLD,
            FOG_COMPLEXITY_THRESHOLD,
            FOG_SERVER_URL,
            CLOUD_SERVER_URL,
            FOG_SERVER_PORT,
            CLOUD_SERVER_PORT,
            REQUEST_TIMEOUT,
            NUM_TEST_IMAGES
        )

        print(f"✓ Edge Threshold: {EDGE_COMPLEXITY_THRESHOLD}")
        print(f"✓ Fog Threshold: {FOG_COMPLEXITY_THRESHOLD}")
        print(f"✓ Fog Server URL: {FOG_SERVER_URL}")
        print(f"✓ Cloud Server URL: {CLOUD_SERVER_URL}")
        print(f"✓ Fog Port: {FOG_SERVER_PORT}")
        print(f"✓ Cloud Port: {CLOUD_SERVER_PORT}")
        print(f"✓ Timeout: {REQUEST_TIMEOUT}s")
        print(f"✓ Test Images: {NUM_TEST_IMAGES}")

        print("\n✓ Configuration test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Configuration test FAILED: {str(e)}")
        return False


def test_imports():
    """Test that all files can be imported"""
    print("\n" + "="*60)
    print("TEST 3: File Imports")
    print("="*60)

    files_to_test = [
        'router_utils',
        'config_routing',
        'server_cloud',
        'server_fog',
        'client_edge_smart',
        'analyze_task4_results'
    ]

    all_passed = True
    for module_name in files_to_test:
        try:
            # Try to import
            __import__(module_name)
            print(f"✓ {module_name}.py imported successfully")
        except Exception as e:
            print(f"✗ {module_name}.py import FAILED: {str(e)}")
            all_passed = False

    if all_passed:
        print("\n✓ All imports test PASSED")
    else:
        print("\n✗ Some imports test FAILED")

    return all_passed


def test_complexity_distribution():
    """Test complexity distribution of random images"""
    print("\n" + "="*60)
    print("TEST 4: Complexity Distribution Analysis")
    print("="*60)

    try:
        import numpy as np
        from router_utils import ImageComplexityRouter
        from config_routing import EDGE_COMPLEXITY_THRESHOLD, FOG_COMPLEXITY_THRESHOLD

        print("Generating 100 random images and analyzing complexity...")

        complexities = []
        for i in range(100):
            np.random.seed(i)
            image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
            image = np.expand_dims(image, axis=0).astype(np.float32)
            complexity = np.var(image)
            complexities.append(complexity)

        complexities = np.array(complexities)

        print(f"\nComplexity Statistics:")
        print(f"  Min:        {np.min(complexities):.2f}")
        print(f"  Max:        {np.max(complexities):.2f}")
        print(f"  Mean:       {np.mean(complexities):.2f}")
        print(f"  Median:     {np.median(complexities):.2f}")
        print(f"  25th %ile:  {np.percentile(complexities, 25):.2f}")
        print(f"  50th %ile:  {np.percentile(complexities, 50):.2f}")
        print(f"  75th %ile:  {np.percentile(complexities, 75):.2f}")

        print(f"\nThreshold Analysis:")
        print(f"  Edge Threshold: {EDGE_COMPLEXITY_THRESHOLD:.2f}")
        below_edge = np.sum(complexities < EDGE_COMPLEXITY_THRESHOLD)
        print(f"    Below: {below_edge}/100 ({below_edge}%)")

        print(f"  Fog Threshold: {FOG_COMPLEXITY_THRESHOLD:.2f}")
        between = np.sum((complexities >= EDGE_COMPLEXITY_THRESHOLD) & (complexities < FOG_COMPLEXITY_THRESHOLD))
        print(f"    Between Edge and Fog: {between}/100 ({between}%)")

        above_fog = np.sum(complexities >= FOG_COMPLEXITY_THRESHOLD)
        print(f"    Above Fog: {above_fog}/100 ({above_fog}%)")

        print(f"\nExpected Distribution:")
        print(f"  Local (Edge):  {below_edge}%")
        print(f"  Fog:           {between}%")
        print(f"  Cloud:         {above_fog}%")

        if below_edge == 0 or above_fog == 0:
            print("\n⚠ WARNING: Thresholds may need adjustment for better distribution")
        else:
            print("\n✓ Thresholds appear reasonable")

        print("\n✓ Complexity distribution test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Complexity distribution test FAILED: {str(e)}")
        return False


def test_server_startup(server_file, port, server_name):
    """Test that a server can start (doesn't actually start it)"""
    print(f"\n  Testing {server_name}...")

    if not os.path.exists(server_file):
        print(f"  ✗ {server_file} not found")
        return False

    # Check if port is available
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        print(f"  ✓ Port {port} is available")
        print(f"  ✓ {server_file} exists")
        return True
    except OSError:
        print(f"  ⚠ Port {port} is in use (may be running already)")
        return True  # Not a failure, just a warning


def test_servers():
    """Test server files"""
    print("\n" + "="*60)
    print("TEST 5: Server Files")
    print("="*60)

    all_passed = True
    all_passed &= test_server_startup('server_cloud.py', 8001, 'Cloud Server')
    all_passed &= test_server_startup('server_fog.py', 8000, 'Fog Server')

    if all_passed:
        print("\n✓ Server files test PASSED")
    else:
        print("\n✗ Server files test FAILED")

    return all_passed


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("TASK 4 LOCAL TESTING SUITE")
    print("="*60)

    results = []

    # Run tests
    results.append(("Router Utilities", test_router_utils()))
    results.append(("Configuration", test_config()))
    results.append(("File Imports", test_imports()))
    results.append(("Complexity Distribution", test_complexity_distribution()))
    results.append(("Server Files", test_servers()))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED - Ready for deployment!")
        print("\nNext steps:")
        print("1. Update IP addresses in config_routing.py")
        print("2. Copy files to respective laptops")
        print("3. Start servers (cloud first, then fog)")
        print("4. Run edge client")
        print("5. Analyze results")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - Please fix errors before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
