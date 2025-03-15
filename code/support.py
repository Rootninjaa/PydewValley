from os import walk #klasörleri sergileyen yapıdır.
import pygame

#Klasörleri istediğim yola ekleyen fonksiyon
def import_folder(path):
    #Grafik dosyalarını bul
    surface_list = []

    #Klasörlerde resim dosyası ara
    for _, _, img_files in walk(path):
        for image in img_files:
            full_path = path+ '/'+image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    #Her bir resmi listeye ekledikten sonra listeyi çağır.
    return surface_list

#Klasör Yolunu Veren Fonksiyon
def import_folder_dict(path):
    surface_dict = {}

    for _, _, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split('.')[0]] = image_surf
    return surface_dict