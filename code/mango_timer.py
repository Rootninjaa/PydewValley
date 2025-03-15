import pygame

#ZAMAN Kütüphanesi
class Timer:
    #duration -> geçen zaman, func -> boş
    def __init__(self, duration, func = None):
        self.duration = duration #Dışarıdan zaman değerleri alacağız.
        self.func = func #Dışarıdan fonksiyonlar alacağız.
        self.start_time = 0 #Başlangıç zamanı sıfır olsun.
        self.active = False #Ben söyleyene kadar Başlama
    
    #Zamanlayıcı aktif olursa
    def activate(self):
        self.active = True #Başlat.
        self.start_time = pygame.time.get_ticks()
    
    #Zamanlayıcı kapanması (de-active) olması
    def deactivate(self):
        self.active = False
        self.start_time = 0
    
    #Zamanlayıcı çalışırken olacaklar
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()