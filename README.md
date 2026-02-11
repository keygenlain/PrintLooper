# PrintLooper

Loop your GCODEs! Automate multiple 3D prints by modifying GCODE files to push prints off the bed and restart automatically.

## Features

- 🖨️ **Multi-Printer Support**: Centauri Carbon and Ender 3 V3 SE
- 🔄 **Automated Looping**: Configure 1-99 print loops
- 📄 **Smart GCODE Detection**: Automatically finds GCODE files in the current directory
- 🔧 **Printer-Specific Sequences**: Custom bed-clearing logic for each printer
- ✅ **Easy to Use**: Interactive command-line interface

## Supported Printers

### Centauri Carbon
Custom push-off sequence optimized for the Centauri Carbon printer with specific movement patterns and speeds.

### Ender 3 V3 SE
Push-off sequence tailored for the Ender 3 V3 SE with appropriate bed dimensions and homing procedures.

## Installation

No installation required! Just download `printlooper.py` and place it in the same directory as your GCODE files.

### Requirements
- Python 3.6 or higher
- No external dependencies needed

## Usage

1. Place `printlooper.py` in the same directory as your GCODE files
2. Run the script:
   ```bash
   python3 printlooper.py
   ```
   Or on Windows:
   ```bash
   python printlooper.py
   ```

3. Follow the interactive prompts:
   - **Select printer mode**: Choose between Centauri Carbon (1) or Ender 3 V3 SE (2)
   - **Select GCODE file**: Pick from detected files in the current directory
   - **Configure loop count**: Enter how many times to loop (1-99)

4. The script will create a new file named `original_filename_looped_Nx.gcode` where N is the loop count

## How It Works

PrintLooper modifies your GCODE file by:

1. **Analyzing** the original GCODE to identify the end sequence
2. **Wrapping** the print sequence in a loop structure
3. **Inserting** printer-specific bed-clearing sequences between loops
4. **Preserving** the final end sequence after all loops complete

### Example Output Structure

```gcode
; ================ LOOP 1 of 3 ================
[Your original print GCODE]
; === Push-Off Sequence ===
[Printer-specific bed clearing commands]
; ================ LOOP 2 of 3 ================
[Your original print GCODE]
; === Push-Off Sequence ===
[Printer-specific bed clearing commands]
; ================ LOOP 3 of 3 ================
[Your original print GCODE]
; ================ FINAL END SEQUENCE ================
[Original end GCODE - motors off, etc.]
```

## Example

```bash
$ python3 printlooper.py

==================================================
PrintLooper - GCODE Loop Automation
==================================================

Select your printer mode:
  1. Centauri Carbon
  2. Ender 3 V3 SE

Enter your choice (1-2): 1

--------------------------------------------------
Available GCODE files:
--------------------------------------------------
  1. my_model.gcode (245.3 KB)
  2. test_print.gcode (1.0 KB)

Select a file (1-2): 1

--------------------------------------------------
Configure loop count
--------------------------------------------------
How many times should the print loop? (1-99): 5

==================================================
Processing GCODE...
==================================================
✓ Read 12543 lines from my_model.gcode
✓ End GCODE sequence starts at line 12520

✓ Successfully created looped GCODE!
✓ Output file: my_model_looped_5x.gcode
✓ Total lines: 62700

==================================================
SUCCESS!
==================================================

Your looped GCODE file has been created:
  📄 my_model_looped_5x.gcode

Configuration:
  🖨️  Printer: Centauri Carbon
  🔄 Loops: 5
  📁 Original: my_model.gcode

You can now upload this file to your printer!
==================================================
```

## Safety Considerations

⚠️ **Important Notes:**
- Always test with a low loop count (1-2) first
- Ensure your printer bed can handle automated print removal
- Monitor the first few loops to ensure proper bed clearing
- Make sure your printer has enough filament for all loops
- Check that bed adhesion is appropriate (not too strong)

## Troubleshooting

### No GCODE files found
- Ensure GCODE files are in the same directory as the script
- Check that files have `.gcode` or `.GCODE` extension

### Script won't run
- Verify Python 3.6+ is installed: `python3 --version`
- Check file permissions: `chmod +x printlooper.py`

### Bed clearing not working properly
- Each printer model has different bed dimensions and movement characteristics
- You may need to adjust the push-off sequences in the script for your specific setup
- Test with small prints first

## Contributing

Feel free to submit issues or pull requests for:
- Additional printer support
- Improved bed-clearing sequences
- Bug fixes
- Feature enhancements

## License

This project is open source and available for use and modification.
