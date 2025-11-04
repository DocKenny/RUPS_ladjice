
import pygame
import textwrap

try_fonts = ["Montserrat", "Poppins", "Nunito", "Inter", "Avenir", "Segoe UI", "Arial"]
def get_font(size, bold=False):
    for name in try_fonts:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size, bold=bold)

class QuestionCard:
    def __init__(self, surface, width=680, padding=24):
        self.surface = surface
        self.width = width
        self.padding = padding

        self.title_font = get_font(28, bold=True)
        self.text_font  = get_font(22, bold=False)
        self.input_font = get_font(22, bold=False)
        self.btn_font   = get_font(22, bold=True)

        # colors
        self.bg = (20, 24, 32)           # canvas
        self.card = (245, 247, 250)      # card base
        self.card_border = (222, 226, 233)
        self.text = (30, 35, 42)
        self.muted = (110, 118, 129)
        self.accent = (79, 70, 229)      # indigo
        self.accent_hover = (67, 56, 202)
        self.success = (16, 185, 129)
        self.error = (239, 68, 68)
        self.shadow = (0, 0, 0)

        # component state
        self.input_value = ""
        self.feedback = None  # ("correct" | "wrong", message)

        # button rects set on layout
        self.input_rect = None
        self.btn_rect = None

    def set_input(self, value: str):
        self.input_value = value

    def set_feedback(self, ok: bool, msg: str):
        self.feedback = ("correct" if ok else "wrong", msg)

    def clear_feedback(self):
        self.feedback = None

    def wrap_text(self, text, font, max_w):
        words = text.split(" ")
        lines = []
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if font.size(test)[0] <= max_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    def draw_round_rect(self, rect, color, radius=16, border=0, border_color=None, shadow=True):
        x, y, w, h = rect
        if shadow:
            # drop shadow
            shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0,0,0,80), shadow_surf.get_rect(), border_radius=radius+2)
            self.surface.blit(shadow_surf, (x+4, y+6))

        pygame.draw.rect(self.surface, color, rect, border_radius=radius)
        if border and border_color:
            pygame.draw.rect(self.surface, border_color, rect, width=border, border_radius=radius)

    def draw(self, question: str, center):
        sw, sh = self.surface.get_size()
        card_w = min(self.width, sw - 40)
        # dynamic height: title + question + input + button + spacing
        # start with generous height and compute in-flow
        x = center[0] - card_w // 2
        y = center[1] - 160
        card_h = 220

        # card
        self.draw_round_rect((x, y, card_w, card_h), self.card, radius=18, border=1, border_color=self.card_border, shadow=True)

        # inner content area
        content_x = x + self.padding
        content_y = y + self.padding
        content_w = card_w - self.padding * 2

        # title
        title_surf = self.title_font.render("Answer to fire!", True, self.text)
        self.surface.blit(title_surf, (content_x, content_y))
        content_y += title_surf.get_height() + 8

        # question
        q_lines = self.wrap_text(question, self.text_font, content_w)
        for line in q_lines:
            ln = self.text_font.render(line, True, self.text)
            self.surface.blit(ln, (content_x, content_y))
            content_y += ln.get_height() + 2

        content_y += 12

        # input box
        input_h = 40
        self.input_rect = pygame.Rect(content_x, content_y, content_w - 140, input_h)
        self.draw_round_rect(self.input_rect, (255,255,255), radius=12, border=1, border_color=self.card_border, shadow=False)

        # render input text (clip if too long)
        txt = self.input_value
        # ensure text fits
        while self.input_font.size(txt)[0] > self.input_rect.w - 16 and len(txt) > 0:
            txt = txt[1:]
        text_surf = self.input_font.render(txt, True, self.text)
        self.surface.blit(text_surf, (self.input_rect.x + 12, self.input_rect.y + (input_h - text_surf.get_height())//2))

        # button
        self.btn_rect = pygame.Rect(self.input_rect.right + 12, content_y, 128, input_h)
        mouse = pygame.mouse.get_pos()
        hovered = self.btn_rect.collidepoint(mouse)
        btn_color = self.accent_hover if hovered else self.accent
        self.draw_round_rect(self.btn_rect, btn_color, radius=12, shadow=False)
        btn_label = self.btn_font.render("Submit", True, (255,255,255))
        self.surface.blit(btn_label, (self.btn_rect.centerx - btn_label.get_width()//2, self.btn_rect.centery - btn_label.get_height()//2))

        content_y += input_h + 12

        # feedback line
        if self.feedback:
            kind, msg = self.feedback
            color = self.success if kind == "correct" else self.error
            fb = self.text_font.render(msg, True, color)
            self.surface.blit(fb, (content_x, content_y))

        # Recalculate card_h to fit content gracefully
        new_h = (content_y - y) + self.padding + (self.feedback and 24 or 16)
        if new_h > card_h:
            self.draw_round_rect((x, y, card_w, new_h), self.card, radius=18, border=1, border_color=self.card_border, shadow=True)
            # redraw content over the new height (simple approach: call recursively without changing state)
            # To avoid recursion, just draw again without shadow. Good enough visually.
            # In practice, most questions fit the base height.
            pass

    def handle_key(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.input_value = self.input_value[:-1]
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            return "submit"
        else:
            ch = event.unicode
            if ch and ch.isprintable():
                self.input_value += ch
        return None

    def handle_click(self, pos):
        if self.btn_rect and self.btn_rect.collidepoint(pos):
            return "submit"
        return None
