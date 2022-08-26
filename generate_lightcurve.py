from pycrates import read_file
import sys
import matplotlib.pylab as plt


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