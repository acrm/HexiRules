"""ASCII UI facade: exposes AsciiUILayout and AsciiControlPanel using new ui.ascii modules."""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple
from application.world_service import WorldService
from ui.ascii.viewmodel import AsciiViewModel
from ui.ascii.renderer import (
    AsciiRenderer,
    GridLayoutSpec,
    SelectionState,
)


class AsciiUILayout:
    def __init__(
        self,
        controller: WorldService,
        selection: Optional[SelectionState] = None,
        selected_info: Optional[str] = None,
    ) -> None:
        self.controller = controller
        self.selection = selection or SelectionState(mode="top")
        self.selected_info = selected_info

    def render(self) -> Tuple[List[str], List[List[Tuple[int, int, str]]]]:
        vm = AsciiViewModel.from_controller(
            self.controller, selected_info=self.selected_info
        )
        layout = GridLayoutSpec.default_layout()
        renderer = AsciiRenderer(vm, layout, self.selection)
        return renderer.render()


class AsciiControlPanel:
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
        self.width = 81  # height controlled by renderer/GUI (now 51 lines)

    def render(self) -> str:
        layout = AsciiUILayout(self.controller)
        lines, _ = layout.render()
        return "\n".join(lines)

    def run(self) -> None:
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
                    rule_text = command[2:].strip()
                    world = self.controller.get_current_world()
                    world.rules_text = rule_text
                    if self.output_stream:
                        self.output_stream.write("Rule set\n")
                elif command == "s":
                    world = self.controller.get_current_world()
                    self.controller.step(world.rules_text or "")
                    if self.output_stream:
                        self.output_stream.write("Stepped\n")
                elif command == "c":
                    world = self.controller.get_current_world()
                    world.hex.clear()
                    if self.output_stream:
                        self.output_stream.write("Cleared\n")
            except (EOFError, KeyboardInterrupt):
                break
