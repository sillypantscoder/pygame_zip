import os

def viewfile(filename: str, fileContents: bytes, preserve_filename=False):
	# Find destination filename
	name = filename[filename.rfind("/") + 1:]
	if preserve_filename: target = filename
	else: target = os.getcwd() + "/" + "_unzipped_" + name
	# Write file
	f = open(target, "wb")
	f.write(fileContents)
	f.close()
	# Open file
	if filename.endswith(".zip"):
		os.system(f"python3 unzip.py '{target}'")
	else:
		# Always use VS Code
		# to disable, replace this line
		# with "input()" so you can edit
		# the file elsewhere
		os.system(f"code --wait '{target}'")
	# Get new file contents
	f = open(target, "rb")
	newFileContents = f.read()
	f.close()
	# And delete file
	os.system(f"rm '{target}'")
	return [fileContents, newFileContents]