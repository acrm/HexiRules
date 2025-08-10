Instructions for testing the new GUI:

1. Launch the GUI (should already be running)
2. Switch to "HexiDirect Symbolic Rules" mode
3. In the rules text area (now smaller), enter: _[t.] => a
4. Click on the grid to place a 't' cell (left click cycles through states)
5. Right click on the 't' cell to give it a direction (should see direction marker)
6. Click "Step" button
7. Observe the processing log shows detailed information about:
   - Rules being used
   - Expanded rules
   - Active cells before/after
   - Rule applications
   
Expected behavior:
- Only cells that the 't' cell points to should become 'a'
- The log should show exactly which rules are being applied and to which cells
- If 't' has no direction, no cells should change
- If 't' has direction 1, only the cell it points to should become 'a'

The GUI now has:
- Compact rules input (height=4 instead of 8)
- Comprehensive processing log taking up the freed space
- Detailed logging of every rule application
- Clear log button to reset the log
