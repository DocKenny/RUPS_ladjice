from main_menu import MainMenu
from app import App
import pygame
import sys

if __name__ == "__main__":
    pygame.init()
    running = True
    
    while running:
        menu = MainMenu()
        choice = menu.run()

        if choice == "start":
            game = App()
            game.run()
            
        elif choice == "multiplayer":
            from multiplayer_menu import start_multiplayer_game
            start_multiplayer_game()
            
        elif choice == "quit":
            running = False
            
        else:
            running = False
    
    pygame.quit()
    sys.exit()