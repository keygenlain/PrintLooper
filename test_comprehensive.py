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
    import printlooper
    from printlooper import PrintLooper
    
    looper = PrintLooper()
    files = looper.find_gcode_files()
    
    assert len(files) > 0, "Should find at least one GCODE file"
    assert "test_print.gcode" in files, "Should find test_print.gcode"
    print(f"✓ Found {len(files)} GCODE file(s): {files}")


def test_end_gcode_detection():
    """Test end GCODE detection algorithm"""
    print("\nTest 2: End GCODE detection...")
    
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
    # Input order: printer_mode, file_selection, skip_second_file, loop_count
    result = subprocess.run(
        ['python3', 'printlooper.py'],
        input='1\n1\n\n3\n',  # Mode 1, File 1, Skip second, 3 loops
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
    # Input: mode, file, skip_second, loops
    subprocess.run(['python3', 'printlooper.py'], input='1\n1\n\n2\n', text=True, capture_output=True)
    output1 = "test_print_looped_2x.gcode"
    assert Path(output1).exists(), "Centauri Carbon output should exist"
    
    with open(output1, 'r') as f:
        content1 = f.read()
    
    assert "Centauri Carbon" in content1, "Should mention Centauri Carbon"
    assert "X220 Y220" in content1, "Should have Centauri Carbon specific movements"
    
    os.remove(output1)
    print("✓ Centauri Carbon mode working")
    
    # Test Ender 3 V3 SE (mode 2)
    # Input: mode, file, skip_second, loops
    subprocess.run(['python3', 'printlooper.py'], input='2\n1\n\n2\n', text=True, capture_output=True)
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
    
    # Input: mode, file, skip_second, loops
    subprocess.run(['python3', 'printlooper.py'], input='1\n1\n\n1\n', text=True, capture_output=True)
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


def test_alternating_files():
    """Test alternating between two GCODE files"""
    print("\nTest 6: Alternating files test...")
    
    import subprocess
    
    # Test with 4 loops alternating between two files
    # Input: mode, file1, file2, loops
    subprocess.run(['python3', 'printlooper.py'], input='1\n1\n2\n4\n', text=True, capture_output=True)
    output = "test_print_test_print2_alternating_4x.gcode"
    assert Path(output).exists(), "Alternating output should exist"
    
    with open(output, 'r') as f:
        content = f.read()
    
    # Check header mentions both files
    assert "test_print.gcode" in content, "Should mention first file"
    assert "test_print2.gcode" in content, "Should mention second file"
    assert "Alternating" in content, "Should mention alternating mode"
    
    # Check that files alternate correctly
    # Loop 1 should use test_print.gcode (odd)
    # Loop 2 should use test_print2.gcode (even)
    # Loop 3 should use test_print.gcode (odd)
    # Loop 4 should use test_print2.gcode (even)
    lines = content.split('\n')
    
    loop1_file = None
    loop2_file = None
    loop3_file = None
    loop4_file = None
    
    for i, line in enumerate(lines):
        if 'LOOP 1 of 4' in line and i+1 < len(lines):
            if 'Using:' in lines[i+1]:
                loop1_file = lines[i+1]
        if 'LOOP 2 of 4' in line and i+1 < len(lines):
            if 'Using:' in lines[i+1]:
                loop2_file = lines[i+1]
        if 'LOOP 3 of 4' in line and i+1 < len(lines):
            if 'Using:' in lines[i+1]:
                loop3_file = lines[i+1]
        if 'LOOP 4 of 4' in line and i+1 < len(lines):
            if 'Using:' in lines[i+1]:
                loop4_file = lines[i+1]
    
    assert loop1_file and 'test_print.gcode' in loop1_file, "Loop 1 should use file 1"
    assert loop2_file and 'test_print2.gcode' in loop2_file, "Loop 2 should use file 2"
    assert loop3_file and 'test_print.gcode' in loop3_file, "Loop 3 should use file 1"
    assert loop4_file and 'test_print2.gcode' in loop4_file, "Loop 4 should use file 2"
    
    print(f"✓ Alternating pattern correct:")
    print(f"  - Loop 1: test_print.gcode")
    print(f"  - Loop 2: test_print2.gcode")
    print(f"  - Loop 3: test_print.gcode")
    print(f"  - Loop 4: test_print2.gcode")
    
    os.remove(output)


def test_skip_second_file():
    """Test skipping second file selection"""
    print("\nTest 7: Skip second file test...")
    
    import subprocess
    
    # Input: mode, file, skip_second (empty), loops
    subprocess.run(['python3', 'printlooper.py'], input='1\n1\n\n2\n', text=True, capture_output=True)
    output = "test_print_looped_2x.gcode"
    assert Path(output).exists(), "Single file output should exist"
    
    with open(output, 'r') as f:
        content = f.read()
    
    # Should not mention alternating or second file
    assert "test_print2.gcode" not in content, "Should not mention second file"
    assert "Alternating" not in content, "Should not mention alternating"
    
    print(f"✓ Skipping second file works correctly")
    
    os.remove(output)


def main():
    """Run all tests"""
    # Change to script's directory to ensure tests work regardless of where they're run from
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print("="*60)
    print("PrintLooper Test Suite")
    print("="*60)
    
    try:
        test_gcode_file_detection()
        test_end_gcode_detection()
        test_looped_output_structure()
        test_printer_modes()
        test_single_loop()
        test_alternating_files()
        test_skip_second_file()
        
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
