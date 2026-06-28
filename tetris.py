import tkinter as tk
import random

# --- CONFIGURATION & PREMIUM STYLING ---
CELL_SIZE = 35  # Clean sizing for modern displays
COLS = 10
ROWS = 20

# Premium Color Palette (Cyberpunk / Modern Luxury Dark Mode)
BG_COLOR = "#0D0E15"       # Deep obsidian background
GRID_COLOR = "#1A1C28"     # Subtle dark grid lines
PANEL_COLOR = "#161824"    # Background for side panels
TEXT_COLOR = "#E2E8F0"     # Crisp off-white text
ACCENT_COLOR = "#6366F1"   # Royal indigo accent

SHAPE_COLORS = {
    'I': "#06B6D4",  # Electric Cyan
    'O': "#EAB308",  # Gold / Amber
    'T': "#A855F7",  # Deep Purple
    'S': "#22C55E",  # Emerald Green
    'Z': "#EF4444",  # Ruby Red
    'L': "#F97316",  # Tangerine Orange
    'J': "#3B82F6"   # Sapphire Blue
}

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'L': [[1, 0, 0], [1, 1, 1]],
    'J': [[0, 0, 1], [1, 1, 1]]
}


class TetraxFullScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("TETRAX // PREMIUM")
        self.root.configure(bg=BG_COLOR)
        
        # --- FULLSCREEN SETUP ---
        self.root.attributes("-fullscreen", True)
        
        # Main background container that expands to fill the entire monitor
        self.fs_container = tk.Frame(root, bg=BG_COLOR)
        self.fs_container.pack(expand=True, fill="both")

        # Visual center wrapper so the game stays beautifully centered on any screen size
        self.main_frame = tk.Frame(self.fs_container, bg=BG_COLOR)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Game Board Canvas
        self.canvas = tk.Canvas(
            self.main_frame, 
            width=COLS * CELL_SIZE, 
            height=ROWS * CELL_SIZE, 
            bg=BG_COLOR, 
            highlightthickness=1, 
            highlightbackground=ACCENT_COLOR
        )
        self.canvas.grid(row=0, column=0, rowspan=2, padx=(0, 30))

        # Side Panel for Stats & Next Piece
        self.side_panel = tk.Frame(self.main_frame, bg=PANEL_COLOR, bd=1, relief="flat", padx=20, pady=20)
        self.side_panel.grid(row=0, column=1, sticky="n")

        # Score Display
        self.score_title = tk.Label(self.side_panel, text="SCORE", font=("Helvetica", 10, "bold"), bg=PANEL_COLOR, fg=ACCENT_COLOR)
        self.score_title.pack(anchor="w", pady=(0, 2))
        self.score_label = tk.Label(self.side_panel, text="000000", font=("Consolas", 22, "bold"), bg=PANEL_COLOR, fg=TEXT_COLOR)
        self.score_label.pack(anchor="w", pady=(0, 25))

        # Lines Cleared Display
        self.lines_title = tk.Label(self.side_panel, text="LINES", font=("Helvetica", 10, "bold"), bg=PANEL_COLOR, fg=ACCENT_COLOR)
        self.lines_title.pack(anchor="w", pady=(0, 2))
        self.lines_label = tk.Label(self.side_panel, text="0", font=("Consolas", 20, "bold"), bg=PANEL_COLOR, fg=TEXT_COLOR)
        self.lines_label.pack(anchor="w", pady=(0, 25))

        # Next Piece Canvas Preview
        self.next_title = tk.Label(self.side_panel, text="NEXT", font=("Helvetica", 10, "bold"), bg=PANEL_COLOR, fg=ACCENT_COLOR)
        self.next_title.pack(anchor="w", pady=(0, 5))
        self.next_canvas = tk.Canvas(self.side_panel, width=120, height=120, bg=BG_COLOR, highlightthickness=0)
        self.next_canvas.pack(pady=(0, 10))

        # Controls Hint Footer
        self.controls_label = tk.Label(
            self.main_frame, 
            text="← → Move  •  ↑ Rotate  •  ↓ Drop  •  Enter Restart  •  Esc Exit", 
            font=("Helvetica", 10), 
            bg=BG_COLOR, 
            fg="#4B5563"
        )
        self.controls_label.grid(row=2, column=0, columnspan=2, pady=(25, 0))

        # --- CONTROLS BINDING ---
        self.root.bind("<Left>", lambda e: self.move(-1))
        self.root.bind("<Right>", lambda e: self.move(1))
        self.root.bind("<Down>", lambda e: self.drop())
        self.root.bind("<Up>", lambda e: self.rotate())
        self.root.bind("<Return>", lambda e: self.reset_game())
        self.root.bind("<Escape>", lambda e: self.root.destroy())  # Smooth window closing

        # Initialize Game State variables
        self.next_shape_type = random.choice(list(SHAPES.keys()))
        self.reset_game()
        self.update_loop()

    def reset_game(self):
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.score = 0
        self.lines_cleared = 0
        self.score_label.config(text="000000")
        self.lines_label.config(text="0")
        self.game_over = False
        
        self.spawn_shape()
        self.draw_game()

    def spawn_shape(self):
        self.current_shape_type = self.next_shape_type
        self.current_shape = SHAPES[self.current_shape_type]
        self.current_color = SHAPE_COLORS[self.current_shape_type]
        
        self.shape_row = 0
        self.shape_col = COLS // 2 - len(self.current_shape[0]) // 2

        self.next_shape_type = random.choice(list(SHAPES.keys()))
        self.draw_next_preview()

        if not self.valid_position():
            self.game_over = True
            self.draw_game()

    def draw_next_preview(self):
        self.next_canvas.delete("all")
        next_shape = SHAPES[self.next_shape_type]
        color = SHAPE_COLORS[self.next_shape_type]
        
        shape_h = len(next_shape)
        shape_w = len(next_shape[0])
        offset_x = (120 - (shape_w * 25)) / 2
        offset_y = (120 - (shape_h * 25)) / 2

        for r, row in enumerate(next_shape):
            for c, val in enumerate(row):
                if val:
                    self.next_canvas.create_rectangle(
                        offset_x + c * 25, offset_y + r * 25,
                        offset_x + (c + 1) * 25, offset_y + (r + 1) * 25,
                        fill=color, outline=BG_COLOR, width=1
                    )

    def draw_game(self):
        self.canvas.delete("all")

        # Structural background grid
        for r in range(ROWS):
            for c in range(COLS):
                self.canvas.create_rectangle(
                    c * CELL_SIZE, r * CELL_SIZE,
                    (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE,
                    outline=GRID_COLOR, width=1
                )

        # Locked Blocks
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c]:
                    self.draw_block(c, r, self.board[r][c])

        # Active Falling Block
        if not self.game_over and self.current_shape:
            for r, row in enumerate(self.current_shape):
                for c, val in enumerate(row):
                    if val:
                        self.draw_block(self.shape_col + c, self.shape_row + r, self.current_color)

        # Premium Game Over Overlay
        if self.game_over:
            self.canvas.create_rectangle(
                0, 0, COLS * CELL_SIZE, ROWS * CELL_SIZE, 
                fill="#000000", stipple="gray50"
            )
            self.canvas.create_text(
                (COLS * CELL_SIZE) / 2, (ROWS * CELL_SIZE) / 2 - 20,
                text="GAME OVER", font=("Helvetica", 26, "bold"), fill="#EF4444"
            )
            self.canvas.create_text(
                (COLS * CELL_SIZE) / 2, (ROWS * CELL_SIZE) / 2 + 25,
                text="Press ENTER to Restart\nEsc to Exit Game", font=("Helvetica", 12), fill=TEXT_COLOR, justify="center"
            )

    def draw_block(self, col, row, color):
        self.canvas.create_rectangle(
            col * CELL_SIZE + 1, row * CELL_SIZE + 1,
            (col + 1) * CELL_SIZE - 1, (row + 1) * CELL_SIZE - 1,
            fill=color, outline="#FFFFFF", width=0.5
        )

    def valid_position(self, shape=None, row=None, col=None):
        shape = shape or self.current_shape
        row = row if row is not None else self.shape_row
        col = col if col is not None else self.shape_col
        for r, row_vals in enumerate(shape):
            for c, val in enumerate(row_vals):
                if val:
                    if row + r >= ROWS or col + c < 0 or col + c >= COLS:
                        return False
                    if self.board[row + r][col + c]:
                        return False
        return True

    def lock_shape(self):
        for r, row_vals in enumerate(self.current_shape):
            for c, val in enumerate(row_vals):
                if val:
                    self.board[self.shape_row + r][self.shape_col + c] = self.current_color
        self.clear_lines()
        self.spawn_shape()

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        cleared = ROWS - len(new_board)
        for _ in range(cleared):
            new_board.insert(0, [0] * COLS)
        self.board = new_board
        
        if cleared > 0:
            self.lines_cleared += cleared
            base_points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += base_points.get(cleared, 100)
            
            self.score_label.config(text=f"{self.score:06d}")
            self.lines_label.config(text=str(self.lines_cleared))

    def move(self, dx):
        if not self.game_over and self.valid_position(col=self.shape_col + dx):
            self.shape_col += dx
            self.draw_game()

    def drop(self):
        if not self.game_over:
            if self.valid_position(row=self.shape_row + 1):
                self.shape_row += 1
            else:
                self.lock_shape()
            self.draw_game()

    def rotate(self):
        if not self.game_over:
            rotated = [list(row) for row in zip(*self.current_shape[::-1])]
            if self.valid_position(shape=rotated):
                self.current_shape = rotated
                self.draw_game()

    def update_loop(self):
        if not self.game_over:
            if self.valid_position(row=self.shape_row + 1):
                self.shape_row += 1
            else:
                self.lock_shape()
            self.draw_game()
        self.root.after(500, self.update_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = TetraxFullScreen(root)
    root.mainloop()