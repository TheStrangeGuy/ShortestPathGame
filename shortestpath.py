import tkinter as tk
from queue import PriorityQueue

# Constants
DEFAULT_GRID_SIZE = 20
CELL_SIZE = 30
BORDER_WIDTH = 50
MAX_WINDOW_SIZE = 700  # Max window size to fit on screen

# Colors
EMPTY_COLOR = "white"
OBSTACLE_COLOR = "black"
START_COLOR = "green"
END_COLOR = "red"
PATH_COLOR = "yellow"
VISITED_COLOR = "lightgray"

class ShortestPathGame:
    def __init__(self, grid_size=DEFAULT_GRID_SIZE):
        self.grid_size = grid_size
        self.cell_size = CELL_SIZE

        # Adjust cell size if the grid is too large
        self.window_size = grid_size * CELL_SIZE + 2 * BORDER_WIDTH
        if self.window_size > MAX_WINDOW_SIZE:
            self.cell_size = (MAX_WINDOW_SIZE - 2 * BORDER_WIDTH) // grid_size
            self.window_size = grid_size * self.cell_size + 2 * BORDER_WIDTH

        self.window = tk.Tk()
        self.window.title("Easiest Path Game")

        self.canvas = tk.Canvas(self.window, width=self.window_size, height=self.window_size, bg=EMPTY_COLOR, highlightthickness=0)
        self.canvas.pack(padx=5, pady=5)

        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.start = None
        self.end = None
        self.drawing = False
        self.visited_cells = set()
        self.create_grid()

        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_obstacle)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        self.canvas.bind("<Button-3>", self.set_start_or_end)
        self.window.bind("<Return>", self.find_shortest_path)

        self.add_ui_controls()

    def create_grid(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x1 = col * self.cell_size + BORDER_WIDTH
                y1 = row * self.cell_size + BORDER_WIDTH
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=EMPTY_COLOR, outline="gray")
                self.grid[row][col] = rect

    def start_drawing(self, event):
        self.drawing = True
        self.add_obstacle(event)

    def draw_obstacle(self, event):
        if self.drawing:
            self.add_obstacle(event)

    def stop_drawing(self, event):
        self.drawing = False

    def add_obstacle(self, event):
        col, row = (event.x - BORDER_WIDTH) // self.cell_size, (event.y - BORDER_WIDTH) // self.cell_size
        if (
            0 <= row < self.grid_size
            and 0 <= col < self.grid_size
            and (row, col) != self.start
            and (row, col) != self.end
            and (row, col) not in self.visited_cells
        ):
            self.canvas.itemconfig(self.grid[row][col], fill=OBSTACLE_COLOR)

    def set_start_or_end(self, event):
        col, row = (event.x - BORDER_WIDTH) // self.cell_size, (event.y - BORDER_WIDTH) // self.cell_size
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            if not self.start:
                self.start = (row, col)
                self.canvas.itemconfig(self.grid[row][col], fill=START_COLOR)
            elif not self.end:
                self.end = (row, col)
                self.canvas.itemconfig(self.grid[row][col], fill=END_COLOR)

    def show_no_path_window(self):
        no_path_window = tk.Toplevel(self.window)
        no_path_window.title("No Path Found")
        no_path_window.geometry("200x100")
        label = tk.Label(no_path_window, text="No path found!", font=("Arial", 12))
        label.pack(pady=10)
        restart_button = tk.Button(no_path_window, text="Restart", command=self.restart_game)
        restart_button.pack(pady=5)

    def restart_game(self):
        self.window.destroy()
        self.__init__(grid_size=self.grid_size)
        self.run()

    def heuristic(self, current, goal):
        # Manhattan distance heuristic
        return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

    def find_shortest_path(self, event):
        if not self.start or not self.end:
            print("Start or end point not set!")
            return

        # A* Algorithm
        def neighbors(row, col):
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, c = row + dr, col + dc
                if 0 <= r < self.grid_size and 0 <= c < self.grid_size and self.canvas.itemcget(self.grid[r][c], "fill") != OBSTACLE_COLOR:
                    yield r, c

        start_row, start_col = self.start
        end_row, end_col = self.end
        open_set = PriorityQueue()
        open_set.put((0, start_row, start_col, []))
        g_score = {self.start: 0}
        visited = set()

        while not open_set.empty():
            _, row, col, path = open_set.get()
            if (row, col) in visited:
                continue
            visited.add((row, col))
            self.visited_cells.add((row, col))

            # Visualize visiting
            if (row, col) != self.start and (row, col) != self.end:
                self.canvas.itemconfig(self.grid[row][col], fill=VISITED_COLOR)
            self.window.update()
            self.window.after(10)

            # Check if reached end
            if (row, col) == self.end:
                for r, c in path:
                    if (r, c) != self.start and (r, c) != self.end:
                        self.canvas.itemconfig(self.grid[r][c], fill=PATH_COLOR)
                return

            for r, c in neighbors(row, col):
                temp_g_score = g_score.get((row, col), float("inf")) + 1
                if temp_g_score < g_score.get((r, c), float("inf")):
                    g_score[(r, c)] = temp_g_score
                    f_score = temp_g_score + self.heuristic((r, c), self.end)
                    open_set.put((f_score, r, c, path + [(r, c)]))

        print("No path found!")
        self.show_no_path_window()

    def add_ui_controls(self):
        controls_frame = tk.Frame(self.window)
        controls_frame.pack(pady=10)

        restart_button = tk.Button(controls_frame, text="Restart", command=self.restart_game)
        restart_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(controls_frame, text="Clear All", command=self.clear_all)
        clear_button.pack(side=tk.LEFT, padx=5)

    def clear_all(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.canvas.itemconfig(self.grid[row][col], fill=EMPTY_COLOR)
        self.start = None
        self.end = None
        self.visited_cells.clear()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    def choose_grid_size():
        size_window = tk.Tk()
        size_window.title("Choose Grid Size")
        size_window.geometry("250x150")

        tk.Label(size_window, text="Select Grid Size:").pack(pady=10)
        size_var = tk.IntVar(value=DEFAULT_GRID_SIZE)

        tk.Scale(size_window, from_=10, to=50, orient=tk.HORIZONTAL, variable=size_var).pack(pady=10)

        def start_game():
            size = size_var.get()
            size_window.destroy()
            game = ShortestPathGame(grid_size=size)
            game.run()

        start_button = tk.Button(size_window, text="Start", command=start_game)
        start_button.pack(pady=10)

        size_window.mainloop()

    choose_grid_size()