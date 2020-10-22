------ Running (exe method) ------
./TilePainter/Code/run.exe

Opens a terminal window and then the tk window.
Close tk window when done.
*For convenience: Create a shortcut to run.exe in ./TilePainter 

------  Use (Controls) ------
*currently hard coded in

All
- Enter <Return>
	- brings focus back to Paint Canvas to allow scroll control
- Left Mouse Button <Button-1> 
	- brings focus back to Paint Canvas to allow scroll control

File Menu
- Open: opens dialogue to select image file. Must be .png
- Save: opens dialogue for saving current image. Must be .png
- Refresh Tileset: reloads all tilesets into the program. Used when adding/changing tilesets 

Tile Palette
- GUI Controls - use to select folder and tileset (i.e. area0.png in Custom Folder)
	- AreaID Spinbox: select tileset within typeid folder 
	- TypeID Radiobuttons: select typeid folder 
- Left Mouse Button <Button-1> 
	- On Click: select tile(s)
	- On Drag:  multiselect

Paint Canvas
- WASD
	- scroll paint canvas by 16pix increments
- Left Mouse Button <Button-1> 
	- On Click: place tile(s)
	- On Drag:  continuous placement
- Right Mouse Button <Button-3>
	- On Click: delete tile
	- On Drag:  continuous delete

------  Use (Custom Tilesets) ------
Custom Tilesets can be made and placed in ./TilePainter/Assets/Tilesets/Custom
*see Notes on Tileset Folder

Custom tilesets must be 256x256 pngs so that the program can split into 16x16 tiles.

Tricks:
- Make quick custom sets by pasting over one from the Palette Canvas to the Paint Canvas and then swapping out tiles and then saving.
	- This is useful for premaking groups of tiles and preparring a custom set to be edited in a image editing program of choice.


------  Notes  ------
Virus Protection
- run.exe might get removed by antivirus software. This shouldn't happen, but the possibility exists.

.py Files
- These are only needed if using the Python setup (see below). If only using run.exe, they can be removed.

AreaID Spinbox
- maximum is currently set to typeid with largest quantity of tilesets. If a typeid does not have a tileset at an areaid, it will appear blank. 
	i.e. OoA has max of 102 and OoS has max of 214. if Areaid is set to a number between 102 and 214 and typeid is OoA, the tile palette will be blank.

Tileset Folder
- tilesets must be sequential and named area{x}.png where {x} is a number. If they are not, it will not load tilesets properly and therefore none may be loaded at all.
	i.e. area0.png, area1.png, ..., area15.png, ..., area214.png etc.
- Do not put any other files in the tileset folders. Same issue will occur as mentioned in previous point.
- If the ./TilePainter/Assets/Tilesets folder does not exist, it will also break.

Save Folder
- whether or not ./TilePainter/Save exists should not break the program, but if anything does break, make sure it exists.

Tile Palette
- You can accidentally click beyond the tileset boundaries. This might cause things to scream. Otherwise you'll enter the neighboring tileset.

File>Save and Open
- If you try and open/save as something that isn't a png, it might scream, or it won't and just not open the file at all.   

------ Python Setup (Optional) ------
https://www.python.org/downloads/
Python 3.8+
IMPORTANT: Make sure to check "add to PATH" when the option appears 

For Windows:
start search> type "cmd" or "command prompt" > right click > run as administrator
Should show "C:\WINDOWS\system32>"

copy and paste each line individually, pressing enter.
pip install -U pip
pip install wheel
pip install Pillow
pip install numpy
pip install opencv-python
pip install pandas

------ Running (Python method) ------
./TilePainter/Code/main.py

Opens a py.exe and tk window.
Close tk then py.exe when done.