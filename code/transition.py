import pygame
from settings import *

#Geçişleri sağlayan sınıf (yatağa geçme gibi etkileşimleri sağlayacak)
class Transition:
    def __init__(self, reset, player):
        #Setup
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        #Resimlerin genel degerleri
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2
    
    #Uyuma durumu olursa veya etkileşim olursa ekrandaki renkler değişecek.
    #Uyuyorsa ekran kararır. Eve girdik. Evin çatısı kararır gibi.
    def play(self):
        self.color +=self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.reset()
        if self.color > 255:
            self.color = 255
            self.player.sleep = False
            self.speed = -2
        #RGB Renk Skalası için (Color 0 ve 255 arasıdır)
        self.image.fill((self.color,self.color,self.color))
        self.display_surface.blit(self.image, (0,0), special_flags= pygame.BLEND_RGBA_MULT)