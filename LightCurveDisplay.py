from typing import Dict
import PySimpleGUI as sg
from Display import Display
import numpy as np
import matplotlib.pyplot as plt
from GraphDisplayer import GraphDisplayer
from pycrates import read_file
from helpers import isFloat

class LightCurveDisplay(Display):
    
    events: Dict = {}
    gtiCount = -1
    
    
    def __init__(self, fits_dir, title=None, xlabel=None, ylabel=None) -> None:
        
        tab = read_file(fits_dir)
        
        self.xx = np.asarray(tab.get_column("time").values)
        self.xdata = self.xx
        
        
        self.yy = np.asarray(tab.get_column("count_rate").values)
        self.ydata = self.yy

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        
    def config_events(self):
        self.events = {'apply-count-limit': self.applyCountLimitEvent, 'reset-count-limit':self.resetLimitEvent}

    def getGUI(self):
        # All the stuff inside your window.
        
        layout = [  
                [sg.Canvas(size=(500,500), key='canvas')],
                [sg.Text("Count Rate Limit")],
                [sg.Text("Limit"),sg.InputText("", key="count-limit", size=(10, 1)), sg.Button('Use', key='apply-count-limit'), sg.Button('Reset', key='reset-count-limit')],
                [sg.Button('Done')]
            ]

        # Create the Window
        window = sg.Window('GTI Selection', layout)
        return window

    def startGUI(self):
        
        window = self.getGUI()
        self.spectraPlot = GraphDisplayer(window['canvas'], self.title, self.xlabel, self.ylabel) #what canvas are you plotting it on
        window.finalize() #show the window
        self.spectraPlot.plot(self.xdata, self.ydata) # plot an empty plot    
        
        self.config_events()
        self.event_loop(window)
        
        plt.close(self.spectraPlot.figure)
        window.close()
        
        return self.gtiCount
        
    def event_loop(self, window):
        while True:
            event, values = window.read()
            
            if event in self.events:
                self.events[event](values)

            if event == sg.WIN_CLOSED or event == 'Done': break # if user closes window or clicks cancel
            
    def applyCountLimitEvent(self, values):
        if isFloat(values['count-limit']):
            self.gtiCount = float(values['count-limit'])
            mask = self.yy  < self.gtiCount
            self.spectraPlot.plot(self.xx[mask], self.yy[mask]) # plot an empty plot   
            
    def resetLimitEvent(self, values):
        self.spectraPlot.plot(self.xx, self.yy) 
        self.gtiCount = -1

        
        