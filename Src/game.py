# game.py
import random
from board import Board, generate_sequences

class Player:
    def __init__(self, name, board):
        self.name = name
        self.board = board

    def all_ships_sunk(self):
        return len(self.board.hits) >= len(self.board.cells_with_colors)


class Game:
    def __init__(self, player_names, sequence_colors, ship_lengths, grid_size=10):
        """
        Game holds players and turn logic. It does not use pygame.
        - player_names: list of strings, e.g. ["P1", "P2"]
        - sequence_colors: list of colors used for ship fills
        - ship_lengths: list of lengths, e.g. [2,3,5]
        - grid_size: grid dimension (default 10)
        """
        self.sequence_colors = sequence_colors
        self.ship_lengths = ship_lengths
        self.grid_size = grid_size

        self.players = []
        for i, name in enumerate(player_names):
            # origin will be set by app (App controls rendering positions)
            board = Board((0, 0), sequence_colors)
            ships = generate_sequences(grid_size, ship_lengths, sequence_colors)
            board.set_cells(ships)
            player = type("P", (), {})()  # tiny anonymous object to hold name and board
            player.name = name
            player.board = board
            self.players.append(player)

        self.current_turn = 0
        self.over = False
        self.winner = None
        self.last_result = ""  # message string (e.g., "Hit!", "Miss", "Already shot here")

    def get_current_player(self):
        return self.players[self.current_turn]

    def get_opponent(self):
        return self.players[(self.current_turn + 1) % len(self.players)]

    def next_turn(self):
        """Advance to the next player's turn."""
        self.current_turn = (self.current_turn + 1) % len(self.players)

    def process_shot(self, cell):
        """
        Process a shot on the opponent's board.
        Returns (result_str, is_game_over, winner_name_or_None).
        """
        shooter = self.get_current_player()
        opponent = self.get_opponent()
        board = opponent.board

        if cell in board.hits or cell in board.misses:
            self.last_result = "Already shot there!"
            return self.last_result, False, None

        if cell in board.cells_with_colors:
            board.hits.add(cell)
            self.last_result = f"{shooter.name} HIT at {cell}!"
        else:
            board.misses.add(cell)
            self.last_result = f"{shooter.name} missed at {cell}."

        # Check win
        total_ship_cells = len(board.cells_with_colors)
        if len(board.hits) >= total_ship_cells > 0:
            self.over = True
            self.winner = shooter.name
            self.last_result = f"{shooter.name} wins!"
            return self.last_result, True, self.winner

        # Not over → advance turn
        self.next_turn()
        return self.last_result, False, None