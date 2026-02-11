; Test GCODE File for PrintLooper
; This is a simplified test file
; START GCODE
G28                    ; Home all axes
G1 Z15.0 F6000         ; Move the platform down 15mm
M104 S200              ; Set hotend temperature
M140 S60               ; Set bed temperature
M190 S60               ; Wait for bed temperature
M109 S200              ; Wait for hotend temperature
G92 E0                 ; Reset extruder
G1 F200 E10            ; Extrude 10mm of filament
G92 E0                 ; Reset extruder

; MAIN PRINT
G1 X50 Y50 Z0.2 F5000  ; Move to start position
G1 X100 Y50 E5 F1500   ; Draw line
G1 X100 Y100 E10 F1500 ; Draw line
G1 X50 Y100 E15 F1500  ; Draw line
G1 X50 Y50 E20 F1500   ; Draw line
G1 Z10 F3000           ; Raise Z

; END GCODE
M104 S0                ; Turn off hotend
M140 S0                ; Turn off bed
M106 S0                ; Turn off fan
G91                    ; Relative positioning
G1 Z10 F3000           ; Raise Z
G90                    ; Absolute positioning
G28 X Y                ; Home X and Y
M84                    ; Disable motors
