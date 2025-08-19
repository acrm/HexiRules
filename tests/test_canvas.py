import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Skip GUI tests if no display is available (e.g., in CI environments)
try:
    import tkinter as tk

    # Test if we can create a Tk instance
    test_root = tk.Tk()
    test_root.withdraw()
    test_root.destroy()
    GUI_AVAILABLE = True
    from main import HexCanvas
except Exception:
    GUI_AVAILABLE = False
    HexCanvas = None


class TestHexCanvas(unittest.TestCase):
    def setUp(self):
        if not GUI_AVAILABLE:
            self.skipTest("GUI not available (no display)")

        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests

    def tearDown(self):
        if hasattr(self, "root"):
            self.root.destroy()

    def test_canvas_creation(self):
        canvas = HexCanvas(self.root, radius=3)
        self.assertIsNotNone(canvas)
        self.assertEqual(canvas.radius, 3)
        self.assertGreater(len(canvas.cells), 0)

    def test_axial_to_pixel_conversion(self):
        canvas = HexCanvas(self.root, radius=2)
        x, y = canvas.axial_to_pixel(0, 0)
        # Center cell should be at canvas center
        self.assertEqual(x, canvas.center_x)
        self.assertEqual(y, canvas.center_y)

    def test_hex_grid_size(self):
        radius = 3
        canvas = HexCanvas(self.root, radius=radius)
        expected_cells = 3 * radius * (radius + 1) + 1
        self.assertEqual(len(canvas.cells), expected_cells)

    def test_polygon_corners_count(self):
        canvas = HexCanvas(self.root, radius=2)
        corners = canvas.polygon_corners(100, 100)
        # Should have 12 coordinates (6 points * 2 coordinates each)
        self.assertEqual(len(corners), 12)


if __name__ == "__main__":
    unittest.main()
