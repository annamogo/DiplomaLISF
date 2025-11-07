import cv2
import numpy as np
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfile
from img_fringe.img_fringe import *
from img_fringe.data_fringe import *
from processing.processing import *
from processing.complex_processing import ComplexProcess as cp
from processing.processing_factory import ProcessFactory as pf
from PIL import Image, ImageTk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure



class GUI(Frame):
    
    def __init__(self, master=None):
        Frame.__init__(self, master)
        w,h = 1300, 650
        master.minsize(width=w,height=h)
        master.maxsize(width=w,height=h)
        self.pack()

        # display next image button
        self.next_img_but = Button(self, text="next", command=self.display_next_img)
        self.next_img_but.grid(row=0, column=0, padx=5, pady=5)

        # The image, displayed on the screen, be it one image or series
        self.img = None
        self.img_label = Label(self, image=self.img)
        self.img_label.grid(row=1, column=0, padx=5, pady=5)

        self.img_label1 = Label(self, text="Hello")
        self.img_label1.grid(row=0, column=1, padx=5, pady=5)


        # Hold objects, currently being analysed
        self.ImgStackObj = ImgFringeStack()
        self.curr_img = 0
        self.ImgObj = ImgFringe()

        self.ImgData = DataFringe()

        # create menu bar
        self.create_menu_bar()




    def create_menu_bar(self):
        menubar = Menu(self)
        self.master.config(menu=menubar)

        # create menu for choosing images
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Choose image", command=self.read_fringe_img)
        file_menu.add_command(label="Choose image series", command=self.read_fringe_imgs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        # menu for cropping images
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cut out area", menu=edit_menu)
        edit_menu.add_command(label="Crop current image in a stack", command=self.crop_curr_img)
        edit_menu.add_command(label="Crop all images in a stack", command = self.crop_curr_stack)
        edit_menu.add_command(label="Crop individual image", command = self.crop_img)

        # menu for getting data and plotting
        data_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Create data", menu=data_menu)
        data_menu.add_command(label="Flattern image", command=self.flatten_img)
        data_menu.add_separator()
        data_menu.add_command(label="Plot flattened data", command = self.plot)
        
        

    def update_img(self):
        image = Image.fromarray(self.img)
        tk_image = ImageTk.PhotoImage(image)

        self.img_label.configure(image=tk_image)
        self.img_label.image = tk_image

        self.master.after(100, self.update_img)

    def display_next_img(self):
        self.curr_img += 1
        if self.curr_img >= self.ImgStackObj.img_count:
            self.curr_img = 0
            
        self.img = self.ImgStackObj[self.curr_img].img
        self.update_img()
        

    def read_fringe_img(self):

        name = askopenfilename(initialdir='./data',
                               filetypes=(("PNG", "*.png"), ("JPG", "*.jpg")),
                               title="Choose an image."
                              )

        try:
            self.ImgObj.read(name)
        except:
            return

        self.ImgStackObj.append_obj(self.ImgObj)
        
        self.img = self.ImgObj.img
        self.update_img()

    

    def read_fringe_imgs(self):
        name = askdirectory(initialdir="./data",
                            title="Choose directory with images"
                            )

        self.curr_img = 0
        self.ImgStackObj.clear()
        self.ImgStackObj.read(name)
        self.img = self.ImgStackObj[0].img
        self.update_img()


    def crop_img(self):
        self.ImgObj.crop()
        self.img = self.ImgObj.img
        self.update_img()
    
        
    def crop_curr_img(self):
        self.ImgStackObj[self.curr_img].crop()
        self.img = self.ImgStackObj[self.curr_img].img
        self.update_img()

    def crop_curr_stack(self):
        self.ImgStackObj.crop(n=self.curr_img)
        self.img = self.ImgStackObj[self.curr_img].img
        self.update_img()

    def flatten_img(self):
        data = self.ImgObj.flatten()
        self.ImgData.store(data)

    def plot(self):
        fig = self.ImgData.plot_data()
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=5, pady=5)
        self.canvas.draw()



if __name__ == "__main__":
    root = Tk()
    app = GUI(master=root)
    root.mainloop()



