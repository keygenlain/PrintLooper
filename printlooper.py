#!/usr/bin/env python3
"""
PrintLooper - Automate multiple 3D prints by looping GCODE files
Supports Centauri Carbon and Ender 3 V3 SE printers
"""

import os
import sys
from pathlib import Path
from typing import List, Optional


class PrintLooper:
    """Main class for GCODE looping automation"""
    
    PRINTER_MODES = {
        "1": "Centauri Carbon",
        "2": "Ender 3 V3 SE"
    }
    
    # Printer-specific push-off-bed sequences
    PUSH_OFF_SEQUENCES = {
        "Centauri Carbon": [
            "; === Centauri Carbon Push-Off Sequence ===",
            "G91                     ; Relative positioning",
            "G1 Z10 F3000           ; Raise Z by 10mm",
            "G90                     ; Absolute positioning",
            "G1 X0 Y220 F9000       ; Move to front-left position",
            "G1 Z10 F3000           ; Lower to push height",
            "G1 X220 Y220 F3000     ; Sweep across to push print off",
            "G1 X220 Y0 F9000       ; Move back",
            "G28 X Y                ; Home X and Y",
            "; === End Push-Off Sequence ===",
            ""
        ],
        "Ender 3 V3 SE": [
            "; === Ender 3 V3 SE Push-Off Sequence ===",
            "G91                     ; Relative positioning",
            "G1 Z10 F1200           ; Raise Z by 10mm",
            "G90                     ; Absolute positioning",
            "G1 X0 Y200 F3000       ; Move to front position",
            "G1 Z5 F1200            ; Lower to push height",
            "G1 X200 Y200 F2000     ; Sweep across to push print off",
            "G1 X200 Y0 F3000       ; Move back",
            "G28 X Y                ; Home X and Y",
            "G28 Z                  ; Home Z",
            "; === End Push-Off Sequence ===",
            ""
        ]
    }
    
    def __init__(self):
        self.printer_mode: Optional[str] = None
        self.gcode_file: Optional[str] = None
        self.gcode_file2: Optional[str] = None  # Second file for alternating
        self.loop_count: int = 1
    
    def find_gcode_files(self) -> List[str]:
        """Find all GCODE files in the current directory"""
        current_dir = Path.cwd()
        gcode_files = []
        
        for file in current_dir.glob("*.gcode"):
            if file.is_file():
                gcode_files.append(file.name)
        
        for file in current_dir.glob("*.GCODE"):
            if file.is_file() and file.name not in gcode_files:
                gcode_files.append(file.name)
        
        return sorted(gcode_files)
    
    def select_printer_mode(self) -> bool:
        """Prompt user to select printer mode"""
        print("\n" + "="*50)
        print("PrintLooper - GCODE Loop Automation")
        print("="*50)
        print("\nSelect your printer mode:")
        for key, name in self.PRINTER_MODES.items():
            print(f"  {key}. {name}")
        print()
        
        while True:
            choice = input("Enter your choice (1-2): ").strip()
            if choice in self.PRINTER_MODES:
                self.printer_mode = self.PRINTER_MODES[choice]
                print(f"\n✓ Selected: {self.printer_mode}")
                return True
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    def select_gcode_file(self) -> bool:
        """Prompt user to select a GCODE file"""
        gcode_files = self.find_gcode_files()
        
        if not gcode_files:
            print("\n✗ No GCODE files found in the current directory!")
            print(f"Current directory: {Path.cwd()}")
            return False
        
        print("\n" + "-"*50)
        print("Available GCODE files:")
        print("-"*50)
        for idx, filename in enumerate(gcode_files, 1):
            file_size = Path(filename).stat().st_size / 1024  # KB
            print(f"  {idx}. {filename} ({file_size:.1f} KB)")
        print()
        
        while True:
            try:
                choice = input(f"Select a file (1-{len(gcode_files)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(gcode_files):
                    self.gcode_file = gcode_files[idx]
                    print(f"\n✓ Selected: {self.gcode_file}")
                    return True
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(gcode_files)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def select_second_gcode_file(self) -> bool:
        """Prompt user to optionally select a second GCODE file for alternating"""
        print("\n" + "-"*50)
        print("Optional: Select a second GCODE file to alternate")
        print("-"*50)
        print("Leave blank to loop only the first file, or select")
        print("a second file to alternate (File1 → File2 → File1 → File2...)")
        print()
        
        gcode_files = self.find_gcode_files()
        
        if len(gcode_files) < 2:
            print("Only one GCODE file available. Skipping second file selection.")
            return True
        
        print("Available files:")
        for idx, filename in enumerate(gcode_files, 1):
            if filename == self.gcode_file:
                file_size = Path(filename).stat().st_size / 1024
                print(f"  {idx}. {filename} ({file_size:.1f} KB) [SELECTED AS FILE 1]")
            else:
                file_size = Path(filename).stat().st_size / 1024
                print(f"  {idx}. {filename} ({file_size:.1f} KB)")
        print()
        
        while True:
            try:
                choice = input(f"Select second file (1-{len(gcode_files)}, or press Enter to skip): ").strip()
                
                if not choice:
                    print("\n✓ No second file selected. Will loop single file.")
                    self.gcode_file2 = None
                    return True
                
                idx = int(choice) - 1
                if 0 <= idx < len(gcode_files):
                    selected_file = gcode_files[idx]
                    if selected_file == self.gcode_file:
                        print("Warning: You selected the same file. Please select a different file or press Enter to skip.")
                        continue
                    self.gcode_file2 = selected_file
                    print(f"\n✓ Second file selected: {self.gcode_file2}")
                    print("Files will alternate in the loop.")
                    return True
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(gcode_files)}.")
            except ValueError:
                print("Invalid input. Please enter a number or press Enter to skip.")
    
    def configure_loop_count(self) -> bool:
        """Prompt user for number of loops"""
        print("\n" + "-"*50)
        print("Configure loop count")
        print("-"*50)
        # Limit is 99 to keep output manageable and avoid extremely long files
        
        while True:
            try:
                choice = input("How many times should the print loop? (1-99): ").strip()
                count = int(choice)
                if 1 <= count <= 99:
                    self.loop_count = count
                    print(f"\n✓ Loop count set to: {self.loop_count}")
                    return True
                else:
                    print("Please enter a number between 1 and 99.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def read_gcode(self, filename: str) -> List[str]:
        """Read GCODE file and return lines"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            print(f"\n✗ Error reading file: {e}")
            return []
    
    def write_gcode(self, filename: str, lines: List[str]) -> bool:
        """Write GCODE lines to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"\n✗ Error writing file: {e}")
            return False
    
    def find_end_gcode_start(self, lines: List[str]) -> int:
        """Find where the end GCODE sequence starts"""
        # Look for common end GCODE markers
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip().upper()
            # Look for heating off commands or end comments
            if any(marker in line for marker in [
                'M104 S0',  # Turn off hotend
                'M140 S0',  # Turn off bed
                'M106 S0',  # Turn off fan
                '; END GCODE',
                ';END GCODE'
            ]):
                return i
        
        # If no end sequence found, return last 20 lines
        return max(0, len(lines) - 20)
    
    def create_looped_gcode(self) -> Optional[str]:
        """Create a looped version of the GCODE file(s)"""
        if not self.gcode_file or not self.printer_mode:
            print("\n✗ Configuration incomplete!")
            return None
        
        print("\n" + "="*50)
        print("Processing GCODE...")
        print("="*50)
        
        # Read first GCODE file
        original_lines = self.read_gcode(self.gcode_file)
        if not original_lines:
            return None
        
        print(f"✓ Read {len(original_lines)} lines from {self.gcode_file}")
        
        # Find where end GCODE starts for first file
        end_gcode_start = self.find_end_gcode_start(original_lines)
        print(f"✓ File 1 end GCODE sequence starts at line {end_gcode_start + 1}")
        
        # Split into main print and end GCODE
        main_gcode = original_lines[:end_gcode_start]
        end_gcode = original_lines[end_gcode_start:]
        
        # Handle second file if present
        main_gcode2 = None
        if self.gcode_file2:
            original_lines2 = self.read_gcode(self.gcode_file2)
            if not original_lines2:
                return None
            
            print(f"✓ Read {len(original_lines2)} lines from {self.gcode_file2}")
            
            end_gcode_start2 = self.find_end_gcode_start(original_lines2)
            print(f"✓ File 2 end GCODE sequence starts at line {end_gcode_start2 + 1}")
            
            main_gcode2 = original_lines2[:end_gcode_start2]
            # We'll use the end_gcode from the first file as the final end
        
        # Create output filename
        base_name = Path(self.gcode_file).stem
        if self.gcode_file2:
            base_name2 = Path(self.gcode_file2).stem
            output_file = f"{base_name}_{base_name2}_alternating_{self.loop_count}x.gcode"
        else:
            output_file = f"{base_name}_looped_{self.loop_count}x.gcode"
        
        # Build looped GCODE
        looped_lines = []
        
        # Add header comment
        looped_lines.append("; ================================================================\n")
        looped_lines.append(f"; PrintLooper - Looped GCODE for {self.printer_mode}\n")
        looped_lines.append(f"; Primary file: {self.gcode_file}\n")
        if self.gcode_file2:
            looped_lines.append(f"; Secondary file: {self.gcode_file2}\n")
            looped_lines.append("; Mode: Alternating between files\n")
        looped_lines.append(f"; Loop count: {self.loop_count}\n")
        looped_lines.append("; ================================================================\n")
        looped_lines.append("\n")
        
        # Get push-off sequence for selected printer
        push_off_sequence = self.PUSH_OFF_SEQUENCES[self.printer_mode]
        
        # Add each loop
        for loop_num in range(1, self.loop_count + 1):
            # Determine which file to use for this loop
            if self.gcode_file2:
                # Alternate between files: odd loops use file1, even loops use file2
                if loop_num % 2 == 1:  # Odd loop number
                    current_gcode = main_gcode
                    current_file = self.gcode_file
                else:  # Even loop number
                    current_gcode = main_gcode2
                    current_file = self.gcode_file2
                
                looped_lines.append(f"; ================ LOOP {loop_num} of {self.loop_count} ================\n")
                looped_lines.append(f"; Using: {current_file}\n")
                looped_lines.append("\n")
            else:
                current_gcode = main_gcode
                looped_lines.append(f"; ================ LOOP {loop_num} of {self.loop_count} ================\n")
                looped_lines.append("\n")
            
            # Add main print GCODE
            looped_lines.extend(current_gcode)
            
            # Add push-off sequence (except after the last loop)
            if loop_num < self.loop_count:
                looped_lines.append("\n")
                looped_lines.extend([line + "\n" for line in push_off_sequence])
                looped_lines.append(f"; Preparing for loop {loop_num + 1}...\n")
                looped_lines.append("\n")
        
        # Add final end GCODE
        looped_lines.append("; ================ FINAL END SEQUENCE ================\n")
        looped_lines.append("\n")
        looped_lines.extend(end_gcode)
        
        # Write output file
        if self.write_gcode(output_file, looped_lines):
            print(f"\n✓ Successfully created looped GCODE!")
            print(f"✓ Output file: {output_file}")
            print(f"✓ Total lines: {len(looped_lines)}")
            return output_file
        else:
            return None
    
    def run(self):
        """Main execution flow"""
        try:
            # Step 1: Select printer mode
            if not self.select_printer_mode():
                return
            
            # Step 2: Select GCODE file
            if not self.select_gcode_file():
                return
            
            # Step 2b: Select optional second GCODE file
            if not self.select_second_gcode_file():
                return
            
            # Step 3: Configure loop count
            if not self.configure_loop_count():
                return
            
            # Step 4: Create looped GCODE
            output_file = self.create_looped_gcode()
            
            if output_file:
                print("\n" + "="*50)
                print("SUCCESS!")
                print("="*50)
                print(f"\nYour looped GCODE file has been created:")
                print(f"  📄 {output_file}")
                print(f"\nConfiguration:")
                print(f"  🖨️  Printer: {self.printer_mode}")
                print(f"  🔄 Loops: {self.loop_count}")
                print(f"  📁 File 1: {self.gcode_file}")
                if self.gcode_file2:
                    print(f"  📁 File 2: {self.gcode_file2}")
                    print(f"  🔄 Mode: Alternating")
                print("\nYou can now upload this file to your printer!")
                print("="*50)
            else:
                print("\n✗ Failed to create looped GCODE file.")
                sys.exit(1)
        
        except KeyboardInterrupt:
            print("\n\n✗ Operation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ An error occurred: {e}")
            sys.exit(1)


def main():
    """Entry point"""
    looper = PrintLooper()
    looper.run()


if __name__ == "__main__":
    main()
