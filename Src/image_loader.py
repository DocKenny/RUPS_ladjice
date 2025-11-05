import pygame
import os

class ImageLoader:
    def __init__(self, images_folder="images"):
        self.images_folder = images_folder
        self.ship_images = {}
        self.load_ship_images()
    
    def load_ship_images(self):
        for length in [2, 3, 5]:
            path = os.path.join(self.images_folder, f"ship_{length}.png")
            if os.path.exists(path):
                self.ship_images[length] = pygame.image.load(path)
                print(f"[IMAGE] Loaded ship_{length}.png")
            else:
                print(f"[WARNING] Missing {path}")
    
    def get_ship_image(self, length):
        return self.ship_images.get(length)