import pygame
import sys
import threading
import time
import socket
from config import DEFAULT_PORT
import styles as st


class MultiplayerMenu:
    def __init__(self, screen_width=800, screen_height=600):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Battleship - Multiplayer")
        self.clock = pygame.time.Clock()
        
        #izgled
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_button = pygame.font.SysFont(None, 42)
        self.font_small = pygame.font.SysFont(None, 28)
        
        self.BG_COLOR = st.COLOR_BG
        self.TEXT_COLOR = st.COLOR_TEXT
        self.BUTTON_COLOR = st.COLOR_BUTTON
        self.BUTTON_HOVER = st.COLOR_BUTTON_HOVER
        
        # state
        self.running = True
        self.choice = None
        self.ip_input = "localhost"
        self.port_input = str(DEFAULT_PORT)
        self.active_field = "ip"
        
        # gumbi
        self.host_rect = pygame.Rect(0, 0, 220, 60)
        self.join_rect = pygame.Rect(0, 0, 220, 60)
        self.back_rect = pygame.Rect(0, 0, 180, 50)
        
        cx = screen_width // 2
        cy = screen_height // 2
        self.host_rect.center = (cx, cy - 50)
        self.join_rect.center = (cx, cy + 30)
        self.back_rect.center = (cx, cy + 120)
        
        # inputs
        self.ip_rect = pygame.Rect(0, 0, 300, 40)
        self.port_rect = pygame.Rect(0, 0, 150, 40)
        self.connect_rect = pygame.Rect(0, 0, 200, 50)
        self.back2_rect = pygame.Rect(0, 0, 150, 50)
        
        self.ip_rect.center = (cx, cy - 70)
        self.port_rect.center = (cx, cy + 30)
        self.connect_rect.center = (cx, cy + 120)
        self.back2_rect.center = (cx, cy + 190)
        
        self.mode = "main"  # "main", "join", "host_waiting"
    


    def draw_text(self, text, font, color, center):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center)
        self.screen.blit(surf, rect)
    
    def draw_button(self, rect, text, mouse_pos, font=None):
        if font is None:
            font = self.font_button
        color = self.BUTTON_HOVER if rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=12)
        self.draw_text(text, font, self.TEXT_COLOR, rect.center)
    
    def draw_input_field(self, rect, text, is_active, label):
        label_y = rect.top - 25
        self.draw_text(label, self.font_small, self.TEXT_COLOR, (rect.centerx, label_y))
        
        border_color = (80, 120, 200) if is_active else (100, 100, 100)
        bg_color = (255, 255, 255)
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
        
        text_surf = self.font_small.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    


    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def draw_main_menu(self, mouse_pos):
        self.screen.fill(self.BG_COLOR)
        w, h = self.screen.get_size()
        
        self.draw_text("Multiplayer", self.font_title, self.TEXT_COLOR, (w // 2, 120))
        
        self.draw_button(self.host_rect, "Host Game", mouse_pos)
        self.draw_button(self.join_rect, "Join Game", mouse_pos)
        self.draw_button(self.back_rect, "Back", mouse_pos, self.font_small)
    
    def draw_join_menu(self, mouse_pos):
        self.screen.fill(self.BG_COLOR)
        w, h = self.screen.get_size()
        
        self.draw_text("Join Game", self.font_title, self.TEXT_COLOR, (w // 2, 120))
        
        self.draw_input_field(self.ip_rect, self.ip_input, self.active_field == "ip", "Server IP:")
        self.draw_input_field(self.port_rect, self.port_input, self.active_field == "port", "Port:")
        
        self.draw_button(self.connect_rect, "Connect", mouse_pos)
        self.draw_button(self.back2_rect, "Back", mouse_pos, self.font_small)
    
    def draw_host_menu(self):
        self.screen.fill(self.BG_COLOR)
        w, h = self.screen.get_size()
        
        self.draw_text("Hosting Game", self.font_title, self.TEXT_COLOR, (w // 2, 100))
        self.draw_text("Waiting for opponent...", self.font_button, self.TEXT_COLOR, (w // 2, 240))
        self.draw_text("Share this with your opponent:", self.font_small, self.TEXT_COLOR, (w // 2, 310))
        
        ip = self.get_local_ip()
        self.draw_text(f"IP: {ip}", self.font_button, (40, 120, 40), (w // 2, 360))
        self.draw_text(f"Port: {DEFAULT_PORT}", self.font_small, self.TEXT_COLOR, (w // 2, 400))
    
    def show_host_waiting_screen(self):
        waiting = True
        self.screen.fill(self.BG_COLOR)
        w, h = self.screen.get_size()
        
        ip = self.get_local_ip()
        
        font_large_ip = pygame.font.SysFont(None, 56)
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            
            self.screen.fill(self.BG_COLOR)
            
            self.draw_text("Server Started!", self.font_title, (40, 120, 40), (w // 2, 80))
            self.draw_text("Waiting for opponent to connect...", self.font_button, self.TEXT_COLOR, (w // 2, 170))
            
            info_rect = pygame.Rect(w // 2 - 250, 240, 500, 180)
            pygame.draw.rect(self.screen, (220, 240, 255), info_rect, border_radius=15)
            pygame.draw.rect(self.screen, (100, 140, 200), info_rect, 4, border_radius=15)
            
            self.draw_text("Player 2 should enter:", self.font_small, self.TEXT_COLOR, (w // 2, 275))
            
            ip_surf = font_large_ip.render(ip, True, (20, 80, 180))
            ip_rect = ip_surf.get_rect(center=(w // 2, 330))
            self.screen.blit(ip_surf, ip_rect)
            
            self.draw_text(f"Port: {DEFAULT_PORT}", self.font_button, (80, 80, 80), (w // 2, 385))
            
            self.draw_text("Press any key when ready to start...", self.font_small, (120, 120, 120), (w // 2, 480))
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def handle_main_click(self, mouse_pos):
        if self.host_rect.collidepoint(mouse_pos):
            self.choice = "host"
            self.running = False
        elif self.join_rect.collidepoint(mouse_pos):
            self.mode = "join"
        elif self.back_rect.collidepoint(mouse_pos):
            self.choice = "back"
            self.running = False
    
    def handle_join_click(self, mouse_pos):
        if self.ip_rect.collidepoint(mouse_pos):
            self.active_field = "ip"
        elif self.port_rect.collidepoint(mouse_pos):
            self.active_field = "port"
        elif self.connect_rect.collidepoint(mouse_pos):
            self.choice = "join"
            self.running = False
        elif self.back2_rect.collidepoint(mouse_pos):
            self.mode = "main"
    
    def handle_text_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            if self.active_field == "ip":
                self.ip_input = self.ip_input[:-1]
            else:
                self.port_input = self.port_input[:-1]
        elif event.key == pygame.K_TAB:
            self.active_field = "port" if self.active_field == "ip" else "ip"
        elif event.key == pygame.K_RETURN:
            self.choice = "join"
            self.running = False
        else:
            if self.active_field == "ip" and len(self.ip_input) < 30:
                self.ip_input += event.unicode
            elif self.active_field == "port" and len(self.port_input) < 5:
                if event.unicode.isdigit():
                    self.port_input += event.unicode
    
    # pokazi meni
    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.mode == "main":
                        self.handle_main_click(mouse_pos)
                    elif self.mode == "join":
                        self.handle_join_click(mouse_pos)
                elif event.type == pygame.KEYDOWN and self.mode == "join":
                    self.handle_text_input(event)

            if self.mode == "main":
                self.draw_main_menu(mouse_pos)
            elif self.mode == "join":
                self.draw_join_menu(mouse_pos)
            elif self.mode == "host_waiting":
                self.draw_host_menu()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        if self.choice == "join":
            port = int(self.port_input) if self.port_input else DEFAULT_PORT
            return self.choice, self.ip_input, port
        return self.choice, None, None


# glavna funkcija, pokazi multiplayer meni, zaženi host game ali join game
def start_multiplayer_game():
    menu = MultiplayerMenu()
    choice, host, port = menu.run()
    
    if choice == "back":
        return None
    
    if choice == "host":
        from server import BattleshipServer
        
        print("[MULTIPLAYER] Starting server...")
        server_thread = threading.Thread(
            target=lambda: BattleshipServer().start(),
            daemon=True
        )
        server_thread.start()
        
        time.sleep(0.5)
        
        menu.show_host_waiting_screen()
        
        print("[MULTIPLAYER] Connecting to own server...")
        from client import BattleshipClient
        client = BattleshipClient(host='localhost')
        client.run()
        
    elif choice == "join":
        print(f"[MULTIPLAYER] Connecting to {host}:{port}...")
        from client import BattleshipClient
        client = BattleshipClient(host=host, port=port)
        client.run()
    
    return "done"