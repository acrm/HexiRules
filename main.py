import math
import tkinter as tk

CELL_SIZE = 20
GRID_RADIUS = 5


class HexCanvas(tk.Canvas):
    def __init__(self, master, radius=GRID_RADIUS, cell_size=CELL_SIZE, **kwargs):
        width = int(cell_size * 3/2 * (radius * 2 + 1) + cell_size)
        height = int(cell_size * math.sqrt(3) * (radius * 2 + 1) + cell_size)
        super().__init__(master, width=width, height=height, **kwargs)
        self.radius = radius
        self.cell_size = cell_size
        self.cells = {}
        self.draw_grid()

    def axial_to_pixel(self, q, r):
        x = self.cell_size * (3/2 * q)
        y = self.cell_size * (math.sqrt(3) / 2 * q + math.sqrt(3) * r)
        return x + self.cell_size, y + self.cell_size

    def polygon_corners(self, x, y):
        points = []
        for i in range(6):
            angle = math.pi / 3 * i + math.pi / 6
            px = x + self.cell_size * math.cos(angle)
            py = y + self.cell_size * math.sin(angle)
            points.extend([px, py])
        return points

    def draw_hex(self, q, r, fill="white"):
        x, y = self.axial_to_pixel(q, r)
        poly = self.create_polygon(self.polygon_corners(x, y), outline="gray", fill=fill)
        self.cells[(q, r)] = poly

    def draw_grid(self):
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                if abs(q + r) <= self.radius:
                    self.draw_hex(q, r)


class Automaton:
    def __init__(self, canvas, rule="B3/S23"):
        self.canvas = canvas
        self.state = {}
        self.parse_rule(rule)

    def parse_rule(self, rule):
        try:
            birth, survive = rule.split("/")
            self.birth = [int(n) for n in birth[1:]]
            self.survive = [int(n) for n in survive[1:]]
            self.rule = rule
        except Exception:
            self.birth = [3]
            self.survive = [2, 3]
            self.rule = "B3/S23"

    def toggle_cell(self, q, r):
        key = (q, r)
        if key in self.state:
            del self.state[key]
            self.canvas.itemconfig(self.canvas.cells[key], fill="white")
        else:
            self.state[key] = 1
            self.canvas.itemconfig(self.canvas.cells[key], fill="black")

    def neighbors(self, q, r):
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        for dq, dr in directions:
            yield q + dq, r + dr

    def step(self):
        counts = {}
        for q, r in self.state:
            for nq, nr in self.neighbors(q, r):
                counts[(nq, nr)] = counts.get((nq, nr), 0) + 1
        new_state = {}
        for cell, count in counts.items():
            if cell in self.state:
                if count in self.survive:
                    new_state[cell] = 1
            else:
                if count in self.birth:
                    new_state[cell] = 1
        for cell in self.canvas.cells:
            color = "black" if cell in new_state else "white"
            self.canvas.itemconfig(self.canvas.cells[cell], fill=color)
        self.state = new_state


def main():
    root = tk.Tk()
    root.title("HexiRules")

    canvas = HexCanvas(root)
    canvas.pack()

    automaton = Automaton(canvas)

    rule_var = tk.StringVar(value=automaton.rule)
    rule_entry = tk.Entry(root, textvariable=rule_var)
    rule_entry.pack(side=tk.LEFT, padx=5)

    def apply_rule():
        automaton.parse_rule(rule_var.get())

    tk.Button(root, text="Set Rule", command=apply_rule).pack(side=tk.LEFT)

    running = {"active": False}

    def on_click(event):
        # determine which cell was clicked
        x, y = event.x, event.y
        for (q, r), item in canvas.cells.items():
            if canvas.type(item) == "polygon":
                if canvas.find_withtag(tk.CURRENT):
                    current = canvas.find_withtag(tk.CURRENT)[0]
                else:
                    current = None
                if item == current:
                    automaton.toggle_cell(q, r)
                    break

    canvas.bind("<Button-1>", on_click)

    def toggle_running():
        running["active"] = not running["active"]
        if running["active"]:
            run_step()

    def run_step():
        if running["active"]:
            automaton.step()
            root.after(200, run_step)

    tk.Button(root, text="Start/Stop", command=toggle_running).pack(side=tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    main()
