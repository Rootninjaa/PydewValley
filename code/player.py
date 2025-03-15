import pygame
from settings import *
from support import *
from mango_timer import Timer

#Player sınıfı -> pygame sprite(resim) ile çalışacak.
class Player(pygame.sprite.Sprite):
    
    #Player init -> başlatılınca çalışacak.
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop): #self -> kendisi, pos,group -> (konum)
        super().__init__(group) #nerede ve nasıl başlatılacak?
        
        #Assets
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        #Genel Ayarlar
        #Karakterin konum, genel gorunum ayarları
        self.image = self.animations[self.status][self.frame_index]
        #self.image.fill("green") #Surface'in arkasını yeşil yap
        self.rect = self.image.get_rect(center = pos)#resmin çerçevesi
        self.z = LAYERS['main'] #Oyunda karakterin katmandaki konumu

        #Hareket Ayarları
        self.direction = pygame.math.Vector2() #Hareket yönü
        self.pos = pygame.math.Vector2(self.rect.center) #pozisyon
        self.speed = 200 #hareket hizi

        #Collision -> Çarpma, çarpışma anlamına gelir.
        self.hitbox = self.rect.copy().inflate((-126,-70))
        self.collision_sprites = collision_sprites

        #Timer Kütüphanesi ve Ayarları
        self.timers = {
                       'tool use': Timer(350,self.use_tool),
                       'tool switch': Timer(200),
                       'seed use': Timer(350, self.use_seed),
                       'seed switch': Timer(200)}

        #Tool'ları belirleme
        self.tools = ['hoe','water','axe'] #hoe=0, water=1, axe=2
        self.tool_index = 0 #Yukaridaki aracin hangisi secilecek(index)
        self.selected_tool = self.tools[self.tool_index] #Araci belirle

        #Seed(Tohum) Ekmeyi Belirleme
        self.seeds = ['corn', 'tomato'] #corn=0, tomato=1
        self.seed_index = 0 #Baslangic aracini belirleme indexi
        self.selected_seed = self.seeds[self.seed_index]#Tohumu belirle

        #Inventory -> Envanter Oluşturma
        self.item_inventory = {'wood': 20,
                               'apple': 20,
                               'corn': 20,
                               'tomato': 20}
        self.seed_inventory = { #Tohumlar
		'corn': 5,
		'tomato': 5
		}
        self.money = 200 #Oyun başlangıç parası

        #Etkileşimler -> Interactions
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer #Toprak Etkileşimi Eklendi.
        self.toogle_shop = toggle_shop

        #Sesler
        self.watering = pygame.mixer.Sound('Pydew Valley/audio/water.mp3')
        self.watering.set_volume(0.2) #Ses şiddeti
    
    # Araç(Tool) Kullanım Fonksiyonu
    def use_tool(self):
        #Çapa
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)

        #Balta
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        #Su
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            self.watering.play()

    #Nişan alınacak hedef konum
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
   
    #Tohum (Seed) Kullanım Fonksiyonu
    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    #Import_Assets
    def import_assets(self):
        #Animasyonlar
        self.animations = {'up':[],'down':[], 'left':[], 'right':[],
                           'right_idle':[], 'left_idle':[],
                           'up_idle':[], 'down_idle':[],
                           'up_hoe':[], 'down_hoe':[], 'right_hoe':[],
                           'left_hoe':[], 'up_axe':[], 'down_axe':[],
                           'left_axe':[], 'right_axe':[],
                           'up_water':[], 'down_water':[],
                           'left_water':[], 'right_water':[]}
        
        #Dosyadaki yolu animations listesine ekle.
        for animation in self.animations.keys():
            full_path = 'Pydew Valley/graphics/character/'+animation
            #import_folder support.py'den gelecek.
            self.animations[animation] = import_folder(full_path)

    #Klasörden gelen animasyonları kullan.
    def animate(self, dt):
        self.frame_index += 4 * dt #Zamana baglı frame'de 4 kare oynat.
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0 #Eger 4'ü gecerse basa don.
        self.image = self.animations[self.status][int(self.frame_index)]
   
    #Klavye Yönetimi
    def input(self):
        keys = pygame.key.get_pressed() #klavyeden basılanı al.

        #Bir işlem yapıp yapmadığını kontrol et.
        if not self.timers['tool use'].active and not self.sleep:
            #Tuşa göre karakterin yönü değişecek.
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            #tool kullanma
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            #Tool Secme -> Aracin Degisme Durumu
            if keys[pygame.K_q] and not self.timers['tool switch'].activate:
                self.timers['tool use'].activate() #Araci kullanmayi aktif et.
                self.tool_index += 1 #Araci Q tusuna bastikca index yoluyla degistir.
                #Eger Tool index bir fazla olunca basa don, ilk araca geri gel
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index] #Araci sec.

            # Seed Kullanma
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
                
            #Seed Secme -> E tusuna basilinca tohum degistirme
            if keys[pygame.K_e] and not self.timers['seed switch'].activate:
                self.timers['seed switch'].activate() #Tohumu kullanmayi aktif et.
                self.seed_index += 1 #Tohumu E tusuna bastikca index yoluyla degistir.
                #Eger Seed index bir fazla olunca basa don, ilk araca geri gel
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index] #Seed secildi.

            #Collision'a denk geldiğimizde Enter tuşuna basarsak çalışsın.
            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction,False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader': #Mağaza Ekranı Yapımı
                        self.toogle_shop()
                    else:
                        self.status = 'left_idle'
                        self.sleep = True

    #Hareket statüsü kontrol eden fonksiyon
    def get_status(self):
        #idle -> Karakterin düz durduğu durumdur.
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        #Araçları Kullanma
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' +self.selected_tool
   
    #Zamanlayıcı çalıştır
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    
    #Collision -> Çarpma Fonksiyonu
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            #hasattr -> has attribute -> Boyle bir ozellik var mi?
            if hasattr(sprite, 'hitbox'): #sprite -> nesnesinde 'hitbox' var mi?
                if(sprite.hitbox.colliderect(self.hitbox)): #Hitbox varsa yonu var mi?
                    if direction == 'horizontal': #hitbox'un yonu ne?
                        if self.direction.x > 0: #Saga dogru git.
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom

                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery
             
    #Hareket etme fonksiyonu
    def move(self, dt):

        #Vektörü normalleştir.
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        #Yatay Hareketi = zaman x hiz x yon 
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        #Resim orta noktadan hareket edecek. Engel noktası
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        #Dikey Hareketi = zaman x hiz x yon
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        #Resim orta noktadan hareket edecek. Engel noktası
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    #input ve move fonksiyonları burada çalışacak!
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()

        self.move(dt)
        self.animate(dt)