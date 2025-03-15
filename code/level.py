import pygame
from settings import * #settings bizim olusturdugumuz kutuphanedir.
#player kutuphanesindeki Player sinifi
from player import Player
from overlay import Overlay # overlay.py'den import et Class Overlay'i
from sprites import Generic, Water, WildFlower,Particle, Tree, Interaction # sprites.py -> Generic, Other Classes
import pytmx #pip install pytmx
from pytmx.util_pygame import load_pygame #Pygame için map_loader (Harita Doldurucu)
from support import *
from transition import Transition
from soil import SoilLayer #Toprak
from sky import Rain, Sky #Yağmur ve Gökyüzü olayları
from random import randint #Rastgele Kütüphanesi
from menu import Menu #Oyunumuzun menüsü -> Mağaza vs.


class Level: #Bolumlerin tasarlanacagi ve uygulanacagi sinifim

    def __init__(self): #init -> initialize (baslatmak) kimi? -> Kendini
        #Ekranin yuzey bilgisini al.
        self.display_surface = pygame.display.get_surface()
        #Sprite(Resim) gruplarini da al
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group() #Fizik motoru için collision
        self.tree_sprites = pygame.sprite.Group() #Ağaç Sprite'ları
        self.interaction_sprites = pygame.sprite.Group() #Etkileşimler için sprites'lar
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites) #Toprak katmanını oyuna çağır.
        self.setup() #init olurken setup yap.
        #Overlay Sınıfını çağır ve bir arayüz başlat
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset,self.player) #Karakterin geçişlerini yapmak için kullanıldı.

        #Gökyüzü olayları -> Yağmur, Güneş vs.
        self.rain = Rain(self.all_sprites) #Yağmur yağma olayı
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining #Hangi katmana yağacak?
        self.sky = Sky()

        #Mağaza
        self.menu = Menu(self.player, self.toggle_shop) #Mağaa menüsü
        self.shop_active = False

        # Müzik Arkaplanda çalacak
        self.success = pygame.mixer.Sound('Pydew Valley/audio/success.wav')
        self.success.set_volume(0.3)
        self.music = pygame.mixer.Sound('Pydew Valley/audio/music.mp3')
        self.music.play(loops = -1)

    def setup(self): #Kurulum fonksiyonları
        #tmx uzantısı pytmx'in harita verisini saklayacağı yol.
        tmx_data = load_pygame('Pydew Valley/data/map.tmx')

        #House -> Ev
        for layer in ['HouseFloor', 'HouseFurnitureBottom']: #Evin Zemini
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
        for layer in ['HouseWalls', 'HouseFurnitureTop']: #Evini çatısı ve duvarları
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
        
        #Fence -> Citler
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

        #Water -> Su
        #Dosya yoluyla suyu belirtelim.
        water_frames = import_folder('Pydew Valley/graphics/water') #Pydew Valley yazmayabilirsiniz
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        
        #Tree -> Agac
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), surf = obj.image,
                 groups =[self.all_sprites, self.collision_sprites, self.tree_sprites],
                 name = obj.name, player_add = self.player_add)
        
        #WildFlowers -> Yabani Çiçekler
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        #self.player = Player((640,360), self.all_sprites)
        #Colision Tiles -> Dokunulabilir alanlar
        for x,y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)), self.collision_sprites)

        #Player'i Collision'lu tmx_data'da bularak hareket ediyoruz. Ayrıca oyunda toprak, ağaç vs. etkileşimleri belirtiyoruz.
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
					pos = (obj.x,obj.y), 
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					toggle_shop = self.toggle_shop)
			
            if obj.name == 'Bed':
                Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

            if obj.name == 'Trader':
                Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

        Generic(pos=(0,0), surf=pygame.image.load('Pydew Valley/graphics/world/ground.png').convert_alpha(),
                groups=self.all_sprites, z=LAYERS['ground'])
        
    #Envantere Item ekleme fonksiyonu
    def player_add(self,item): #item denilen nesne her ne ise bu fonksiyon ile 1 arttır.
        self.player.item_inventory[item] += 1
        self.success.play()
    
    #Mağaza ekranı
    def toggle_shop(self):
        self.shop_active = not self.shop_active

    #Ağaçları ve ortamdaki nesneleri resetleme
    def reset(self):
        # Bitkiler Güncelleme
        self.soil_layer.update_plants()

		# Toprak Olayları -> Yağmur yağma, büyüme
        self.soil_layer.remove_water()
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

		# Ağaçlardaki elmalar
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

		# Gökyüzü
        self.sky.start_color = [255,255,255]
    
    #Ekme Collision'ı
    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

    def run(self,dt): #Ekrani guncelle ve cizimleri calistir.
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        # Güncellemeler
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()

		# Hava durumu
        self.overlay.display()
        if self.raining and not self.shop_active:
            self.rain.update()
        self.sky.display(dt)

        #Geçişleri oynatma /Uyursa karakter...
        if self.player.sleep:
            self.transition.play()

#Sprite Gruplarını Görselleştir.
class CameraGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
    
    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)