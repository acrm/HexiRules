"""ASCII control panel for HexiRules."""

from __future__ import annotations

import sys
from typing import Callable, TextIO

from application.world_service import WorldService

PANEL_WIDTH = 32


class AsciiControlPanel:
    """Simple text-based control panel."""

    def __init__(
        self,
        controller: WorldService,
        on_update: Callable[[], None],
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        self.controller = controller
        self.on_update = on_update
        self.inp = input_stream or sys.stdin
        self.out = output_stream or sys.stdout
        self.width = PANEL_WIDTH

    def render(self) -> str:
        """Return the panel UI as a string."""
        world = self.controller.get_current_world()
        lines = [
            "+" + "-" * (self.width - 2) + "+",
            "| HexiRules Control Panel".ljust(self.width - 1) + "|",
            "+" + "-" * (self.width - 2) + "+",
            "| [S]tep [C]lear [R]ule [Q]uit".ljust(self.width - 1) + "|",
            "+" + "-" * (self.width - 2) + "+",
            f"| World: {world.name}".ljust(self.width - 1) + "|",
            f"| Alive: {len(world.hex.get_active_cells())}".ljust(self.width - 1) + "|",
            "+" + "-" * (self.width - 2) + "+",
        ]
        return "\n".join(lines)

    def handle_command(self, command: str) -> bool:
        """Process a single command. Return False to exit."""
        cmd = command.strip()
        if not cmd:
            return True
        key = cmd[0].lower()
        world = self.controller.get_current_world()
        if key == "s":
            self.controller.step(world.rules_text)
            self.on_update()
            self.out.write("Stepped\n")
        elif key == "c":
            self.controller.clear()
            self.on_update()
            self.out.write("Cleared\n")
        elif key == "r":
            parts = cmd.split(" ", 1)
            if len(parts) > 1:
                world.rules_text = parts[1]
                self.out.write("Rule set\n")
            else:
                self.out.write("Usage: r RULE\n")
        elif key == "q":
            return False
        else:
            self.out.write("?\n")
        return True

    def run(self) -> None:
        """Run the interactive panel."""
        while True:
            self.out.write(self.render() + "\n> ")
            self.out.flush()
            line = self.inp.readline()
            if not line:
                break
            if not self.handle_command(line):
                break
