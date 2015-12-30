# taken from EMC2 linux CNC manual
#
# G0	Rapid positioning
# G1	Linear interpolation
# G2	Circular/helical interpolation (clockwise)
# G3	Circular/helical interpolation (c-clockwise)
# G4	Dwell
# G10	Coordinate system origin setting
# G17	XY plane selection
# G18	XZ plane selection
# G19	YZ plane selection
# G20	Imperial system selection
# G21	Metric system selection
# G40	Cancel cutter diameter compensation
# G41	Start cutter diameter compensation left
# G42	Start cutter diameter compensation right
# G43	Tool length offset (plus)
# G49	Cancel tool length offset
# G53	Motion in machine coordinate system
# G54	Use preset work coordinate system 1
# G55	Use preset work coordinate system 2
# G56	Use preset work coordinate system 3
# G57	Use preset work coordinate system 4
# G58	Use preset work coordinate system 5
# G59	Use preset work coordinate system 6
# G59.1	Use preset work coordinate system 7
# G59.2	Use preset work coordinate system 8
# G59.3	Use preset work coordinate system 9
# G80	Cancel motion mode (includes canned)
# G81	Drilling canned cycle
# G82	Drilling with dwell canned cycle
# G83	Chip-breaking drilling canned cycle
# G84	Right hand tapping canned cycle
# G85	Bring, no dwell, feed out canned cycle
# G86	Boring, spindle stop, rapid out canned
# G87	Back boring canned cycle
# G88	Boring, spindle stop, manual out canned
# G89	Boring, dwell, feed out canned cycle
# G90	Absolute distance mode
# G91	Incremental distance mode
# G92	Offset coordinate systems
# G92.2	Cancel offset coordinate systems
# G93	Inverse time feed mode
# G94	Feed per minute mode
# G98	Initial level return in canned cycles
#
#
# Table 5. G-Code Modal Groups
# Modal Group Meaning	Member Words
# Non-modal codes (Group 0)
#
# G4, G10 G28, G30, G53 G92, G92.1, G92.2, G92.3,
#
# Motion (Group 1)
#
# G0, G1, G2, G3, G33, G38.x, G73, G76, G80, G81
#
# G82, G83, G84, G85, G86, G87, G88, G89
#
# Plane selection (Group 2)
#
# G17, G18, G19, G17.1, G18.1, G19.1
#
# Distance Mode (Group 3)
#
# G90, G91
#
# Arc IJK Distance Mode (Group 4)
#
# G90.1, G91.1
#
# Feed Rate Mode (Group 5)
#
# G93, G94, G95
#
# Units (Group 6)
#
# G20, G21
#
# Cutter Diameter Compensation (Group 7)
#
# G40, G41, G42, G41.1, G42.1
#
# Tool Length Offset (Group 8)
#
# G43, G43.1, G49
#
# Canned Cycles Return Mode (Group 10)
#
# G98, G99
#
# Coordinate System (Group 12)
#
# G54, G55, G56, G57, G58, G59, G59.1, G59.2, G59.3
#
# Control Mode (Group 13)
#
# G61, G61.1, G64
#
# Spindle Speed Mode (Group 14)
#
# G96, G97
#
# Lathe Diameter Mode (Group 15)
#
# G7, G8
#
# Table 6. M-Code Modal Groups
# Modal Group Meaning	Member Words
# Stopping (Group 4)
#
# M0, M1, M2, M30, M60
#
# I/O on/off (Group 5)
#
# M6 Tn
#
# Tool Change (Group 6)
#
# M6 Tn
#
# Spindle (Group 7)
#
# M3, M4, M5
#
# Coolant (Group 8)
#
# (M7 M8 can both be on), M9
#
# Override Switches (Group 9)
#
# M48, M49
#
# User Defined (Group 10)
#
# M100-M199
#
