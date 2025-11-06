import pygame
import sys
import socket
import threading
from board import Board
from config import (GRID_PIXELS, SEQUENCE_COLORS, COLOR_BG, DEFAULT_PORT)
from network_utils import send_json, receive_json, deserialize_board_state, deserialize_board_ships
from toast import StatusToast
from question_ui import QuestionCard

# config
OUTER_MARGIN = 30
GAP_BETWEEN_GRIDS = 80
TOP_BAR = 25

LEFT_ORIGIN = (OUTER_MARGIN, TOP_BAR + OUTER_MARGIN)
RIGHT_ORIGIN = (OUTER_MARGIN + GRID_PIXELS + GAP_BETWEEN_GRIDS, TOP_BAR + OUTER_MARGIN)

WIDTH = RIGHT_ORIGIN[0] + GRID_PIXELS + OUTER_MARGIN
HEIGHT = TOP_BAR + OUTER_MARGIN + GRID_PIXELS + OUTER_MARGIN + 100

LABEL_COLOR = (60, 60, 60)


class BattleshipClient:
    def __init__(self, host='localhost', port=DEFAULT_PORT):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Battleship – Online")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.font_large = pygame.font.SysFont(None, 36)
        self.running = True
        
        self.toast = StatusToast(self.screen)
        self.question_card = QuestionCard(self.screen, width=700)
        
        # network
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
        # game
        self.player_name = ""
        self.player_id = -1
        self.my_board = None
        self.opponent_board = None
        self.receive_thread = None

        # ui state
        self.state = "CONNECTING"
        self.message = "Connecting to server..."
        self.current_question = ""
        self.user_answer = ""
        self.can_shoot = False
        self.game_over = False
        self.winner = None
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"[CLIENT] Connected to {self.host}:{self.port}")
            
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"[CLIENT] Connection failed: {e}")
            self.message = f"Connection failed: {e}"
            self.state = "ERROR"
            return False
    
    def send_message(self, data):
        if not send_json(self.socket, data):
            self.connected = False
    
    def receive_messages(self):
        buffer = b''
        while self.connected and self.running:
            msg, buffer = receive_json(self.socket, buffer)
            if msg is None:
                print("[CLIENT] Server disconnected")
                self.connected = False
                break
            self.handle_message(msg)
    
    def handle_message(self, msg):
        msg_type = msg.get('type')
        
        if msg_type == 'connection_success':
            self.player_name = msg['player_name']
            self.player_id = msg['player_id']
            self.message = f"Connected as {self.player_name}. Waiting for opponent..."
            self.state = "WAITING"
            print(f"[CLIENT] You are {self.player_name}")
            
        elif msg_type == 'game_start':
            print("[CLIENT] Game starting!")
            self.initialize_boards(msg)
            self.state = "WAITING"
            self.message = "Game started! Waiting for your turn..."
            
        elif msg_type == 'quiz_question':
            self.current_question = msg['question']
            self.user_answer = ""
            self.state = "ANSWERING"
            self.message = f"Answer the question: {self.current_question}"
            self.question_card.set_input("")
            self.question_card.clear_feedback()

            
        elif msg_type == 'opponent_turn':
            self.state = "WAITING"
            self.message = msg['message']
            
        elif msg_type == 'answer_result':
            if msg['correct']:
                self.state = "SHOOTING"
                self.message = msg['message']
                self.can_shoot = True
                self.question_card.set_feedback(True, "Correct! Fire away 🚀")
                self.toast.show("Correct! Take your shot.", positive=True)
            else:
                self.state = "SHOW_RESULT"
                self.message = msg['message']
                self.question_card.set_feedback(False, "Wrong answer. Turn lost.")
                self.toast.show("Wrong answer. Turn lost.", positive=False)
                pygame.time.set_timer(pygame.USEREVENT, 2000, 1)
                
        elif msg_type == 'shot_result':
            self.update_opponent_board(msg['opponent_board'])
            self.message = msg['result']
            self.can_shoot = False
            
            if msg['game_over']:
                self.state = "GAME_OVER"
                self.winner = msg['winner']
                self.message = f"Game Over! {self.winner} wins!"
            else:
                self.state = "SHOW_RESULT"
                pygame.time.set_timer(pygame.USEREVENT, 2000, 1)
                
        elif msg_type == 'opponent_shot':
            self.update_my_board(msg['your_board'])
            self.message = msg['result']
            
            if msg['game_over']:
                self.state = "GAME_OVER"
                self.winner = msg['winner']
                self.message = f"Game Over! {self.winner} wins!"
            else:
                self.state = "SHOW_RESULT"
                pygame.time.set_timer(pygame.USEREVENT, 2000, 1)
                
        elif msg_type == 'turn_skipped':
            self.state = "SHOW_RESULT"
            self.message = msg['message']
            pygame.time.set_timer(pygame.USEREVENT, 2000, 1)
    
    def initialize_boards(self, msg):
        self.my_board = Board(LEFT_ORIGIN, SEQUENCE_COLORS)
        self.opponent_board = Board(RIGHT_ORIGIN, SEQUENCE_COLORS)
        
        deserialize_board_ships(self.my_board, msg['your_board'])
        deserialize_board_state(self.my_board, msg['your_board'])
        deserialize_board_state(self.opponent_board, msg['opponent_board'])
    
    def update_my_board(self, board_data):
        if self.my_board:
            deserialize_board_state(self.my_board, board_data)
    
    def update_opponent_board(self, board_data):
        if self.opponent_board:
            deserialize_board_state(self.opponent_board, board_data)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.USEREVENT:
                if self.state == "SHOW_RESULT":
                    self.state = "WAITING"
                    self.message = "Waiting for your turn..."
                    
            elif self.state == "ANSWERING":
                if event.type == pygame.KEYDOWN:
                    action = self.question_card.handle_key(event)
                    if action == "submit":
                        self.send_message({
                            'type': 'answer',
                            'answer': self.question_card.input_value
                        })
                        self.state = "WAITING"
                        self.message = "Answer submitted. Waiting for result..."
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = self.question_card.handle_click(event.pos)
                    if action == "submit":
                        self.send_message({
                            'type': 'answer',
                            'answer': self.question_card.input_value
                        })
                        self.state = "WAITING"
                        self.message = "Answer submitted. Waiting for result..."
                        
            elif self.state == "SHOOTING" and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.can_shoot and self.opponent_board:
                    pos = event.pos
                    cell = self.opponent_board.cell_from_pos(pos)
                    if cell:
                        self.send_message({
                            'type': 'shot',
                            'cell': list(cell)
                        })
                        self.state = "WAITING"
                        self.message = "Shot sent. Waiting for result..."
                        self.can_shoot = False
    
    def draw_text_center(self, text, y, font=None, color=LABEL_COLOR):
        if font is None:
            font = self.font
        label = font.render(text, True, color)
        rect = label.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(label, rect)
    
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        if self.state in ["CONNECTING", "WAITING", "ERROR"] and not self.my_board:
            self.draw_text_center(self.message, HEIGHT // 2, self.font_large)
        else:
            if self.my_board:
                label = self.font.render(f"{self.player_name}'s Board", True, LABEL_COLOR)
                self.screen.blit(label, (LEFT_ORIGIN[0], LEFT_ORIGIN[1] - 25))
                self.my_board.draw(self.screen, show_ships=True)
            
            if self.opponent_board:
                label = self.font.render("Opponent's Board", True, LABEL_COLOR)
                self.screen.blit(label, (RIGHT_ORIGIN[0], RIGHT_ORIGIN[1] - 25))
                self.opponent_board.draw(self.screen, show_ships=False)
            
            if self.state == "ANSWERING":
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 80))
                self.screen.blit(overlay, (0, 0))
                
                center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
                self.question_card.draw(self.current_question, center)
            elif self.state == "GAME_OVER":
                y_pos = TOP_BAR + OUTER_MARGIN + GRID_PIXELS + 40
                self.draw_text_center(self.message, y_pos, self.font_large, 
                                     (200, 40, 40) if self.winner != self.player_name else (40, 120, 40))
            
            self.toast.draw()
        
        pygame.display.flip()
    
    def run(self):
        if not self.connect():
            for _ in range(180):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        break
                self.draw()
                self.clock.tick(60)
            self.running = False
        
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        if self.connected:
            self.socket.close()
        pygame.quit()
        sys.exit()