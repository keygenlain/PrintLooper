; Second Test GCODE File for PrintLooper
; This represents a different model
; START GCODE
G28                    ; Home all axes
G1 Z15.0 F6000         ; Move the platform down 15mm
M104 S210              ; Set hotend temperature (slightly higher)
M140 S65               ; Set bed temperature (slightly higher)
M190 S65               ; Wait for bed temperature
M109 S210              ; Wait for hotend temperature
G92 E0                 ; Reset extruder
G1 F200 E10            ; Extrude 10mm of filament
G92 E0                 ; Reset extruder

; MAIN PRINT - DIFFERENT PATTERN (CIRCLE)
G1 X110 Y110 Z0.2 F5000  ; Move to center
G2 X110 Y110 I10 J0 E10 F1500  ; Draw circle
G1 Z10 F3000             ; Raise Z

; END GCODE
M104 S0                ; Turn off hotend
M140 S0                ; Turn off bed
M106 S0                ; Turn off fan
G91                    ; Relative positioning
G1 Z10 F3000           ; Raise Z
G90                    ; Absolute positioning
G28 X Y                ; Home X and Y
M84                    ; Disable motors
