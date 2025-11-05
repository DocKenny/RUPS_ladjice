import pygame
import random
from image_loader import ImageLoader

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

image_loader = None

def init_image_loader():
    global image_loader
    if image_loader is None:
        image_loader = ImageLoader()

def generate_sequences(grid_size, lengths, sequence_colors):
    # Randomly generate ship-like colored sequences.
    occupied = set()
    cell_to_color = {}

    for length, color in zip(lengths, sequence_colors):
        placed = False
        for _ in range(500):
            orientation = random.choice(["H", "V"])
            if orientation == "H":
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - length)
                cells = [(row, col + i) for i in range(length)]
            else:
                row = random.randint(0, grid_size - length)
                col = random.randint(0, grid_size - 1)
                cells = [(row + i, col) for i in range(length)]

            if all(c not in occupied for c in cells):
                for c in cells:
                    occupied.add(c)
                    cell_to_color[c] = color
                placed = True
                break

        if not placed:
            # fallback placement
            cells = [(0, i) for i in range(length)] if orientation == "H" else [(i, 0) for i in range(length)]
            for c in cells:
                occupied.add(c)
                cell_to_color[c] = color

    return cell_to_color


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

    def draw_ship_images(self, surface):
        if image_loader is None:
            init_image_loader()
        
        ships = self.group_ships()
        
        for ship_cells in ships:
            if not ship_cells:
                continue
            
            ship_length = len(ship_cells)
            img = image_loader.get_ship_image(ship_length)
            
            if img is None:
                # Fallback
                for (r, c) in ship_cells:
                    color = self.cells_with_colors.get((r, c))
                    if color:
                        self.draw_cell_fill(surface, r, c, color)
                continue
            
            # orientacija, pozicija
            ship_cells = sorted(ship_cells)
            first_cell = ship_cells[0]

            is_horizontal = all(r == first_cell[0] for r, c in ship_cells)

            ox, oy = self.origin

            if is_horizontal:
                img_resized = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE * ship_length))
                img_resized = pygame.transform.rotate(img_resized, -90)
                x = ox + first_cell[1] * CELL_SIZE
                y = oy + first_cell[0] * CELL_SIZE
            else:
                img_resized = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE * ship_length))
                x = ox + first_cell[1] * CELL_SIZE
                y = oy + first_cell[0] * CELL_SIZE

            surface.blit(img_resized, (x, y))



    # grupiraj celice v ladje
    def group_ships(self):
        visited = set()
        ships = []
        
        for cell in self.cells_with_colors:
            if cell in visited:
                continue
            
            # najdi povezane celice
            ship = []
            color = self.cells_with_colors[cell]
            stack = [cell]
            
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                
                if current in self.cells_with_colors and self.cells_with_colors[current] == color:
                    visited.add(current)
                    ship.append(current)
                    
                    r, c = current
                    # preveri adjacent celice
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        neighbor = (r + dr, c + dc)
                        if neighbor not in visited:
                            stack.append(neighbor)
            
            if ship:
                ships.append(ship)
        
        return ships


    def draw(self, surface, show_ships=False):
        if show_ships:
            self.draw_ship_images(surface)


        self.draw_grid(surface)

        # Draw hits/misses
        for (r, c) in self.misses:
            self.draw_x(surface, r, c)
        for (r, c) in self.hits:
            self.draw_o(surface, r, c)
