
## About

GameCube File Tools (GCFT) is a GUI tool for editing the following common file formats used by GameCube games:
* GCM (GameCube ISOs)
* RARC (archives)
* Yaz0 compression

Currently, it can:
* Open and view GCMs and RARCs (including file IDs inside RARCs)
* Extract and replace individual files in GCMs and RARCs
* Extract all files in a GCM or RARC at once to a folder
* Import a folder of files onto an existing GCM or RARC, overwriting the existing files (this preserves the original file IDs in RARCs)
* Add new files to GCMs and RARCs
* Delete files from GCMs and RARCs
* Compress and decompress Yaz0 files

It currently cannot create brand new GCMs or RARCs from scratch.  

### Usage

Importing and exporting entire GCMs and RARCs can be done via the buttons in the appropriate tabs.  
Extracting, replacing, or deleting a single file can be done by first importing the GCM/RARC the file is in, and then right-clicking on the file you want to edit.  
Adding a new file can similarly be done by importing a GCM or RARC, and then right-clicking on the folder you want to add the file to.  
Note that GCFT currently has no progress bars, so certain slow operations like compressing Yaz0 or saving GCMs might look like the program is frozen, but it's actually working.  

### Running from source

Download and install git from here: https://git-scm.com/downloads  
Then clone this repository with git by running this in a command prompt:  
`git clone --recurse-submodules https://github.com/LagoLunatic/GCFT.git`  

Download and install Python 3.6.6 from here: https://www.python.org/downloads/release/python-366/  
"Windows x86-64 executable installer" is the one you want if you're on Windows, "macOS 64-bit installer" if you're on Mac.  

Open the GCFT folder in a command prompt and install dependencies by running:  
`py -3.6 -m pip install -r requirements.txt` (on Windows)  
`python3 -m pip install -r requirements.txt` (on Mac)  

Then run the randomizer with:  
`py -3.6 gcft.py` (on Windows)  
`python3 gcft.py` (on Mac)  
