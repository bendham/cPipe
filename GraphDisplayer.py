import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Thank you David Megson-Smith
# From https://stackoverflow.com/questions/63155989/automated-updating-matplotlib-plot-in-pysimplegui-window
# For the base framework of this code
class GraphDisplayer():
    def __init__(self, canvas, title, xlabel, ylabel) -> None:
        self.fig_agg = None
        self.figure = None
        self.canvas = canvas

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        self.isXLog = False
        self.isYLog = False

    def plot(self, xdata, ydata, yerr=None, title=None, xlabel=None, ylabel=None):
        if title:
            self.title = title
            
        if xlabel:
            self.xlabel = xlabel
        
        if ylabel:
            self.ylabel = ylabel
        
        self.xdata = xdata
        self.ydata = ydata
        self.yerr = yerr
        self.plot_figure_controller()
        self.figure_drawer()

    def toggleXLog(self):
        if self.figure is not None:
            if self.isXLog:
                self.axes.set_xscale("linear")
            else:
                self.axes.set_xscale("log")
                
            self.isXLog = not self.isXLog
            
            self.figure_drawer()
        
    def toggleYLog(self):
        if self.figure is not None:
        
            if self.isYLog:
                self.axes.set_yscale("linear")
            else:
                self.axes.set_yscale("log")
            
            self.isYLog = not self.isYLog
            
            self.figure_drawer()
        

    #put all of your normal matplotlib stuff in here
    def plot_figure_controller(self):
        self.figure = plt.figure()
        self.axes = self.figure.add_subplot(111)
        
        if self.yerr is not None:
            self.line = self.axes.errorbar(self.xdata, self.ydata, yerr=self.yerr)
        else:
            self.line, = self.axes.plot(self.xdata, self.ydata)
            
        self.axes.set_title(self.title)
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        #first run....
        # if self.figure is None:
        #     self.figure = plt.figure()
        #     self.axes = self.figure.add_subplot(111)
            
        #     if self.yerr is not None:
        #         self.line = self.axes.errorbar(self.xdata, self.ydata, yerr=self.yerr)
        #     else:
        #         self.line, = self.axes.plot(self.xdata, self.ydata)
                
        #     self.axes.set_title(self.title)
        #     self.axes.set_xlabel(self.xlabel)
        #     self.axes.set_ylabel(self.ylabel)

        #all other runs
        # else:      
            
        #     if self.yerr is not None:
        #         self.line.markerline.set_xdata(self.xdata)#update xdata  
        #         self.line.markerline.set_ydata(self.ydata)#update ydata   
                     
        #         self.line.set_yerrdata(self.yerr) # update yerr
        #     else:
        #         self.line.markerline.set_xdata(self.xdata)#update xdata  
        #         self.line.markerline.set_ydata(self.ydata)#update ydata   
                
        #     self.axes.relim() #scale the y scale
        #     self.axes.autoscale_view() #scale the y scale

    #finally draw the figure on a canvas
    def figure_drawer(self):
        if self.fig_agg is not None: self.fig_agg.get_tk_widget().forget()
        self.fig_agg = FigureCanvasTkAgg(self.figure, self.canvas.TKCanvas)
        self.fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.fig_agg.draw()


