import os

class FileFolderPaths():
    '''
    contains all paths and allows simplified calls to specific files
    '''
    def __init__(self):
        #Root of program directory
        #TODO: need to check if running from outside
        #      code directory will change this
        self.rootpath=os.path.split(os.getcwd())[0]

        #Code Folder
        self.codepath=os.path.join(self.rootpath,"Code")

        #Asset Folder and sub directories
        self.assetpath=os.path.join(self.rootpath,"Assets")
        self.tilesetpath=os.path.join(self.assetpath,"Tilesets")
        self.rawtilepath=os.path.join(self.assetpath,"Raw Tiles")
        self.UIpath=os.path.join(self.assetpath,"UI")
        self.savepath=os.path.join(self.rootpath,"Save")

    def getTileSet(self,typeid,areaid,test=False,testnum=1):
        if test:
            return os.path.join(self.tilesetpath,f"Test{testnum}",f"{areaid}.bmp")
        else:
            return os.path.join(self.tilesetpath,f"{typeid}",f"area{areaid}.bmp")
