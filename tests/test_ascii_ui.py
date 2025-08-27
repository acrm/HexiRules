import io
import os
import tempfile
import unittest

from infrastructure.ui.hexios.desktop.ascii.facade import AsciiControlPanel
from application.world_service import WorldService


class TestAsciiUI(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["HEXI_DATA_DIR"] = self.tmp.name
        self.controller = WorldService()
        self.controller.create_world("w", 3, True, "a => _")
        self.controller.select_world("w")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_render_width(self) -> None:
        panel = AsciiControlPanel(self.controller, lambda: None)
        lines = panel.render().splitlines()
        width = max(len(line) for line in lines)
        self.assertEqual(width, panel.width)

    def test_render_no_world(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HEXI_DATA_DIR"] = tmp
            controller = WorldService()
            panel = AsciiControlPanel(controller, lambda: None)
            lines = panel.render().splitlines()
            width = max(len(line) for line in lines)
            self.assertEqual(width, panel.width)
            self.assertIn("No world selected", panel.render())

    def test_run_commands(self) -> None:
        world = self.controller.get_current_world()
        world.hex.set_cell(0, 0, "a")
        inp = io.StringIO("r a=>a\ns\nc\nq\n")
        out = io.StringIO()
        panel = AsciiControlPanel(
            self.controller, lambda: None, input_stream=inp, output_stream=out
        )
        panel.run()
        self.assertEqual(world.rules_text.strip(), "a=>a")
        self.assertEqual(world.hex.get_cell(0, 0).state, "_")
        self.assertIn("Rule set", out.getvalue())
        self.assertIn("Stepped", out.getvalue())
        self.assertIn("Cleared", out.getvalue())


if __name__ == "__main__":
    unittest.main()
