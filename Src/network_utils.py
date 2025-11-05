import json
import socket

def send_json(sock, data):
    try:
        message = json.dumps(data) + '\n'
        sock.sendall(message.encode('utf-8'))
        return True
    except Exception as e:
        print(f"[NET] Send error: {e}")
        return False

# return: (message_dict, remaining_buffer) ali (None, buffer)
def receive_json(sock, buffer=b''):
    try:
        while b'\n' not in buffer:
            chunk = sock.recv(1024)
            if not chunk:
                return None, buffer
            buffer += chunk
        
        line, buffer = buffer.split(b'\n', 1)
        if line:
            return json.loads(line.decode('utf-8')), buffer
        return None, buffer
    except Exception as e:
        print(f"[NET] Receive error: {e}")
        return None, buffer

# spremeni board v dict
def serialize_board(board, show_ships=False):
    data = {
        'hits': list(board.hits),
        'misses': list(board.misses),
    }
    if show_ships:
        data['ships'] = {f"{r},{c}": list(color) for (r, c), color in board.cells_with_colors.items()}
    return data

# posodobi hits in misses
def deserialize_board_state(board, board_data):
    board.hits = set(tuple(h) for h in board_data.get('hits', []))
    board.misses = set(tuple(m) for m in board_data.get('misses', []))

# set board ships, na začetku
def deserialize_board_ships(board, board_data):
    ships_dict = board_data.get('ships', {})
    cells_with_colors = {}
    for key, color in ships_dict.items():
        r, c = map(int, key.split(','))
        cells_with_colors[(r, c)] = tuple(color)
    board.set_cells(cells_with_colors)