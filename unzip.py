from math import floor
import sys
import pygame
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import zipHelpers

pygame.init()
pygame.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
FONTHEIGHT = FONT.render("0", True, BLACK).get_height()
SCREENSIZE = [1000, 500 + FONTHEIGHT]
FILENAME = sys.argv[1]
if not FILENAME:
	print("Need to specify a file!")
	exit(1)
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
rawItems = zipHelpers.extract_zip(FILENAME).items

# SELECT FILE

# getFilesForDir(dir = "")
#   for Each item, if it does not have dir as a prefix, skip it
#   ...if it does have dir as a prefix:
#     determine if it's in a subdir or not:
#       if it has any slash after the prefix, it's a subdir and the name of the subdir is the name between the prefix and the first subsequent slash
#         there may be more than one such file, so we need to remove duplicate subdir mentions
#       otherwise, it's a file in the current dir

def getFiles(dir):
	r = []
	for n in rawItems:
		if not ("/" + n).startswith(dir):
			# Above this directory
			continue
		subname = n[len(dir):]
		slashPos = subname.find("/")
		if slashPos == -1:
			# If this file exists, we have a new file!
			if subname != "": r.append(subname)
	return r
def getFolders(dir):
	r = []
	for n in rawItems:
		if not ("/" + n).startswith(dir):
			# Above this directory
			continue
		subname = n[len(dir):]
		slashPos = subname.find("/")
		if slashPos != -1:
			# Below this directory!!!
			newDirName = subname[:slashPos]
			# If we have not already found this dir, we have a new directory!
			if newDirName not in r: r.append(newDirName)
	return r
def selectFile(filename):
	print(filename)

currentDir = ""

c = pygame.time.Clock()
running = True
while running:
	currentFolders = getFolders(currentDir)
	currentFiles = getFiles(currentDir)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			SCREENSIZE = [*event.dict["size"]]
			screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
		elif event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()[1]
			pos /= FONTHEIGHT
			pos -= 1
			pos = floor(pos)
			if pos == -1:
				currentDir = currentDir[:currentDir.rfind("/")]
			elif pos < len(currentFolders):
				currentDir += "/" + currentFolders[pos]
			elif pos < len(currentFiles) + len(currentFolders):
				selectFile(currentDir + "/" + currentFiles[pos - len(currentFolders)])
	screen.fill(WHITE)
	# HEADER
	pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, SCREENSIZE[0], FONTHEIGHT))
	f = FILENAME[FILENAME.rfind("/") + 1:]
	screen.blit(FONT.render(f + currentDir + f" ({len(currentFolders) + len(currentFiles)} items)", True, WHITE), (FONTHEIGHT + 10, 0))
	# arrow
	arrow = pygame.Surface((10, 10))
	arrow.fill(BLACK)
	pygame.draw.polygon(arrow, WHITE, ((10, 3), (5, 3), (5, 0), (0, 5), (5, 10), (5, 7), (10, 7)))
	screen.blit(pygame.transform.scale(arrow, (FONTHEIGHT, FONTHEIGHT)), (0, 0))
	# DIRECTORY
	pos = FONTHEIGHT
	for filename in currentFolders:
		screen.blit(FONT.render(filename + " >", True, BLACK), (0, pos))
		pos += FONTHEIGHT
	for filename in currentFiles:
		screen.blit(FONT.render(filename, True, GRAY), (0, pos))
		pos += FONTHEIGHT
	# FLIP
	pygame.display.flip()
	c.tick(60)