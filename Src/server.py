import socket
import json
from game import Game
from quiz import QuizManager
from config import SEQUENCE_COLORS, SHIP_LENGTHS, DEFAULT_HOST, DEFAULT_PORT

class BattleshipServer:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.clients = []  # list (conn, addr, player_name)
        self.game = None
        self.running = False
        
        # vprasanja
        self.quiz = QuizManager()
        
    # zaženi server, cakaj da se clienta povezeta
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        self.running = True
        print(f"[SERVER] Started on {self.host}:{self.port}")
        print("[SERVER] Waiting for 2 players to connect...")
        
        # sprejmi igralca
        for i in range(2):
            conn, addr = self.server_socket.accept()
            player_name = f"Player {i + 1}"
            self.clients.append((conn, addr, player_name))
            print(f"[SERVER] {player_name} connected from {addr}")
            
            # player info
            self.send_message(conn, {
                'type': 'connection_success',
                'player_name': player_name,
                'player_id': i
            })
        
        print("[SERVER] Both players connected. Starting game...")
        self.initialize_game()
        self.game_loop()
    
    def initialize_game(self):
        player_names = [c[2] for c in self.clients]
        self.game = Game(player_names, SEQUENCE_COLORS, ship_lengths=SHIP_LENGTHS, grid_size=10)
        
        # poslji boards obema igralcema
        for i, (conn, _, _) in enumerate(self.clients):
            player_board = self.serialize_board(self.game.players[i].board, show_ships=True)
            opponent_board = self.serialize_board(self.game.players[1-i].board, show_ships=False)
            
            self.send_message(conn, {
                'type': 'game_start',
                'your_board': player_board,
                'opponent_board': opponent_board,
                'grid_size': self.game.grid_size
            })
    
    def serialize_board(self, board, show_ships=False):
        data = {
            'hits': list(board.hits),
            'misses': list(board.misses),
        }
        if show_ships:
            data['ships'] = {f"{r},{c}": color for (r, c), color in board.cells_with_colors.items()}
        return data
    

    def game_loop(self):
        while self.running and not self.game.over:
            current_player_idx = self.game.current_turn
            current_conn = self.clients[current_player_idx][0]
            opponent_idx = 1 - current_player_idx
            opponent_conn = self.clients[opponent_idx][0]
            
            # vprasanje za trenutnega igralca
            question, correct_answer = self.quiz.get_question()
            
            print(f"[SERVER] Asking {self.game.get_current_player().name}: {question}")
            
            self.send_message(current_conn, {
                'type': 'quiz_question',
                'question': question
            })
            
            self.send_message(opponent_conn, {
                'type': 'opponent_turn',
                'message': f"{self.game.get_current_player().name} is answering a question..."
            })
            
            # cakaj odgovor
            try:
                answer_msg = self.receive_message(current_conn)
                if not answer_msg:
                    break
                    
                user_answer = answer_msg.get('answer', '').strip().lower()
                
                if user_answer == correct_answer.lower():
                    # pravilni odgovor
                    print(f"[SERVER] Correct answer from {self.game.get_current_player().name}")
                    
                    self.send_message(current_conn, {
                        'type': 'answer_result',
                        'correct': True,
                        'message': 'Correct! Take your shot.'
                    })
                    
                    # cakaj na shot
                    shot_msg = self.receive_message(current_conn)
                    if not shot_msg:
                        break
                    
                    cell = tuple(shot_msg.get('cell', []))
                    result, game_over, winner = self.game.process_shot(cell)
                    
                    print(f"[SERVER] Shot at {cell}: {result}")
                    
                    # posodobi oba clienta z rezultatom shota
                    opponent_board = self.serialize_board(self.game.players[opponent_idx].board, show_ships=False)
                    
                    self.send_message(current_conn, {
                        'type': 'shot_result',
                        'result': result,
                        'opponent_board': opponent_board,
                        'game_over': game_over,
                        'winner': winner
                    })
                    
                    self.send_message(opponent_conn, {
                        'type': 'opponent_shot',
                        'result': result,
                        'cell': list(cell),
                        'your_board': self.serialize_board(self.game.players[opponent_idx].board, show_ships=True),
                        'game_over': game_over,
                        'winner': winner
                    })
                    
                    if game_over:
                        print(f"[SERVER] Game over! Winner: {winner}")
                        self.running = False
                        break
                    
                else:
                    # napacni odogovror
                    print(f"[SERVER] Wrong answer from {self.game.get_current_player().name}")
                    
                    self.send_message(current_conn, {
                        'type': 'answer_result',
                        'correct': False,
                        'message': 'Incorrect. Turn skipped.'
                    })
                    
                    self.send_message(opponent_conn, {
                        'type': 'turn_skipped',
                        'message': f"{self.game.get_current_player().name} answered incorrectly. Turn skipped."
                    })
                    
                    self.game.next_turn()
                    
            except Exception as e:
                print(f"[SERVER] Error in game loop: {e}")
                break
        
        print("[SERVER] Game ended. Closing connections...")
        self.cleanup()
    
    # poslji sporocilo clientu
    def send_message(self, conn, data):
        try:
            message = json.dumps(data) + '\n'
            conn.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"[SERVER] Error sending message: {e}")
    
    # pridobi sporocilo od clienta
    def receive_message(self, conn):
        try:
            data = b''
            while b'\n' not in data:
                chunk = conn.recv(1024)
                if not chunk:
                    return None
                data += chunk
            
            message = data.decode('utf-8').strip()
            return json.loads(message)
        except Exception as e:
            print(f"[SERVER] Error receiving message: {e}")
            return None
    
    def cleanup(self):
        for conn, _, _ in self.clients:
            try:
                conn.close()
            except:
                pass
        self.server_socket.close()
        print("[SERVER] Server shut down.")