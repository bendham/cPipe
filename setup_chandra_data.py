from ast import arg
import subprocess
import sys
import os
from getopt import getopt, GetoptError
from helpers import *
from numpy import extract
"""
- Run in folder containing folders of obsId folders
- Will by default 
- Also generate a 0.3-10 keV evt2 file for you :)




"""
        
def main(cmd_args):
    chandra_repro = False
    extract = False
    filter = False
    multiple = False
    working_directory = ""
    
    try:
        opts, args = getopt(cmd_args, "femr")
    except GetoptError:
        print("Error parsing command")
        sys.exit(2)

    if len(args) > 1:
        print("Please provide one argument which is a directory.")
        sys.exit(2)
        
    # Test if directory provided exists
    if( not isValidPath(args[0])):
        print("Please provide an actual directory")
        sys.exit(2)
    else:
        working_directory = args[0]
        
    for opt, arg in opts:
        if opt == "-r": # Reprocess
            chandra_repro = True
        elif opt == "-e": # Extract files (from gzip)
            extract = True
        elif opt == "-f": # Filter to 0.3-10keV
            filter = True
        elif opt == "-m": # If you have multiple obsid folders
            multiple = True
        
    # Assumes obsId directories are integers
    if(multiple):
        obsid_paths = [os.path.join(working_directory, f) for f in os.listdir(args[0]) if( os.path.isdir(os.path.join(working_directory, f)) and f.isnumeric())] # Get all obsId folders
    else:
        obsid_paths = [working_directory]
        
    for obsPath in obsid_paths:
        repro_path = os.path.join(obsPath, "repro")
        
        
        if extract:
            unZipFilesInPath(os.path.join(obsPath, "primary"))
            unZipFilesInPath(os.path.join(obsPath, "secondary"))
        
        if(chandra_repro):
            subprocess.call(["chandra_repro", f"indir={obsPath}", f"outdir={repro_path}", "clobber=yes"])
            
        if(filter):
            resp = ""
            if(not isValidPath(repro_path)):
                resp = input("Data has not been reprocessed. Please do this before filtering. Reprocess? (Y/n)")
                if(resp != "n"):
                    subprocess.call(["chandra_repro", f"indir={obsPath}", f"outdir={repro_path}", "clobber=yes"])
            if(resp != "n"):
                print("blas")
                
                if findAndSetBadPixelFile(repro_path):
                    
                    evt2_file = findFile(repro_path, "repro_evt2.fits")
                    
                    path_to_evt2_file = os.path.join(repro_path, evt2_file)
                    
                    filtered_evt2_file = path_to_evt2_file[:-5] + "_0.3-10.fits"
                    # Filter
                    print(f'dmcopy "{path_to_evt2_file}[energy=300:10000]" {filtered_evt2_file}')
                    subprocess.call(["dmcopy", f'{path_to_evt2_file}[energy=300:10000]', f"{filtered_evt2_file}"])
            
                
def unZipFilesInPath(path):
    filesToUnzip = getGzipFilePaths(path)
    
    if( len(filesToUnzip) > 0):
        for file in filesToUnzip:
            subprocess.call(["gunzip", f"{file}"])
        

def getGzipFilePaths(path):
    return [os.path.join(path, f) for f in os.listdir(path) if( f[-3:] == ".gz")]


if __name__ == "__main__":
    main(sys.argv[1:])