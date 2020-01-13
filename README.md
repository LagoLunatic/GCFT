
## About

GameCube File Tools (GCFT) is a GUI tool for editing the following common file formats used by GameCube games:
* GCM (GameCube ISOs)
* RARC (archives)
* Yaz0 compression

Currently it can open GCMs and RARCs, and view, extract, and replace the individual files in them (including the file IDs inside RARCs). It can also compress and decompress Yaz0 files.
It cannot yet extract all of the files from a GCM or RARC to a folder, nor import them all back at once. But this is a planned feature.
It has only been tested on Wind Waker so far but should work with other games.

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
