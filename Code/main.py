import cv2
import numpy as np
from PIL import Image as PIL_Image, ImageTk as PIL_ImageTk
import os
import tkinter.filedialog as tk_filedialog
import tkinter as tk

from FileFolderPaths import FileFolderPaths
from Tile_Manager import Tile_Manager
from tile_painter import tile_painter

def main():
    master = tk.Tk()
    master.title("TilePainter")
    TM=Tile_Manager()
    tp=tile_painter(master,TM)
    master.mainloop()


if __name__=="__main__":
    main()
