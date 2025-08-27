import unittest
from infrastructure.ui.hexios.desktop.ascii.renderer import AsciiRenderer
from tests.ascii_samples import sample_border, sample_selection, sample_text


class TestAsciiRenderer(unittest.TestCase):
    def test_border_rendering(self) -> None:
        vm, layout, selection, expected = sample_border()
        renderer = AsciiRenderer(vm, layout, selection)
        lines, _ = renderer.render()
        self.assertEqual(lines, expected)

    def test_text_rendering(self) -> None:
        vm, layout, selection, expected = sample_text()
        renderer = AsciiRenderer(vm, layout, selection)
        lines, _ = renderer.render()
        self.assertEqual(lines, expected)

    def test_selection_tag(self) -> None:
        vm, layout, selection, expected = sample_selection()
        renderer = AsciiRenderer(vm, layout, selection)
        lines, tags = renderer.render()
        self.assertEqual(lines, expected)
        self.assertIn((0, 7, "border_sel"), tags[0])
        self.assertIn((7, 14, "border"), tags[0])


if __name__ == "__main__":
    unittest.main()
