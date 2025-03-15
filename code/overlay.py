#KUTUPHANELER
import pygame
from settings import *

#Overlay Adinda bir sinif olusutur.
#Katmanlara islem yapmak icin olusuturlan gorsel bir kutuphane aracidir.
class Overlay:
    #Baslatici (initialize) islemleri
    def __init__(self, player):
        #Genel Ayarlar -> ekranda gozukme ayarlari
        self.display_surface = pygame.display.get_surface()
        self.player = player #Bu kodun player içinde çalışacağı çok açık.

        #Eklenecek Grafikler
        #Overlay gorsellerin dosya yolunu bulma
        overlay_path = 'Pydew Valley/graphics/overlay/'
        #Player'ın tool ve seed nesneleri icin Layer'lara gorsel islem yapalim.
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png')
                                                   .convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png')
                                                   .convert_alpha() for seed in player.seeds}
        
##DEF DİSPLAY DE KALDIK. -> LEVEL'e bunu yazacağız (S7)
    def display(self):
        #tool Surface İşlemleri
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf,tool_rect)

        #Seed Surface İşlemleri
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf,seed_rect)
