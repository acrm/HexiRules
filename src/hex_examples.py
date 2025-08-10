#!/usr/bin/env python3
"""
HexiRules - Hexagonal Rule Examples

This file demonstrates various hexagonal rule notation patterns
that can be used in the HexiRules application.

Hex Rule Notation Guide:
- Simple transformation: a => b (all 'a' cells become 'b')
- Conditional: a[x] => b ('a' becomes 'b' if it has 'x' neighbor)
- Directional: a1 => b2 ('a' pointing direction 1 becomes 'b' pointing direction 2)
- Negated condition: a[-x] => b ('a' becomes 'b' if it doesn't have 'x' neighbor)
- Specific direction: a[1x] => b ('a' becomes 'b' if direction 1 has 'x')

Direction numbers (1-6):
  2   1
 3  C  6
  4   5

Example Rules:

Conway-style rules (backward compatible):
- B3/S23 (Conway's Game of Life on hexagonal grid)

Basic hex rules:
- a => b                    # Simple state change
- a[b] => c                 # Conditional on any neighbor
- a1 => a2                  # Rotation (direction 1 -> 2)
- a[1b] => c               # Conditional on specific direction
- a[-b] => c               # Conditional on absence of neighbor

Complex patterns:
- t1[x] => t2              # Directional cell rotates when condition met
- _[t.] => a               # Empty cell becomes 'a' if any 't' points to it
- a[x] => b, b => c, c => a # Multi-rule cycle

To try these rules:

GUI Methods:
1. Run the unified GUI: python main.py
   - Toggle between "Conway/Totalistic Rules" and "HexiDirect Symbolic Rules"
   - Conway mode: Click to toggle cells
   - HexiDirect mode:
     * Left click: cycle through states (_, a, b, c, x, t, y, z)
     * Right click: cycle directions (1→2→3→4→5→6→None)
     * Middle click: clear cell

Programmatic Methods:
Example (programmatic usage):
from hex_rules import HexAutomaton

# Create automaton
automaton = HexAutomaton(radius=8)

# Set basic symbolic states
automaton.set_cell(0, 0, "a")      # State 'a'
automaton.set_cell(1, 0, "b")      # State 'b'
automaton.set_cell(2, 0, "x")      # State 'x'

# Set directional states (state + direction 1-6)
automaton.set_cell(0, 1, "t", 1)   # State 't' pointing direction 1
automaton.set_cell(1, 1, "t", 3)   # State 't' pointing direction 3

# Set rules and run
automaton.set_rules(["a[b] => c", "t1 => t2"])
automaton.step()  # Advance one generation
"""

# Example rule sets for testing
EXAMPLE_RULES = {
    "Simple Cycle": ["a => b", "b => c", "c => a"],
    "Conditional Growth": ["a[b] => c", "c => b"],
    "Directional Movement": [
        "t1 => t2",
        "t2 => t3",
        "t3 => t4",
        "t4 => t5",
        "t5 => t6",
        "t6 => t1",
    ],
    "Complex Interaction": ["a[x] => b", "b => y", "x => a", "y => x"],
}

if __name__ == "__main__":
    print(__doc__)

    print("\nExample Rule Sets:")
    print("==================")

    for name, rules in EXAMPLE_RULES.items():
        print(f"\n{name}:")
        for rule in rules:
            print(f"  {rule}")

    print(f"\nTo test these rules, copy any rule set into the GUI rule field.")
    print("Multiple rules can be separated by commas or entered one at a time.")
