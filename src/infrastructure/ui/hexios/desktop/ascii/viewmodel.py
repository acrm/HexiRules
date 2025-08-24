from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from application.world_service import WorldService


@dataclass
class FrameVM:
    id: str
    title: str
    hotkey: str
    lines: List[str]


@dataclass
class HeaderVM:
    def to_frame(self) -> FrameVM:
        return FrameVM(id="header", title="HEXIOS v0.0.1 [Ctrl+Q] for quit", hotkey="", lines=[""])


@dataclass
class WorldsVM:
    world_name: str
    radius: int
    active: int
    world_names: List[str]

    def to_frame(self) -> FrameVM:
        lines: List[str] = [
            f"Current: {self.world_name}",
            f"Radius: {self.radius} | Active: {self.active}",
            "\u2500" * 36,
            "World List:",
        ]
        for i, name in enumerate(self.world_names[:10], start=1):
            mark = "*" if name == self.world_name else " "
            lines.append(f"{i}. {name} {mark}")
        return FrameVM(id="worlds", title="Worlds", hotkey="w", lines=lines)


@dataclass
class RulesVM:
    rules_text: str

    def to_frame(self) -> FrameVM:
        lines: List[str] = ["Current Rules:", "\u2500" * 36]
        if self.rules_text:
            for rule in self.rules_text.splitlines():
                rule = rule.strip()
                if rule:
                    lines.append(rule)
        return FrameVM(id="rules", title="Rules", hotkey="r", lines=lines)


@dataclass
class HistoryVM:
    generation: int
    active: int
    history_counts: List[tuple[int, int]]

    def to_frame(self) -> FrameVM:
        lines: List[str] = [
            f"Generation: {self.generation} | Active: {self.active}",
            "\u2500" * 36,
        ]
        for idx, count in self.history_counts[:12]:
            lines.append(f"Gen {idx}: {count} cells")
        return FrameVM(id="history", title="History", hotkey="h", lines=lines)


@dataclass
class LogsVM:
    logs: List[str]

    def to_frame(self) -> FrameVM:
        lines: List[str] = ["Recent Actions:", "\u2500" * 36]
        for lg in self.logs[:12]:
            lines.append(lg)
        return FrameVM(id="logs", title="Step Logs", hotkey="l", lines=lines)


@dataclass
class SelectedVM:
    text: str

    def to_frame(self) -> FrameVM:
        return FrameVM(id="selected", title=self.text, hotkey="", lines=[""])


@dataclass
class FooterVM:
    def to_frame(self) -> FrameVM:
        return FrameVM(id="footer", title=">", hotkey="", lines=[""])


@dataclass
class AsciiViewModel:
    frames: List[FrameVM]

    @staticmethod
    def from_controller(controller: WorldService, selected_info: Optional[str] = None) -> "AsciiViewModel":
        world = controller.get_current_world()
        active = len(world.hex.get_active_cells())

        header_f = HeaderVM().to_frame()
        worlds_f = WorldsVM(
            world_name=world.name,
            radius=world.radius,
            active=active,
            world_names=list(controller.worlds.keys()),
        ).to_frame()
        rules_f = RulesVM(rules_text=world.rules_text or "").to_frame()
        hist_list = controller.history_list()
        history_f = HistoryVM(
            generation=controller.history_current_index(),
            active=active,
            history_counts=hist_list,
        ).to_frame()
        logs_f = LogsVM(
            logs=controller.history_get_logs(controller.history_current_index()) or []
        ).to_frame()
        frames: List[FrameVM] = [header_f, worlds_f, rules_f, history_f, logs_f]
        if selected_info:
            frames.append(SelectedVM(text=selected_info).to_frame())
        frames.append(FooterVM().to_frame())
        return AsciiViewModel(frames=frames)
