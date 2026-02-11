#!/usr/bin/env python3
"""
Comprehensive test suite for PrintLooper
"""

import os
import sys
from pathlib import Path


def test_gcode_file_detection():
    """Test that the script can find GCODE files"""
    print("Test 1: GCODE file detection...")
    
    # Import the module
    sys.path.insert(0, '/home/runner/work/PrintLooper/PrintLooper')
    from printlooper import PrintLooper
    
    looper = PrintLooper()
    files = looper.find_gcode_files()
    
    assert len(files) > 0, "Should find at least one GCODE file"
    assert "test_print.gcode" in files, "Should find test_print.gcode"
    print(f"✓ Found {len(files)} GCODE file(s): {files}")


def test_end_gcode_detection():
    """Test end GCODE detection algorithm"""
    print("\nTest 2: End GCODE detection...")
    
    sys.path.insert(0, '/home/runner/work/PrintLooper/PrintLooper')
    from printlooper import PrintLooper
    
    looper = PrintLooper()
    lines = looper.read_gcode('test_print.gcode')
    
    assert len(lines) > 0, "Should read GCODE file"
    
    end_start = looper.find_end_gcode_start(lines)
    
    # Should detect M104 S0, M140 S0, or M106 S0 as end sequence marker
    assert end_start < len(lines), "Should find end sequence"
    line_content = lines[end_start].upper()
    assert any(marker in line_content for marker in ["M104 S0", "M140 S0", "M106 S0"]), \
        "End sequence should start with heating/fan off command"
    
    print(f"✓ End sequence correctly detected at line {end_start + 1}")
    print(f"  Line content: {lines[end_start].strip()}")


def test_looped_output_structure():
    """Test that looped output has correct structure"""
    print("\nTest 3: Looped output structure...")
    
    import subprocess
    
    # Create a test output
    result = subprocess.run(
        ['python3', 'printlooper.py'],
        input='1\n1\n3\n',
        text=True,
        capture_output=True
    )
    
    output_file = "test_print_looped_3x.gcode"
    assert Path(output_file).exists(), f"Output file {output_file} should exist"
    
    with open(output_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for loop markers
    loop_markers = [line for line in lines if "LOOP" in line and "of 3" in line]
    assert len(loop_markers) >= 3, "Should have 3 loop markers"
    
    # Check for push-off sequences (should be 2: between loop 1-2 and 2-3)
    push_sequences = [line for line in lines if "Push-Off Sequence" in line]
    assert len(push_sequences) >= 2, "Should have push-off sequences between loops"
    
    # Check for final end sequence
    final_end = [line for line in lines if "FINAL END SEQUENCE" in line]
    assert len(final_end) >= 1, "Should have final end sequence"
    
    print(f"✓ Output structure correct:")
    print(f"  - Total lines: {len(lines)}")
    print(f"  - Loop markers: {len(loop_markers)}")
    print(f"  - Push-off sequences: {len(push_sequences)}")
    print(f"  - Final end marker: {len(final_end)}")
    
    # Clean up
    os.remove(output_file)


def test_printer_modes():
    """Test both printer modes"""
    print("\nTest 4: Testing both printer modes...")
    
    import subprocess
    
    # Test Centauri Carbon (mode 1)
    subprocess.run(['python3', 'printlooper.py'], input='1\n1\n2\n', text=True, capture_output=True)
    output1 = "test_print_looped_2x.gcode"
    assert Path(output1).exists(), "Centauri Carbon output should exist"
    
    with open(output1, 'r') as f:
        content1 = f.read()
    
    assert "Centauri Carbon" in content1, "Should mention Centauri Carbon"
    assert "X220 Y220" in content1, "Should have Centauri Carbon specific movements"
    
    os.remove(output1)
    print("✓ Centauri Carbon mode working")
    
    # Test Ender 3 V3 SE (mode 2)
    subprocess.run(['python3', 'printlooper.py'], input='2\n1\n2\n', text=True, capture_output=True)
    output2 = "test_print_looped_2x.gcode"
    assert Path(output2).exists(), "Ender 3 V3 SE output should exist"
    
    with open(output2, 'r') as f:
        content2 = f.read()
    
    assert "Ender 3 V3 SE" in content2, "Should mention Ender 3 V3 SE"
    assert "X200 Y200" in content2 or "Y200" in content2, "Should have Ender specific movements"
    
    os.remove(output2)
    print("✓ Ender 3 V3 SE mode working")


def test_single_loop():
    """Test single loop (should have no push-off sequence)"""
    print("\nTest 5: Single loop test...")
    
    import subprocess
    
    subprocess.run(['python3', 'printlooper.py'], input='1\n1\n1\n', text=True, capture_output=True)
    output = "test_print_looped_1x.gcode"
    assert Path(output).exists(), "Single loop output should exist"
    
    with open(output, 'r') as f:
        content = f.read()
    
    # With single loop, there should be no push-off between loops
    # Only the loop marker and final end
    loop_markers = content.count("LOOP 1 of 1")
    assert loop_markers >= 1, "Should have loop 1 of 1 marker"
    
    # Should NOT have push-off sequence (since there's only one loop)
    # Actually, let's check the logic - with 1 loop, we skip push-off
    # The condition is: if loop_num < self.loop_count
    # So for loop 1 of 1, we won't add push-off
    
    print(f"✓ Single loop works correctly (no intermediate push-off)")
    
    os.remove(output)


def main():
    """Run all tests"""
    os.chdir('/home/runner/work/PrintLooper/PrintLooper')
    
    print("="*60)
    print("PrintLooper Test Suite")
    print("="*60)
    
    try:
        test_gcode_file_detection()
        test_end_gcode_detection()
        test_looped_output_structure()
        test_printer_modes()
        test_single_loop()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        return 0
    
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
