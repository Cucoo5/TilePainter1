import cv2
import numpy as np
import os
from PIL import Image as PIL_Image, ImageTk as PIL_ImageTk

from FileFolderPaths import FileFolderPaths
from MasterTilesetManager import MasterTilesetManager

class Tile_Manager():
    '''
    manages loading from tileset file and stores Master Matrix
    '''

    def __init__(self):

        #get path to master tileset
        self.FFP=FileFolderPaths()
        self.MTM=MasterTilesetManager()

        self.MasterMatrix=self.MTM.createMaster()

        #Initialize current tile system
        self.typeid=0
        self.areaid=0
        self.subx=[0,0]
        self.suby=[0,0]

        #Matrix Variables
        self.canvasmatrix=np.empty([16,16],dtype=object)
        self.memory=[0,0]

        #Master Image
        masterimg=self.imagestitchTool(self.canvasmatrix)
        (h, w,_) = np.shape(masterimg)
        imgTk=PIL_ImageTk.PhotoImage(image=masterimg)
        self.masterimgref=[(0,0),imgTk,masterimg]


    def gettile(self):
        '''
        given main and sub coords, return tile img
        '''

        #convert main and sub coords to index
        x=self.subx+self.typeid*16
        y=self.suby+self.areaid*16

        img=self.MasterMatrix[x,y]

        return img

    def changecoords(self,typeid,areaid,subx,suby):
        '''
        compact way to change coordinates
        '''
        self.typeid=typeid
        self.areaid=areaid
        self.subx=subx
        self.suby=suby


    def MultitileTool(self,subxrange=None,subyrange=None):
        '''
        processes input for either single or multiselect
        returns a matrix of images accordingly

        subxrange=[xmin,xmax]
        subyrange=[ymin,ymax]
        '''

        if subxrange==None:
            subxrange=self.subx
        if subyrange==None:
            subyrange=self.suby

        # determine selection size (+1 due to exclusion)
        deltax=int(subxrange[1]-subxrange[0]+1)
        deltay=int(subyrange[1]-subyrange[0]+1)

        selectmatrix=np.empty(((deltax),(deltay)),dtype=object)
        for x,row in enumerate(selectmatrix):
            for y,val in enumerate(row):
                m=int(x+subxrange[0])+self.typeid*16
                n=int(y+subyrange[0])+self.areaid*16
                selectmatrix[x,y]=self.MasterMatrix[m,n]

        return selectmatrix

    def tilepaintTool(self,canvasmatrix,x,y,tilematrix=None,memory=[0,0]):
        '''
        pastes tilematrix onto canvasmatrix at coordinates
        dynamic matrix scaling to fit

        memory serves to store how much the matrix grows in the
        negative direction

        memory = [xmem,ymem]
        '''

        A=canvasmatrix

        if tilematrix is None:
            B=self.MultitileTool()
        else:
            B=tilematrix

        Bx=np.shape(B)[0]
        By=np.shape(B)[1]

        Ax=np.shape(A)[0]
        Ay=np.shape(A)[1]

        xmem=int(memory[0])
        ymem=int(memory[1])

        x=int(x-xmem)
        y=int(y-ymem)


        if x<0:
            Mx=abs(x)
        else:
            Mx=x+Bx-Ax

        if y<0:
            My=abs(y)
        else:
            My=y+By-Ay

        if x<0 or x+Bx>Ax:
            Ax+=Mx
            M=np.empty([Mx,Ay],dtype=object)

            if x<0:
                x=0
                xmem-=Mx
                A=np.vstack((M,A))
            else:
                A=np.vstack((A,M))

        if y<0 or y+By>Ay:
            Ay+=My
            M=np.empty([Ax,My],dtype=object)

            if y<0:
                y=0
                ymem-=My
                A=np.hstack((M,A))
            else:
                A=np.hstack((A,M))

        A[x:x+Bx,y:y+By]=B

        memory=[xmem,ymem]

        return A,memory

    def MatrixShrinkTool(self,matrix):
        '''
        iterates through matrix
        removes excess rows and columns
        returns matrix
        '''
        #find row and col min and max that contain tiles

        xmin=np.shape(matrix)[0]
        ymin=np.shape(matrix)[1]

        xmax=0
        ymax=0

        #find upperleft corner and lower right corner
        for x,row in enumerate(matrix):
            for y,val in enumerate(row):
                if val is not None:
                    if x<xmin:
                        xmin=x
                    if y<ymin:
                        ymin=y
                    if x+1>xmax:
                        xmax=x+1
                    if y+1>ymax:
                        ymax=y+1

        return matrix[xmin:xmax,ymin:ymax]



    def exportimageTool(self,matrix,filename):
        '''
        pastes all tiles from matrix to new image
        '''

        matrixN=self.MatrixShrinkTool(matrix)

        dst=self.imagestitchTool(matrixN)

        #filename=input()
        #savepath=os.path.join(self.FFP.savepath,f"{filename}.png")
        savepath=filename
        dst.save(savepath)

    def imagestitchTool(self,matrix):
        '''
        used to take tiles from matrix and return as single image.
        '''
        xmax=int((np.shape(matrix)[0])*16)
        ymax=int((np.shape(matrix)[1])*16)

        # stitch tiles together and export as png image
        dst=PIL_Image.new('RGBA',(ymax,xmax),(0, 0, 0, 0))
        blankimg=PIL_Image.new('RGBA',(16,16),(0, 0, 0, 0))

        for x,row in enumerate(matrix):
            for y,val in enumerate(row):
                if val is None:
                    im_pil=blankimg
                else:
                    im_pil = PIL_Image.fromarray(val)

                xc=x*16
                yc=y*16

                dst.paste(im_pil,(yc,xc))

        return dst



    def importimageTool(self,filename):
        '''
        creates image matrix from file
        '''

        #get path to image
        #imagepath=os.path.join(self.FFP.savepath,f"{filename}.png")
        imagepath=filename

        #open image in normal colors
        img=cv2.cvtColor(cv2.imread(imagepath,cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGBA)

        #create image matrix (paste into larger matrix if smaller than 16x16)
        row=int(img.shape[0]/16)
        col=int(img.shape[1]/16)

        rown=row
        coln=col

        ImageMatrix=np.empty(((row),(col)),dtype=object)

        for x,row in enumerate(ImageMatrix):
            for y,val in enumerate(row):
                m=x*16
                n=y*16
                ImageMatrix[x,y]=img[m:m+16, n:n+16,:]

        if rown<16 or coln<16:
            if rown<16:
                row=rown
                rown=16
            if coln<16:
                col=coln
                coln=16

            ImageMatrixT=np.empty(((rown),(coln)),dtype=object)
            ImageMatrixT[0:row,0:col]=ImageMatrix

            #weird variable nonsense flip for sanity
            ImageMatrix=ImageMatrixT

        return ImageMatrix

    def MasterTilesetRefresh(self):
        '''
        refreshes MasterTileset by rebuilding it
        '''

        self.MasterMatrix=self.MTM.createMaster()
        #self.exportimageTool(self.MasterMatrix,self.MTM.mastertilesetpath)

        print("Complete")

    def masterimgupdate(self,TileList):
        '''
        iterates through list of tiles paired with coordinates and pastes onto
        masterimage stored in masterimgref=[(x,y),imgTk,masterimg]
        '''
        mstrimg=self.masterimgref[2]
        (xi,yi)=self.masterimgref[0] #previous coords

        (yc,xc)=self.memory #coord adjustment

        xmax=int((np.shape(self.canvasmatrix)[0])*16)
        ymax=int((np.shape(self.canvasmatrix)[1])*16)

        newmaster=PIL_Image.new('RGBA',(ymax,xmax),(0, 0, 0, 0))

        (xp,yp)=((xi-xc)*16,(yi-yc)*16) # prev master to new paste coordinates

        newmaster.paste(mstrimg,(xp,yp))

        blankimg=PIL_Image.new('RGBA',(16,16),(0, 0, 0, 0))

        for tile in TileList:

            (xf,yf)=tile[0]

            (x,y)=(int((xf-xc)*16),int((yf-yc)*16))

            im_pil=tile[2]
            if im_pil is not None:
                newmaster.paste(im_pil,(x,y))
            else:
                newmaster.paste(blankimg,(x,y))


        masterimg=newmaster
        imgTk=PIL_ImageTk.PhotoImage(image=masterimg)
        self.masterimgref=[(xc,yc),imgTk,masterimg]

        
