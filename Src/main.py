from main_menu import MainMenu
from app import App

if __name__ == "__main__":
    menu = MainMenu()
    choice = menu.run()

    if choice == "start":
        game = App()
        game.run()
