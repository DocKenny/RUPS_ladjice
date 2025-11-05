import socket
from game import Game
from quiz import QuizManager
from config import SEQUENCE_COLORS, SHIP_LENGTHS, DEFAULT_HOST, DEFAULT_PORT
from network_utils import send_json, receive_json, serialize_board

class BattleshipServer:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.game = None
        self.quiz = QuizManager()
    
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        print(f"[SERVER] Started on {self.host}:{self.port}")
        
        for i in range(2):
            conn, addr = self.server_socket.accept()
            player_name = f"Player {i + 1}"
            self.clients.append((conn, addr, player_name))
            print(f"[SERVER] {player_name} connected from {addr}")
            
            send_json(conn, {
                'type': 'connection_success',
                'player_name': player_name,
                'player_id': i
            })
        
        print("[SERVER] Starting game...")
        self.initialize_game()
        self.game_loop()
    
    def initialize_game(self):
        player_names = [c[2] for c in self.clients]
        self.game = Game(player_names, SEQUENCE_COLORS, ship_lengths=SHIP_LENGTHS, grid_size=10)
        
        for i, (conn, _, _) in enumerate(self.clients):
            send_json(conn, {
                'type': 'game_start',
                'your_board': serialize_board(self.game.players[i].board, show_ships=True),
                'opponent_board': serialize_board(self.game.players[1-i].board, show_ships=False),
                'grid_size': self.game.grid_size
            })
    
    def game_loop(self):
        buffers = [b'', b'']  # One buffer per client
        
        while not self.game.over:
            curr_idx = self.game.current_turn
            opp_idx = 1 - curr_idx
            curr_conn = self.clients[curr_idx][0]
            opp_conn = self.clients[opp_idx][0]
            
            question, correct_answer = self.quiz.get_question()
            print(f"[SERVER] Question for {self.game.get_current_player().name}: {question}")
            
            send_json(curr_conn, {'type': 'quiz_question', 'question': question})
            send_json(opp_conn, {'type': 'opponent_turn', 'message': f"{self.game.get_current_player().name} answering..."})
            
            # Get answer
            answer_msg, buffers[curr_idx] = receive_json(curr_conn, buffers[curr_idx])
            if not answer_msg:
                break
            
            user_answer = answer_msg.get('answer', '').strip().lower()
            
            if user_answer == correct_answer.lower():
                print(f"[SERVER] Correct from {self.game.get_current_player().name}")
                send_json(curr_conn, {'type': 'answer_result', 'correct': True, 'message': 'Correct! Take your shot.'})
                
                # Get shot
                shot_msg, buffers[curr_idx] = receive_json(curr_conn, buffers[curr_idx])
                if not shot_msg:
                    break
                
                cell = tuple(shot_msg.get('cell', []))
                result, game_over, winner = self.game.process_shot(cell)
                print(f"[SERVER] Shot at {cell}: {result}")
                
                # Send results
                send_json(curr_conn, {
                    'type': 'shot_result',
                    'result': result,
                    'opponent_board': serialize_board(self.game.players[opp_idx].board, show_ships=False),
                    'game_over': game_over,
                    'winner': winner
                })
                
                send_json(opp_conn, {
                    'type': 'opponent_shot',
                    'result': result,
                    'cell': list(cell),
                    'your_board': serialize_board(self.game.players[opp_idx].board, show_ships=True),
                    'game_over': game_over,
                    'winner': winner
                })
                
                if game_over:
                    print(f"[SERVER] Winner: {winner}")
                    break
            else:
                print(f"[SERVER] Wrong answer from {self.game.get_current_player().name}")
                send_json(curr_conn, {'type': 'answer_result', 'correct': False, 'message': 'Incorrect. Turn skipped.'})
                send_json(opp_conn, {'type': 'turn_skipped', 'message': f"{self.game.get_current_player().name} answered incorrectly."})
                self.game.next_turn()
        
        print("[SERVER] Game ended")
        self.cleanup()
    
    def cleanup(self):
        for conn, _, _ in self.clients:
            try:
                conn.close()
            except:
                pass
        self.server_socket.close()