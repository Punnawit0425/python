import pygame
import math

pygame.init()
screen = pygame.display.set_mode((700,700))
pygame.display.set_caption("Spinning Square")


clock = pygame.time.Clock()
angle = 0
radius = 150
speed = 0.03

running = True
while running == True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            continue
    x = 600 // 2 + int(math.cos(angle) * radius)
    y = 600 // 2 + int(math.sin(angle) * radius)

    screen.fill((30,30,30))
    pygame.draw.rect(screen,(255,100,0),(x,y,100,100))
    pygame.draw.circle(screen, (0,255,255),(x,y),20)
    
    angle+=speed

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
