#!/bin/bash

# Quick Start Script for Edge Computing Benchmark
# This script helps you run the benchmark easily

echo "======================================================================="
echo "       EDGE COMPUTING PERFORMANCE BENCHMARK - QUICK START"
echo "======================================================================="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed!"
    echo "Please install Python 3.8 or higher first."
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"
echo ""

# Function to check if package is installed
check_package() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

# Check dependencies
echo "Checking dependencies..."
MISSING_DEPS=0

if ! check_package tensorflow; then
    echo "❌ TensorFlow not installed"
    MISSING_DEPS=1
else
    echo "✓ TensorFlow installed"
fi

if ! check_package numpy; then
    echo "❌ NumPy not installed"
    MISSING_DEPS=1
else
    echo "✓ NumPy installed"
fi

if ! check_package psutil; then
    echo "❌ psutil not installed"
    MISSING_DEPS=1
else
    echo "✓ psutil installed"
fi

echo ""

# Install dependencies if missing
if [ $MISSING_DEPS -eq 1 ]; then
    echo "Some dependencies are missing."
    read -p "Would you like to install them now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing dependencies..."
        pip3 install -r requirements.txt
        echo ""
    else
        echo "Please install dependencies manually with:"
        echo "  pip3 install -r requirements.txt"
        exit 1
    fi
fi

# Main menu
echo "======================================================================="
echo "                           MAIN MENU"
echo "======================================================================="
echo ""
echo "Select what you want to do:"
echo ""
echo "1. Run standard benchmark (MobileNetV2, 100 images)"
echo "2. Run multi-model comparison (all models, 100 images)"
echo "3. Run quick test (MobileNetV2, 20 images)"
echo "4. Compare existing results"
echo "5. Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "======================================================================="
        echo "Running Standard Benchmark"
        echo "======================================================================="
        echo ""
        echo "IMPORTANT: Make sure you're in the correct power mode!"
        echo ""
        echo "For Power Saver Mode:"
        echo "  - Disconnect from power"
        echo "  - Set power mode to 'Battery Saver' or 'Power Saver'"
        echo ""
        echo "For High Performance Mode:"
        echo "  - Connect to power"
        echo "  - Set power mode to 'High Performance' or 'Best Performance'"
        echo ""
        read -p "Press Enter when ready to start..."
        echo ""
        python3 edge_performance_benchmark.py
        ;;
    2)
        echo ""
        echo "======================================================================="
        echo "Running Multi-Model Comparison"
        echo "======================================================================="
        echo ""
        echo "This will test multiple models (MobileNetV2, MobileNetV3, EfficientNet, ResNet50)"
        echo "This may take 10-20 minutes depending on your hardware."
        echo ""
        read -p "Press Enter to continue..."
        echo ""
        python3 multi_model_benchmark.py
        ;;
    3)
        echo ""
        echo "======================================================================="
        echo "Running Quick Test"
        echo "======================================================================="
        echo ""
        echo "This will run a quick test with only 20 images for rapid testing."
        echo ""
        read -p "Press Enter to continue..."
        echo ""
        python3 -c "
from edge_performance_benchmark import EdgePerformanceBenchmark
benchmark = EdgePerformanceBenchmark()
benchmark.run_full_benchmark(num_images=20)
"
        ;;
    4)
        echo ""
        echo "======================================================================="
        echo "Comparing Existing Results"
        echo "======================================================================="
        echo ""
        echo "Looking for result files..."
        if ls edge_benchmark_results_*.json 1> /dev/null 2>&1; then
            python3 compare_results.py
        else
            echo "❌ No result files found in current directory!"
            echo "Please run a benchmark first (option 1, 2, or 3)"
        fi
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "======================================================================="
echo "                         BENCHMARK COMPLETE!"
echo "======================================================================="
echo ""
echo "Next steps:"
echo "1. Run the benchmark in different power modes for comparison"
echo "2. Share results with your group members"
echo "3. Use compare_results.py to compare multiple laptops"
echo "4. Analyze the implications for your AIoT application"
echo ""
echo "For more information, see README.md"
echo ""
