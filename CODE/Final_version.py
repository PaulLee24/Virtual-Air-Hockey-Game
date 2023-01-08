# -*- coding: utf-8 -*-
"""
Created on Sun May 16 23:36:57 2021

@author: Paul
"""

import random
import pygame
import math
import time
import numpy as np
import cv2
import sys
from time import sleep

pygame.init()

cheer_sound = pygame.mixer.Sound("music/cheer.ogg")

pygame.mixer.music.load("music/background.ogg")
pygame.mixer.music.play(-1)

cascPath = "hand.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

cap = cv2.VideoCapture(0)
cap.set(3,800)
cap.set(4,400)


def getHand():
    global cap, faceCascade
    
    if not cap.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass

    # Capture frame-by-frame
    ret, frame_og = cap.read()
    frame=cv2.flip(frame_og,1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(25, 25)
    )
    
    hand_1_x = 0
    hand_1_y = 0
    hand_2_x = 0
    hand_2_y = 0

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        xmid=x+w/2
        ymid=y+h/2
        if xmid < 400:
            hand_1_x = xmid
            hand_1_y = ymid
        else:
            hand_2_x = xmid
            hand_2_y = ymid
            
    #cv2.imshow('Video', frame)
                
    return hand_1_x, hand_1_y, hand_2_x, hand_2_y, frame


def getHand_2():
    global cap, faceCascade
    
    if not cap.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass

    # Capture frame-by-frame
    ret, frame_og = cap.read()
    frame=cv2.flip(frame_og,1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(25, 25)
    )
    
    xmid = 0
    ymid = 0
    
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        xmid=x+w/2
        ymid=y+h/2
                    
    return xmid, ymid



windows_width = 1000
windows_height = 600
table_width = 800
table_height = 400
x_offset = (windows_width - table_width) / 2
y_offset = (windows_height - table_height) / 2

p1_score = 0
p2_score = 0

size = 64

ball_size = 40

ballImage = pygame.Surface((ball_size, ball_size), pygame.SRCALPHA)
#pygame.draw.circle(ballImage, (255, 255, 0), (ball_size//2, ball_size//2), ball_size//2)
    
handImage = pygame.Surface((size, size), pygame.SRCALPHA)
#pygame.draw.circle(handImage, (255, 255, 255), (size//2, size//2), size//2)

class Ball(pygame.sprite.Sprite):
    def __init__(self, startpos, velocity, startdir):
        super().__init__()
        self.pos = pygame.math.Vector2(startpos)
        self.velocity = velocity
        self.dir = pygame.math.Vector2(startdir).normalize()
        self.image = ballImage
        self.rect = self.image.get_rect(center = (round(self.pos.x), round(self.pos.y)))
        self.state = "PLAY"

    def reflect(self, NV):
        self.dir = self.dir.reflect(pygame.math.Vector2(NV))
    
    def set_v(self, v):
        if self.state == "PLAY":
            self.velocity = v
            
    def play(self):
        self.velocity = 3
        self.state = "PLAY"

    def update(self):
        global p1_score, p2_score        
        self.pos += self.dir * self.velocity
        self.rect.center = round(self.pos.x), round(self.pos.y)
        
        if self.rect.left <= x_offset:
            if self.pos.y >= y_offset+table_height//3+ball_size//2 and self.pos.y <= y_offset+table_height*2//3-ball_size//2:
                self.pos.x = windows_width // 2 + 5
                self.pos.y = windows_height // 2 + 5
                self.rect.center = round(self.pos.x), round(self.pos.y)
                self.velocity = 0
                self.state = "GOAL"
                cheer_sound.play()
                p2_score += 1
                self.dir = pygame.math.Vector2((-10, 0)).normalize()               
            else:
                self.reflect((1, 0))
                self.pos.x = x_offset + ball_size//2
        if self.pos.x >= windows_width - x_offset - ball_size//2:
            if self.pos.y >= y_offset+table_height//3+ball_size//2 and self.pos.y <= y_offset+table_height*2//3-ball_size//2:
                self.pos.x = windows_width // 2 + 5
                self.pos.y = windows_height // 2 + 5
                self.rect.center = round(self.pos.x), round(self.pos.y)
                self.velocity = 0
                self.state = "GOAL"
                cheer_sound.play()
                p1_score += 1
                self.dir = pygame.math.Vector2((10, 0)).normalize()
            else:
                self.pos.x = windows_width - x_offset - ball_size//2
                self.reflect((-1, 0))
        if self.rect.top <= y_offset:
            self.reflect((0, 1))
            self.pos.y = y_offset + ball_size//2
        if self.pos.y >= y_offset + table_height - ball_size//2:
            self.pos.y = y_offset + table_height - ball_size//2
            self.reflect((0, -1))
        
            
            

class Hand(pygame.sprite.Sprite):
    def __init__(self, startpos, velocity, startdir, num):
        super().__init__()
        self.pos = pygame.math.Vector2(startpos)
        self.velocity = velocity
        self.dir = pygame.math.Vector2(startdir).normalize()
        self.image = handImage
        self.rect = self.image.get_rect(center = (round(self.pos.x), round(self.pos.y)))
        self.num = num
        
        
    def update(self, x, y, dir_x, dir_y):
        prev_x = self.pos.x
        prev_y = self.pos.y
        
        if self.num == 1:
            if x >= x_offset + 32 and x <= x_offset + table_width//2-32:
                self.pos.x = x
            if y >= y_offset + 32 and y <= y_offset + table_height-32:
                self.pos.y = y
        elif self.num == 2:
            if x >= x_offset + table_width//2+32 and x <= x_offset + table_width-32:
                self.pos.x = x
            if y >= y_offset + 32 and y <= y_offset + table_height-32:
                self.pos.y = y
        
        self.rect.center = round(self.pos.x), round(self.pos.y)
        #v = math.sqrt( math.pow(dir_x,2)+math.pow(dir_y,2) ) * 60
        dx = self.pos.x - prev_x
        dy = self.pos.y - prev_y
        v = math.sqrt( math.pow(dx,2)+math.pow(dy,2) ) * 30
        self.velocity = v
        self.dir = pygame.math.Vector2((dir_x, dir_y))
        
            
    def reflect(self, NV):
        pass
    
    def set_v(self, v):
        pass

        


#pygame.init()
window = pygame.display.set_mode((windows_width, windows_height))

cam_show = pygame.display.set_mode((windows_width, windows_height))

clock = pygame.time.Clock()

all_balls = pygame.sprite.Group()

start, velocity, direction = (500, 300), 3, (random.random(), random.random())
ball_1 = Ball(start, velocity, direction)

start, velocity, direction = (150, 300), 0, (random.random(), random.random())
hand_1 = Hand(start, velocity, direction, 1)

start, velocity, direction = (600, 300), 0, (random.random(), random.random())
hand_2 = Hand(start, velocity, direction, 2)

all_balls.add(ball_1, hand_1, hand_2)

def reflectBalls(ball_1, hand_1, ball_v):
    c1 = pygame.math.Vector2(ball_1.rect.center)
    c2 = pygame.math.Vector2(hand_1.rect.center)
    r1 = ball_1.rect.width // 2
    r2 = hand_1.rect.width // 2
    d = c1.distance_to(c2)
    if d <= r1 + r2 :
        dnext = (c1 + ball_1.dir).distance_to(c2 + hand_1.dir)        
        nv = c2 - c1
        if dnext < d and nv.length() > 0:
            if ball_1.state == "PLAY":
                ball_1.set_v(ball_v)
                ball_1.reflect(nv)

run = True

'''
hand_1_x, hand_1_y = pygame.mouse.get_pos()
key_press = pygame.key.get_pressed()
#print(mouse_x, mouse_y)
hand_1_prev_x, hand_1_prev_y = hand_1_x, hand_1_y
'''

detect_criteria = 50

hand_1_x = 150
hand_1_y = 300
hand_2_x = 600
hand_2_y = 300

hand_1_prev_x = 150
hand_1_prev_y = 300
hand_2_prev_x = 600
hand_2_prev_y = 300

STATE = "START"
n = 0
n2 = 0

ball_v = 0

m1_clock = 0
m2_clock = 0
m3_clock = 0
m4_clock = 0

again_clock = 0
end_clock = 0

BG = "BLACK"

game_start_sec = 0

end_cond = "time"
end_point = 0
end_time = 0


while run:
    clock.tick(60)
    
    window.fill(0)
    
    if STATE == "START":
        if n < 100:
            n = n + 1
            window.fill(0)
            logo = pygame.image.load("image/hockey_logo.png") 
            logo = pygame.transform.scale(logo, (300, 250))
            window.blit(logo, (100,180))
            
            VIRTUAL = pygame.image.load("image/Virtual.PNG")
            VIRTUAL = pygame.transform.scale(VIRTUAL, (330, 80))
            window.blit(VIRTUAL, (500,180))
            
            AIR = pygame.image.load("image/Air_hockey.PNG")
            AIR = pygame.transform.scale(AIR, (400, 100))
            window.blit(AIR, (460,320))
        else:
            STATE = "SET_BG"
            n = 0
            
    
    if STATE == "SET_BG":
        window.fill(0)
        pointer_x, pointer_y = getHand_2()
        pointer_x = pointer_x + x_offset
        pointer_y = pointer_y + y_offset
        if n < 400:
            n = n + 1
            
            font_p1 = pygame.font.SysFont("simhei", 50)
            text_p1 = font_p1.render("Choose the background", True, (255,255,255), (0,0,0))
            window.blit(text_p1, (280,80))
            
            pygame.draw.rect(window, (255,255,255),[200, 200, 200, 100], 0)
            
            PA = pygame.image.load("image/grass.jpg")
            PA = pygame.transform.scale(PA, (200, 100))
            window.blit(PA, (200,400))
            
            pygame.draw.rect(window, (255,255,255),[600, 200, 200, 100], 2)
            
            getx1, gety1, getx2, gety2, frame = getHand()
            frame = np.swapaxes(frame, 0, 1)
            new_surf = pygame.pixelcopy.make_surface(frame)
            new_surf = pygame.transform.scale(new_surf, (200, 150))
            window.blit(new_surf, (600, 400))
            
            pygame.draw.circle(window, (255, 0, 0), (round(pointer_x), round(pointer_y)), 10)
            
            if pointer_x >= 205 and pointer_x <= 395 and pointer_y >= 205 and pointer_y <= 295:
                m1_clock = m1_clock + 1
            if pointer_x >= 605 and pointer_x <= 795 and pointer_y >= 205 and pointer_y <= 295:
                m2_clock = m2_clock + 1
            if pointer_x >= 205 and pointer_x <= 395 and pointer_y >= 405 and pointer_y <= 495:
                m3_clock = m3_clock + 1
            if pointer_x >= 605 and pointer_x <= 795 and pointer_y >= 405 and pointer_y <= 495:
                m4_clock = m4_clock + 1
                        
            if m1_clock > detect_criteria:
                STATE = "SHOW_BG_RESULT"
                BG = "WHITE"
                n = 0
            elif m2_clock > detect_criteria:
                STATE = "SHOW_BG_RESULT"
                BG = "BLACK"
                n = 0
            elif m3_clock > detect_criteria:
                STATE = "SHOW_BG_RESULT"
                BG = "GRASS"
                n = 0
            elif m4_clock > detect_criteria:
                STATE = "SHOW_BG_RESULT"
                BG = "CAMERA"
                n = 0
        else:
            STATE = "SHOW_BG_RESULT"
            BG = "BLACK"
            n = 0
            
    
    if STATE == "SHOW_BG_RESULT":
        window.fill(0)
        if n < 100:
            n = n + 1
            if BG == "BLACK":
                pygame.draw.rect(window, (255,255,255),[600, 200, 200, 100], 2)
            elif BG == "WHITE":
                pygame.draw.rect(window, (255,255,255),[200, 200, 200, 100], 0)
            elif BG == "GRASS":
                PA = pygame.image.load("image/grass.jpg")
                PA = pygame.transform.scale(PA, (200, 100))
                window.blit(PA, (200,400))
            else:
                getx1, gety1, getx2, gety2, frame = getHand()
                frame = np.swapaxes(frame, 0, 1)
                new_surf = pygame.pixelcopy.make_surface(frame)
                new_surf = pygame.transform.scale(new_surf, (200, 150))
                window.blit(new_surf, (600, 400))
        else:
            STATE = "SET_RULE"
            n = 0
            m1_clock = 0
            m2_clock = 0
            m3_clock = 0
            m4_clock = 0
    
    
    if STATE == "SET_RULE":
        window.fill(0)
        pointer_x, pointer_y = getHand_2()
        pointer_x = pointer_x + x_offset
        pointer_y = pointer_y + y_offset
        if n < 400:
            n = n + 1
            pygame.draw.rect(window, (255,255,255),[200, 200, 200, 200], 2)
            PA = pygame.image.load("image/point.png")
            PA = pygame.transform.scale(PA, (180, 90))
            window.blit(PA, (210,255))
            pygame.draw.rect(window, (255,255,255),[600, 200, 200, 200], 2)
            QUIT = pygame.image.load("image/time.png")
            QUIT = pygame.transform.scale(QUIT, (180, 90))
            window.blit(QUIT, (610,255))
            pygame.draw.circle(window, (255, 0, 0), (round(pointer_x), round(pointer_y)), 10)
            
            
            if pointer_x >= 205 and pointer_x <= 395 and pointer_y >= 205 and pointer_y <= 395:
                m1_clock = m1_clock + 1
            if pointer_x >= 605 and pointer_x <= 795 and pointer_y >= 205 and pointer_y <= 395:
                m2_clock = m2_clock + 1
                            
            if m1_clock > detect_criteria:
                STATE = "SET_COND"
                n = 0
                end_cond = "point"
                m1_clock = 0
                m2_clock = 0
            if m2_clock > detect_criteria:
                STATE = "SET_COND"
                n = 0
                end_cond = "time"
                m1_clock = 0
                m2_clock = 0
        else:
            STATE = "SET_COND"
            n = 0
            end_cond = "time"
            m1_clock = 0
            m2_clock = 0
    
    
    if STATE == "SET_COND":
        window.fill(0)
        pointer_x, pointer_y = getHand_2()
        pointer_x = pointer_x + x_offset
        pointer_y = pointer_y + y_offset
        if n < 50:
            n = n + 1
            if end_cond == "time":
                pygame.draw.rect(window, (255,255,255),[600-4*n, 200, 200, 200], 2)
                QUIT = pygame.image.load("image/time.png")
                QUIT = pygame.transform.scale(QUIT, (180, 90))
                window.blit(QUIT, (610-4*n,255))
            else:
                pygame.draw.rect(window, (255,255,255),[200+4*n, 200, 200, 200], 2)
                PA = pygame.image.load("image/point.png")
                PA = pygame.transform.scale(PA, (180, 90))
                window.blit(PA, (210+4*n,255))
        elif n < 100:
            n = n + 1
            pygame.draw.rect(window, (255,255,255),[400, 200, 200, 200], 2)
            if end_cond == "time":
                QUIT = pygame.image.load("image/time.png")
                QUIT = pygame.transform.scale(QUIT, (180, 90))
                window.blit(QUIT, (410,255))
            else:
                PA = pygame.image.load("image/point.png")
                PA = pygame.transform.scale(PA, (180, 90))
                window.blit(PA, (410,255))
        elif n < 150:
            n = n + 1
            pygame.draw.rect(window, (255,255,255),[400, 200, 200, 200], 2)
            pygame.draw.rect(window, (255,255,255),[400-6*(n-100), 200, 200, 200], 2)
            pygame.draw.rect(window, (255,255,255),[400+6*(n-100), 200, 200, 200], 2)
        elif n < 400:            
            n = n + 1
            pygame.draw.rect(window, (255,255,255),[100, 200, 200, 200], 2)            
            pygame.draw.rect(window, (255,255,255),[400, 200, 200, 200], 2)            
            pygame.draw.rect(window, (255,255,255),[700, 200, 200, 200], 2)
            if end_cond == "time":
                font_p1 = pygame.font.SysFont("simhei", 60)
                text_p1 = font_p1.render("1 min", True, (255,255,255), (0,0,0))
                window.blit(text_p1, (150,275))
                font_p1 = pygame.font.SysFont("simhei", 60)
                text_p1 = font_p1.render("3 min", True, (255,255,255), (0,0,0))
                window.blit(text_p1, (450,275))
                font_p1 = pygame.font.SysFont("simhei", 60)
                text_p1 = font_p1.render("5 min", True, (255,255,255), (0,0,0))
                window.blit(text_p1, (750,275))
                if pointer_x >= 105 and pointer_x <= 295 and pointer_y >= 205 and pointer_y <= 395:
                    m1_clock = m1_clock + 1
                if pointer_x >= 405 and pointer_x <= 595 and pointer_y >= 205 and pointer_y <= 395:
                    m2_clock = m2_clock + 1
                if pointer_x >= 705 and pointer_x <= 895 and pointer_y >= 205 and pointer_y <= 395:
                    m3_clock = m3_clock + 1
                
                if m1_clock > detect_criteria:
                    STATE = "SHOW_COND"
                    n = 0
                    end_time = 1
                if m2_clock > detect_criteria:
                    STATE = "SHOW_COND"
                    n = 0
                    end_time = 3
                if m3_clock > detect_criteria:
                    STATE = "SHOW_COND"
                    n = 0
                    end_time = 5
            if end_cond == "point":
                font_p1 = pygame.font.SysFont("simhei", 60)
                text_p1 = font_p1.render("3 pt", True, (255,255,255), (0,0,0))
                window.blit(text_p1, (160,275))
                font_p1 = pygame.font.SysFont("simhei", 60)
                text_p1 = font_p1.render("5 pt", True, (255,255,255), (0,0,0))
                window.blit(text_p1, (465,275))
                font_p1 = pygame.font.SysFont("simhei", 60)
                text_p1 = font_p1.render("10 pt", True, (255,255,255), (0,0,0))
                window.blit(text_p1, (755,275))
                if pointer_x >= 105 and pointer_x <= 295 and pointer_y >= 205 and pointer_y <= 395:
                    m1_clock = m1_clock + 1
                if pointer_x >= 405 and pointer_x <= 595 and pointer_y >= 205 and pointer_y <= 395:
                    m2_clock = m2_clock + 1
                if pointer_x >= 705 and pointer_x <= 895 and pointer_y >= 205 and pointer_y <= 395:
                    m3_clock = m3_clock + 1
                
                if m1_clock > detect_criteria:
                    STATE = "SHOW_COND"
                    n = 0
                    end_point = 3
                if m2_clock > detect_criteria:
                    STATE = "SHOW_COND"
                    n = 0
                    end_point = 5
                if m3_clock > detect_criteria:
                    STATE = "SHOW_COND"
                    n = 0
                    end_point = 10
            pygame.draw.circle(window, (255, 0, 0), (round(pointer_x), round(pointer_y)), 10)
        else:
            STATE = "SHOW_COND"
            n = 0
            if end_cond == "time":
                end_time = 1
            else:
                end_point = 5
            
            
    if STATE == "SHOW_COND":
        window.fill(0)
        if n < 50:
            n = n + 1
            if end_cond == "time":
                if end_time == 1:
                    pygame.draw.rect(window, (255,255,255),[100, 200, 200, 200], 2)
                    font_p1 = pygame.font.SysFont("simhei", 60)
                    text_p1 = font_p1.render("1 min", True, (255,255,255), (0,0,0))
                    window.blit(text_p1, (150,275))
                elif end_time == 3:
                    pygame.draw.rect(window, (255,255,255),[400, 200, 200, 200], 2)  
                    font_p1 = pygame.font.SysFont("simhei", 60)
                    text_p1 = font_p1.render("3 min", True, (255,255,255), (0,0,0))
                    window.blit(text_p1, (450,275))
                elif end_time == 5:
                    pygame.draw.rect(window, (255,255,255),[700, 200, 200, 200], 2)
                    font_p1 = pygame.font.SysFont("simhei", 60)
                    text_p1 = font_p1.render("5 min", True, (255,255,255), (0,0,0))
                    window.blit(text_p1, (750,275))
            elif end_cond == "point":
                if end_point == 5:
                    pygame.draw.rect(window, (255,255,255),[100, 200, 200, 200], 2)
                    font_p1 = pygame.font.SysFont("simhei", 60)
                    text_p1 = font_p1.render("5 pt", True, (255,255,255), (0,0,0))
                    window.blit(text_p1, (160,275))
                elif end_point == 11:
                    pygame.draw.rect(window, (255,255,255),[400, 200, 200, 200], 2)  
                    font_p1 = pygame.font.SysFont("simhei", 60)
                    text_p1 = font_p1.render("11 pt", True, (255,255,255), (0,0,0))
                    window.blit(text_p1, (455,275))
                elif end_point == 21:
                    pygame.draw.rect(window, (255,255,255),[700, 200, 200, 200], 2)
                    font_p1 = pygame.font.SysFont("simhei", 60)
                    text_p1 = font_p1.render("21 pt", True, (255,255,255), (0,0,0))
                    window.blit(text_p1, (755,275))
        else:
            STATE = "SET_MODE"
            n = 0
            m1_clock = 0
            m2_clock = 0
            m3_clock = 0
            m4_clock = 0    
    
    
    if STATE == "SET_MODE":
        window.fill(0)
        pointer_x, pointer_y = getHand_2()
        pointer_x = pointer_x + x_offset
        pointer_y = pointer_y + y_offset
        if n < 400:
            n = n + 1
            pygame.draw.rect(window, (0,255,0),[100, 200, 200, 200], 2)
            EASY = pygame.image.load("image/EASY.PNG")
            EASY = pygame.transform.scale(EASY, (180, 80))
            window.blit(EASY, (110,260))
            pygame.draw.rect(window, (255,255,0),[400, 200, 200, 200], 2)
            MEDIUM = pygame.image.load("image/MEDIUM.PNG")
            MEDIUM = pygame.transform.scale(MEDIUM, (180, 70))
            window.blit(MEDIUM, (410,265))
            pygame.draw.rect(window, (255,0,0),[700, 200, 200, 200], 2)
            HARD = pygame.image.load("image/HARD.PNG")
            HARD = pygame.transform.scale(HARD, (180, 80))
            window.blit(HARD, (710,260))
            pygame.draw.circle(window, (255, 0, 0), (round(pointer_x), round(pointer_y)), 10)
            
            if pointer_x >= 105 and pointer_x <= 295 and pointer_y >= 205 and pointer_y <= 395:
                m1_clock = m1_clock + 1
            if pointer_x >= 405 and pointer_x <= 595 and pointer_y >= 205 and pointer_y <= 395:
                m2_clock = m2_clock + 1
            if pointer_x >= 705 and pointer_x <= 895 and pointer_y >= 205 and pointer_y <= 395:
                m3_clock = m3_clock + 1
            
            
            if m1_clock > detect_criteria:
                STATE = "EASY"
                n = 0
            if m2_clock > detect_criteria:
                STATE = "MED"
                n = 0
            if m3_clock > detect_criteria:
                STATE = "HARD"
                n = 0
                
        else:
            STATE = "MED"
            n = 0

    
    if STATE == "EASY":
        if n < 30:
            pygame.draw.rect(window, (0,255,0),[100, 200, 200, 200], 2)
            EASY = pygame.image.load("image/EASY.PNG")
            EASY = pygame.transform.scale(EASY, (180, 80))
            window.blit(EASY, (110,260))
            n = n + 1
        elif n < 120:
            font_p1 = pygame.font.SysFont("simhei", 80)
            text_p1 = font_p1.render("Level: Easy", True, (255,255,255), (0,0,0))
            window.blit(text_p1, (330,280))
            n = n + 1
        else:
            STATE = "PLAY"
            ball_v = 15
            game_start_sec = time.time()
    
    if STATE == "MED":
        if n < 30:
            pygame.draw.rect(window, (255,255,0),[400, 200, 200, 200], 2)
            MEDIUM = pygame.image.load("image/MEDIUM.PNG")
            MEDIUM = pygame.transform.scale(MEDIUM, (180, 70))
            window.blit(MEDIUM, (410,265))
            n = n + 1
        elif n < 120:
            font_p1 = pygame.font.SysFont("simhei", 80)
            text_p1 = font_p1.render("Level: Medium", True, (255,255,255), (0,0,0))
            window.blit(text_p1, (300,280))
            n = n + 1
        else:
            STATE = "PLAY"
            ball_v = 30
            game_start_sec = time.time()
    
    if STATE == "HARD":
        if n < 30:
            pygame.draw.rect(window, (255,0,0),[700, 200, 200, 200], 2)
            HARD = pygame.image.load("image/HARD.PNG")
            HARD = pygame.transform.scale(HARD, (180, 80))
            window.blit(HARD, (710,260))
            n = n + 1
        elif n < 120:
            font_p1 = pygame.font.SysFont("simhei", 80)
            text_p1 = font_p1.render("Level: Hard", True, (255,255,255), (0,0,0))
            window.blit(text_p1, (330,280))
            n = n + 1
        else:
            STATE = "PLAY"
            ball_v = 50
            game_start_sec = time.time()
            
    if STATE == "PLAY":
        
        m1_clock = 0
        m2_clock = 0
        m3_clock = 0
        m4_clock = 0
        
        game_durarion = time.time() - game_start_sec
                
        game_min = int(game_durarion // 60)
        game_sec = int(game_durarion % 60)
        
        if game_sec < 10:
            show_sec = "0" + str(game_sec)
        else:
            show_sec = str(game_sec)
        
        #########  Draw Time Duraton  ########################################
        font_s1 = pygame.font.SysFont("simhei", 40)
        text_s1 = font_s1.render("Game Duration ", True, (255,255,255), (0,0,0))
        window.blit(text_s1, (325,40))
        
        font_s1 = pygame.font.SysFont("simhei", 40)
        text_s1 = font_s1.render(str(game_min), True, (255,255,255), (0,0,0))
        window.blit(text_s1, (555,40))
        
        font_s2 = pygame.font.SysFont("simhei", 40)
        text_s2 = font_s2.render(" : ", True, (255,255,255), (0,0,0))
        window.blit(text_s2, (575,40))
        
        font_s2 = pygame.font.SysFont("simhei", 40)
        text_s2 = font_s2.render(show_sec, True, (255,255,255), (0,0,0))
        window.blit(text_s2, (600,40))
        #####################################################################
        
        font_s1 = pygame.font.SysFont("simhei", 30)
        text_s1 = font_s1.render("End Condition : ", True, (255,0,0), (0,0,0))
        window.blit(text_s1, (375,540))
        
        if end_cond == "time":
            endstr = str(end_time) + " " + "min"
                
        elif end_cond == "point":
            endstr = str(end_point) + " " + "pt"
                 
        font_s1 = pygame.font.SysFont("simhei", 30)
        text_s1 = font_s1.render(endstr, True, (255,0,0), (0,0,0))
        window.blit(text_s1, (535,540))
        
        getx1, gety1, getx2, gety2, frame = getHand()
        
        if BG == "BLACK":
            pygame.draw.rect(window, (0,0,0),[x_offset, y_offset, 800, 400], 0)
        elif BG == "WHITE":
            pygame.draw.rect(window, (255,255,255),[x_offset, y_offset, 800, 400], 0)
        elif BG == "GRASS":
            PA = pygame.image.load("image/grass.jpg")
            PA = pygame.transform.scale(PA, (800, 400))
            window.blit(PA, (x_offset, y_offset))
        else:
            ########  Show camera view  ############################################################
            frame = np.swapaxes(frame, 0, 1)
            new_surf = pygame.pixelcopy.make_surface(frame)
            window.blit(new_surf, (x_offset, y_offset))
            ########################################################################################
                
        
        pygame.draw.rect(window, (255,255,128),[10, 10, 80, 60], 2)
        font_p1 = pygame.font.SysFont("simhei", 24)
        text_p1 = font_p1.render("Player 1", True, (0,0,255), (0,0,0))
        window.blit(text_p1, (20,75))
        
        pygame.draw.rect(window, (255,255,128),[windows_width-90, 10, 80, 60], 2)
        font_p2 = pygame.font.SysFont("simhei", 24)
        text_p2 = font_p1.render("Player 2", True, (0,0,255), (0,0,0))
        window.blit(text_p2, (windows_width-80,75))       
                    
        
        if getx1 != 0 and gety1 != 0:
            hand_1_x, hand_1_y = getx1, gety1   
            hand_1_x = hand_1_x + x_offset
            hand_1_y = hand_1_y + y_offset
            
        if getx2 != 0 and gety2 != 0:
            hand_2_x, hand_2_y = getx2, gety2
            hand_2_x = hand_2_x + x_offset
            hand_2_y = hand_2_y + y_offset
               
        
        hand_1_dir_x = hand_1_x - hand_1_prev_x
        hand_1_dir_y = hand_1_y - hand_1_prev_y
        
        hand_2_dir_x = hand_2_x - hand_2_prev_x
        hand_2_dir_y = hand_2_y - hand_2_prev_y

        
        ######################################################################################################################
        v1 = pygame.math.Vector2(ball_1.rect.center)
        v2 = pygame.math.Vector2((hand_1_x, hand_1_y))
        r1 = ball_1.rect.width // 2
        r2 = hand_1.rect.width // 2
        d = v1.distance_to(v2)
        vt = v1-v2
        v_dir = pygame.math.Vector2((hand_1_dir_x, hand_1_dir_y))
        if d > r1 + r2 - 2:
            hand_1.update(hand_1_x, hand_1_y, hand_1_dir_x, hand_1_dir_y)
            hand_1_prev_x = hand_1_x
            hand_1_prev_y = hand_1_y
        elif vt.dot(v_dir) <= 0:
            hand_1.update(hand_1_x, hand_1_y, hand_1_dir_x, hand_1_dir_y)
            hand_1_prev_x = hand_1_x
            hand_1_prev_y = hand_1_y
        ######################################################################################################################
        
        
        
        ######################################################################################################################
        v2 = pygame.math.Vector2((hand_2_x, hand_2_y))
        r1 = ball_1.rect.width // 2
        r2 = hand_2.rect.width // 2
        d = v1.distance_to(v2)
        vt = v1-v2
        v_dir = pygame.math.Vector2((hand_2_dir_x, hand_2_dir_y))
        if d > r1 + r2 - 2:
            hand_2.update(hand_2_x, hand_2_y, hand_2_dir_x, hand_2_dir_y)
            hand_2_prev_x = hand_2_x
            hand_2_prev_y = hand_2_y
        elif vt.dot(v_dir) <= 0:
            hand_2.update(hand_2_x, hand_2_y, hand_2_dir_x, hand_2_dir_y)
            hand_2_prev_x = hand_2_x
            hand_2_prev_y = hand_2_y    
        ######################################################################################################################
        
            
        if ball_1.state == "GOAL":
            if hand_1_x <= windows_width//2 - table_width //4 and hand_2.pos.x >= windows_width//2 + table_width //4:
                ball_1.play()
            else:
                if hand_1_x > windows_width//2 - table_width //4:
                    pygame.draw.line(window, (255,128,0), (windows_width//2 - table_width //4 + size //2, y_offset), (windows_width//2 - table_width //4 + size //2, y_offset+table_height), 3)
                if hand_2.pos.x < windows_width//2 + table_width //4:
                    pygame.draw.line(window, (255,128,0), (windows_width//2 + table_width //4 - size //2, y_offset), (windows_width//2 + table_width //4 - size //2, y_offset+table_height), 3)

        ball_list = all_balls.sprites()
        for i, b1 in enumerate(ball_list):
            for b2 in ball_list[i+1:]:
                reflectBalls(b1, b2, ball_v)
        '''
        reflectBalls(ball_1, hand_1)
        reflectBalls(ball_1, hand_2)
        '''
                    
        ball_1.update()
        
        if end_cond == "time":
            if game_min == end_time:
                STATE = "SHOW_GAME_OVER"
                n = 0
                
        elif end_cond == "point":
            if p1_score >= end_point or p2_score >= end_point:
                 STATE = "SHOW_GAME_OVER"
                 n = 0
        
        #########  Draw Score Board  ########################################
        if p1_score < 10:
            font_s1 = pygame.font.SysFont("simhei", 50)
            text_s1 = font_s1.render(str(p1_score), True, (0,0,255), (0,0,0))
            window.blit(text_s1, (40,25))
        else:
            font_s1 = pygame.font.SysFont("simhei", 50)
            text_s1 = font_s1.render(str(p1_score), True, (0,0,255), (0,0,0))
            window.blit(text_s1, (30,25))
            
        if p2_score < 10:
            font_s2 = pygame.font.SysFont("simhei", 50)
            text_s2 = font_s2.render(str(p2_score), True, (0,0,255), (0,0,0))
            window.blit(text_s2, (windows_width-60,25))
        else:
            font_s2 = pygame.font.SysFont("simhei", 50)
            text_s2 = font_s2.render(str(p2_score), True, (0,0,255), (0,0,0))
            window.blit(text_s2, (windows_width-70,25))
        #####################################################################

        #window.fill(0)
        #########  Draw Table  ##############################################
        pygame.draw.line(window, (255,0,255), (x_offset, y_offset+table_height//3), (x_offset, y_offset+table_height*2//3), 10)
        pygame.draw.line(window, (255,0,255), (windows_width-x_offset, y_offset+table_height//3), (windows_width-x_offset, y_offset+table_height*2//3), 10)
        pygame.draw.line(window, (255,0,0), (windows_width//2, y_offset), (windows_width//2, windows_height//2-table_height//8), 4)
        pygame.draw.line(window, (255,0,0), (windows_width//2, windows_height//2+table_height//8), (windows_width//2, windows_height-y_offset), 4)
        pygame.draw.circle(window, (255,0,0),(windows_width//2,windows_height//2), table_height//8, 4)
        pygame.draw.rect(window, (255, 255, 255), [x_offset, y_offset, table_width, table_height], 2)
        #####################################################################
        
        pygame.draw.circle(window, (255, 255, 0), (round(ball_1.pos.x), round(ball_1.pos.y)), ball_size//2)
        pygame.draw.circle(window, (128, 255, 255), (round(hand_1.pos.x), round(hand_1.pos.y)), size//2)
        pygame.draw.circle(window, (128, 255, 255), (round(hand_2.pos.x), round(hand_2.pos.y)), size//2)
    
    
    if STATE == "SHOW_GAME_OVER":
        window.fill(0)
        if n < 80:
            n = n + 1
            if end_cond == "time":
                TU = pygame.image.load("image/TU.png")
                TU = pygame.transform.scale(TU, (400, 80))
                window.blit(TU, (300,250))
            else:
                GO = pygame.image.load("image/game_over.png")
                GO = pygame.transform.scale(GO, (370, 100))
                window.blit(GO, (300,250))
        elif n < 200:
            n = n + 1
            if p1_score == p2_score:
                tie = pygame.image.load("image/tie.png")
                tie = pygame.transform.scale(tie, (400, 90))
                window.blit(tie, (275,250))
            elif p1_score > p2_score:
                win1 = pygame.image.load("image/win1.png")
                win1 = pygame.transform.scale(win1, (500, 90))
                window.blit(win1, (250,250))
            else:
                win2 = pygame.image.load("image/win2.png")
                win2 = pygame.transform.scale(win2, (500, 90))
                window.blit(win2, (250,250))
        else:
            STATE = "CHOOSE_STATE"
            n = 0
    
    
    if STATE == "CHOOSE_STATE":
        p1_score = 0
        p2_score = 0        
        pointer_x, pointer_y = getHand_2()
        pointer_x = pointer_x + x_offset
        pointer_y = pointer_y + y_offset
        if n < 500:
            n = n + 1
            pygame.draw.rect(window, (255,255,255),[200, 200, 200, 200], 2)
            PA = pygame.image.load("image/PLAY_AGAIN.png")
            PA = pygame.transform.scale(PA, (180, 160))
            window.blit(PA, (210,220))
            pygame.draw.rect(window, (255,255,255),[600, 200, 200, 200], 2)
            QUIT = pygame.image.load("image/QUIT.PNG")
            QUIT = pygame.transform.scale(QUIT, (180, 80))
            window.blit(QUIT, (610,260))
            pygame.draw.circle(window, (255, 0, 0), (round(pointer_x), round(pointer_y)), 10)
            
            if pointer_x >= 205 and pointer_x <= 395 and pointer_y >= 205 and pointer_y <= 395:
                again_clock = again_clock + 1
            
            if pointer_x >= 605 and pointer_x <= 795 and pointer_y >= 205 and pointer_y <= 395:
                end_clock = end_clock + 1
            
                
            if again_clock > detect_criteria:
                STATE = "RETURN"
                n = 0
                again_clock = 0
            if end_clock > detect_criteria:
                STATE = "END"
                n = 0
            
        else:
            STATE = "END"
            n = 0
    
    if STATE == "RETURN":
        if n < 30:
            pygame.draw.rect(window, (255,255,255),[200, 200, 200, 200], 2)
            PA = pygame.image.load("image/PLAY_AGAIN.png")
            PA = pygame.transform.scale(PA, (180, 160))
            window.blit(PA, (210,220))
            n = n + 1
        else:
            STATE = "SET_BG"
            n = 0
            game_start_sec = 0
            BG = "BLACK"
            end_cond = "time"
            end_point = 0
            end_time = 0
            m1_clock = 0
            m2_clock = 0
            m3_clock = 0
            m4_clock = 0            
            again_clock = 0
            end_clock = 0
    
    if STATE == "END":
        window.fill(0)
        if n < 30:
            pygame.draw.rect(window, (255,255,255),[600, 200, 200, 200], 2)
            QUIT = pygame.image.load("image/QUIT.png")
            QUIT = pygame.transform.scale(QUIT, (180, 80))
            window.blit(QUIT, (610,260))
            n = n + 1
        elif n < 90:
            font_p1 = pygame.font.SysFont("simhei", 80)
            text_p1 = font_p1.render("-", True, (255,255,255), (0,0,0))
            window.blit(text_p1, (300,280))
            n = n + 1
        elif n < 180:
            font_p1 = pygame.font.SysFont("simhei", 80)
            text_p1 = font_p1.render("-", True, (255,255,255), (0,0,0))
            window.blit(text_p1, (300,280))
            font_p2 = pygame.font.SysFont("simhei", 80)
            text_p2 = font_p2.render("-", True, (255,255,255), (0,0,0))
            window.blit(text_p2, (500,280))
            n = n + 1
        elif n < 240:
            font_p1 = pygame.font.SysFont("simhei", 80)
            text_p1 = font_p1.render("-", True, (255,255,255), (0,0,0))
            window.blit(text_p1, (300,280))
            font_p2 = pygame.font.SysFont("simhei", 80)
            text_p2 = font_p2.render("-", True, (255,255,255), (0,0,0))
            window.blit(text_p2, (500,280))
            font_p3 = pygame.font.SysFont("simhei", 80)
            text_p3 = font_p3.render("-", True, (255,255,255), (0,0,0))
            window.blit(text_p3, (700,280))
            n = n + 1
        else:
            run = False
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    all_balls.draw(window)
    pygame.display.flip()


pygame.mixer.music.stop()

pygame.quit()


# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
