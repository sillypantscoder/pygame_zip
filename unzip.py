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
modified = False

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
	global modified
	fileContents = rawItems[filename[1:]]
	name = filename[filename.rfind("/") + 1:]
	f = open("_unzipped_" + name, "wb")
	f.write(fileContents)
	f.close()
	os.system(f"xdg-open '{'_unzipped_' + name}'")
	f = open("_unzipped_" + name, "rb")
	newFileContents = f.read()
	rawItems[filename[1:]] = newFileContents
	f.close()
	if newFileContents != fileContents:
		modified = True
	os.system(f"rm '{'_unzipped_' + name}'")

currentDir = ""

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
		elif event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()[1]
			pos /= FONTHEIGHT
			pos -= 1
			pos = floor(pos)
			pos += offset
			if pos == -1:
				currentDir = currentDir[:currentDir.rfind("/")]
			elif pos < len(currentFolders):
				currentDir += "/" + currentFolders[pos]
			elif pos < len(currentFiles) + len(currentFolders):
				selectFile(currentDir + "/" + currentFiles[pos - len(currentFolders)])
		elif event.type == pygame.KEYDOWN:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_UP]:
				if offset > 0: offset -= 1
			elif keys[pygame.K_DOWN]: offset += 1
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
	f = FILENAME[FILENAME.rfind("/") + 1:]
	headerText = currentDir + f" ({len(currentFolders) + len(currentFiles)} items)"
	if modified: headerText = "*" + headerText
	headerText = f + headerText
	screen.blit(FONT.render(headerText, True, WHITE), (FONTHEIGHT + 10, 0))
	# arrow
	arrow = pygame.Surface((10, 10))
	arrow.fill(BLACK)
	pygame.draw.polygon(arrow, WHITE, ((10, 3), (5, 3), (5, 0), (0, 5), (5, 10), (5, 7), (10, 7)))
	screen.blit(pygame.transform.scale(arrow, (FONTHEIGHT, FONTHEIGHT)), (0, 0))
	# FLIP
	pygame.display.flip()
	c.tick(60)

# SAVING

if modified:
	running = True
	save = False
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.VIDEORESIZE:
				SCREENSIZE = [*event.dict["size"]]
				screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
			elif event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()[1]
				pos /= FONTHEIGHT
				pos = floor(pos)
				if floor(pygame.mouse.get_pos()[1] / FONTHEIGHT) == 1:
					if (pygame.mouse.get_pos()[0] / SCREENSIZE[0]) < 0.5: save = True
					running = False
		screen.fill(WHITE)
		# HEADER
		pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, SCREENSIZE[0], FONTHEIGHT))
		f = FILENAME[FILENAME.rfind("/") + 1:]
		screen.blit(FONT.render("Save changes to " + f + "?", True, WHITE), (FONTHEIGHT + 10, 0))
		# Yes
		pygame.draw.rect(screen, BLACK, pygame.Rect(0, FONTHEIGHT + 10, SCREENSIZE[0] / 2, FONTHEIGHT))
		f = FONT.render("Yes", True, WHITE)
		screen.blit(f, ((SCREENSIZE[0] / 4) - (f.get_width() / 2), FONTHEIGHT + 10))
		# No
		f = FONT.render("No", True, BLACK)
		screen.blit(f, ((SCREENSIZE[0] * 0.75) - (f.get_width() / 2), FONTHEIGHT + 10))
		# FLIP
		pygame.display.flip()
		c.tick(60)
if save:
	done = 0
	newFile = zipHelpers.InMemoryZip()
	for i in rawItems:
			newFile.append(i, rawItems[i])
			done += 1
			screen.fill(WHITE)
			screen.blit(FONT.render(f"Saving items... {done}/{len(rawItems)} done", True, BLACK), (0, 0))
			pygame.display.flip()
	newFile.writetofile("new_zip.zip")
	print("save")