import pygame
from random import randint, choice
from mango_timer import Timer
from settings import *

#Oyunumuzun temas edilebilir alanlarını tanımlayabiliyoruz.
class Generic(pygame.sprite.Sprite):
    #self, karakter pozisyonu, surface, resim grupları ve katman
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf #Hangi Sprite alınacak?
        self.rect = self.image.get_rect(topleft=pos) #Sprite yerleştirme
        self.z = z #Sprite'ı katmana gömüyoruz.
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, #Hitbox Collision için gerekir.
                                               -self.rect.height * 0.75)
        
#Interactions -> Etkileşimler oluşturma
class Interaction(Generic):
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name 

#Su katmanını tasarım olarak tanımlayalım.
class Water(Generic): #Generic olmadan çalışamazsın!
    #intialize etmekle başlıyoruz.
    def __init__(self, pos, frames, groups):
        #animasyon setup
        self.frames = frames
        self.frame_index = 0

        #sprite setup
        super().__init__(pos=pos, surf=self.frames[self.frame_index], groups=groups, z=LAYERS['water'])

    #Animasyonu yapma -> Player'daki mantık yapılacak.
    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    
    #Animasyonu çalıştırma
    def update(self, dt):
        self.animate(dt)

#Yabani Çiçekler Ekleyelim.
class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

#Particle -> Molekül efektleri
#Molekül efekti hareketli resimlerle oluşan yapılardır. Animasyon yapımın
class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks() #Particle'ın sayacı
        self.duration = duration #Particle ne kadar sürecek.

        #Beyaz yüzey
        mask_surf = pygame.mask.from_surface(self.image) #Particle nasıl gözükecek?
        new_surf = mask_surf.to_surface() #Particle yüzeyine resmi ekle.
        new_surf.set_colorkey((0,0,0)) #Particle'ın rengi
        self.image = new_surf

    #Particle Update etme
    def update(self,dt):
        current_time = pygame.time.get_ticks()
        if current_time -self.start_time > self.duration:
            self.kill() #Particle'ın süresi tamamlanınca sil


#Ağaçlar ekleyelim.
class Tree(Generic):
    def __init__(self, pos, surf, groups, name, player_add):
        super().__init__(pos, surf, groups)

        #Ağaçların Genel Özellikleri
        self.health = 5 #Ağacı kırmak için can
        self.alive = True #Ağaç yaşıyor mu?
        #Görselleştirelim.
        stump_path = f'Pydew Valley/graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()
        
        #Ağaçtaki Elmalar
        self.apple_surf = pygame.image.load('Pydew Valley/graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit() #Meyveleri ağaçta oluştur.

        self.player_add = player_add
        # Ses
        self.axe_sound = pygame.mixer.Sound('Pydew Valley/audio/axe.mp3')

    #Ağaca hasar verme
    def damage(self):
        #Ağacın minimum hasari
        self.health -= 1 #self.health = self.health - 1

        self.axe_sound.play()

        #Elmaları silme
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites()) #Rastgele elma seçilecek.
            Particle(pos = random_apple.rect.topleft,
                     surf = random_apple.image,
                     groups = self.groups()[0],
                     z =LAYERS['fruit'])
            self.player_add('apple') #Envantere elma ekle.
            random_apple.kill() #Seçilen rastgele elma gidecek.
    
    #Ölüm Kontrol
    def check_death(self):
        #Can sıfır olmuşsa
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'], 300)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            self.player_add('wood') #Ağaçtan odun topla

    #Güncelleme
    def update(self, dt):
        if self.alive:
            self.check_death()
    
    #Meyve yarat.
    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0,10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic(pos = (x,y),
                        surf = self.apple_surf,
                        groups = [self.apple_sprites,self.groups()[0]],
                        z = LAYERS['fruit'])