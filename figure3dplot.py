from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

import mmap
import struct
import datetime as dt
from datetime import date
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
import matplotlib as mpl



class Window(Frame):
	def __init__(self, master=None):
		
		Frame.__init__(self, master)
		self.master = master
		self.init_window()


		menu = Menu(self.master)
		self.master.config(menu=menu)

		file = Menu(menu)
		file.add_command(label="Load", command=self.open_bin)
		file.add_command(label="Clear Figure", command=self.clrfig)
		file.add_command(label="Exit", command=self.client_exit)

		menu.add_cascade(label="File", menu=file)

		separator = Frame(master=self.master, relief="sunken")
		separator.grid()

		self.sampLentxt = StringVar()
		self.sampLentxt.set("Number of Samples:")
		self.sampLen=Label(master=self.master, textvariable=self.sampLentxt)
		self.sampLen.place(x=10, y=405)


		self.sample_length = Entry(master = self.master)
		self.sample_length.place(x=150, y=405, width=100)
		self.sample_length.insert(0, 2000)
		self.sample_length.bind('<Return>', self.comp_s)

		self.offset_slide = Scale(master = self.master, from_=1000, to=0, command=self.upd_plot)
		self.offset_slide.place(x=500, y = 75, width=100, height=200)

		
		self.fig = Figure(figsize=(5, 4))
		self.canvas = FigureCanvasTkAgg(self.fig, master=separator)
		self.ax = self.fig.add_subplot(111, projection='3d')
		self.ax.view_init(azim=-90, elev=90)
		self.offset=0
		self.canvas.draw()
		self.canvas.get_tk_widget().grid(row=0)
		#self.canvas.get_tk_widget().pack(side=LEFT, expand=False)

	def init_window(self):
		self.master.title("3D Spectrum Plot")
		self.master.grid_rowconfigure(2, weight=1)
		self.master.grid_columnconfigure(3, weight=1)
		#self.pack(fill=BOTH, expand = 1)
		#self.pack_propagate(0)

	def comp_s(self, event):
		#self.numSets = int(self.sample_length.get())
		self.plotfig()

	def client_exit(self):
		exit()

	def upd_plot(self, value):
		self.offset = int(value)
		try:
			self.plotfig()
		except:
			pass

	def clrfig(self):
		self.ax.clear()
		self.canvas.draw()

	def open_bin(self):
		self.filename = filedialog.askopenfilename()
		#print("Selected: ", self.filename)
		self.fp = open(self.filename, 'rb')
		self.mm = mmap.mmap(self.fp.fileno(), 0, access=mmap.ACCESS_READ)

		self.dataRange_start = range(52, len(self.mm), 3336) #get start indices
		self.dataChunk = 3284 #RF levels are stored in this chunk size
		self.dataRange_stop = range(52+self.dataChunk, len(self.mm)+1, 3336) #get end indices
		self.ax.clear()
		self.plotfig()
		
	
	def plotfig(self):
		self.ax.clear()
		self.numSets = int(self.sample_length.get())
		self.y = np.arange(0, self.numSets)
		self.x = np.arange(0, 821)

		self.a = []
		
		for i,j in zip(self.dataRange_start[self.offset:(self.numSets+self.offset)],
		 self.dataRange_stop[self.offset:(self.numSets+self.offset)]):
			data = struct.iter_unpack(">f", self.mm[i:j])
			dataLevels = [float(d[0]) for d in data]
			self.a.append(dataLevels)
		
		self.X, self.Y = np.meshgrid(self.x, self.y)
		self.Z = np.array(self.a)
		self.surf = self.ax.plot_surface(self.X, self.Y, self.Z, cmap=cm.jet,
		linewidth=0, antialiased=False)
		#self.ax.view_init(azim=-90, elev=90)
		self.ax.set_xlabel('X axis')
		self.ax.set_ylabel('Y axis')
		self.ax.set_zlabel('Z axis')
		self.canvas.draw()
		self.offset_slide.focus()

	def process_binfile(self):
		for i,j in zip(self.dataRange_start, self.dataRange_stop):
			data = struct.iter_unpack(">f", self.mm[i:j])
			dataLevels = [float(d[0]) for d in data]
			self.a.append(dataLevels)

#tkinter.mainloop()

root = Tk()
root.geometry("1500x800")
root.resizable(0,0)
#root.wm_title("3D Spectrum Plot")

app = Window(root)
root.mainloop()