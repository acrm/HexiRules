import math
import tkinter as tk
from typing import Dict, Tuple, Optional

from automaton import Automaton
from version import __version__

CELL_SIZE = 30
GRID_RADIUS = 8
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class HexCanvas(tk.Canvas):
    def __init__(self, master: tk.Widget, radius: int = GRID_RADIUS, 
                 window_width: int = WINDOW_WIDTH, window_height: int = WINDOW_HEIGHT, **kwargs) -> None:
        # Calculate cell size based on window dimensions to fit the grid
        max_cells_x = radius * 2 + 1
        max_cells_y = radius * 2 + 1
        
        # Calculate optimal cell size to fit window
        cell_size_x = window_width / (max_cells_x * 1.5)
        cell_size_y = (window_height - 80) / (max_cells_y * math.sqrt(3))  # Reserve space for controls
        
        cell_size = min(cell_size_x, cell_size_y)
        
        # Calculate actual canvas dimensions
        canvas_width = int(cell_size * 1.5 * max_cells_x + cell_size)
        canvas_height = int(cell_size * math.sqrt(3) * max_cells_y + cell_size)
        
        super().__init__(master, width=canvas_width, height=canvas_height, bg="lightgray", **kwargs)
        self.radius = radius
        self.cell_size = cell_size
        self.cells = {}
        self.center_x = canvas_width // 2
        self.center_y = canvas_height // 2
        self.draw_grid()

    def axial_to_pixel(self, q, r):
        # Convert axial coordinates to pixel coordinates with proper centering
        x = self.cell_size * (3/2 * q)
        y = self.cell_size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        return x + self.center_x, y + self.center_y

    def polygon_corners(self, x, y):
        points = []
        radius = self.cell_size * 0.98  # Make hexagons almost touch each other (remove gaps)
        for i in range(6):
            # Start from top vertex (flat-top hexagons)
            angle = math.pi / 3 * i
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.extend([px, py])
        return points

    def draw_hex(self, q, r, fill="white"):
        x, y = self.axial_to_pixel(q, r)
        poly = self.create_polygon(self.polygon_corners(x, y), outline="gray", fill=fill, width=1)
        self.cells[(q, r)] = poly

    def draw_grid(self):
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                if abs(q + r) <= self.radius:
                    self.draw_hex(q, r)




def main() -> None:
    """Main application entry point."""
    try:
        root = tk.Tk()
        root.title(f"HexiRules v{__version__} - Hexagonal Cellular Automaton")
        
        # Set fixed window size
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        root.resizable(False, False)
        
        # Center the window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Create canvas that fits the window
        canvas = HexCanvas(root)
        canvas.pack(expand=True, fill="both", padx=10, pady=10)

        automaton = Automaton()

        def refresh_canvas() -> None:
            """Update canvas to reflect current automaton state."""
            for cell in canvas.cells:
                color = "black" if cell in automaton.state else "white"
                canvas.itemconfig(canvas.cells[cell], fill=color)

        # Create control frame
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        rule_var = tk.StringVar(value=automaton.rule)
        tk.Label(control_frame, text="Rule:").pack(side=tk.LEFT, padx=5)
        rule_entry = tk.Entry(control_frame, textvariable=rule_var, width=10)
        rule_entry.pack(side=tk.LEFT, padx=5)

        def apply_rule():
            automaton.parse_rule(rule_var.get())

        tk.Button(control_frame, text="Set Rule", command=apply_rule).pack(side=tk.LEFT, padx=5)

        running = {"active": False}
        start_stop_button = tk.Button(control_frame, text="Start", command=lambda: None)

        def on_click(event):
            # determine which cell was clicked
            clicked_item = canvas.find_closest(event.x, event.y)[0]
            for (q, r), item in canvas.cells.items():
                if item == clicked_item:
                    automaton.toggle_cell(q, r)
                    color = "black" if (q, r) in automaton.state else "white"
                    canvas.itemconfig(item, fill=color)
                    break

        canvas.bind("<Button-1>", on_click)

        def toggle_running():
            running["active"] = not running["active"]
            if running["active"]:
                start_stop_button.config(text="Stop", bg="lightcoral")
                run_step()
            else:
                start_stop_button.config(text="Start", bg="lightgreen")

        def run_step():
            if running["active"]:
                automaton.step()
                refresh_canvas()
                root.after(200, run_step)

        start_stop_button.config(command=toggle_running, bg="lightgreen")
        start_stop_button.pack(side=tk.LEFT, padx=5)
        
        # Add clear button
        def clear_grid():
            automaton.state = {}
            refresh_canvas()
        
        tk.Button(control_frame, text="Clear", command=clear_grid).pack(side=tk.LEFT, padx=5)

        root.mainloop()
        
    except Exception as e:
        print(f"Error running HexiRules: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    main()
