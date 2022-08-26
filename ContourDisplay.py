####################################################
# import matplotlib.pyplot as plt
# from RadialProfileData import RadialProfileData

# def main():
#     fig, ax = plt.subplots()

#     def inputData(data, fmtString):
#         ax.errorbar(data.xRadialDistance, data.yCounts, yerr=data.yErr, fmt=fmtString, linewidth=1, label=data.name)


#     data1 = RadialProfileData("g309_profile.dat", "G309")
#     data2 = RadialProfileData("radialprofilePeak\\blur_0.25.dat", "PSF: Blur 0.25", data1.yCounts[0])
#     data3 = RadialProfileData("radialprofilePeak\\blur_0.30.dat", "PSF: Blur 0.30", data1.yCounts[0])
#     data4 = RadialProfileData("radialprofilePeak\\blur_0.35.dat", "PSF: Blur 0.35", data1.yCounts[0])

#     inputData(data1, "r")
#     inputData(data2, "g--")
#     inputData(data3, "m-.")
#     inputData(data4, "c:")

#     ax.axhline(y=0.0242066)
#     ax.set_xlim(right=5)

#     ax.set_title("Radial Profile Comparison With PSF")
#     ax.set_xlabel("Radial distance (arcsec)")
#     ax.set_ylabel("Surface Brightness (cnts/arcsec**2)")
#     ax.set_yscale("log")
#     ax.minorticks_on()
#     ax.legend()

#     plt.show()

# if __name__=="__main__":
#     main()
#############################


                
from typing import Dict
import PySimpleGUI as sg
from Display import Display
import numpy as np
import matplotlib.pyplot as plt
from GraphDisplayer import GraphDisplayer
from pycrates import read_file
from helpers import sysCMD, unlearn, pathAdd
import os
from pycrates import read_file


class ContourDisplay(Display):
    
    events: Dict = {}
    
    def __init__(self, dir, fits_dir, init_source=None, init_bkg=None) -> None:
        
        self.dir = dir
        self.fits_dir = fits_dir
        
        
        self.regionDir = self.dir
        self.contourDir = os.path.join(self.dir, "RADIAL_PROFILES")
        
        self.configOptionMenus()
        
        
        self.xdata = [1, 2, 3]
        self.ydata = [1, 2, 3]
        
        self.title = "Radial Profile Comparison With PSF"
        self.xlabel = "CEL_RMID (arc sec)"
        self.ylabel = "SUR_BRI (photons/cm**2/pixel**2/s)"
        
    def config_events(self):
        self.events = {'-EVENT-MAKE-CONTOUR-DATA-': self.extract_from_region_event, 
                       '-REFRESH-EVENT-': self.refresh_files, 
                       '-EVENT-MAKE-CONTOUR-PLOT-': self.setGraphData,
                       '-Y-LOG-EVENT-': self.ylogRequest,
                       '-X-LOG-EVENT-':self.xlogRequest
                       }

    def getGUI(self):
        # All the stuff inside your window.
        
        first_column = [
            [sg.Button("Refresh Files", key='-REFRESH-EVENT-', size=(30, 5))],
            [sg.Text("Radial Region To Contour Data")],
            [sg.Text('Radial Source'), sg.OptionMenu(values=self.radial_source, key="-SOURCE-RADIAL-SELECT-")],
            [sg.Text('Radial Background'), sg.OptionMenu(values=self.radial_bkg, key="-BKG-RADIAL-SELECT-")],
            [sg.Text("Save Name"), sg.InputText("", key="-EXTRACT-SAVE-NAME-", size=(10, 1))],
            [sg.Button('Extract Contour Data', key='-EVENT-MAKE-CONTOUR-DATA-')],
            [sg.Canvas(size=(200, 200))],
            [sg.Text("Contour Data To Contour Plot")],
            [sg.Text('File Name'), sg.OptionMenu(values=self.contour_files, key="-CONTOUR-SELECT-")],
            [sg.Button('Set Contour Plot', key='-EVENT-MAKE-CONTOUR-PLOT-')],
            [sg.Button('Toggle X Log Scale', key='-X-LOG-EVENT-'), sg.Button('Toggle Y Log Scale', key='-Y-LOG-EVENT-')]
        ]
        
        graph_column = [
            [sg.Canvas(size=(500,500), key='-GRAPH-')]
        ]
        
        layout = [  
            [
                sg.Column(first_column),
                sg.VSeparator(),
                sg.Column(graph_column)
            ]
        ]

        # Create the Window
        window = sg.Window('GTI Selection', layout)
        return window

    def xlogRequest(self, value):
        self.spectraPlot.toggleXLog()
        
    def ylogRequest(self, value):
        self.spectraPlot.toggleYLog()
        
    def setGraphData(self, values):
        
        if not values["-CONTOUR-SELECT-"] or values["-CONTOUR-SELECT-"] == "None":
            return
        
        file = os.path.join(self.contourDir, values["-CONTOUR-SELECT-"])
        
        tab = read_file(file)
        self.xdata  = np.asarray(tab.get_column("cel_rmid").values)
        self.ydata = np.asarray(tab.get_column("sur_bri").values)
        self.ydata_error = np.asarray(tab.get_column("sur_bri_err").values)
        
        shortened_name = file.split("/")[-1]
        
        self.title = f"{shortened_name}: Radial Profile"
        self.xlabel = "CEL_RMID (arc sec)"
        self.ylabel = "SUR_BRI (photons/cm**2/pixel**2/s)"
        
        self.spectraPlot.plot(self.xdata, self.ydata, self.ydata_error, self.title, self.xlabel, self.ylabel)


    def startGUI(self):
        
        self.config_events()
        
        
        self.window = self.getGUI()
        self.spectraPlot = GraphDisplayer(self.window['-GRAPH-'], self.title, self.xlabel, self.ylabel) #what canvas are you plotting it on
        self.window.finalize() #show the window
        # self.spectraPlot.plot(self.xdata, self.ydata) # plot an empty plot    
        
        self.event_loop(self.window)
        
        plt.close(self.spectraPlot.figure)
        self.window.close()
        
        return True
    
    def configOptionMenus(self):
        self.radial_files = [f for f in os.listdir(self.regionDir) if os.path.isfile(os.path.join(self.dir, f)) and "radial" in f and ".reg" in f ]  
             
        self.radial_bkg = [f for f in self.radial_files if "bkg" in f or "back" in f]
        self.radial_source = [f for f in self.radial_files if f not in self.radial_bkg ]
        self.contour_files = [f for f in os.listdir(self.contourDir) if os.path.isfile(os.path.join(self.contourDir, f))]
    
        self.radial_bkg.append("None")
        self.radial_source.append("None")
        self.contour_files.append("None")
        
    def refresh_files(self, values):
        self.configOptionMenus()
        
        self.window["-SOURCE-RADIAL-SELECT-"].update(values=self.radial_source)
        self.window["-BKG-RADIAL-SELECT-"].update(values=self.radial_bkg)
        self.window["-CONTOUR-SELECT-"].update(values=self.contour_files)
        
        self.window.refresh()
            
    def extract_from_region_event(self, values):
        if values["-SOURCE-RADIAL-SELECT-"] and values["-SOURCE-RADIAL-SELECT-"] != "None":
            if values["-BKG-RADIAL-SELECT-"] and values["-BKG-RADIAL-SELECT-"] != "None":
                if values["-EXTRACT-SAVE-NAME-"]:
                    source_region_file = pathAdd(self.dir, values["-SOURCE-RADIAL-SELECT-"])
                    bkg_region_file = pathAdd(self.dir, values["-BKG-RADIAL-SELECT-"])
                    tag = values["-EXTRACT-SAVE-NAME-"]
                                    
                    unlearn("dmextract")
                    sysCMD("dmextract", f"infile={self.fits_dir}[bin sky=@{source_region_file}]", f"outfile={pathAdd(self.dir, 'RADIAL_PROFILES', f'{tag}_radial.fits')}", f"bkg={self.fits_dir}[bin sky=@{bkg_region_file}]", "opt=generic", "error=gaussian", "bkgerror=gaussian")

                    self.refresh_files(values)
                    
    def event_loop(self, window):
        while True:
            event, values = window.read()
            
            if event in self.events:
                self.events[event](values)

            if event == sg.WIN_CLOSED or event == 'Done': break # if user closes window or clicks cancel

        
class RadialProfileData:

    def __init__(self, filePath, name, referenceVal=1.0):
        self.name = name
        self.filePath = filePath
        self.xRadialDistance = []
        self.yCounts = []
        self.yErr = []

        self.referenceVal = referenceVal
        self.normFactor = 1.0

        self.getData()

    def addX(self, x):
        self.xRadialDistance.append(x)

    def addY(self, y):
        self.yCounts.append(y/self.normFactor)

    def addYErr(self, yEr):
        self.yErr.append(yEr/self.normFactor)

    def getData(self):
        with open(self.filePath, 'r') as dataFile:
            firstLine = dataFile.readline().strip().split()

            self.normFactor = float(firstLine[1])/self.referenceVal

            self.addX(float(firstLine[0]))
            self.addY(float(firstLine[1]))
            self.addYErr(float(firstLine[2]))

            for currentLine in dataFile:
                line = currentLine.strip().split()
                self.addX(float(line[0]))
                self.addY(float(line[1]))
                self.addYErr(float(line[2]))