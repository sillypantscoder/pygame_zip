import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def dialog(msg, options=["OK"]):
	pygame.init()
	pygame.font.init()
	FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
	msgRendered = FONT.render(msg, True, BLACK)
	msgWidth = msgRendered.get_width()
	msgHeight = msgRendered.get_height()
	SCREENSIZE = [msgWidth + 100, msgHeight + 50 + msgHeight]
	screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
	# Loop
	running = True
	c = pygame.time.Clock()
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.VIDEORESIZE:
				SCREENSIZE = [*event.dict["size"]]
				screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
		screen.fill(WHITE)
		screen.blit(msgRendered, ((SCREENSIZE[0] - msgWidth) / 2, ((SCREENSIZE[1] - msgHeight) - msgHeight) / 2))
		# Options
		option_width = (SCREENSIZE[0] / len(options)) - ((len(options) - 1) * 5)
		for o in options:
			pygame.draw.rect(screen, BLACK, pygame.Rect(0, SCREENSIZE[1] - msgHeight, SCREENSIZE[0], msgHeight))
		# Flip
		pygame.display.flip()
		c.tick(60)
	# End
	pygame.quit()
