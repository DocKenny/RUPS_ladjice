# game.py
import random
from board import Board
#from quiz import QuizManager

class Player:
    def __init__(self, name, board):
        self.name = name
        self.board = board
        self.hits = 0
        self.misses = 0

    def all_ships_sunk(self):
        # Win condition
        total_ship_cells = len(self.board.cells_with_colors)
        return len(self.board.hits) >= total_ship_cells


class Game:
    def __init__(self, player_names):
        self.players = []
        self.current_turn = 0
       # self.quiz = QuizManager()

        # Initialize player boards
        for name in player_names:
            board = Board(origin=(0, 0), sequence_colors=[(189,226,255), (255,235,205), (221,197,255)])
            self.players.append(Player(name, board))

        # TODO: Ship placing logic

    def get_current_player(self):
        return self.players[self.current_turn]

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)

    def ask_question(self):
        """Ask a question; return True if answered correctly."""
        question, answer = self.quiz.get_question()
        # Later this will open a UI popup or text box
        print(f"Question for {self.get_current_player().name}: {question}")
        user_answer = input("Answer: ")
        return user_answer.strip().lower() == answer.lower()

    # Handle a players turn
    def take_turn(self, cell):
        current = self.get_current_player()
        opponent = self.players[(self.current_turn + 1) % len(self.players)]

        if self.ask_question():
            if cell in opponent.board.cells_with_colors:
                opponent.board.hits.add(cell)
                print(f"{current.name} HIT at {cell}")
            else:
                opponent.board.misses.add(cell)
                print(f"{current.name} MISSED at {cell}")
        else:
            print(f"{current.name} answered incorrectly and loses their turn.")

        # Check for win
        if opponent.all_ships_sunk():
            print(f"{current.name} wins!")
            return True  # Game over

        self.next_turn()
        return False
