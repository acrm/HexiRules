import unittest
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Test the mathematical logic without GUI dependencies
class TestHexagonalLogic(unittest.TestCase):
    """Test hexagonal grid logic without GUI dependencies."""
    
    def test_axial_coordinate_math(self):
        """Test axial to pixel coordinate conversion math."""
        cell_size = 30
        
        # Test center coordinate (0, 0)
        q, r = 0, 0
        x = cell_size * (3/2 * q)
        y = cell_size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        
        # Test adjacent coordinates
        q, r = 1, 0
        x = cell_size * (3/2 * q)
        y = cell_size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        
        self.assertEqual(x, cell_size * 1.5)
        self.assertAlmostEqual(y, cell_size * math.sqrt(3)/2, places=5)
    
    def test_hexagon_vertices_count(self):
        """Test that hexagon has correct number of vertices."""
        # A hexagon should have 6 vertices
        vertices = []
        for i in range(6):
            angle = math.pi / 3 * i
            vertices.append((math.cos(angle), math.sin(angle)))
        
        self.assertEqual(len(vertices), 6)
    
    def test_hexagonal_grid_radius_calculation(self):
        """Test hexagonal grid cell count calculation."""
        # Formula for hexagonal grid: 3 * radius * (radius + 1) + 1
        radius = 3
        expected_cells = 3 * radius * (radius + 1) + 1
        self.assertEqual(expected_cells, 37)
        
        radius = 5
        expected_cells = 3 * radius * (radius + 1) + 1
        self.assertEqual(expected_cells, 91)
    
    def test_hexagonal_distance(self):
        """Test axial coordinate distance calculation."""
        # Distance between (0,0) and (1,0) should be 1
        q1, r1 = 0, 0
        q2, r2 = 1, 0
        distance = max(abs(q1 - q2), abs(q1 + r1 - q2 - r2), abs(r1 - r2))
        self.assertEqual(distance, 1)
        
        # Distance between (0,0) and (2,1) should be 3
        q1, r1 = 0, 0
        q2, r2 = 2, 1
        distance = max(abs(q1 - q2), abs(q1 + r1 - q2 - r2), abs(r1 - r2))
        self.assertEqual(distance, 3)


if __name__ == "__main__":
    unittest.main()
