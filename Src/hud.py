# hud.py
import pygame
import math

def _get_font(size, bold=False):
    for name in ["Inter", "Poppins", "Nunito", "Segoe UI", "Arial"]:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size, bold=bold)

class TurnHUD:
    """Top-center pill showing current player's turn + right-side badge for last shot result."""
    def __init__(self, surface):
        self.surface = surface
        self.player_name = "Player"
        self.status_text = None     # "Hit!" / "Miss!" / "Skipped"
        self.status_hit = None      # True/False/None (None hides badge)

        self.title_font = _get_font(22, bold=True)
        self.small_font = _get_font(18, bold=False)

        self.pill_bg = (20, 24, 32, 210)     # translucent dark
        self.pill_border = (255, 255, 255, 40)
        self.text_color = (245, 247, 250)
        self.subtle = (180, 190, 200)

        self.hit_bg = (16, 185, 129)         # green
        self.miss_bg = (239, 68, 68)         # red
        self.badge_text = (255, 255, 255)

        self.created_ms = pygame.time.get_ticks()
        self.badge_updated_ms = pygame.time.get_ticks()

    def set_player(self, name: str):
        self.player_name = name
        self.created_ms = pygame.time.get_ticks()

    def set_status(self, hit: bool | None, text: str | None):
        self.status_hit = hit
        self.status_text = text
        self.badge_updated_ms = pygame.time.get_ticks()

    def _round_rect(self, surf, rect, color, radius=16, border=0, border_color=None):
        x, y, w, h = rect
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
        if border and border_color:
            pygame.draw.rect(s, border_color, (0, 0, w, h), width=border, border_radius=radius)
        surf.blit(s, (x, y))

    def draw(self):
        sw, sh = self.surface.get_size()

        pill_w = min(520, sw - 40)
        pill_h = 48  # thinner
        x = (sw - pill_w) // 2
        y = 4  # closer to the top

        # shadow
        shadow = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), shadow.get_rect(), border_radius=18)
        self.surface.blit(shadow, (x, y + 4))

        self._round_rect(self.surface, (x, y, pill_w, pill_h), self.pill_bg, radius=18, border=1, border_color=self.pill_border)

        # left text
        left_pad = 18
        label_text = f"TURN: {self.player_name}"
        label = self.title_font.render(label_text, True, self.text_color)
        self.surface.blit(label, (x + left_pad, y + (pill_h - label.get_height()) // 2))

        # right badge
        if self.status_hit is not None and self.status_text:
            elapsed = (pygame.time.get_ticks() - self.badge_updated_ms) / 1000.0
            pulse = 1.0 + 0.05 * math.sin(elapsed * 8.0)

            badge_w = int(130 * pulse)
            badge_h = int(36 * pulse)
            bx = x + pill_w - badge_w - 14
            by = y + (pill_h - badge_h) // 2

            bg = self.hit_bg if self.status_hit else self.miss_bg
            self._round_rect(self.surface, (bx, by, badge_w, badge_h), bg, radius=12)

            txt = self.small_font.render(self.status_text, True, self.badge_text)
            self.surface.blit(txt, (bx + (badge_w - txt.get_width()) // 2, by + (badge_h - txt.get_height()) // 2))
