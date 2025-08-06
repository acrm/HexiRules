#!/usr/bin/env python3
"""
HexiRules - Hexagonal Cellular Automaton

Main entry point for the HexiRules application.
Supports both Conway-style totalistic rules and HexiDirect symbolic rules.
"""

from gui import create_gui

def main():
    """Main entry point for HexiRules."""
    gui = create_gui()
    gui.run()

if __name__ == "__main__":
    main()
