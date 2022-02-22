import os

def viewfile(filename: str, fileContents: bytes):
	# Write file
	name = filename[filename.rfind("/") + 1:]
	f = open("_unzipped_" + name, "wb")
	f.write(fileContents)
	f.close()
	# Open file
	if filename.endswith(".zip"):
		os.system(f"python3 unzip.py '{'_unzipped_' + name}'")
	else:
		os.system(f"xdg-open '{'_unzipped_' + name}'")
	# Get new file contents
	f = open("_unzipped_" + name, "rb")
	newFileContents = f.read()
	f.close()
	# And delete file
	os.system(f"rm '{'_unzipped_' + name}'")
	return [fileContents, newFileContents]