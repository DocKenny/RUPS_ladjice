import pygame
import sys
import random
from board import Board, generate_sequences
from game import Game
from quiz import QuizManager
from question_ui import QuestionCard


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


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Battleship – Quiz Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.running = True

        # Polished question UI card
        self.question_card = QuestionCard(self.screen, width=700)

        # make the game (players; Game handles ship placement)
        self.game = Game(["Player 1", "Player 2"], SEQUENCE_COLORS, ship_lengths=[2, 3, 5], grid_size=GRID_SIZE)

        # set origins so boards draw in the right place
        # (Game created Board objects with origin=(0,0) so update the origins here)
        self.game.players[0].board.origin = LEFT_ORIGIN
        self.game.players[1].board.origin = RIGHT_ORIGIN

        self.quiz = QuizManager()

        # UI state
        self.state = "ASK_QUESTION"  # ASK_QUESTION -> ANSWERING -> (SHOOTING or SHOW_RESULT)
        self.current_question = ""
        self.correct_answer = ""
        self.message = ""

    # --- Quiz flow helpers ---
    def ask_question(self):
        self.current_question, self.correct_answer = self.quiz.get_question()
        self.state = "ANSWERING"
        # reset the card each time
        self.question_card.set_input("")
        self.question_card.clear_feedback()

    def on_correct_answer(self):
        self.message = "Correct! Take your shot."
        self.state = "SHOOTING"

    def on_wrong_answer(self):
        self.message = "Incorrect. Turn skipped."
        self.game.next_turn()
        self.state = "SHOW_RESULT"

    # --- Event handling ---
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self.state == "ANSWERING":
                if event.type == pygame.KEYDOWN:
                    action = self.question_card.handle_key(event)
                    if action == "submit":
                        user_answer = self.question_card.input_value.strip()
                        if user_answer.lower() == self.correct_answer.lower():
                            self.question_card.set_feedback(True, "Correct! Fire away 🚀")
                            self.on_correct_answer()
                        else:
                            self.question_card.set_feedback(False, "Wrong answer. Turn lost.")
                            self.on_wrong_answer()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = self.question_card.handle_click(event.pos)
                    if action == "submit":
                        user_answer = self.question_card.input_value.strip()
                        if user_answer.lower() == self.correct_answer.lower():
                            self.question_card.set_feedback(True, "Correct! Fire away 🚀")
                            self.on_correct_answer()
                        else:
                            self.question_card.set_feedback(False, "Wrong answer. Turn lost.")
                            self.on_wrong_answer()

            elif self.state == "SHOOTING" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                opponent = self.game.get_opponent()
                cell = opponent.board.cell_from_pos(pos)
                if cell:
                    self.message = self.game.process_shot(cell)[0]
                    self.state = "SHOW_RESULT"

    # --- Drawing helpers ---
    def draw_text_center(self, text, y):
        label = self.font.render(text, True, LABEL_COLOR)
        rect = label.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(label, rect)

    def draw(self):
        self.screen.fill(BG_COLOR)

        player = self.game.get_current_player()
        opponent = self.game.get_opponent()

        # Draw both boards
        player.board.origin = LEFT_ORIGIN
        opponent.board.origin = RIGHT_ORIGIN
        player.board.draw(self.screen, show_ships=True)
        opponent.board.draw(self.screen, show_ships=False)

        # Turn label
        self.draw_text_center(f"Current turn: {player.name}", 30)

        # State-specific UI
        if self.state == "ANSWERING":
            # Dim background for focus
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            self.screen.blit(overlay, (0, 0))

            center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
            self.question_card.draw(self.current_question, center)

        elif self.state == "SHOW_RESULT":
            self.draw_text_center(self.message, HEIGHT - 80)

        elif self.state == "SHOOTING":
            self.draw_text_center(self.message, HEIGHT - 80)

        pygame.display.flip()

    # --- Main loop ---
    def run(self):
        # Start with a question
        self.ask_question()

        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

            # After showing result briefly, move to next question
            if self.state == "SHOW_RESULT":
                pygame.time.wait(1200)
                if not self.game.over:
                    self.ask_question()
                else:
                    self.state = "GAME_OVER"
                    self.message = f"{self.game.get_current_player().name} wins!"

        pygame.quit()
        sys.exit()
