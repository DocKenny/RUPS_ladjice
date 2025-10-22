import pygame
import sys
import random

# --- config ---
GRID_SIZE = 10
CELL_SIZE = 48
LINE_WIDTH = 2
X_MARGIN = 8
BG_COLOR = (245, 245, 245)
GRID_COLOR = (30, 30, 30)
X_COLOR = (200, 40, 40)
O_COLOR = (40, 120, 200)
LABEL_COLOR = (60, 60, 60)

# colors for sequences (like ships)
SEQUENCE_COLORS = [
    (189, 226, 255),  # light blue
    (255, 235, 205),  # light bisque
    (221, 197, 255),  # light purple
]

GAP_BETWEEN_GRIDS = 80
OUTER_MARGIN = 30
GRID_PIXELS = GRID_SIZE * CELL_SIZE

LEFT_ORIGIN = (OUTER_MARGIN, OUTER_MARGIN)
RIGHT_ORIGIN = (OUTER_MARGIN + GRID_PIXELS + GAP_BETWEEN_GRIDS, OUTER_MARGIN)

WIDTH = RIGHT_ORIGIN[0] + GRID_PIXELS + OUTER_MARGIN
HEIGHT = OUTER_MARGIN + GRID_PIXELS + OUTER_MARGIN


# ---------------- utility functions ----------------
def cell_from_pos(pos, origin):
    x, y = pos
    ox, oy = origin
    gx, gy = x - ox, y - oy
    if 0 <= gx < GRID_PIXELS and 0 <= gy < GRID_PIXELS:
        col = gx // CELL_SIZE
        row = gy // CELL_SIZE
        return (int(row), int(col))
    return None


def draw_grid(surface, origin):
    ox, oy = origin
    for c in range(GRID_SIZE + 1):
        x = ox + c * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR, (x, oy), (x, oy + GRID_PIXELS), LINE_WIDTH)
    for r in range(GRID_SIZE + 1):
        y = oy + r * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR, (ox, y), (ox + GRID_PIXELS, y), LINE_WIDTH)


def draw_cell_fill(surface, origin, row, col, color):
    ox, oy = origin
    rect = pygame.Rect(
        ox + col * CELL_SIZE + 1,
        oy + row * CELL_SIZE + 1,
        CELL_SIZE - 2,
        CELL_SIZE - 2,
    )
    pygame.draw.rect(surface, color, rect)


def draw_x(surface, origin, row, col):
    ox, oy = origin
    x0 = ox + col * CELL_SIZE + X_MARGIN
    y0 = oy + row * CELL_SIZE + X_MARGIN
    x1 = ox + (col + 1) * CELL_SIZE - X_MARGIN
    y1 = oy + (row + 1) * CELL_SIZE - X_MARGIN
    pygame.draw.line(surface, X_COLOR, (x0, y0), (x1, y1), LINE_WIDTH + 2)
    pygame.draw.line(surface, X_COLOR, (x0, y1), (x1, y0), LINE_WIDTH + 2)


def draw_o(surface, origin, row, col):
    ox, oy = origin
    cx = ox + col * CELL_SIZE + CELL_SIZE // 2
    cy = oy + row * CELL_SIZE + CELL_SIZE // 2
    radius = CELL_SIZE // 2 - X_MARGIN
    pygame.draw.circle(surface, O_COLOR, (cx, cy), radius, LINE_WIDTH + 2)


def draw_label(surface, text, center_above_xy, font):
    label = font.render(text, True, LABEL_COLOR)
    rect = label.get_rect(midbottom=(center_above_xy[0], center_above_xy[1] - 8))
    surface.blit(label, rect)


def generate_sequences(grid_size, lengths):
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
            cells = [(0, i) for i in range(length)] if orientation == "H" else [(i, 0) for i in range(length)]
            for c in cells:
                occupied.add(c)
                cell_to_color[c] = color

    return cell_to_color


# ---------------- main ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Battleship – Hits (O) and Misses (X)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # track clicks
    hits = set()   # clicked cells that are colored on right
    misses = set() # clicked cells that are not colored

    # generate random "ships" on right grid
    right_grid_fills = generate_sequences(GRID_SIZE, lengths=[2, 3, 5])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = cell_from_pos(event.pos, LEFT_ORIGIN)
                if cell is not None:
                    if cell in right_grid_fills:
                        hits.add(cell)
                    else:
                        misses.add(cell)

        screen.fill(BG_COLOR)

        # draw colored sequences (ships) on right grid
        for (r, c), color in right_grid_fills.items():
            draw_cell_fill(screen, RIGHT_ORIGIN, r, c, color)

        # draw grids on top
        draw_grid(screen, LEFT_ORIGIN)
        draw_grid(screen, RIGHT_ORIGIN)

        # labels
        left_center = (LEFT_ORIGIN[0] + GRID_PIXELS // 2, LEFT_ORIGIN[1])
        right_center = (RIGHT_ORIGIN[0] + GRID_PIXELS // 2, RIGHT_ORIGIN[1])
        draw_label(screen, "Left Grid (clickable)", left_center, font)
        draw_label(screen, "Right Grid (ships)", right_center, font)

        # draw X (miss) and O (hit) on both grids
        for (r, c) in misses:
            draw_x(screen, LEFT_ORIGIN, r, c)
            draw_x(screen, RIGHT_ORIGIN, r, c)
        for (r, c) in hits:
            draw_o(screen, LEFT_ORIGIN, r, c)
            draw_o(screen, RIGHT_ORIGIN, r, c)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
