from math import floor
import pygame
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
from viewfile import viewfile
import dialog

#pygame.init()
pygame.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
FONTHEIGHT = FONT.render("0", True, BLACK).get_height()
SCREENSIZE = [1000, 500 + FONTHEIGHT]
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)

# SELECT FILE

def getFiles(dir):
	a = os.listdir(dir)
	r = []
	for n in a:
		if not os.path.isdir(dir + "/" + n):
			r.append(n)
	return r
def getFolders(dir):
	a = os.listdir(dir)
	r = []
	for n in a:
		if os.path.isdir(dir + "/" + n):
			r.append(n)
	return r
def selectFile(filename):
	f = open(filename, "rb")
	fileContents, newFileContents = viewfile(filename, f.read(), preserve_filename=True)
	f.close()
	f = open(filename, "wb")
	f.write(newFileContents)
	f.close()

currentDir = os.getcwd()

c = pygame.time.Clock()
running = True
offset = 0
while running:
	currentFolders = getFolders(currentDir)
	currentFiles = getFiles(currentDir)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			SCREENSIZE = [*event.dict["size"]]
			screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()[1]
			pos /= FONTHEIGHT
			pos -= 1
			pos = floor(pos)
			pos += offset
			if pos == -1:
				# Clicked on header
				currentDir = currentDir[:currentDir.rfind("/")]
			elif pos < len(currentFolders):
				# Clicked on a folder
				currentDir += "/" + currentFolders[pos]
			elif pos < len(currentFiles) + len(currentFolders):
				# Clicked on a file
				selectFile(currentDir + "/" + currentFiles[pos - len(currentFolders)])
		elif event.type == pygame.KEYDOWN:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_UP]:
				if offset > 0: offset -= 1
			elif keys[pygame.K_DOWN]: offset += 1
		if event.type == pygame.DROPFILE:
			path = event.file
			selectFile(path)
	screen.fill(WHITE)
	# DIRECTORY
	pos = ((-offset) + 1) * FONTHEIGHT
	for filename in currentFolders:
		screen.blit(FONT.render(filename + " >", True, BLACK), (0, pos))
		pos += FONTHEIGHT
	for filename in currentFiles:
		screen.blit(FONT.render(filename, True, GRAY), (0, pos))
		pos += FONTHEIGHT
	# HEADER
	pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, SCREENSIZE[0], FONTHEIGHT))
	screen.blit(FONT.render(currentDir + f" ({len(currentFolders) + len(currentFiles)} items)", True, WHITE), (FONTHEIGHT + 10, 0))
	# arrow
	arrow = pygame.Surface((10, 10))
	arrow.fill(BLACK)
	pygame.draw.polygon(arrow, WHITE, ((10, 3), (5, 3), (5, 0), (0, 5), (5, 10), (5, 7), (10, 7)))
	screen.blit(pygame.transform.scale(arrow, (FONTHEIGHT, FONTHEIGHT)), (0, 0))
	# FLIP
	pygame.display.flip()
	c.tick(60)