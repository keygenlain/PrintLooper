#!/bin/bash
# Automated test script for printlooper.py

cd /home/runner/work/PrintLooper/PrintLooper

# Test 1: Centauri Carbon with 3 loops
echo "Testing Centauri Carbon with 3 loops..."
echo -e "1\n1\n3\n" | python3 printlooper.py

# Check if output file was created
if [ -f "test_print_looped_3x.gcode" ]; then
    echo "✓ Test 1 passed: Looped file created"
    echo "File size: $(wc -l < test_print_looped_3x.gcode) lines"
    rm test_print_looped_3x.gcode
else
    echo "✗ Test 1 failed: File not created"
    exit 1
fi

# Test 2: Ender 3 V3 SE with 2 loops
echo ""
echo "Testing Ender 3 V3 SE with 2 loops..."
echo -e "2\n1\n2\n" | python3 printlooper.py

# Check if output file was created
if [ -f "test_print_looped_2x.gcode" ]; then
    echo "✓ Test 2 passed: Looped file created"
    echo "File size: $(wc -l < test_print_looped_2x.gcode) lines"
    
    # Show a sample of the output
    echo ""
    echo "Sample output (first 50 lines):"
    head -50 test_print_looped_2x.gcode
    
    rm test_print_looped_2x.gcode
else
    echo "✗ Test 2 failed: File not created"
    exit 1
fi

echo ""
echo "✓ All tests passed!"
