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

                row=int(img.shape[0]/16)
                col=int(img.shape[1]/16)


                MainMatrix=np.empty(((row),(col)),dtype=object)
                for x,row in enumerate(MainMatrix):
                    for y,val in enumerate(row):
                        m=x*16
                        n=y*16
                        MainMatrix[x,y]=img[m:m+16, n:n+16,:]

                matrixlst.append(MainMatrix)

            tilesetmatrixlst[t]=matrixlst


        xmax=max([len(x) for x in tilesetmatrixlst.values()])
        ymax=max(tilesetmatrixlst.keys())

        row=(ymax+1)*16
        col=(xmax)*16

        MasterMatrix=np.empty(((row),(col)),dtype=object)

        for typeid,value in tilesetmatrixlst.items():
            for areaid,matrix in enumerate(value):
                for subx,row in enumerate(matrix):
                    for suby,val in enumerate(row):

                        '''
                        typeid=np.floor(x/16)
                        areaid=np.floor(y/16)
                        subx=x-typeid*16
                        suby=y-areaid*16
                        m=int(16*subx+typeid*256)
                        n=int(16*suby+areaid*256)
                        '''

                        x=subx+typeid*16
                        y=suby+areaid*16

                        #print(x,y)

                        MasterMatrix[x,y]=val

        return MasterMatrix
