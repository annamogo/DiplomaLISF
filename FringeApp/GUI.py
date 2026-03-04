from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfile
from PIL import Image, ImageTk
import cv2

from img_fringe.img_fringe import *
from processing.processing import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

LARGE_FONT= ("Verdana", 12)


class GUIapp(Tk):

    def __init__(self):

        super().__init__()

        # general app settings
        self.geometry("700x700")


        # main window frame
        self.main_win = MainWindow(self, bd=3, highlightbackground="black",
                               highlightthickness=1)




class MainWindow(Frame):

    def __init__(self, parent, **config):
        super().__init__(parent, **config)
        self.p = parent
        self.conf_set = config
        
        self.pack(pady=5, fill=BOTH, expand=True)

        self.columnconfigure(index=0,weight=1)
        self.columnconfigure(index=1,weight=3)
        self.rowconfigure(index=0,weight=1)
        self.rowconfigure(index=1,weight=3)

        
        # vars to hold objects, currently being analysed
        self.ImgStackObj = ImgFringeStack()
        self.curr_img = None
        self.ImgObj = ImgFringe()

        self.ImgData = DataFringe()
        self.ImgDataStack = DataFringeStack()



        # create main menu
        self.create_menu_bar()


        # create child frames
        self.img_fr = ShowImgFrame(self, **self.conf_set)
        self.plt_fr = PlotSigFrame(self, **self.conf_set)
        self.res_fr = ResultsFrame(self, **self.conf_set)



    def create_menu_bar(self):
        menubar = Menu(self)
        self.p.config(menu=menubar)

        # create menu for choosing images
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Choose image",
                              command = self.read_fringe_img)
        file_menu.add_command(label="Choose image series",
                              command=self.read_fringe_stack)
        file_menu.add_separator()
        file_menu.add_command(label="Exit")

        # menu for cropping images
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cut out area", menu=edit_menu)
        edit_menu.add_command(label="Crop current image in a stack",
                              command=self.crop_curr_img)
        edit_menu.add_command(label="Crop all images in a stack",
                              command=self.crop_curr_stack)
        edit_menu.add_command(label="Crop individual image")

        # menu for getting data and plotting
        data_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Create data", menu=data_menu)
        data_menu.add_command(label="Flattern image",
                              command=self.flatten_curr_img)
        data_menu.add_command(label="Flattern all images in the stack",
                              command=self.flatten_curr_stack)

        

    def read_fringe_img(self):

        name = askopenfilename(initialdir='./data',
                                filetypes=(("PNG", "*.png"), ("JPG", "*.jpg")),
                                title="Choose an image."
                                )

        try:
            self.ImgObj.read(name)
        except Exception as e:
            print(f"{e}: reading to object failed.")

        self.ImgStackObj.clear()
        self.curr_img = 0
        self.ImgStackObj.append_obj(self.ImgObj)
        
        self.img_fr.update_img()

        self.plt_fr.up_to_date_data = False




    def read_fringe_stack(self):
        name = askdirectory(initialdir="./data",
                            title="Choose directory with images"
                            )

        self.curr_img = 0
        self.ImgStackObj.clear()
        self.ImgStackObj.read(name)
        
        self.img_fr.update_img()

        self.plt_fr.up_to_date_data = False



    def crop_curr_img(self):
        self.ImgStackObj[self.curr_img].crop()
        
        self.img_fr.update_img()


    def crop_curr_stack(self):
        self.ImgStackObj.crop(n=self.curr_img)
        
        self.img_fr.update_img()


    def flatten_curr_img(self):
        #data = self.ImgStackObj[self.curr_img].flatten()
        
        #self.ImgData.store(data)
        self.ImgData = self.ImgStackObj[self.curr_img].create_data()

        self.ImgDataStack.clear()
        self.ImgDataStack.append_obj(self.ImgData)
        
        self.plt_fr.update_data()
        #self.res_fr.update_data()


    def flatten_curr_stack(self):
        #data = [img_obj.flatten() for img_obj in self.ImgStackObj]
    
        #self.ImgDataStack.from_array(data)
        self.ImgDataStack = self.ImgStackObj.create_data_stack()

        self.plt_fr.update_data()
        self.res_fr.update_data()

        


class ShowImgFrame(Frame):

    def __init__(self, parent, **config):
        super().__init__(parent, **config)
        self.p = parent

        self.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)

        self.ImgStackObj = self.p.ImgStackObj
        self.curr_img = self.p.curr_img
        
        self.img = None

    
        self.label = Label(self, text = f"picture *** out of ***")
        self.label.pack(pady=10)

        self.img_label = Label(self, image=self.img)
        self.img_label.pack(pady=10, padx=20)

        self.next_button = Button(self, text="Next image",
                                  command=self.display_next_img)
        self.next_button.pack(pady=10, padx=20)

 
    def update_lbl(self):
        new_text = f"picture {self.curr_img} out of {len(self.ImgStackObj.img_stack)}"
        self.label.configure(text = new_text)

        self.after(100, self.display_img)

    def update_img(self):
        self.ImgStackObj = self.p.ImgStackObj
        self.curr_img = self.p.curr_img
        
        self.img = self.ImgStackObj[self.curr_img].img

        self.display_img()
        self.update_lbl()
        

    def display_img(self):
        image = Image.fromarray(self.img)
        tk_image = ImageTk.PhotoImage(image)

        self.img_label.configure(image=tk_image)
        self.img_label.image = tk_image

        self.after(100, self.display_img)


    def display_next_img(self):
        self.curr_img += 1
        self.p.curr_img += 1
        if self.curr_img >= self.ImgStackObj.img_count:
            self.curr_img = 0
            self.p.curr_img = 0
            
        self.img = self.ImgStackObj[self.curr_img].img
        self.display_img()
        
        self.update_lbl()

        self.p.plt_fr.update_current()

    


class PlotSigFrame(Frame):

    def __init__(self, parent, **config):
        super().__init__(parent, **config)
        self.p = parent
        self.ImgDataStack = self.p.ImgDataStack
        self.curr_img = self.p.curr_img

        self.up_to_date_data = False

        self.grid(row=1, column=0, padx=5, pady=5, sticky=NSEW)

        self.button = Button(self, text="Plot flattened",
                             command=self.update_plot)
        self.button.pack(pady=10)

        self.create_plot()
    

    def update_data(self):
        self.ImgDataStack = self.p.ImgDataStack
        self.curr_img = self.p.curr_img
        self.up_to_date_data = True
        print(f"current image {self.curr_img}")

    def update_current(self):
        self.curr_img = self.p.curr_img
        print(f"current image {self.curr_img}")

    def create_plot(self):
        self.fig = Figure(figsize=(3,2))
        self.a = self.fig.add_subplot(1,1,1)

        self.graph, = self.a.plot([], [], 'b-')
         
        self.a.set_title("Signal plot")
        
        self.a.set_xlabel("pixels")
        self.a.set_ylabel("relative intencity")

                
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.widget = self.canvas.get_tk_widget().pack(pady=20)
        #self.canvas.draw()

    def update_plot(self):

        if self.up_to_date_data:
            data_obj = self.ImgDataStack[self.curr_img]

            x = np.arange(data_obj.pcount)
            y = data_obj.data
            
            self.graph.set_data(x,y)

            self.a.relim()
            self.a.autoscale_view(True,True,True)
            
            self.canvas.draw()

            


class ResultsFrame(Frame):

    def __init__(self, parent, **config):
        super().__init__(parent, **config)
        self.p = parent
        self.ImgDataStack = self.p.ImgDataStack

        self.DataStackFLT = self.ImgDataStack.copy()
        self.N = self.DataStackFLT.sig_count

        self.grid(row=0, column=1, rowspan=2,
                  padx=5, pady=5, sticky=NSEW)

        self.label = Label(self, text="This place is dedicated to results")
        self.label.grid(row=0, column=0, columnspan=2)
        

        self.button_hpass = Button(self, text="High Pass Filter",
                                   command = self.high_pass_flt)
        self.button_hpass.grid(row=1,column=0)

        self.button_plot = Button(self, text="plot",
                                  command=lambda: self.plot(self.create_window()))
        self.button_plot.grid(row=1, column=1)


        self.button_hpass = Button(self, text="Band Pass Filter",
                                   command = self.band_pass_flt)
        self.button_hpass.grid(row=2,column=0)

        self.button_hpass = Button(self, text="plot Spectral peaks",
                                   command = lambda: self.plot_spectr(self.create_window()))
        self.button_hpass.grid(row=3,column=1)

        self.button_hpass = Button(self, text="plot Phase Velocity graph",
                                   command = lambda: self.plot_phvel(self.create_window()))
        self.button_hpass.grid(row=4,column=1)

 
    def update_data(self):
        self.ImgDataStack = self.p.ImgDataStack

        self.DataStackFLT = self.ImgDataStack.copy()
        self.N = self.DataStackFLT.sig_count
        

    def high_pass_flt(self):
        
        my_high = HighPass()
        data_flt = my_high.process_stack(self.DataStackFLT)

        self.DataStackFLT = data_flt

    def band_pass_flt(self):

        my_band = BandPass()
        data_flt = my_band.process_stack(self.DataStackFLT)

        self.DataStackFLT = data_flt
        


    def plot(self, parent):

        fig = Figure()
        fig.suptitle("Filtered signal")

        for i in range(self.N):
            data_obj = self.DataStackFLT[i]

            x = np.arange(data_obj.pcount)
            y = data_obj.data
            
            ax = fig.add_subplot(self.N,1,i+1)

            graph, = ax.plot([],[],'b-')

            graph.set_data(x,y)

            ax.relim()
            ax.autoscale_view(True,True,True)


        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.draw()
        self.widget = self.canvas.get_tk_widget().pack(pady=20)

    def plot_spectr(self, parent):

        band = BandPass()

        fig = Figure()
        fig.suptitle("Welch spectral dencity results and chosen peak")

        for i in range(self.N):
            sig = self.DataStackFLT[i].data
            
            ax = fig.add_subplot(self.N,1,i+1)
            ax.set_xlim(-0.01, 0.5)

            for line in band.plot_welch_peaks(sig):
                ax.add_line(line)
                
            

        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.draw()
        self.widget = self.canvas.get_tk_widget().pack(pady=20)

    def plot_phvel(self, parent):
        # we need to send here time perionds between the samples
        dt = 1 # time periods

        x = np.arange(self.N)*dt
        y = self.DataStackFLT.get_phase_vel()
        

        fig = Figure()
        fig.suptitle("Phase velocity from time")

        ax = fig.add_subplot(1,1,1)
        ax.plot(x,1/np.array(y))

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    

    def create_window(self):
        win = Toplevel(self)
        return win


        



if __name__ == "__main__":
    
    app = GUIapp()
    app.mainloop()
