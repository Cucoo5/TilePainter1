import cv2
import numpy as np
import os
from PIL import Image as PIL_Image, ImageTk as PIL_ImageTk

from FileFolderPaths import FileFolderPaths

class MasterTilesetManager():
    '''
    manages the update and creation of the MasterTileset
    '''

    def __init__(self):
        self.FFP=FileFolderPaths()

        self.mastertilesetpath=os.path.join(self.FFP.tilesetpath,"MasterTileset.png")

        self.tilesize=16


    def createMaster(self):
        '''
        Generates master matrix from all tilesets
        '''

        # Generate Master Tileset from tilesets
        path=[os.path.join(self.FFP.tilesetpath,x) for x in ["OoA","OoS","Custom"]]
        #target0=[x for x in range(0,103)]
        #target1=[x for x in range(0,215)]

        tilesetmatrixlst={}

        for t,folder in enumerate(path):
            matrixlst=[]
            for i,filen in enumerate(os.listdir(folder)):

                filename=os.path.join(folder,f"area{i}.png")
                img=cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)

                row=int(img.shape[0]/self.tilesize)
                col=int(img.shape[1]/self.tilesize)


                MainMatrix=np.empty(((row),(col)),dtype=object)
                for x,row in enumerate(MainMatrix):
                    for y,val in enumerate(row):
                        m=x*self.tilesize
                        n=y*self.tilesize
                        MainMatrix[x,y]=img[m:m+self.tilesize, n:n+self.tilesize,:]

                matrixlst.append(MainMatrix)

            tilesetmatrixlst[t]=matrixlst


        xmax=max([len(x) for x in tilesetmatrixlst.values()])
        ymax=max(tilesetmatrixlst.keys())

        row=(ymax+1)*self.tilesize
        col=(xmax)*self.tilesize

        MasterMatrix=np.empty(((row),(col)),dtype=object)

        for typeid,value in tilesetmatrixlst.items():
            for areaid,matrix in enumerate(value):
                for subx,row in enumerate(matrix):
                    for suby,val in enumerate(row):

                        '''
                        typeid=np.floor(x/self.tilesize)
                        areaid=np.floor(y/self.tilesize)
                        subx=x-typeid*self.tilesize
                        suby=y-areaid*self.tilesize
                        m=int(self.tilesize*subx+typeid*256)
                        n=int(self.tilesize*suby+areaid*256)
                        '''

                        x=subx+typeid*self.tilesize
                        y=suby+areaid*self.tilesize

                        #print(x,y)

                        MasterMatrix[x,y]=val

        return MasterMatrix
