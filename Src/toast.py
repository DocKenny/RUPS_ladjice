# toast.py
import pygame, math

def _font(size, bold=False):
    for name in ["Inter", "Poppins", "Nunito", "Segoe UI", "Arial"]:
        p = pygame.font.match_font(name, bold=bold)
        if p: return pygame.font.Font(p, size)
    return pygame.font.SysFont(None, size, bold=bold)

class StatusToast:
    """
    Slide/fade toast near the bottom center.
    Usage:
      toast = StatusToast(screen)
      toast.show("Correct! Take your shot.", positive=True)   # green
      toast.show("Wrong answer. Turn lost.", positive=False)  # red
      ...
      toast.draw()  # every frame
    """
    def __init__(self, surface):
        self.surface = surface
        self.text = None
        self.positive = True
        self.font = _font(20, bold=True)
        self.bg_ok = (16, 185, 129)    # green
        self.bg_bad = (239, 68, 68)    # red
        self.txt = (255, 255, 255)
        self.shadow = (0, 0, 0, 90)
        self.started = 0
        self.duration = 1400  # ms visible
        self.padding_x = 18
        self.padding_y = 10
        self.max_w = 540

    def show(self, text, positive=True, duration_ms=None):
        self.text = text
        self.positive = positive
        self.started = pygame.time.get_ticks()
        if duration_ms:
            self.duration = duration_ms

    def active(self):
        if not self.text: return False
        return pygame.time.get_ticks() - self.started <= self.duration + 300  # keep for fade out

    def _round_rect(self, surf, rect, color, radius=14):
        x,y,w,h = rect
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0,0,w,h), border_radius=radius)
        surf.blit(s, (x,y))

    def draw(self):
        if not self.active():
            return

        elapsed = pygame.time.get_ticks() - self.started
        # Ease in/out for Y position and alpha
        t = max(0, min(1, elapsed / 250.0))            # in (first 250ms)
        o = max(0, min(1, (self.duration - elapsed) / 250.0)) if elapsed > self.duration - 250 else 1.0  # out
        alpha = int(255 * min(t, o))

        # Prepare text (wrap if too long)
        words, lines, line = self.text.split(" "), [], ""
        while words:
            w = words.pop(0)
            test = (line + " " + w).strip()
            if self.font.size(test)[0] <= self.max_w - self.padding_x*2:
                line = test
            else:
                lines.append(line); line = w
        if line: lines.append(line)

        sw, sh = self.surface.get_size()
        text_surfs = [self.font.render(l, True, self.txt) for l in lines]
        text_w = max(s.get_width() for s in text_surfs)
        text_h = sum(s.get_height() for s in text_surfs) + (len(text_surfs)-1)*2

        w = text_w + self.padding_x*2
        h = text_h + self.padding_y*2

        x = (sw - w) // 2
        baseline_y = sh - 40 - h   # baseline resting Y
        # slide from +20px below
        y = baseline_y + int((1 - t) * 20)

        # shadow
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, self.shadow, shadow.get_rect(), border_radius=16)
        shadow.set_alpha(alpha)
        self.surface.blit(shadow, (x, y + 4))

        bg = self.bg_ok if self.positive else self.bg_bad
        bg = (*bg[:3], alpha)
        self._round_rect(self.surface, (x, y, w, h), bg, radius=16)

        # text
        ty = y + self.padding_y
        for s in text_surfs:
            s2 = s.copy(); s2.set_alpha(alpha)
            self.surface.blit(s2, (x + (w - s.get_width())//2, ty))
            ty += s.get_height() + 2
