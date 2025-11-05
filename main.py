from tkinter import *
from tkinter import ttk
import numpy as np
#root = Tk()
#frm = ttk.Frame(root, padding=10)
#frm.grid()
#ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
#ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
#root.mainloop()
from img_fringe import img_fringe as imfr

path = './drop-211025-2/drop-010.jpg'
dir_path = './drop-211025-2'

img = imfr.ImgFringeStack()
img.read_multiple('./drop-211025-2')


img_cropped = img.crop(inplace=False)
img_cropped.set_resolution(1000, mode='all')
#img.show()
print(img_cropped[3].resolution)



