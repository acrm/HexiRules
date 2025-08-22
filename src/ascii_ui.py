"""Small ascii-ui framework for composing fixed-size ASCII panels.

This module provides simple composition primitives that guarantee a
fixed output width (80 chars) and height (80 lines). It returns a list
of lines together with per-line tag spans for coloring in a tkinter
Text widget. Each frame controls its own borders and content.
"""

from __future__ import annotations

from typing import List, Tuple, Dict, Callable, Any, Optional
from application.world_service import WorldService

WIDTH = 80
HEIGHT = 80


class Frame:
    """A frame that controls its own borders and content rendering."""

    def __init__(self, x: int, y: int, width: int, height: int, title: str = ""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.content_lines: List[str] = []
        self.content_tags: List[List[Tuple[int, int, str]]] = []

    def set_content(
        self, lines: List[str], tags: Optional[List[List[Tuple[int, int, str]]]] = None
    ):
        """Set the content lines and tags for this frame."""
        self.content_lines = lines
        self.content_tags = tags or [[] for _ in lines]

    def render_to(
        self, canvas: List[List[str]], tag_canvas: List[List[Tuple[int, int, str]]]
    ):
        """Render this frame to the canvas with proper border control."""
        # Determine which borders this frame should draw
        draws_left = self.x == 0
        draws_right = self.x + self.width == WIDTH
        draws_center = (
            self.x == 0 and self.width == WIDTH // 2
        )  # Left frame draws center border

        # Draw title row with borders
        if self.title:
            title_line = self.title.center(self.width - 2) if self.width > 2 else ""
            row = ["║", *list(title_line[: self.width - 2].ljust(self.width - 2)), "║"]
        else:
            row = ["║"] + [" "] * (self.width - 2) + ["║"]

        # Apply border logic
        if draws_left:
            canvas[self.y][self.x] = row[0]
        if draws_center:
            canvas[self.y][self.x + self.width - 1] = "║"
        if draws_right:
            canvas[self.y][self.x + self.width - 1] = row[-1]

        # Fill content area
        for i in range(1, self.width - 1):
            if self.title and i - 1 < len(title_line):
                canvas[self.y][self.x + i] = title_line[i - 1]

        # Draw content lines
        content_start_y = self.y + 1
        for i, line in enumerate(self.content_lines):
            if content_start_y + i >= self.y + self.height - 1:
                break

            row_y = content_start_y + i
            # Truncate/pad content to fit inside borders
            content_width = self.width - 2
            display_line = line[:content_width].ljust(content_width)

            # Set borders
            if draws_left:
                canvas[row_y][self.x] = "║"
            if draws_center:
                canvas[row_y][self.x + self.width - 1] = "║"
            if draws_right:
                canvas[row_y][self.x + self.width - 1] = "║"

            # Fill content
            for j, char in enumerate(display_line):
                canvas[row_y][self.x + 1 + j] = char

            # Apply tags for this line
            if i < len(self.content_tags):
                for start, end, tag in self.content_tags[i]:
                    # Adjust tag positions to account for border
                    adj_start = self.x + 1 + start
                    adj_end = min(self.x + 1 + end, self.x + self.width - 1)
                    if adj_start < adj_end:
                        tag_canvas[row_y].append((adj_start, adj_end, tag))


class AsciiUILayout:
    """Compose a full 80x80 rendering from application data with proper frame border control."""

    def __init__(self, controller: WorldService) -> None:
        self.controller = controller

    def render(self) -> Tuple[List[str], List[List[Tuple[int, int, str]]]]:
        world = self.controller.get_current_world()
        active = len(world.hex.get_active_cells())

        # Create canvas
        canvas = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]
        tag_canvas: List[List[Tuple[int, int, str]]] = [[] for _ in range(HEIGHT)]

        # Draw top border
        for i in range(WIDTH):
            if i == 0:
                canvas[0][i] = "╔"
            elif i == WIDTH - 1:
                canvas[0][i] = "╗"
            elif i == WIDTH // 2:
                canvas[0][i] = "╦"
            else:
                canvas[0][i] = "═"

        # Title line with left-aligned title and right-aligned Esc hint
        from version import __version__

        title_left = f"HEXIOS v.{__version__}"
        title_right = "Esc: Exit"
        title_space = WIDTH - 2 - len(title_left) - len(title_right)
        title_line = title_left + " " * title_space + title_right

        for i, char in enumerate(title_line[: WIDTH - 2]):
            canvas[1][i + 1] = char
        canvas[1][0] = "║"
        canvas[1][WIDTH // 2] = "║"
        canvas[1][WIDTH - 1] = "║"

        # Separator after title
        for i in range(WIDTH):
            if i == 0:
                canvas[2][i] = "╠"
            elif i == WIDTH - 1:
                canvas[2][i] = "╣"
            elif i == WIDTH // 2:
                canvas[2][i] = "╬"
            else:
                canvas[2][i] = "═"

        # Create frames
        worlds_frame = Frame(0, 3, WIDTH // 2, 23, "WORLDS")
        rules_frame = Frame(WIDTH // 2, 3, WIDTH // 2, 23, "RULES")
        history_frame = Frame(0, 26, WIDTH // 2, 23, "HISTORY")
        logs_frame = Frame(WIDTH // 2, 26, WIDTH // 2, 23, "STEP LOGS")

        # Populate Worlds frame
        worlds_content = []
        worlds_content.append(f"Current: {world.name[:20]:20}")
        worlds_content.append(f"Radius: {world.radius:2} | Active: {active:3}")
        worlds_content.append("─" * 36)
        worlds_content.append("World List:")

        worlds = list(self.controller.worlds.keys())
        for i, name in enumerate(worlds[:5]):
            prefix = f"{i + 1}. "
            text = prefix + name
            if name == world.name:
                worlds_content.append(f"{text[:35]:35}")
            else:
                worlds_content.append(f"{text[:35]:35}")

        worlds_content.extend(
            [
                "─" * 36,
                "Hotkeys:",
                "[n] New World",
                "[d] Delete Current",
                "[s] Select World",
                "[↑↓] Navigate List",
            ]
        )

        worlds_frame.set_content(worlds_content)

        # Populate Rules frame
        rules_content = []
        rules_content.append("Current Rules:")
        rules_content.append("─" * 36)

        rules = world.rules_text.split("\n") if world.rules_text else []
        for rule in rules[:15]:
            rule = rule.strip()
            if rule:
                if ">=" in rule or "=>" in rule:
                    parts = rule.split("=>") if "=>" in rule else rule.split(">=")
                    pattern = parts[0].strip()
                    result = parts[1].strip() if len(parts) > 1 else ""
                    display = f"{pattern} → {result}"
                else:
                    display = rule
                rules_content.append(display[:36])

        rules_frame.set_content(rules_content)

        # Populate History frame
        history_content = []
        history_content.append(
            f"Generation: {self.controller.history_current_index():3} | Active: {active:3}"
        )
        history_content.append("─" * 36)

        history = self.controller.history_list()
        for i, (idx, count) in enumerate(history[:10]):
            history_content.append(f"Gen {idx:2}: {count:3} cells")

        history_content.extend(
            ["─" * 36, "Navigation:", "[p] Previous Step", "[n] Next Step"]
        )

        history_frame.set_content(history_content)

        # Populate Logs frame
        logs_content = []
        logs_content.append("Recent Actions:")
        logs_content.append("─" * 36)

        logs = (
            self.controller.history_get_logs(self.controller.history_current_index())
            if history
            else []
        )
        for log in logs[:10]:
            logs_content.append(log[:36])

        logs_content.extend(
            [
                "─" * 36,
                "Debug Info:",
                f"Cells processed: {active * 7}",
                f"Rules checked: {len([r for r in rules if r.strip()])}",
            ]
        )

        logs_frame.set_content(logs_content)

        # Render all frames
        worlds_frame.render_to(canvas, tag_canvas)
        rules_frame.render_to(canvas, tag_canvas)
        history_frame.render_to(canvas, tag_canvas)
        logs_frame.render_to(canvas, tag_canvas)

        # Draw middle separator
        for i in range(WIDTH):
            if i == 0:
                canvas[25][i] = "╠"
            elif i == WIDTH - 1:
                canvas[25][i] = "╣"
            elif i == WIDTH // 2:
                canvas[25][i] = "╬"
            else:
                canvas[25][i] = "═"

        # Draw bottom border
        for i in range(WIDTH):
            if i == 0:
                canvas[49][i] = "╚"
            elif i == WIDTH - 1:
                canvas[49][i] = "╝"
            elif i == WIDTH // 2:
                canvas[49][i] = "╩"
            else:
                canvas[49][i] = "═"

        # Command area
        for i in range(50, 54):
            if i == 50:
                line = "┌─ Command Input " + "─" * 62 + "┐"
            elif i == 51:
                line = "│ > " + " " * 75 + "│"
            elif i == 52:
                line = "│" + " " * 78 + "│"
            else:
                line = "└" + "─" * 78 + "┘"
            for j, char in enumerate(line):
                canvas[i][j] = char

        # Convert canvas to strings
        result_lines = ["".join(row) for row in canvas]
        result_tags = tag_canvas

        # Ensure exact HEIGHT
        while len(result_lines) < HEIGHT:
            result_lines.append(" " * WIDTH)
            result_tags.append([])

        return result_lines[:HEIGHT], result_tags[:HEIGHT]


class AsciiControlPanel:
    """ASCII control panel for command-line interface testing."""

    def __init__(
        self,
        controller: WorldService,
        quit_callback: Callable[[], None],
        input_stream=None,
        output_stream=None,
    ):
        self.controller = controller
        self.quit_callback = quit_callback
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.width = 80

    def render(self) -> str:
        """Render the current state as a string."""
        layout = AsciiUILayout(self.controller)
        lines, _ = layout.render()
        return "\n".join(lines)

    def run(self) -> None:
        """Run the command loop."""
        import sys

        input_stream = self.input_stream or sys.stdin
        output_stream = self.output_stream or sys.stdout

        while True:
            try:
                line = input_stream.readline()
                if not line:
                    break

                command = line.strip()
                if not command:
                    continue

                if command == "q":
                    break
                elif command.startswith("r "):
                    # Rule command: r <rule>
                    rule_text = command[2:].strip()
                    world = self.controller.get_current_world()
                    world.rules_text = rule_text
                    if self.output_stream:
                        self.output_stream.write("Rule set\n")
                elif command == "s":
                    # Step command
                    world = self.controller.get_current_world()
                    self.controller.step(world.rules_text or "")
                    if self.output_stream:
                        self.output_stream.write("Stepped\n")
                elif command == "c":
                    # Clear command
                    world = self.controller.get_current_world()
                    world.hex.clear()
                    if self.output_stream:
                        self.output_stream.write("Cleared\n")

            except (EOFError, KeyboardInterrupt):
                break
