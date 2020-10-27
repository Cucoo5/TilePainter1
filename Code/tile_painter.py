import cv2
import numpy as np
import pandas as pd
from PIL import Image as PIL_Image, ImageTk as PIL_ImageTk
import os
import tkinter.filedialog as tk_filedialog
import tkinter as tk

from FileFolderPaths import FileFolderPaths
from Tile_Manager import Tile_Manager


class tile_painter():
    def __init__(self,master,TileManager):

        '''
        Main Window
        '''
        self.master=master

        '''
        Window Resizable
        '''
        self.master.resizable(True,True)


        '''
        Tile Manager Class Object
        Most variables are stored within
        '''

        self.TM=TileManager

        '''
        Cursor Coordinates List
        Used for Click and Drag Selection Event

        '''

        self.CursorCoordList=[]

        '''
        Paths and Tile Dimension Variables
        stored in self.TM.FFP
        '''

        '''
        Canvas Matrix
        stored in TM
        '''

        '''
        current selected tiles
        starts at [0,0,[0,0],[0,0]]

        remember: tiles sub coordinates always in form of range.
        single tiles will be submin==submax

        stored within TM, call MultitileTool when needed
        '''

        #self.currenttiles=self.TM.MultitileTool()

        # stores canvas img objects for simple iteration
        #self.TPallCanvasImgObj={(x,y):canvasimgobj,...}
        #self.TPainCanvasImgObj={(x,y):canvasimgobj,...}

        #self.TPallCanvasImgObj={}
        #self.TPainCanvasImgObj={}

        self.TPallStorage=[(0,0),None,None] #[(x,y),imgtk,img_pil]
        self.TPainStorage={} #dict of imgtag:[(x,y),imgtk,img_pil]
        #list of tiles will be in: tilelist=obj.find_withtag("tiles")

        #tilepreviewstorage
        tp_pil=self.TM.createtilepreview()
        self.tpTk=PIL_ImageTk.PhotoImage(image=tp_pil)

        '''
        Initialize master image
        used in conjunction with canvas matrix to display tiles without
        needing individual tile objects
        Located in TM
        '''




        """
        ---------------------------------------------------------------------
                                    WIDGETS SECTION
        ---------------------------------------------------------------------
        """


        '''
        Initialize Area ID Spinbox

        '''


        self.areaidspinboxOut=tk.IntVar()
        self.areaidspinboxOut.set(self.TM.areaid)

        self.areaidspinboxWidget=self.SpinboxFunc(0,(np.shape(self.TM.MasterMatrix)[1]/self.TM.tilesize)-1,self.areaidspinboxOut,5)

        self.areaidspinboxWidget.grid(row=1,column=0,sticky = 'W', pady = 2)

        # Area ID Spinbox Label
        self.labelareaIDspinbox=tk.Label(master,text="Area ID")
        self.labelareaIDspinbox.grid(row=0,column=0, sticky= 'W',pady = 2)

        #Area ID Spinbox event trigger
        try:
            self.areaidspinboxOut.trace('w',self.on_areaID_change)
        except:
            pass


        '''
        Initialize Label for Current Selected Tile
        changes on current tile change
        '''

        self.labelcurseltile=tk.Label(master,
                  text=f"| T:{self.TM.typeid}-A:{self.TM.areaid}-Tile:({self.TM.subx},{self.TM.suby})")
        self.labelcurseltile.grid(row=0,column=1,columnspan=4,sticky = 'W', pady = 2)


        '''
        Initialize Tile Palette Canvas
        '''
        self.TilePaletteCanvas=self.CanvasFunc(width=self.TM.tilesize**2,height=self.TM.tilesize**2,background="grey")
        self.TilePaletteCanvas.grid(row=4,column=0, columnspan=4, rowspan=2,sticky = tk.N+tk.W,padx=2,pady=2)

        self.TileSetPaletteBuilder()

        #initialize cursor and selected cursor
        #self.Cursor0img=self.imagetkmaker(self.uipath+"/Cursor0.png","tilecursor")
        #self.Cursor1img=self.imagetkmaker(self.uipath+"/Cursor1.png","selectedtilecursor")
        try:
            coord=[(0,0),(0,0)]
            color1="red"
            bbox1=self.CursorRectangle(coord)[1]
            Cursor1=self.TilePaletteCanvas.create_rectangle(bbox1,outline=color1,width=2,tags="Cursor1")
            #self.Cursor1=self.TilePaletteCanvas.create_image((2,2),image=self.Cursor1img,anchor=tk.NW,tags="cursor")
        except tk.TclError:
            pass



        '''
        Initialize Radiobuttons for typeid change
        '''

        self.typeidradiobuttonout=tk.StringVar()
        self.typeidradiobuttonout.set(self.TM.typeid)

        self.Radioinputs=[("OoA",0),("OoS",1),("Custom",2)]

        #TODO: Change control function
        self.typeidradiobuttonWidgets=self.RadiobutFunc(self.Radioinputs,self.typeidradiobuttonout)

        radiocol=1
        for radiobuttonwidget in self.typeidradiobuttonWidgets:
            radiobuttonwidget.grid(row=1,column=radiocol,sticky = tk.W,padx=2,pady=2)
            radiocol+=1

        self.typeidradiobuttonout.trace('w',self.on_typeID_change)


        '''
        Initialize Menu bar
        '''
        menubar=tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.filemenuopen)
        filemenu.add_command(label="Save", command=self.filemenusave)

        filemenu.add_separator()
        filemenu.add_command(label="Refresh Tileset", command=self.filemenurefresh)

        menubar.add_cascade(label="File", menu=filemenu)

        master.config(menu=menubar)

        '''
        Initialize Tile Paint Canvas
        '''

        self.master.rowconfigure(4,weight=1)
        self.master.columnconfigure(5,weight=1)
        self.TilePaintCanvas=self.CanvasFunc(width=self.TM.tilesize**2,height=self.TM.tilesize**2,background="grey")
        self.TilePaintCanvas.grid(row=4,column=5, columnspan=5, rowspan=5,sticky = tk.N+tk.S+tk.E+tk.W,padx=2,pady=2)
        self.TilePaintCanvas.configure(scrollregion = self.TilePaintCanvas.bbox("all"))
        self.TilePaintCanvas.configure(yscrollincrement=self.TM.tilesize)
        self.TilePaintCanvas.configure(xscrollincrement=self.TM.tilesize)

        #initialize grid pattern
        self.gridlines={}
        self.prevXminmax=[0,self.TM.tilesize**2]
        self.prevYminmax=[0,self.TM.tilesize**2]
        (x1,y1,x2,y2)=self.CanvasCoords()
        self.CreateGrid(0,0,self.TM.tilesize**2,self.TM.tilesize**2)

        #self.CanvasTileManager(initialize=True)


        '''
        Initialize Label for Current view coords
        changes on scroll
        '''

        self.labelcurview=tk.Label(master,text=f"({x1},{y1})-({x2},{y2})")
        self.labelcurview.grid(row=0,column=5,columnspan=5,sticky = 'W', pady = 2)


        """
        ---------------------------------------------------------------------
                                    CONTROLS SECTION
        ---------------------------------------------------------------------
        """

        '''
        Control Bindings
        '''
        self.BindCursorControl(self.TilePaletteCanvas)
        self.BindCursorControl(self.TilePaintCanvas,canvasid=True)

        self.BindTilePaletteControl()

        self.BindTilePaintControl()

        self.BindTileDeleteControl()

        self.BindTilePaintScrollControl()

        self.BindTilePaintResize()

        self.BindFocusReturn(obj=self.TilePaintCanvas)

    """
    ---------------------------------------------------------------------
                               SPECIAL FUNCTIONS SECTION
    ---------------------------------------------------------------------
    """

    def CursorRectangle(self,coords):
        '''
        generates bbox for rectangle

        coords currently contains [(startx,starty),(endx,endy)]
        use from matrix indexing

        '''
        startc=coords[0]
        endc=coords[1]

        [(xi,yi),(xn,yn)]=[(min(startc[0],endc[0]),min(startc[1],endc[1])),(max(startc[0],endc[0]),max(startc[1],endc[1]))]

        deltax=abs(xi-xn)+1
        deltay=abs(yi-yn)+1
        #xn+=deltax
        #yn+=deltay

        bboxraw=(xi,yi,xn+1,yn+1)
        bboxpix=[i*self.TM.tilesize for i in bboxraw]


        return [bboxraw,bboxpix]

    def TileSetPaletteBuilder(self):
        '''
        Canvas Initializer
        assembles tiles into canvas

        multiselect from master matrix subc=[0,15]
        '''
        obj=self.TilePaletteCanvas

        imgtag="tileset"
        tileset=self.TM.MultitileTool([0,15],[0,15])
        im_pil=self.TM.imagestitchTool(tileset)
        imgTk=PIL_ImageTk.PhotoImage(image=im_pil)

        self.TPallStorage[1]=imgTk
        self.TPallStorage[2]=im_pil
        tilecheck=len(obj.find_withtag(imgtag))

        if tilecheck==0:
            canvasimgobj=obj.create_image((0,0),image=imgTk,anchor=tk.NW,tags=imgtag)

        else:
            obj.itemconfig(imgtag,image=imgTk)


    def TilePaintCanvasChanger(self,imagematrix):
        '''
        Used to clear and load image to canvas
        '''
        obj=self.TilePaintCanvas

        obj.delete("tiles")

        self.gridlines={}

        (x1,y1,x2,y2)=self.CanvasCoords()

        self.CreateGrid(x1,y1,x2,y2)

        self.TPainStorage={}

        self.TM.canvasmatrix=np.empty([self.TM.tilesize,self.TM.tilesize],dtype=object)
        self.TM.memory=[0,0]

        self.TM.canvasmatrix,self.TM.memory=self.TM.tilepaintTool(canvasmatrix=self.TM.canvasmatrix,x=0,y=0,tilematrix=imagematrix,memory=self.TM.memory)

        #create base layer image: master image

        self.CanvasTileManager(initialize=True)

        obj.tag_lower("grid")



    """
    ---------------------------------------------------------------------
                               WIDGET FUNCTIONS SECTION
    ---------------------------------------------------------------------
    """



    def SpinboxFunc(self,minval,maxval,outputvar,width,wrap=True):
        '''
        returns a spinbox to be assigned to a variable

        Notes:
        tk.IntVar() needs master=tk.Tk() to work
        .get() returns contents
        .set() changes contents
        '''
        return tk.Spinbox(self.master,from_=minval, to=maxval,textvariable=outputvar,wrap=wrap,width=width)

    def CanvasFunc(self,width,height,background="grey"):
        '''
        returns canvas to be assigned to a variable

        '''
        return tk.Canvas(self.master, width=width, height=height,background=background)


    def RadiobutFunc(self,inputs,output):
        radiobuttons=[]

        for key,value in inputs:
            b=tk.Radiobutton(self.master,text=key,variable=output,value=value)
            radiobuttons.append(b)

        return radiobuttons


    """
    ---------------------------------------------------------------------
                              CONTROL/EVENT FUNCTIONS SECTION
    ---------------------------------------------------------------------
    """

    #===============
    #EVENT FUNCTIONS
    #===============

    def on_areaID_change(self,a,b,c):
        '''
        changes tile set palette and sets area ID
        '''
        try:
            self.TM.areaid=int(self.areaidspinboxOut.get())
        except:
            pass
        # use Tile Set Palette Changer function
        self.TileSetPaletteBuilder()

    def on_typeID_change(self,a,b,c):
        '''
        changes tile set palette and sets type ID
        '''
        self.TM.typeid=int(self.typeidradiobuttonout.get())

        # use Tile Set Palette Changer function
        self.TileSetPaletteBuilder()

    def on_currenttile_change(self,a=0,b=0,c=0):
        '''
        changes current selected tile
        '''

        self.labelcurseltile.config(text=f"| T:{self.TM.typeid}-A:{self.TM.areaid}-Tile:({self.TM.subx},{self.TM.suby})")


    def on_scroll_key(self,event,key):
        obj=self.TilePaintCanvas
        keyscroll={"w":-1,"s":1,"a":-1,"d":1}
        scroll=keyscroll[key]
        if key=="w" or key=="s":
            obj.yview_scroll(scroll, "units")
        elif key=="a" or key=="d":
            obj.xview_scroll(scroll, "units")

        (x1,y1,x2,y2)=self.CanvasCoords()

        self.CreateGrid(x1,y1,x2,y2)

        self.labelcurview.config(text=f"({x1},{y1})-({x2},{y2})")

        obj.tag_lower("grid")


    def on_window_resize(self,event):
        '''
        makes sure grid updates for canvas
        '''

        (x1,y1,x2,y2)=self.CanvasCoords()

        self.CreateGrid(x1,y1,x2,y2)

        self.labelcurview.config(text=f"({x1},{y1})-({x2},{y2})")

        obj=self.TilePaintCanvas
        obj.tag_lower("grid")


    def on_enter_key(self,event,obj):
        obj.focus_set()



    #===============
    #MENU FUNCTIONS
    #===============

    def filemenuopen(self):
        '''
        imports image and loads onto canvas matrix
        '''
        filename= tk_filedialog.askopenfilename(filetypes=[("Image files","*.png")])
        try:
            imagematrix=self.TM.importimageTool(filename)
            self.TilePaintCanvasChanger(imagematrix)
            self.TM.canvasmatrix=imagematrix
        except:
            pass

    def filemenusave(self):
        '''
        exports map image from canvas matrix
        '''
        filename= tk_filedialog.asksaveasfilename(filetypes=[("Image files","*.png")])
        if ".png" not in filename:
            filename+=".png"
        try:
            self.TM.exportimageTool(self.TM.canvasmatrix,filename)
        except:
            pass

    def filemenurefresh(self):
        '''
        refreshes mastertileset with new tiles
        '''
        self.TM.MasterTilesetRefresh()

        self.TileSetPaletteBuilder()



    #===============
    #OTHER FUNCTIONS
    #===============


    def CursorLocation(self,event):
        '''
        returns coordinates of cursor in widget in multiples of self.TM.tilesize pixels
        '''
        x=np.fix((event.x-2)/self.TM.tilesize)
        y=np.fix((event.y-2)/self.TM.tilesize)
        return (x,y)

    def CanvasCoords(self):
        '''
        get canvas current visible area
        '''

        obj=self.TilePaintCanvas
        x1=int(obj.canvasx(0))+2
        y1=int(obj.canvasy(0))+2

        x2=int(obj.canvasx(obj.winfo_width()))+2
        y2=int(obj.canvasy(obj.winfo_height()))+2


        return (x1,y1,x2,y2)

    def CreateGrid(self,x1,y1,x2,y2):
        '''
        creates 2 grids: self.TM.tilesize**2xself.TM.tilesize**2 and self.TM.tilesizexself.TM.tilesize
        '''
        obj=self.TilePaintCanvas

        largeXrange=range(x1,x2,self.TM.tilesize**2)
        smallXrange=range(x1,x2,self.TM.tilesize)
        largeYrange=range(y1,y2,self.TM.tilesize**2)
        smallYrange=range(y1,y2,self.TM.tilesize)

        #create vertical lines:
        for i in smallXrange:
            #i=int(i)
            linetag=f"{i},small V"

            if linetag in self.gridlines:
                line=self.gridlines[linetag]
                if y1 not in self.prevYminmax or y2 not in self.prevXminmax:
                    obj.coords(line,(i,y1,i,y2))
                    self.prevYminmax=[y1,y2]
            else:
                line=obj.create_line((i,y1,i,y2),dash=(4),fill="black",tag="grid")
                self.gridlines[linetag]=line

        #create horizontal lines:
        for i in smallYrange:
            #i=int(i)
            linetag=f"{i},small H"

            if linetag in self.gridlines:
                line=self.gridlines[linetag]
                obj.coords(line,(x1,i,x2,i))
                self.prevXminmax=[x1,x2]
            else:
                line=obj.create_line((x1,i,x2,i),dash=(4),fill="black",tag="grid")
                self.gridlines[linetag]=line



    def CanvasTileManager(self,initialize=False,listcheck=10):
        '''
        updates master image and removes individual tile objects
        '''

        #New
        #TODO: create master image updater that iterates through TPainStorage
        #TPainStorage has deleted tiles in the form of img_pil==None.

        obj=self.TilePaintCanvas
        tilelist=list(self.TPainStorage.values())
        mastercheck=len(obj.find_withtag("master"))

        if initialize:
            masterimg=self.TM.imagestitchTool(self.TM.canvasmatrix)
            imgTk=PIL_ImageTk.PhotoImage(image=masterimg)
            xc=0
            yc=0
            self.TM.memory=[xc,yc]
            self.TM.masterimgref=[(xc,yc),imgTk,masterimg]

            if mastercheck==0:
                tilepaintimg=obj.create_image((xc*self.TM.tilesize,yc*self.TM.tilesize),image=imgTk,anchor=tk.NW,tags="master")
            else:
                obj.coords("master",(xc*self.TM.tilesize,yc*self.TM.tilesize))
                obj.itemconfig("master",image=imgTk)

            self.TPainStorage={}
            obj.delete("tiles")
            self.TM.masterimgref=[(xc,yc),imgTk,masterimg]

        if len(tilelist)>=listcheck:
            self.TM.masterimgupdate(tilelist)
            imgTk=self.TM.masterimgref[1]

            xc=self.TM.memory[1]
            yc=self.TM.memory[0]

            if mastercheck==0:
                tilepaintimg=obj.create_image((xc*self.TM.tilesize,yc*self.TM.tilesize),image=imgTk,anchor=tk.NW,tags="master")
            else:
                obj.coords("master",(xc*self.TM.tilesize,yc*self.TM.tilesize))
                obj.itemconfig("master",image=imgTk)

            self.TPainStorage={}
            obj.delete("tiles")










    #=================
    #CONTROL FUNCTIONS
    #=================

    def BindCursorControl(self,widobj,canvasid=False):
        controllist=["<Motion>","<Enter>","<Leave>"]
        for binding in controllist:
            widobj.bind(binding,lambda event, obj=widobj: self.CursorControl(event,obj,canvasid))

    def CursorControl(self,event,obj,canvasid):
        '''
        Consolidates Mouse Control Functions:
            - Motion
            - Enter
            - Leave
        Uses event.type and obj to determine Cursor movement/behavior
        Use only for canvas objects
        '''

        x=np.floor((obj.canvasx(event.x))/self.TM.tilesize)
        y=np.floor((obj.canvasy(event.y))/self.TM.tilesize)
        #[x,y]=self.CursorLocation(event)

        coords=[(x,y),(x,y)] #single location coords
        bbox0=self.CursorRectangle(coords)[1]

        currenttiles=self.TM.MultitileTool()
        (ym,xm)=np.shape(currenttiles)

        coords1=[(x,y),(x+xm-1,y+ym-1)] #multitile location coords
        bbox1=self.CursorRectangle(coords1)[1]
        pixcoord=bbox1[0:2]

        if str(event.type)=="Enter":
            '''
            Create cursor in current widget
            '''

            color0="white"
            Cursor0=obj.create_rectangle(bbox0,outline=color0,tags="Cursor0")

            #Tile placement preview
            if canvasid:
                tp_pil=self.TM.createtilepreview()
                tp_pil.putalpha(100)
                self.tpTk=PIL_ImageTk.PhotoImage(image=tp_pil)
                imgtag="preview"
                tilepreview=obj.create_image(pixcoord,image=self.tpTk,anchor=tk.NW,tags=imgtag)
                obj.coords("Cursor0",bbox1)


        if str(event.type)=="Leave":
            '''
            Delete cursor in current widget
            '''
            try:
                obj.delete("Cursor0")
                obj.delete("preview")
            except:
                pass

        if str(event.type)=="Motion":
            '''
            Move cursor
            '''

            obj.tag_raise("Cursor0")

            if canvasid:
                obj.coords("Cursor0",bbox1)
                obj.coords("preview",pixcoord)
                obj.tag_raise("preview")

            else:
                obj.coords("Cursor0",bbox0)





    def BindTilePaletteControl(self):
        self.TilePaletteCanvas.bind("<Button-1>",lambda event, controltype="click": self.TileSelectionControl(event,controltype))
        self.TilePaletteCanvas.bind("<B1-Motion>",lambda event, controltype="drag": self.TileSelectionControl(event,controltype))
        self.TilePaletteCanvas.bind("<ButtonRelease-1>",lambda event, controltype="release": self.TileSelectionControl(event,controltype))


    def TileSelectionControl(self,event,controltype):
        '''
        Click and drag in TilePaletteCanvas

        TODO: Determine what needs to change here
        '''
        obj=self.TilePaletteCanvas
        self.TilePaintCanvas.focus_set()
        if controltype=="click":
            '''
            Change selected tile
            '''

            x=np.floor((obj.canvasx(event.x))/self.TM.tilesize)
            y=np.floor((obj.canvasy(event.y))/self.TM.tilesize)
            #(x,y)=self.CursorLocation(event)

            coords=[(x,y),(x,y)] #single location coords
            bbox1=self.CursorRectangle(coords)[1]

            obj.coords("Cursor1",bbox1)
            obj.tag_raise("Cursor1")

            (subymin,subxmin,subymax,subxmax)=self.CursorRectangle(coords)[0]

            self.TM.subx=[subxmin,subxmax-1]
            self.TM.suby=[subymin,subymax-1]

        if controltype=="drag":

            x=np.floor((obj.canvasx(event.x))/self.TM.tilesize)
            y=np.floor((obj.canvasy(event.y))/self.TM.tilesize)
            #(x,y)=self.CursorLocation(event)

            self.CursorCoordList.append((x,y))

            #real time selection update
            vi=self.CursorCoordList[0]
            vn=self.CursorCoordList[-1]

            coords=(vi,vn)
            bboxT=self.CursorRectangle(coords)[1]

            obj.coords("Cursor0",bboxT)
            obj.coords("Cursor1",bboxT)

        if controltype=="release":

            if self.CursorCoordList != []:
                vi=self.CursorCoordList[0]
                vn=self.CursorCoordList[-1]
                coords=(vi,vn)
                bboxT=self.CursorRectangle(coords)[1]
                (subymin,subxmin,subymax,subxmax)=self.CursorRectangle(coords)[0]

                self.TM.subx=[subxmin,subxmax-1]
                self.TM.suby=[subymin,subymax-1]

                self.CursorCoordList=[]
                obj.coords("Cursor0",bboxT)

        #update label
        self.on_currenttile_change()

    def BindTilePaintControl(self):
        self.TilePaintCanvas.bind("<Button-1>",lambda event, controltype="click": self.TilePaintControl(event,controltype))
        self.TilePaintCanvas.bind("<B1-Motion>",lambda event, controltype="drag": self.TilePaintControl(event,controltype))
        self.TilePaintCanvas.bind("<ButtonRelease-1>",lambda event, controltype="release": self.TilePaintControl(event,controltype))

    def TilePaintControl(self,event,controltype):
        '''
        placing tiles on canvas


        TODO: Fix to use new matrix system
        - align matrix to canvas
        - grow matrix only if tiles are placed in new coords
            - confirm how coords behave when scrolling
                - Coords stay in original area
        '''

        obj=self.TilePaintCanvas

        tilelist=obj.find_withtag("tiles")

        x=np.floor((obj.canvasx(event.x))/self.TM.tilesize)
        y=np.floor((obj.canvasy(event.y))/self.TM.tilesize)

        #(x,y)=self.CursorLocation(event)

        obj.focus_set()

        currenttiles=self.TM.MultitileTool()

        if controltype=="click":

            listcheck=len(self.TPainStorage.keys())+1

            #place single tile/group
            obj.tag_lower("Cursor0")

            #Insert to canvas matrix
            self.TM.canvasmatrix,self.TM.memory=self.TM.tilepaintTool(canvasmatrix=self.TM.canvasmatrix,x=y,y=x,tilematrix=currenttiles,memory=self.TM.memory)

            #-----------------------
            #Display tiles on canvas
            for m,row in enumerate(currenttiles):
                for n,tile in enumerate(row):
                    xt=x+n
                    yt=y+m
                    imgtag=f"({xt},{yt})"

                    im_pil = PIL_Image.fromarray(tile)
                    imgTk=PIL_ImageTk.PhotoImage(image=im_pil)

                    self.TPainStorage[imgtag]=[(xt,yt),imgTk,im_pil]

                    tilecheck=len(obj.find_withtag(imgtag))

                    if tilecheck==0:
                        tilepaintimg=obj.create_image((xt*self.TM.tilesize,yt*self.TM.tilesize),image=imgTk,anchor=tk.NW,tags=("tiles",imgtag))

                    else:
                        obj.itemconfig(imgtag,image=imgTk)

        if controltype=="drag":

            obj.tag_lower("Cursor0")
            self.CursorCoordList.append((x,y))
            (xi,yi)=self.CursorCoordList[0]
            (xn,yn)=self.CursorCoordList[-1]


            xmax=np.shape(currenttiles)[1]-1
            ymax=np.shape(currenttiles)[0]-1


            xlim1=xi-xmax
            xlim2=xi+xmax
            ylim1=yi-ymax
            ylim2=yi+ymax

            #tile placement preview
            (ym,xm)=np.shape(currenttiles)

            coords1=[(x,y),(x+xm-1,y+ym-1)] #multitile location coords
            bbox1=self.CursorRectangle(coords1)[1]

            obj.coords("Cursor2",bbox1)
            obj.tag_raise("Cursor2")


            if (xn>=xlim1 and xn<=xlim2) and (yn>=ylim1 and yn<=ylim2):
                pass
            else:
                self.CursorCoordList[0]=(xn,yn)

                #Insert to canvas matrix
                self.TM.canvasmatrix,self.TM.memory=self.TM.tilepaintTool(canvasmatrix=self.TM.canvasmatrix,x=y,y=x,tilematrix=currenttiles,memory=self.TM.memory)

                #-----------------------
                #Display tiles on canvas
                for m,row in enumerate(currenttiles):
                    for n,tile in enumerate(row):
                        xt=x+n
                        yt=y+m
                        imgtag=f"({xt},{yt})"

                        im_pil = PIL_Image.fromarray(tile)
                        imgTk=PIL_ImageTk.PhotoImage(image=im_pil)

                        self.TPainStorage[imgtag]=[(xt,yt),imgTk,im_pil]

                        tilecheck=len(obj.find_withtag(imgtag))


                        if tilecheck==0:
                            tilepaintimg=obj.create_image((xt*self.TM.tilesize,yt*self.TM.tilesize),image=imgTk,anchor=tk.NW,tags=("tiles",imgtag))

                        else:
                            obj.itemconfig(imgtag,image=imgTk)

            #continuous placement
            listcheck=len(self.TPainStorage.keys())+1

        if controltype=="release":
            #reset continuous placement parameters
            self.CursorCoordList=[]
            listcheck=1

        self.CanvasTileManager(listcheck=listcheck)

    def BindTileDeleteControl(self):
        self.TilePaintCanvas.bind("<Button-3>",lambda event, controltype="click": self.TileDeleteControl(event,controltype))
        self.TilePaintCanvas.bind("<B3-Motion>",lambda event, controltype="drag": self.TileDeleteControl(event,controltype))
        self.TilePaintCanvas.bind("<ButtonRelease-3>",lambda event, controltype="release": self.TileDeleteControl(event,controltype))


    def TileDeleteControl(self,event,controltype):
        '''
        clears selected tiles
        '''
        obj=self.TilePaintCanvas
        x=np.floor((obj.canvasx(event.x))/self.TM.tilesize)
        y=np.floor((obj.canvasy(event.y))/self.TM.tilesize)
        #(x,y)=self.CursorLocation(event)
        value=(y,x)

        imgtag=f'({x},{y})'

        blankimg=PIL_Image.new('RGBA',(self.TM.tilesize,self.TM.tilesize),(127, 127, 127, 255)) #matches current grey of background
        imgTk=PIL_ImageTk.PhotoImage(image=blankimg)

        self.TPainStorage[imgtag]=[(x,y),imgTk,None]

        tilecheck=len(obj.find_withtag(imgtag))

        if tilecheck==0:
            tilepaintimg=obj.create_image((x*self.TM.tilesize,y*self.TM.tilesize),image=imgTk,anchor=tk.NW,tags=("tiles",imgtag))
        else:
            obj.itemconfig(imgtag,image=imgTk)

        blankmatrix=np.empty((1,1),dtype=object)
        blankmatrix[0,0]=None
        self.TM.canvasmatrix,self.TM.memory=self.TM.tilepaintTool(canvasmatrix=self.TM.canvasmatrix,x=y,y=x,tilematrix=blankmatrix,memory=self.TM.memory)

        if controltype=="click":
            listcheck=1

        if controltype=="drag":
            listcheck=len(self.TPainStorage.keys())+1

        if controltype=="release":
            listcheck=1

        self.CanvasTileManager(listcheck=listcheck)



    def BindTilePaintScrollControl(self):
        self.TilePaintCanvas.bind("a", lambda event: self.on_scroll_key(event,"a"))
        self.TilePaintCanvas.bind("d", lambda event: self.on_scroll_key(event,"d"))
        self.TilePaintCanvas.bind("w", lambda event: self.on_scroll_key(event,"w"))
        self.TilePaintCanvas.bind("s", lambda event: self.on_scroll_key(event,"s"))
        self.TilePaintCanvas.focus_set()


    def BindTilePaintResize(self):
        self.TilePaintCanvas.bind("<Configure>",lambda event: self.on_window_resize(event))


    def BindFocusReturn(self,obj):
        self.master.bind("<Return>", lambda event: self.on_enter_key(event,obj))
