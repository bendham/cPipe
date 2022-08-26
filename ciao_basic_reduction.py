#!/usr/bin/env python

from genericpath import isdir
from ciao_contrib.runtool import *
from getopt import getopt, GetoptError
from matplotlib.pyplot import title, xlabel, ylabel
from helpers import *
from pycrates import read_file
import sys
import matplotlib.pylab as plt
import numpy as np


# Adjust for flaring
# Extract sources and bkgs
# Extract source from bkg
from LightCurveDisplay import LightCurveDisplay
from ContourDisplay import ContourDisplay


def main(cmd_args):

    input_file = None
    lightcurve_region = None
    lightcurve_file = None

    extraction_type = ""

    source_region_file = None
    bkg_region_file = None
    
    tag=""

    try:
        opts, args = getopt(cmd_args, "i:l:s:b:k:ce")
    except GetoptError:
        print("Error parsing command")
        sys.exit(2)

    if len(args) > 1:
        print("Please provide one argument which is a directory.")
        sys.exit(2)

    # Test if directory provided exists
    # print(opts)
    # print(args)

    # Command Type Set up

    # for arg in args:
    #     print(arg)
    #     if not extraction_type:
    #         if arg == "-e":
    #             extraction_type = "source_extract"
    #         elif arg == "-c":
    #             extraction_type = "contour_extract"

    # Command Set up

    for opt, arg in opts:
        if opt == "-k":
            tag = arg + "_"
        elif opt == "-e" or opt == "-c":
            if not extraction_type:
                extraction_type = "source_extract" if arg == "-e" else "contour_extract"
        else:
            validation_leave(arg, opt)
            verifyValidFile(arg)
            if opt == "-l":
                lightcurve_region = arg
            elif opt == "-i":
                input_file = arg
            elif opt == "-s":
                source_region_file = arg
            elif opt == "-b":
                bkg_region_file = arg

    if "n" in args:
        plot = False

    if input_file:
        directory = "/".join(input_file.strip("/").split("/")[:-1])
    elif lightcurve_region:
        directory = "/".join(lightcurve_region.strip("/").split("/")[:-1])
        input_file = findFile(directory, "evt2_0.3-10.fits")
        if not input_file:
            print(input_file)
            print("Could not find a file to use based. Please specify one instead.")
            sys.exit(2)

    if findAndSetBadPixelFile(directory):

        if lightcurve_region and input_file:
            command = []
            subprocess.call(["punlearn", "dmextract"])
            command = command + \
                ["dmextract",
                    f"infile={input_file}[exclude sky=region({lightcurve_region})][bin time=::3.24104]"]
            command = command + \
                [f'outfile={pathAdd(directory, f"{tag}backlight_lc.fits")}']
            command = command + ['opt=ltc1']
            # command = command + ['clobber=yes']
            subprocess.call(command)
            lightcurve_file = os.path.join(directory, f"{tag}backlight_lc.fits")

        if lightcurve_file:
            lCD = LightCurveDisplay(
                lightcurve_file, title="Light Curve", xlabel="Time (s)", ylabel="counts/s")
            gti = lCD.startGUI()

            if gti >= 0:
                output_gti_filt = pathAdd(directory, "bkg_gti.fits")
                # Aplly gti
                command = []
                subprocess.call(["punlearn", "dmgti"])
                command = command + ["dmgti", f"infile={lightcurve_file}"]
                command = command + [f'outfile={output_gti_filt}']
                command = command + [f'userlimit=count_rate<={gti}']
                command = command + ['clobber=yes']
                subprocess.call(command)

                subprocess.call(['dmcopy', f'{input_file}[@{output_gti_filt}]',
                                appendToFilename(input_file, f"_{tag}filt", ".fits"), "clobber=yes"])

                os.remove(output_gti_filt)

                input_file = appendToFilename(input_file, f"{tag}_filt", ".fits")

        if extraction_type:
            
            
            if extraction_type == "source_extract":
                if source_region_file and bkg_region_file:
                    unlearn("specextract")
                    sysCMD("specextract", f"infile={input_file}[sky=region({source_region_file})]", f"outroot={pathAdd(directory, f'{tag}ROI', f'{tag}ROI')}" , f"bkgfile={input_file}[bin sky=region({bkg_region_file})]")
                else:
                    print("Please specify both a source and background region")
                    
            elif extraction_type == "contour_extract":
                
                radialProfileDir = pathAdd(directory, "RADIAL_PROFILES")
                if not isdir(radialProfileDir):
                    os.mkdir(radialProfileDir)
                
                if source_region_file and bkg_region_file:
                    unlearn("dmextract")
                    sysCMD("dmextract", f"infile={input_file}[bin sky=@{source_region_file}]", f"outfile={pathAdd(directory, 'RADIAL_PROFILES', f'{tag}radial.fits')}", f"bkg={input_file}[bin sky=@{bkg_region_file}]", "opt=generic", "error=gaussian", "bkgerror=gaussian")
                
                cD = ContourDisplay(
                    directory, input_file, init_source=source_region_file, init_bkg=bkg_region_file
                )
                cD.startGUI()
            else:
                print("Invalid extraction type.")
            
            
            
            
            
        
        
        
        
def validation_leave(arg, opt):
    if not arg:
        print(f"Specify arg for {opt}.")
        sys.exit(2)
            
def verifyValidFile(file_path):
    if( not isValidFile(file_path)):
        print(f"'{file_path}' is not a file. Please provide an actual file.")
        sys.exit(2)

def func():
    
    if(len(sys.argv) == 2): # python file and one other
        print(len(sys.argv))
        try:
            fileDir = sys.argv[1] #get second argument
            
            snrName = fileDir.split("/")[-4]
            
            tab = read_file(fileDir)
            xx = tab.get_column("time").values
            yy = tab.get_column("count_rate").values
            plt.plot(xx,yy,marker="o",linestyle="")
            plt.xlabel("Time (s)")
            plt.ylabel("Count Rate (c/s)")
            plt.title(snrName)
            plt.show()
        except:
            print("Could not open provided file. Please ensure it is correct.")

    else:
        print("Please provide the file to generate a lightcurve for")

if __name__ == "__main__":
    main(sys.argv[1:])
