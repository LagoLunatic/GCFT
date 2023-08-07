
## About

GameCube File Tools (GCFT) is a GUI tool for editing the following common file formats used by GameCube games:
* GCM (GameCube ISOs)
* RARC (archives)
* BTI (images)
* Various J3D formats (e.g. textures in BDL and BMD models)
* JPC (particle effect archives) (versions 1-00 and 2-10)
* Yaz0 (compression)

Features:
* Open and view GCMs, RARCs, BTIs, and JPCs
* Extract and replace individual files in GCMs and RARCs
* Extract all files in a GCM, RARC, or JPC at once to a folder
* Import a folder of files onto an existing GCM or RARC, overwriting the existing files
* Create brand new RARCs from scratch
* Add/delete files in GCMs and RARCs, as well as folders in RARCs
* Convert BTI images to PNG and back
* Dump all BTI images in a GCM or a RARC to a folder as PNG
* Edit the header attributes of BTI images (e.g. image format, palette format, wrapping, filter mode)
* View and extract the images contained in GameCube banner files (.bnr)
* Extract and replace the BTI textures embedded in J3D BDL and BMD models and BMT material tables, and JPC particle archives
* Import a folder of particle files onto an existing JPC, adding/overwriting all the particles from the folder to the JPC
* Viewing DOL executable sections, and converting between offsets within the DOL file and RAM addresses in the game's memory
* Compress and decompress Yaz0 files

It currently cannot create brand new GCMs or JPCs from scratch.  

You can download GCFT here: https://github.com/LagoLunatic/GCFT/releases  
You can also try out the latest development build here (may have bugs): https://nightly.link/LagoLunatic/GCFT/workflows/python-app/master  

### Usage

Importing and exporting entire GCMs, RARCs, or JPCs can be done via the buttons in the appropriate tabs. Alternatively, you can drag and drop files onto GCFT and it will automatically open them in the correct tab (based on the file extension).  
Extracting, replacing, or deleting a single file can be done by first importing the GCM/RARC the file is in, and then right-clicking on the file you want to edit.  
Adding a new file can similarly be done by importing a GCM or RARC, and then right-clicking on the folder you want to add the file to.  
Editing the file name, folder type, or file ID of RARC files/folders can be done by double clicking on the field you want to edit, and then typing the new value into the text field.

Modifying BTI images can be done by importing a standalone .bti file from the BTI Images tab, or first opening a GCM/RARC/JPC/J3D file that has BTIs inside it, right clicking on the image you want to edit there, and clicking "Open Image".  
Once you're on the BTI Images tab, you can import or export the image as a PNG via the buttons at the top, and modify various attributes of the BTI image via the sidebar on the right.  

Note that compressing Yaz0 is slow and doesn't have a progress bar, so the program might look frozen for a while, but it's actually working.  

### Running from source

Download and install git from here: https://git-scm.com/downloads  
Then clone this repository with git by running this in a command prompt:  
`git clone --recurse-submodules https://github.com/LagoLunatic/GCFT.git`  

Download and install Python 3.10.7 from here: https://www.python.org/downloads/release/python-3107/  
"Windows installer (64-bit)" is the one you want if you're on Windows, "macOS 64-bit universal2 installer" if you're on Mac.  
If you're on Linux, run this command instead: `sudo apt-get install python3.10`  

Open the GCFT folder in a command prompt and install dependencies by running:  
`py -3.10 -m pip install -r requirements.txt` (on Windows)  
`python3 -m pip install -r requirements.txt` (on Mac)  
`python3 -m pip install $(cat requirements.txt) --user` (on Linux)  

Then run GCFT with:  
`py gcft.py` (on Windows)  
`python3 gcft.py` (on Mac)  
`python3 gcft.py` (on Linux)  
