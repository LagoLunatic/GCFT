
## About

GameCube File Tools (GCFT) is a GUI tool for editing the following common file formats used by GameCube games:
* GCM (GameCube ISOs)
* RARC (archives)
* BTI (images)
* JPC (particle effect archives)
* Yaz0 (compression)

Features:
* Open and view GCMs, RARCs, BTIs, and JPCs
* Extract and replace individual files in GCMs and RARCs
* Extract all files in a GCM, RARC, or JPC at once to a folder
* Import a folder of files onto an existing GCM or RARC, overwriting the existing files
* Add/delete files in GCMs and RARCs
* Convert BTI images to PNG and back
* Edit the header attributes of BTI images (e.g. image format, palette format, wrapping, filter mode)
* Extract and replace the BTI textures embedded in J3D BDL and BMD models and BMT material tables, and JPC particle archives
* Import a folder of particle files onto an existing JPC, adding/overwriting all the particles from the folder to the JPC
* Compress and decompress Yaz0 files

It currently cannot create brand new GCMs, RARCs, BTIs, or JPCs from scratch.  

If you're on Windows, you can download GCFT here: <https://github.com/LagoLunatic/GCFT/releases>  
If you're on Mac or Linux, executable builds are not provided, so you must run it from the source code instead. See the "Running from source" section at the bottom of this readme.  

### Usage

Importing and exporting entire GCMs, RARCs, or JPCs can be done via the buttons in the appropriate tabs.  
Extracting, replacing, or deleting a single file can be done by first importing the GCM/RARC the file is in, and then right-clicking on the file you want to edit.  
Adding a new file can similarly be done by importing a GCM or RARC, and then right-clicking on the folder you want to add the file to.  

Modifying BTI images can be done by importing a standalone .bti file from the BTI Images tab, or first opening a GCM/RARC/JPC/J3D file that has BTIs inside it, right clicking on the image you want to edit there, and clicking "Open Image".
Once you're on the BTI Images tab, you can import or export the image as a PNG via the buttons at the top, and modify various attributes of the BTI image via the sidebar on the right.

Note that GCFT currently has no progress bars, so certain slow operations like compressing Yaz0 or saving GCMs might look like the program is frozen, but it's actually working.  

### Running from source

Download and install git from here: https://git-scm.com/downloads  
Then clone this repository with git by running this in a command prompt:  
`git clone --recurse-submodules https://github.com/LagoLunatic/GCFT.git`  

Download and install Python 3.8.2 from here: https://www.python.org/downloads/release/python-382/  
"Windows x86-64 executable installer" is the one you want if you're on Windows, "macOS 64-bit installer" if you're on Mac.  
If you're on Linux, run this command instead: `sudo apt-get install python3.8`  

Open the GCFT folder in a command prompt and install dependencies by running:  
`py -3.8 -m pip install -r requirements.txt` (on Windows)  
`python3 -m pip install -r requirements.txt` (on Mac)  
`python3 -m pip install $(cat requirements.txt) --user` (on Linux)  

Then run GCFT with:  
`py -3.8 gcft.py` (on Windows)  
`python3 gcft.py` (on Mac)  
`python3 gcft.py` (on Linux)  
