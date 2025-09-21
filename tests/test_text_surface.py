import unittest

from application.text_surface import render_world_to_text
from domain.worlds.world import World


class TestTextSurface(unittest.TestCase):
    def test_basic_frame_dimensions(self) -> None:
        w = World(name="T", radius=6)
        frame = render_world_to_text(w, history_index=0, width=40, height=10)
        lines = frame.splitlines()
        self.assertLessEqual(len(lines), 10)
        self.assertTrue(lines[0].startswith("HexiOS"))
        for ln in lines:
            self.assertLessEqual(len(ln), 40)

    def test_active_cells_render_as_letters(self) -> None:
        w = World(name="T", radius=6)
        # place two active cells with distinct states
        w.hex.set_cell(0, 0, "a", None)
        w.hex.set_cell(1, -1, "b", None)
        frame = render_world_to_text(w, history_index=0, width=120, height=40)
        self.assertIn("a", frame)
        self.assertIn("b", frame)

    def test_smoke_after_step(self) -> None:
        w = World(name="T", radius=6, rules_text="")
        w.hex.set_cell(0, 0, "a", None)
        before = render_world_to_text(w, history_index=0, width=80, height=24)
        # step without rules: should not raise and frame remains a string
        w.hex.step()
        after = render_world_to_text(w, history_index=1, width=80, height=24)
        self.assertIsInstance(before, str)
        self.assertIsInstance(after, str)


if __name__ == "__main__":
    unittest.main()
