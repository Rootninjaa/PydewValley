import pygame, sys
from settings import *
from level import Level

class Game: #Ana oyunumuz

    def __init__(self): #Oyunu baslatiyoruz.
        pygame.init() #Pygame'i baslatmak.
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Pydew Valley!')
        self.clock = pygame.time.Clock()
        self.level = Level() # Level sinifini oyunda baslatiyorum.

    def run(self): #run -> oyun calisirken demek
        while True:
            for event in pygame.event.get(): #Olan olaylari al!
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            #Zamani ayarlama ve oyunu zamanla calistirma
            dt = self.clock.tick() / 1000
            self.level.run(dt) #Oyunum belirledigim oyun zamaniyla calisir.
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()