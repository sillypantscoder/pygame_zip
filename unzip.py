from math import floor
import sys
import pygame
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import zipHelpers
from viewfile import viewfile
import dialog

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
originalRawItems = zipHelpers.extract_zip(FILENAME).items
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
	fileContents, newFileContents = viewfile(filename, rawItems[filename[1:]])
	rawItems[filename[1:]] = newFileContents

def save():
	global originalRawItems
	done = 0
	newFile = zipHelpers.InMemoryZip()
	for i in rawItems:
		newFile.append(i, rawItems[i])
		done += 1
		screen.fill(WHITE)
		screen.blit(FONT.render(f"Saving items... {done}/{len(rawItems)} done", True, BLACK), (0, 0))
		pygame.display.flip()
	f = open(FILENAME, "wb")
	f.write(newFile.read())
	f.close()
	originalRawItems = zipHelpers.extract_zip(FILENAME).items

currentDir = ""

c = pygame.time.Clock()
running = True
offset = 0
ctxmenupos = None
menuitems = []
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
			if ctxmenupos:
				cpos = pygame.mouse.get_pos()[1]
				cpos -= ctxmenupos[1]
				cpos /= FONTHEIGHT
				cpos = floor(cpos)
				if cpos < len(menuitems):
					menuitems = []
					pos = ctxmenupos[1]
					pos /= FONTHEIGHT
					pos -= 1
					pos = floor(pos)
					pos += offset
					if pos == -1:
						# Clicked on header
						if cpos == 0:
							rawItems[currentDir[1:] + "/" + dialog.prompt("New file name")] = b""
						if cpos == 1:
							rawItems[currentDir[1:] + "/" + dialog.prompt("New folder name") + "/"] = b""
					elif pos < len(currentFolders):
						# Clicked on a folder
						selectedItem = currentDir + "/" + currentFolders[pos]
						if cpos == 0: print("Rename:", selectedItem)
						if cpos == 1 and dialog.dialog(f"Are you sure you want to delete {selectedItem}?", ["OK", "Cancel"]) == "OK":
							del rawItems[selectedItem[1:] + "/"]
					elif pos < len(currentFiles) + len(currentFolders):
						# Clicked on a file
						selectedItem = currentDir + "/" + currentFiles[pos - len(currentFolders)]
						if cpos == 0: print("Rename:", selectedItem)
						if cpos == 1 and dialog.dialog(f"Are you sure you want to delete {selectedItem}?", ["OK", "Cancel"]) == "OK":
							del rawItems[selectedItem[1:]]
				ctxmenupos = None
			else:
				pos = pygame.mouse.get_pos()[1]
				pos /= FONTHEIGHT
				pos -= 1
				pos = floor(pos)
				pos += offset
				buttons = pygame.mouse.get_pressed()
				if pos == -1:
					# Clicked on header
					if buttons[0]: currentDir = currentDir[:currentDir.rfind("/")]
					if buttons[2]:
						# Right-clicked on header
						ctxmenupos = (*pygame.mouse.get_pos(),)
				elif pos < len(currentFolders):
					# Clicked on a folder
					if buttons[0]: currentDir += "/" + currentFolders[pos]
					if buttons[2]:
						# Right-clicked on a folder
						ctxmenupos = (*pygame.mouse.get_pos(),)
				elif pos < len(currentFiles) + len(currentFolders):
					# Clicked on a file
					if buttons[0]: selectFile(currentDir + "/" + currentFiles[pos - len(currentFolders)])
					if buttons[2]:
						# Right-clicked on a file
						ctxmenupos = (*pygame.mouse.get_pos(),)
		elif event.type == pygame.KEYDOWN:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_UP]:
				if offset > 0: offset -= 1
			elif keys[pygame.K_DOWN]: offset += 1
			if keys[pygame.K_s]:
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					save()
		elif event.type == pygame.DROPFILE:
			path = event.file
			if dialog.dialog("Add " + path[path.rfind("/") + 1:], ["Add", "Cancel"]) == "Add":
				f = open(path, "rb")
				rawItems[currentDir + path[path.rfind("/") + 1:]] = f.read()
				f.close()
	screen.fill(WHITE)
	# DIRECTORY
	pos = ((-offset) + 1) * FONTHEIGHT
	for filename in currentFolders:
		screen.blit(FONT.render(filename + " >", True, BLACK), (0, pos))
		pos += FONTHEIGHT
	for filename in currentFiles:
		screen.blit(FONT.render(filename, True, GRAY), (0, pos))
		pos += FONTHEIGHT
	# MODIFICATIONS
	modified = rawItems != originalRawItems
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
	# CONTEXT MENU
	if ctxmenupos:
		menuitems = []
		pos = ctxmenupos[1]
		pos /= FONTHEIGHT
		pos -= 1
		pos = floor(pos)
		pos += offset
		if pos == -1:
			# Clicked on header
			menuitems.append("Add file")
			menuitems.append("Add subfolder")
		elif pos < len(currentFolders):
			# Clicked on a folder
			menuitems.append("Rename")
			menuitems.append("Delete")
		elif pos < len(currentFiles) + len(currentFolders):
			# Clicked on a file
			menuitems.append("Rename")
			menuitems.append("Delete")
		width = 0
		for i in menuitems:
			r_i = FONT.render(i, True, BLACK)
			if width < r_i.get_width(): width = r_i.get_width()
		pygame.draw.rect(screen, GRAY, pygame.Rect(*ctxmenupos, width, len(menuitems)*FONTHEIGHT))
		cum_y = 0
		for i in menuitems:
			screen.blit(FONT.render(i, True, BLACK), (ctxmenupos[0], ctxmenupos[1] + cum_y))
			cum_y += FONTHEIGHT
	# FLIP
	pygame.display.flip()
	c.tick(60)

# SAVING

if modified:
	running = True
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
					if (pygame.mouse.get_pos()[0] / SCREENSIZE[0]) < 0.5: save()
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
