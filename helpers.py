import os
import subprocess
import sys

from traitlets import Bool

# def process_cmd_input():
#     chandra_repro = False
#     extract = False
#     filter = False
#     multiple = False
#     working_directory = ""
    
#     try:
#         opts, args = getopt(cmd_args, "femr")
#     except GetoptError:
#         print("Error parsing command")
#         sys.exit(2)

#     if len(args) > 1:
#         print("Please provide one argument which is a directory.")
#         sys.exit(2)
        
#     # Test if directory provided exists
#     if( not isValidPath(args[0])):
#         print("Please provide an actual directory")
#         sys.exit(2)
#     else:
#         working_directory = args[0]
        
#     for opt, arg in opts:
#         if opt == "-r": # Reprocess
#             chandra_repro = True
#         elif opt == "-e": # Extract files (from gzip)
#             extract = True
#         elif opt == "-f": # Filter to 0.3-10keV
#             filter = True
#         elif opt == "-m": # If you have multiple obsid folders
#             multiple = True


def isValidPath(path):
    return os.path.isdir(path)

def isValidFile(path):
    return os.path.isfile(path)

def findFile(path, name_to_find):
    if isValidPath(path):
        
        for f in os.listdir(path):
            if( name_to_find in f):
                
                return f

    return None

def findBadPixelFile(path):
    return findFile(path, "repro_bpix1.fits")

def setBadPixelFile(path):
    subprocess.call(["punlearn", "ardlib"])
    subprocess.call(["acis_set_ardlib", f"{path}", "verbose=0"])
    
def findAndSetBadPixelFile(repro_path) -> Bool:
    pixel_name = findBadPixelFile(repro_path)
    pixel_path = os.path.join(repro_path, pixel_name)
    
    if pixel_path:
        setBadPixelFile(pixel_path)
        return True
    print("Could not locate bad pixel file. Exiting...")
    return False
    
def isFloat(potench):
    try:
        float(potench)
        return True
    except ValueError:
        return False
    
def pathAdd(dir, other, *args):
    path = os.path.join(dir, other)
    for arg in args:
        path = os.path.join(path, arg)
    return path
    
def appendToFilename(fname, toAdd, ending):
    return fname[:-len(ending)] + toAdd + ending

def unlearn(key):
    return subprocess.call(["punlearn", key])

def sysCMD(*args):
    command = []
    for arg in args:
        command.append(arg)
    try:
        subprocess.call(command)
    except Exception as ex:
        print("Could not process command. Exiting...")
        template = f"An exception of type {type(ex).__name__} occurred. Arguments:\n{ex.args}"
        print(template)
        sys.exit(2)
        
    
    
    