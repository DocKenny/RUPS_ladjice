import pygame

# --- config ---
GRID_SIZE = 10
CELL_SIZE = 48
LINE_WIDTH = 2
X_MARGIN = 8
BG_COLOR = (245, 245, 245)
GRID_COLOR = (30, 30, 30)
X_COLOR = (200, 40, 40)
O_COLOR = (40, 120, 200)


GRID_PIXELS = GRID_SIZE * CELL_SIZE


class Board:
    def __init__(self, origin, sequence_colors):
        self.origin = origin
        self.sequence_colors = sequence_colors
        self.hits = set()
        self.misses = set()
        self.cells_with_colors = {}

    def set_cells(self, cell_to_color):
        # Assigns pre-generated ship/sequence colors to board cells.
        self.cells_with_colors = cell_to_color

    def cell_from_pos(self, pos):
        # Returns (row, col) of cell if click is inside this board.
        x, y = pos
        ox, oy = self.origin
        gx, gy = x - ox, y - oy
        if 0 <= gx < GRID_PIXELS and 0 <= gy < GRID_PIXELS:
            col = gx // CELL_SIZE
            row = gy // CELL_SIZE
            return (int(row), int(col))
        return None

    def handle_click(self, pos):
        # Registers a hit or miss based on click position.
        cell = self.cell_from_pos(pos)
        if cell is None:
            return
        if cell in self.cells_with_colors:
            self.hits.add(cell)
        else:
            self.misses.add(cell)

    def draw_grid(self, surface):
        ox, oy = self.origin
        for c in range(GRID_SIZE + 1):
            x = ox + c * CELL_SIZE
            pygame.draw.line(surface, GRID_COLOR, (x, oy), (x, oy + GRID_PIXELS), LINE_WIDTH)
        for r in range(GRID_SIZE + 1):
            y = oy + r * CELL_SIZE
            pygame.draw.line(surface, GRID_COLOR, (ox, y), (ox + GRID_PIXELS, y), LINE_WIDTH)

    def draw_cell_fill(self, surface, row, col, color):
        ox, oy = self.origin
        rect = pygame.Rect(
            ox + col * CELL_SIZE + 1,
            oy + row * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2,
        )
        pygame.draw.rect(surface, color, rect)

    def draw_x(self, surface, row, col):
        ox, oy = self.origin
        x0 = ox + col * CELL_SIZE + X_MARGIN
        y0 = oy + row * CELL_SIZE + X_MARGIN
        x1 = ox + (col + 1) * CELL_SIZE - X_MARGIN
        y1 = oy + (row + 1) * CELL_SIZE - X_MARGIN
        pygame.draw.line(surface, X_COLOR, (x0, y0), (x1, y1), LINE_WIDTH + 2)
        pygame.draw.line(surface, X_COLOR, (x0, y1), (x1, y0), LINE_WIDTH + 2)

    def draw_o(self, surface, row, col):
        ox, oy = self.origin
        cx = ox + col * CELL_SIZE + CELL_SIZE // 2
        cy = oy + row * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - X_MARGIN
        pygame.draw.circle(surface, O_COLOR, (cx, cy), radius, LINE_WIDTH + 2)

    def draw(self, surface, show_ships=False):
        # Optional: show ship colors for one of the grids
        if show_ships:
            for (r, c), color in self.cells_with_colors.items():
                self.draw_cell_fill(surface, r, c, color)

        self.draw_grid(surface)

        # Draw hits/misses
        for (r, c) in self.misses:
            self.draw_x(surface, r, c)
        for (r, c) in self.hits:
            self.draw_o(surface, r, c)
