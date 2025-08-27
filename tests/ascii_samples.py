from infrastructure.ui.hexios.desktop.ascii.viewmodel import AsciiViewModel, FrameVM
from infrastructure.ui.hexios.desktop.ascii.renderer import (
    GridLayoutSpec,
    SelectionState,
)
from typing import List, Tuple


def sample_border() -> Tuple[AsciiViewModel, GridLayoutSpec, SelectionState, List[str]]:
    vm = AsciiViewModel(frames=[FrameVM(id="header", title="A", hotkey="", lines=[""])])
    layout = GridLayoutSpec(
        width=7,
        height=3,
        header=(0, 0, 7, 3),
        worlds=(0, 0, 0, 0),
        rules=(0, 0, 0, 0),
        history=(0, 0, 0, 0),
        logs=(0, 0, 0, 0),
        selected=(0, 0, 0, 0),
        footer=(0, 0, 0, 0),
    )
    selection = SelectionState(mode="top")
    expected = ["┌─ A ─┐", "│     │", "└─────┘"]
    return vm, layout, selection, expected


def sample_text() -> Tuple[AsciiViewModel, GridLayoutSpec, SelectionState, List[str]]:
    vm = AsciiViewModel(
        frames=[FrameVM(id="worlds", title="T", hotkey="", lines=["abc", "defg"])]
    )
    layout = GridLayoutSpec(
        width=10,
        height=5,
        header=(0, 0, 0, 0),
        worlds=(0, 0, 10, 5),
        rules=(0, 0, 0, 0),
        history=(0, 0, 0, 0),
        logs=(0, 0, 0, 0),
        selected=(0, 0, 0, 0),
        footer=(0, 0, 0, 0),
    )
    selection = SelectionState(mode="top")
    expected = [
        "┌── T ───┐",
        "│abc     │",
        "│defg    │",
        "│        │",
        "└────────┘",
    ]
    return vm, layout, selection, expected


def sample_selection() -> (
    Tuple[AsciiViewModel, GridLayoutSpec, SelectionState, List[str]]
):
    vm = AsciiViewModel(
        frames=[
            FrameVM(id="worlds", title="W", hotkey="", lines=[""]),
            FrameVM(id="rules", title="R", hotkey="", lines=[""]),
        ]
    )
    layout = GridLayoutSpec(
        width=14,
        height=3,
        header=(0, 0, 0, 0),
        worlds=(0, 0, 7, 3),
        rules=(7, 0, 7, 3),
        history=(0, 0, 0, 0),
        logs=(0, 0, 0, 0),
        selected=(0, 0, 0, 0),
        footer=(0, 0, 0, 0),
    )
    selection = SelectionState(mode="frame", frame_id="worlds")
    expected = ["┌─ W ─┐┌─ R ─┐", "│     ││     │", "└─────┘└─────┘"]
    return vm, layout, selection, expected
