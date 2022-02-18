import pygame
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

WHITE = (255, 255, 255)
screen = pygame.display.set_mode([500, 500])

c = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(WHITE)
    pygame.display.flip()
    c.tick(60)