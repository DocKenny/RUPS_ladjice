import pygame
import sys
import styles as st


class MainMenu:
    def __init__(self, screen_width=800, screen_height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Battleship – Main Menu")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_button = pygame.font.SysFont(None, 48)
        self.running = True
        self.selected_option = None

        # Colors
        self.BG_COLOR = st.COLOR_BG
        self.TEXT_COLOR = st.COLOR_TEXT
        self.BUTTON_COLOR = st.COLOR_BUTTON
        self.BUTTON_HOVER = st.COLOR_BUTTON_HOVER

        # Button rectangles
        self.start_rect = pygame.Rect(0, 0, 200, 60)
        self.test_rect = pygame.Rect(0, 0, 200, 60)
        self.quit_rect = pygame.Rect(0, 0, 200, 60)
        self.start_rect.center = (screen_width // 2, screen_height // 2 - 75)
        self.test_rect.center = (screen_width // 2, screen_height // 2)
        self.quit_rect.center = (screen_width // 2, screen_height // 2 + 75)

    def draw_text(self, text, font, color, center):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center)
        self.screen.blit(surf, rect)

    def draw_button(self, rect, text, mouse_pos):
        color = self.BUTTON_HOVER if rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=12)
        self.draw_text(text, self.font_button, self.TEXT_COLOR, rect.center)

    def run(self):
        # Display the menu until user starts or quits the game.
        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_rect.collidepoint(mouse_pos):
                        self.selected_option = "start"
                        self.running = False
                    elif self.quit_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

            # Draw background
            self.screen.fill(self.BG_COLOR)

            # Title
            self.draw_text("Battleship", self.font_title, self.TEXT_COLOR, (self.screen.get_width() // 2, 140))

            # Buttons
            self.draw_button(self.start_rect, "Start Game", mouse_pos)
            self.draw_button(self.test_rect, "Multiplayer", mouse_pos)
            self.draw_button(self.quit_rect, "Quit", mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)

        return self.selected_option
