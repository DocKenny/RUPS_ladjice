import pygame
import sys
import random
from board import Board

# --- Config ---
GRID_SIZE = 10
CELL_SIZE = 48
OUTER_MARGIN = 30
GAP_BETWEEN_GRIDS = 80
GRID_PIXELS = GRID_SIZE * CELL_SIZE

LEFT_ORIGIN = (OUTER_MARGIN, OUTER_MARGIN)
RIGHT_ORIGIN = (OUTER_MARGIN + GRID_PIXELS + GAP_BETWEEN_GRIDS, OUTER_MARGIN)

WIDTH = RIGHT_ORIGIN[0] + GRID_PIXELS + OUTER_MARGIN
HEIGHT = OUTER_MARGIN + GRID_PIXELS + OUTER_MARGIN

BG_COLOR = (245, 245, 245)
LABEL_COLOR = (60, 60, 60)

# colors for sequences (like ships)
SEQUENCE_COLORS = [
    (189, 226, 255),  # light blue
    (255, 235, 205),  # light bisque
    (221, 197, 255),  # light purple
]


def generate_sequences(grid_size, lengths):
    # Randomly generate ship-like colored sequences.
    occupied = set()
    cell_to_color = {}

    for length, color in zip(lengths, SEQUENCE_COLORS):
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


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Battleship – Hits (O) and Misses (X)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.running = True

        # Create boards
        self.left_board = Board(LEFT_ORIGIN, SEQUENCE_COLORS)
        self.right_board = Board(RIGHT_ORIGIN, SEQUENCE_COLORS)

        # Generate ships for right board
        ships = generate_sequences(GRID_SIZE, lengths=[2, 3, 5])
        self.right_board.set_cells(ships)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.left_board.handle_click(event.pos)
                # Mirror hits/misses on right board
                self.right_board.hits = self.left_board.hits
                self.right_board.misses = self.left_board.misses

    def draw_label(self, text, center_above_xy):
        label = self.font.render(text, True, LABEL_COLOR)
        rect = label.get_rect(midbottom=(center_above_xy[0], center_above_xy[1] - 8))
        self.screen.blit(label, rect)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.left_board.draw(self.screen)
        self.right_board.draw(self.screen, show_ships=True)

        left_center = (LEFT_ORIGIN[0] + GRID_PIXELS // 2, LEFT_ORIGIN[1])
        right_center = (RIGHT_ORIGIN[0] + GRID_PIXELS // 2, RIGHT_ORIGIN[1])
        self.draw_label("Left Grid (clickable)", left_center)
        self.draw_label("Right Grid (ships)", right_center)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()
