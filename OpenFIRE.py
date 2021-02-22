""" In OpenFIRE 3.0...devices, entities and element sets can be created simultaneously ( If one have structural
elements before performing the FDS analysis, this program will be generate the files for all three analysis
i.e. fire modelling, HT analysis,  structural analysis """

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
import csv
import os
import subprocess
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style

root = tk.Tk()

root.title("OpenFIRE v3.0")
root.geometry("700x250")

frameInfo = tk.LabelFrame(root, padx=15, pady=10)
frameInfo.grid(row=0, column=0, sticky="nsew")

frame = tk.LabelFrame(root, text="OpenFIRE Modules", padx=15, pady=10)
frame.grid(row=1, column=0, sticky="nsew")

info = tk.Label(frameInfo, text="                  \n"
                                "                 This middleware is a part of the OpenFIRE framework to evaluate\n"
                                "        the structural response to fire. This middleware was developed by Aatif Ali Khan\n"
                                "in The Polytechnic University of Hong Kong.OpenFIRE is an integrated part of 'OpenSEES for fire'.\n\n")

info.grid()
# modules in the OpenFIRE
modules = ["FDS2OpenSEES", "Devices and Elements", "Batch File", "BNDF2OpenSEES", "Run FDS/OpenSEES", "HT_Plots"]
clicked = tk.StringVar()
clicked.set(modules[0])  # use variables as list
drop = tk.OptionMenu(frame, clicked, *modules)
drop.config(width=15)
drop.grid(row=0, column=1, padx=5, pady=5)
module_label = tk.Label(frame, width=30, text="Choose from the available modules", anchor='e').grid(row=0, column=0, padx=5, pady=5)


def createFolder(directory):  # creating folders in the directory
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating Directory.' + directory)

        #############----Making a Scrollbar
        '''This scrollbar is used in some of the modules'''


# noinspection PyUnusedLocal
class VerticalScrolledFrame:

    def __init__(self, master, **kwargs):
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        bg = kwargs.pop('bg', kwargs.pop('background', None))
        self.outer = tk.Frame(master, **kwargs)

        self.vsb = tk.Scrollbar(self.outer, orient=tk.VERTICAL)
        self.vsb.pack(fill=tk.Y, side=tk.RIGHT)
        self.canvas = tk.Canvas(self.outer, highlightthickness=0, width=width, height=height, bg=bg)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vsb.set
        # mouse scroll does not seem to work with just "bind"; You have
        # to use "bind_all". Therefore to use multiple windows you have
        # to bind_all in the current widget
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vsb['command'] = self.canvas.yview

        self.inner = tk.Frame(self.canvas, bg=bg)
        # pack the inner Frame into the Canvas with the top left corner 4 pixels offset
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(tk.Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion=(0, 0, x2, max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

        ###################################################################


j = 1  # increment recorder for AST devices in "Creating Device Module "
k = 1  # increment recorder for HF devices
l = 1  # increment recorder for HTC devices
j1 = 1  # increment recorder for OpenSEES Entity number
j2 = 1  # increment recorder for OpenSEES Mesh tags (with entity tag)
j3 = 1  # increment recorder for OpenSEES NodeSet Number
j4 = 1  # increment recorder for OpenSEES Fire Model Number
j5 = 1  # increment recorder for OpenSEES HTPattern number
j6 = 1  # increment recorder for OpenSEES Output Recorder number
ent = 1  # increment for numbering of Longitudinal beam
ent2 = 1  # increment for numbering of Transverse beam
ent3 = 1  # increment for numbering of Columns
ent4 = 1  # increment for numbering of Slabs
entLT = 1  # increment for longitudinal truss
entTT = 1  # increment for transverse truss
iPLT = 1  # counter for plotting HT data
modules = []  # list of the files for plotting
filenamePLT = []
ELEMENT_SET = 'elementset.txt'
ELEMENT_SET2 = 'elementset2.txt'
'''The main output for the OpenFIRE is written below, it contains all the modules'''


# noinspection PyGlobalUndefined
def mainOutput():  # it allows the user to proceed the chooses module
    def location():  # asking directory location, this function is used by all modules to find the working directory
        get = filedialog.askdirectory()
        os.chdir(get)

    if clicked.get() == "FDS2OpenSEES":                                ########################-----First Module
        window1 = tk.Tk()  # window for this module
        window1.title("FDS2OpenSEES")
        window1.geometry("500x400")

        frame1 = tk.LabelFrame(window1, text="Creation of Boundary Condition", padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky="nsew")

        tk.Button(frame1, text="Directory", command=location, width=15, height=1).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(frame1, width=20, text="Get Working Directory", anchor='e').grid(row=0, column=0, padx=5, pady=5)

        data = ["AST", "AST_HTC", "HF", "HF_HTC"]   # Thermal boundary condition type required by OpenSEES
        clicked2 = tk.StringVar()
        clicked2.set(data[0])  # use variables as list
        dropD = tk.OptionMenu(frame1, clicked2, *data)
        dropD.config(width=12)
        dropD.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame1, width=20, text="Boundary Condition", anchor='e').grid(row=1, column=0, padx=5, pady=5)

        # noinspection PyGlobalUndefined
        def openfile():    # function to open the FDS output file (DEVC file)
            global filename
            filename = filedialog.askopenfilename(title="Select a file", filetypes=(('All files', '*.*'),
                                                                                    ('Text Files', ('*.txt', '*.csv'))))

        tk.Button(frame1, text="Browse File", command=openfile, width=15, height=1).grid(row=2, column=1, padx=10, pady=10)
        tk.Label(frame1, width=20, text="Browse FDS Output File", anchor='e').grid(row=2, column=0, padx=5, pady=5)

        num = tk.Entry(frame1, width=15)
        num.grid(row=5, column=1, padx=5, pady=5)
        tk.Label(frame1, width=20, text="Number of Devices", anchor='e').grid(row=5, column=0, padx=5, pady=5)

        # noinspection PyGlobalUndefined
        def fdsFile():
            global filename3
            filename3 = 'Devices.csv'
            with open(filename) as f:
                with open(filename3, 'w') as f1:
                    next(f)  # skip header line
                    next(f)
                    for line in f:
                        f1.write(line)

        # below button will update the FDS file, it will remove the header lines from the output also keep open the file
        tk.Button(frame1, text="Update File", command=fdsFile, width=15).grid(row=4, column=1, padx=5, pady=5)
        tk.Label(frame1, width=20, text="Reformat FDS File", anchor='e').grid(row=4, column=0, padx=5, pady=5)

        # noinspection PyShadowingNames
        def bcfile(bcOption, counter):  # this function generate the files for each boundary condition
            while counter <= int(num.get()):
                with open(filename3) as f:
                    data1 = open("{0}/{0}{1}.dat".format(bcOption, counter), "w", newline='')
                    reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
                    w = csv.writer(data1, delimiter=' ')
                    if clicked2.get() == "AST":
                        for row in reader:
                            my_row = [row[0], row[counter]]
                            w.writerow(my_row)

                    if clicked2.get() == "HF":
                        for row in reader:
                            hf = int(num.get()) + counter
                            my_row = [row[0], row[hf] * 1000]
                            w.writerow(my_row)

                    if clicked2.get() == "AST_HTC":
                        for row in reader:
                            htc = 2 * int(num.get()) + counter
                            my_row = [row[0], row[counter], row[htc]]
                            w.writerow(my_row)

                    if clicked2.get() == "HF_HTC":
                        for row in reader:
                            htc = 2 * int(num.get()) + counter
                            hf = int(num.get()) + counter
                            my_row = [row[0], row[hf] * 1000, row[htc]]
                            w.writerow(my_row)

                    data1.close()
                counter += 1

        def output():  # this is the main function for providing the output based on the user requirement
            iDev = 1   # counter for devices
            if clicked2.get() == "AST":
                createFolder("./AST")
                bcfile("AST", iDev)

            if clicked2.get() == "HF":
                createFolder("./HF")
                bcfile("HF", iDev)

            if clicked2.get() == "AST_HTC":
                createFolder("./AST_HTC")
                bcfile("AST_HTC", iDev)

            if clicked2.get() == "HF_HTC":
                createFolder("./HF_HTC")
                bcfile("HF_HTC", iDev)

        tk.Button(frame1, text="Save File", command=output, width=15, height=1).grid(row=6, column=1, padx=5, pady=5)

    #################################################-------Second Module (Creating Devices)----- #############

    if clicked.get() == "Devices and Elements":
        global jEle
        global iEle
        windowX2 = tk.Tk()
        windowX2.title("Devices, Entities & Element Sets")
        windowX2.geometry("1500x800")
        window2 = VerticalScrolledFrame(windowX2, width=100, borderwidth=2, relief=tk.SUNKEN, background="light gray")
        window2.pack(fill=tk.BOTH, expand=True)
        # this is a frame for the entries of files and options for the user to chose the devices
        frame1 = tk.LabelFrame(window2, text="FDS Inputs", padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky="nsew")


        # button and label for location of the directory
        tk.Button(frame1, text="Directory", command=location, width=25, height=1).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(frame1, width=20, text="Get Working Directory", anchor='e').grid(row=0, column=0, padx=5, pady=5)

        data = ["ADIABATIC SURFACE TEMPERATURE", "HEAT FLUX", "HEAT TRANSFER COEFFICIENT"]  # devices to be added in FDS
        clicked3 = tk.StringVar()
        clicked3.set(data[0])  # use variables as list
        dropList = tk.OptionMenu(frame1, clicked3, *data)
        dropList.config(width=25)
        dropList.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(frame1, width=20, text="Data to Extract", anchor='e').grid(row=3, column=0, padx=5, pady=5)

        # structural components
        strCom = ["Columns", "Longitudinal Beams", "Transverse Beam", "Slabs", "Longitudinal Truss", "Transverse Truss"]
        clicked4 = tk.StringVar()
        clicked4.set(strCom[0])  # use variables as list
        drop2 = tk.OptionMenu(frame1, clicked4, *strCom)
        drop2.config(width=25)
        drop2.grid(row=4, column=1, padx=5, pady=5)
        tk.Label(frame1, width=20, text="Structural Components", anchor='e').grid(row=4, column=0, padx=5, pady=5)

        choose1 = tk.StringVar()
        choose1.set("Yes")
        option = tk.OptionMenu(frame1, choose1, "Yes", "No")
        option.config(width=25)
        option.grid(row=5, column=1, padx=5, pady=5)
        tk.Label(frame1, width=20, text="Devices to be installed", anchor='e').grid(row=5, column=0, padx=5, pady=5)

        # this is a frame for the entries for OpenSEES
        frameO = tk.LabelFrame(window2, text="OpenSEES Inputs", padx=5, pady=5)
        frameO.grid(row=0, column=2, sticky="nsew")

        makeOpenSEES = tk.StringVar()  # to chose if entities to be created
        makeOpenSEES.set("Yes")
        option1 = tk.OptionMenu(frameO, makeOpenSEES, "Yes", "No")
        option1.config(width=10)
        option1.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frameO, width=20, text="Creating Entities", anchor='e').grid(row=1, column=0, padx=5, pady=5)

        htConst = tk.Entry(frameO, width=15)
        htConst.grid(row=3, column=1)
        htConst.insert(tk.END, "1")
        tk.Label(frameO, width=20, text="Tag for HT Constants", anchor='e').grid(row=3, column=0)

        matT = tk.Entry(frameO, width=15)
        matT.grid(row=3, column=3)
        matT.insert(tk.END, "1")
        tk.Label(frameO, width=20, text="Material Tag", anchor='e').grid(row=3, column=2)

        pChange = tk.Entry(frameO, width=15)
        pChange.grid(row=4, column=1)
        pChange.insert(tk.END, "0")
        tk.Label(frameO, width=20, text="Phase Change", anchor='e').grid(row=4, column=0)

        fNodeset = tk.Entry(frameO, width=15)
        fNodeset.grid(row=4, column=3)
        fNodeset.insert(tk.END, "1 4 5")
        tk.Label(frameO, width=20, text="Faces for Node Sets", anchor='e').grid(row=4, column=2)

        fModel = tk.Entry(frameO, width=15)
        fModel.grid(row=5, column=1)
        fModel.insert(tk.END, "1")
        tk.Label(frameO, width=20, text="Fire Model Type", anchor='e').grid(row=5, column=0)

        fMBfile = tk.Entry(frameO, width=15)
        fMBfile.grid(row=5, column=3)
        fMBfile.insert(tk.END, "AST")
        tk.Label(frameO, width=20, text="Input Boundary File", anchor='e').grid(row=5, column=2)

        hffaces = tk.Entry(frameO, width=15)
        hffaces.grid(row=6, column=1)
        hffaces.insert(tk.END, "1 4 5 6 7 8 9")
        tk.Label(frameO, width=20, text="Faces for Heat Flux", anchor='e').grid(row=6, column=0)

        #####################################------Columns------##########################################

        frame2 = tk.LabelFrame(window2, text="Columns Inputs", padx=5, pady=5)
        frame2.grid(row=1, column=0, sticky="nsew")

        x = tk.Entry(frame2, width=15)
        x.grid(row=0, column=1)
        x.insert(tk.END, "1")
        tk.Label(frame2, width=15, text="Value of X", anchor='e').grid(row=0, column=0)

        y = tk.Entry(frame2, width=15)
        y.grid(row=0, column=3)
        y.insert(tk.END, "1")
        tk.Label(frame2, width=15, text="Value of Y", anchor='e').grid(row=0, column=2)

        z = tk.Entry(frame2, width=15)
        z.insert(tk.END, "0")
        z.grid(row=1, column=1)
        tk.Label(frame2, width=15, text="Initial Value of Z", anchor='e').grid(row=1, column=0)

        z_max = tk.Entry(frame2, width=15)
        z_max.grid(row=1, column=3)
        z_max.insert(tk.END, "4")
        tk.Label(frame2, width=15, text="Height of Columns", anchor='e').grid(row=1, column=2)

        e = tk.Entry(frame2, width=15)
        e.grid(row=2, column=1)
        e.insert(tk.END, "1")
        tk.Label(frame2, width=15, text="Increment", anchor='e').grid(row=2, column=0)

        ior = tk.Entry(frame2, width=15)
        ior.grid(row=2, column=3)
        ior.insert(tk.END, "-1")
        tk.Label(frame2, width=15, text="Orientation", anchor='e').grid(row=2, column=2)

        #####################################------Longitudinal Beams------##########################################

        frame3 = tk.LabelFrame(window2, text="Longitudinal Beam Inputs", padx=5, pady=5)
        frame3.grid(row=2, column=0, sticky="nsew")

        y2 = tk.Entry(frame3, width=15)
        y2.grid(row=0, column=1)
        y2.insert(tk.END, "1")
        tk.Label(frame3, width=15, text="Value of Y", anchor='e').grid(row=0, column=0)

        z2 = tk.Entry(frame3, width=15)
        z2.grid(row=0, column=3)
        z2.insert(tk.END, "1")
        tk.Label(frame3, width=15, text="Value of Z", anchor='e').grid(row=0, column=2)

        initialX = tk.DoubleVar()
        x_int = tk.Entry(frame3, width=15, textvariable=initialX)
        x_int.grid(row=1, column=1)
        x_int.insert(tk.END, "1")
        tk.Label(frame3, width=15, text="Initial Value of X", anchor='e').grid(row=1, column=0)

        x_max = tk.Entry(frame3, width=15)
        x_max.grid(row=1, column=3)
        x_max.insert(tk.END, "5")
        tk.Label(frame3, width=15, text="Length of Beam", anchor='e').grid(row=1, column=2)

        e1 = tk.Entry(frame3, width=15)
        e1.grid(row=2, column=1)
        e1.insert(tk.END, "1")
        tk.Label(frame3, width=15, text="Increment", anchor='e').grid(row=2, column=0)

        ior1 = tk.Entry(frame3, width=15)
        ior1.grid(row=2, column=3)
        ior.insert(tk.END, "1")
        tk.Label(frame3, width=15, text="Orientation", anchor='e').grid(row=2, column=2)

        #####################################------Transverse Beams------##########################################

        frame4 = tk.LabelFrame(window2, text="Transverse Beams Inputs", padx=5, pady=5)
        frame4.grid(row=3, column=0, sticky="nsew")

        x2 = tk.Entry(frame4, width=15)
        x2.grid(row=0, column=1)
        x2.insert(tk.END, "1")
        tk.Label(frame4, width=15, text="Value of X", anchor='e').grid(row=0, column=0)

        z3 = tk.Entry(frame4, width=15)
        z3.grid(row=0, column=3)
        z3.insert(tk.END, "1")
        tk.Label(frame4, width=15, text="Value of Z", anchor='e').grid(row=0, column=2)

        y_int = tk.Entry(frame4, width=15)
        y_int.grid(row=1, column=1)
        y_int.insert(tk.END, "1")
        tk.Label(frame4, width=15, text="Initial Value of Y", anchor='e').grid(row=1, column=0)

        y_max = tk.Entry(frame4, width=15)
        y_max.grid(row=1, column=3)
        y_max.insert(tk.END, "4")
        tk.Label(frame4, width=15, text="Length of Beam", anchor='e').grid(row=1, column=2)

        e2 = tk.Entry(frame4, width=15)
        e2.grid(row=2, column=1)
        e2.insert(tk.END, "1")
        tk.Label(frame4, width=15, text="Increment", anchor='e').grid(row=2, column=0)

        ior2 = tk.Entry(frame4, width=15)
        ior2.grid(row=2, column=3)
        ior2.insert(tk.END, "1")
        tk.Label(frame4, width=15, text="Orientation", anchor='e').grid(row=2, column=2)

        #####################################------Longitudinal Trusses------##########################################
        frameT1 = tk.LabelFrame(window2, text="Longitudinal Truss", padx=5, pady=5)
        frameT1.grid(row=4, column=0, sticky="nsew")

        xLT = tk.Entry(frameT1, width=15)
        xLT.grid(row=0, column=1)
        xLT.insert(tk.END, "0")
        tk.Label(frameT1, width=15, text="Value of X", anchor='e').grid(row=0, column=0)

        yLT = tk.Entry(frameT1, width=15)
        yLT.grid(row=0, column=3)
        yLT.insert(tk.END, "0")
        tk.Label(frameT1, width=15, text="Value of Y", anchor='e').grid(row=0, column=2)

        lLimit = tk.Entry(frameT1, width=15)
        lLimit.grid(row=1, column=1)
        lLimit.insert(tk.END, "0")
        tk.Label(frameT1, width=15, text="Lower Height", anchor='e').grid(row=1, column=0)

        uLimit = tk.Entry(frameT1, width=15)
        uLimit.grid(row=1, column=3)
        uLimit.insert(tk.END, ".5")
        tk.Label(frameT1, width=15, text="Upper Height", anchor='e').grid(row=1, column=2)

        incXT = tk.Entry(frameT1, width=15)
        incXT.grid(row=2, column=1)
        incXT.insert(tk.END, "1")
        tk.Label(frameT1, width=15, text="Increment in X", anchor='e').grid(row=2, column=0)

        lenTruss = tk.Entry(frameT1, width=15)
        lenTruss.grid(row=2, column=3)
        lenTruss.insert(tk.END, "5")
        tk.Label(frameT1, width=15, text="Length of Truss", anchor='e').grid(row=2, column=2)

        iorLT = tk.Entry(frameT1, width=15)
        iorLT.grid(row=3, column=1)
        iorLT.insert(tk.END, "-3")
        tk.Label(frameT1, width=15, text="Orientation", anchor='e').grid(row=3, column=0)

        #####################################------Transverse Trusses------##########################################

        frameT2 = tk.LabelFrame(window2, text="Transverse Truss", padx=5, pady=5)
        frameT2.grid(row=5, column=0, sticky="nsew")

        xTT = tk.Entry(frameT2, width=15)
        xTT.grid(row=0, column=1)
        xTT.insert(tk.END, "0")
        tk.Label(frameT2, width=15, text="Value of X", anchor='e').grid(row=0, column=0)

        yTT = tk.Entry(frameT2, width=15)
        yTT.grid(row=0, column=3)
        yTT.insert(tk.END, "0")
        tk.Label(frameT2, width=15, text="Value of Y", anchor='e').grid(row=0, column=2)

        lLimitTT = tk.Entry(frameT2, width=15)
        lLimitTT.grid(row=1, column=1)
        lLimitTT.insert(tk.END, "0")
        tk.Label(frameT2, width=15, text="Lower Height", anchor='e').grid(row=1, column=0)

        uLimitTT = tk.Entry(frameT2, width=15)
        uLimitTT.grid(row=1, column=3)
        uLimitTT.insert(tk.END, ".5")
        tk.Label(frameT2, width=15, text="Upper Height", anchor='e').grid(row=1, column=2)

        incYT = tk.Entry(frameT2, width=15)
        incYT.grid(row=2, column=1)
        incYT.insert(tk.END, "1")
        tk.Label(frameT2, width=15, text="Increment in Y", anchor='e').grid(row=2, column=0)

        lenTrussT = tk.Entry(frameT2, width=15)
        lenTrussT.grid(row=2, column=3)
        lenTrussT.insert(tk.END, "5")
        tk.Label(frameT2, width=15, text="Length of Truss", anchor='e').grid(row=2, column=2)

        iorTT = tk.Entry(frameT2, width=15)
        iorTT.grid(row=3, column=1)
        iorTT.insert(tk.END, "-3")
        tk.Label(frameT2, width=15, text="Orientation", anchor='e').grid(row=3, column=0)

        #####################################------Slabs------##########################################

        frame5 = tk.LabelFrame(window2, text="Slabs Inputs", padx=5, pady=5)
        frame5.grid(row=6, column=0, sticky="nsew")

        y3 = tk.Entry(frame5, width=15)
        y3.grid(row=0, column=1)
        y3.insert(tk.END, "1")
        tk.Label(frame5, width=15, text="Value of Y", anchor='e').grid(row=0, column=0)

        z4 = tk.Entry(frame5, width=15)
        z4.grid(row=0, column=3)
        z4.insert(tk.END, "1")
        tk.Label(frame5, width=15, text="Value of Z", anchor='e').grid(row=0, column=2)

        x1_int = tk.Entry(frame5, width=15)
        x1_int.grid(row=1, column=1)
        x1_int.insert(tk.END, "1")
        tk.Label(frame5, width=15, text="Initial Value of X", anchor='e').grid(row=1, column=0)

        x1_max = tk.Entry(frame5, width=15)
        x1_max.grid(row=1, column=3)
        x1_max.insert(tk.END, "4")
        tk.Label(frame5, width=15, text="Length Along the Slab", anchor='e').grid(row=1, column=2)

        e3 = tk.Entry(frame5, width=15)
        e3.grid(row=2, column=1)
        e3.insert(tk.END, "1")
        tk.Label(frame5, width=15, text="Increment", anchor='e').grid(row=2, column=0)

        ior3 = tk.Entry(frame5, width=15)
        ior3.grid(row=2, column=3)
        ior3.insert(tk.END, "-3")
        tk.Label(frame5, width=15, text="Orientation", anchor='e').grid(row=2, column=2)

        yIncrement = tk.Entry(frame5, width=15)
        yIncrement.grid(row=3, column=1)
        yIncrement.insert(tk.END, "1")
        tk.Label(frame5, width=15, text="Increment in Y", anchor='e').grid(row=3, column=0)

        widthSLB = tk.Entry(frame5, width=15)
        widthSLB.grid(row=3, column=3)
        widthSLB.insert(tk.END, "5")
        tk.Label(frame5, width=15, text="Total Width of Slab", anchor='e').grid(row=3, column=2)

        ################################################################################################
        # noinspection PyGlobalUndefined
        fdsFile = 'fds.txt'   # this is FDS file it is saved in the working directory
        osFile = 'OpenSees.txt'  # this is OpenSEES File
        '''Here it begins the main output function of the Creating Device modules'''

        def fdsFileMaker(begin, final, increment, Bfile, Quantity, Cord1, Cord2, IOR):
            global j
            if clicked4.get() == "Columns":
                while begin < final:
                    with open(fdsFile, 'a') as f1:
                        f1.writelines("\n&DEVC ID = '{1}{0}', QUANTITY={2}, XYZ={3},{4},{5}, "
                                      "IOR={6}/".format(j, Bfile, Quantity, Cord1, Cord2, begin, IOR))
                    j += 1
                    begin += increment

            if clicked4.get() == "Longitudinal Beams":
                while begin < final:
                    with open(fdsFile, 'a') as f1:
                        f1.writelines("\n&DEVC ID = '{1}{0}', QUANTITY={2}, XYZ={3},{4},{5}, "
                                      "IOR={6}/".format(j, Bfile, Quantity, begin, Cord1, Cord2, IOR))
                    j += 1
                    begin += increment

            if clicked4.get() == "Transverse Beam":
                while begin < final:
                    with open(fdsFile, 'a') as f1:
                        f1.writelines("\n&DEVC ID = '{1}{0}', QUANTITY={2}, XYZ={3},{4},{5}, "
                                      "IOR={6}/".format(j, Bfile, Quantity, Cord1, begin, Cord2, IOR))
                    j += 1
                    begin += increment

            if clicked4.get() == "Slabs":
                while begin < final:
                    with open(fdsFile, 'a') as f1:
                        f1.writelines("\n&DEVC ID = '{1}{0}', QUANTITY={2}, XYZ={3},{4},{5}, "
                                      "IOR={6}/".format(j, Bfile, Quantity, begin, Cord1, Cord2, IOR))
                    j += 1
                    begin += increment

            if clicked4.get() == "Longitudinal Truss":
                while begin < final:
                    with open(fdsFile, 'a') as f1:
                        f1.writelines("\n&DEVC ID = '{1}{0}', QUANTITY={2}, XYZ={3},{4},{5}, "
                                      "IOR={6}/".format(j, Bfile, Quantity, begin, Cord1, Cord2, IOR))
                    j += 1
                    begin += increment

            if clicked4.get() == "Transverse Truss":
                while begin < final:
                    with open(fdsFile, 'a') as f1:
                        f1.writelines("\n&DEVC ID = '{1}{0}', QUANTITY={2}, XYZ={3},{4},{5}, "
                                      "IOR={6}/".format(j, Bfile, Quantity, Cord1, begin, Cord2, IOR))
                    j += 1
                    begin += increment

        #####################----Functions, frames and Entries for Element Sets

        frame8 = tk.LabelFrame(window2, text="Element Sets", padx=5, pady=5)
        frame8.grid(row=3, column=2, sticky="nsew")

        elementSetGen = tk.StringVar()
        elementSetGen.set("Yes")
        optionES = tk.OptionMenu(frame8, elementSetGen, "Yes", "No")
        optionES.config(width=10)
        optionES.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame8, width=16, text="Element Set Generation", anchor='e').grid(row=0, column=0, padx=5, pady=5)

        # noinspection PyGlobalUndefined
        def openNodesFile():  # opening the FDS file before using it to write
            global fb
            fb = filedialog.askopenfilename(title="select a file", filetypes=(('All files', '*.*'),
                                                                              ('Text Files', ('*.txt', '*.dat'))))

        tk.Button(frame8, text="Browse Nodes File", command=openNodesFile, width=15, height=1).grid(row=1, column=1)
        tk.Label(frame8, width=16, text="Open Nodes File", anchor='e').grid(row=1, column=0, padx=5, pady=5)

        def openElementFile():  # opening the FDS file before using it to write
            # noinspection PyGlobalUndefined
            global fbE
            fbE = filedialog.askopenfilename(
                title="select a file", filetypes=(('All files', '*.*'), ('Text Files', ('*.txt', '*.csv', '*.dat'))))

        tk.Button(frame8, text="BC Element File", command=openElementFile, width=15, height=1).grid(row=2, column=1)
        tk.Label(frame8, width=16, text="Open BC Element File", anchor='e').grid(row=2, column=0, padx=5, pady=5)

        ################## frame for Shell Element files

        # noinspection PyGlobalUndefined
        def openShellElementFile():  # opening SHELL file before using it to write
            global fbSE
            fbSE = filedialog.askopenfilename(
                title="select a file", filetypes=(('All files', '*.*'), ('Text Files', ('*.txt', '*.csv', '*.dat'))))

        tk.Button(frame8, text="Browse Element File", command=openShellElementFile, width=15, height=1).grid(row=3, column=1)
        tk.Label(frame8, width=16, text="Shell Element File", anchor='e').grid(row=3, column=0, padx=5, pady=5)

        def nodes1():   # this method is when member is in Z direction and X is fixed and Y is in range
            matchingNodes = [key for key, (X, Y, Z) in newDict.items()
                             if (X == float(x.get())) and (Y == float(y.get())) and (lowerL <= Z <= upperL)]
            return matchingNodes

        def nodes3():  # this method is when member is in Y direction and Z is fixed and X is in range
            matchingNodes = [key for key, (X, Y, Z) in newDict.items()
                             if (X == float(x2.get()) and lowerLBT <= Y <= upperLBT and Z == float(z3.get()))]
            return matchingNodes

        def nodes4():   # this method is when member is in X direction and Z is fixed and Y is in range
            matchingNodes = [key for key, (X, Y, Z) in newDict.items()
                             if (lowerLB <= X <= upperLB and (Y == float(y2.get())) and Z == float(z2.get()))]
            return matchingNodes

        def nodes5():  # this method is used when X is member direction and Z is vertical component (Longitudinal Truss)
            matchingNodes = [key for key, (X, Y, Z) in newDict.items()
                             if (trussEleL <= X <= trussEleU and Y == float(yLT.get()) and
                                 float(lLimit.get()) <= Z <= float(uLimit.get()))]
            return matchingNodes

        def nodes6():  # this method is used when Y is member direction Transverse Truss
            matchingNodes = [key for key, (X, Y, Z) in newDict.items()
                             if (X == float(xTT.get())) and trussTEleL <= Y <= trussTEleU and
                             float(lLimit.get()) <= Z <= float(uLimit.get())]
            return matchingNodes

        def nodes7():  # this method is when member is in Y direction and Z is fixed and X is in range
            matchingNodes = [key for key, (X, Y, Z) in newDict.items()
                             if lowerSLL <= X <= upperSLL and lowerSLW <= Y <= upperSLW and
                             Z == float(z4.get())]
            return matchingNodes

        iEle = 1   # counter for the BC elements
        jEle = 1   # counter for shell elements, so used for slabs in OpenSEES

        # noinspection PyGlobalUndefined
        def nodesDict():  # creating dictionaries and nodes files
            global fb
            createFolder('./ElementFiles')
            NODES_OUTPUT = 'ElementFiles/Nodes.csv'        # writing to make an CSV file
            NODES_OUTPUT2 = 'ElementFiles/Nodes2.csv'      # writing new files by Removing blank lines
            with open(fb) as f1:
                stripped = (line.strip() for line in f1)
                lines = (line.replace("\t", ",").split() for line in stripped if line)
                csv.reader(f1, delimiter=',')
                with open(NODES_OUTPUT, 'w', newline='') as out_file:
                    writer = csv.writer(out_file, quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerows(lines)

            fn = open(NODES_OUTPUT2, 'w', newline='')
            df = pd.read_csv(NODES_OUTPUT)
            first_column = df.columns[0]
            df = df.drop([first_column], axis=1)
            df.to_csv(fn, index=False)
            fn.close()

            def read_lines():
                with open(NODES_OUTPUT2) as file:
                    reader = csv.reader(file)
                    for row in reader:
                        yield [float(jItem) for jItem in row]

            allLines = list(read_lines())
            finalDict = {nodes[0]: nodes[1:] for nodes in allLines}
            # convert key (node) as an integer and rounding all values to significant figures using ROUND (round) command
            global newDict
            newDict = {int(kDict): (round(X, 3), round(Y, 3), round(Z, 3)) for kDict, (X, Y, Z) in finalDict.items()}

        d1_button = tk.Button(frame8, text="Nodes Creation", command=nodesDict, width=15, height=1)
        d1_button.grid(row=1, column=3, padx=10, pady=10)
        tk.Label(frame8, width=15, text="Generate Nodes File", anchor='e').grid(row=1, column=2, padx=5, pady=5)

        # noinspection PyGlobalUndefined
        def bcElementDict():
            global fbE
            createFolder('./ElementFiles')
            ELEMENT_OUTPUT = 'ElementFiles/Element.csv'
            ELEMENT_OUTPUT2 = 'ElementFiles/Element2.csv'
            with open(fbE) as elementFile:
                strippedEle = (ele.strip() for ele in elementFile)
                elements = (ele.replace("\t", ",").split() for ele in strippedEle if ele)  # be noted that elimination is tab here
                csv.reader(elementFile, delimiter=',')
                with open(ELEMENT_OUTPUT, 'w', newline='') as outFile:
                    writer = csv.writer(outFile, quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerows(elements)

            df1 = pd.read_csv(ELEMENT_OUTPUT)
            c1 = df1.columns[0]
            c2 = df1.columns[1]
            c6 = df1.columns[5]
            c7 = df1.columns[6]
            c8 = df1.columns[7]
            c9 = df1.columns[8]
            c10 = df1.columns[9]

            fn2 = open(ELEMENT_OUTPUT2, 'w', newline='')
            df1 = df1.drop([c1, c2, c6, c7, c8, c9, c10], axis=1)
            df1.to_csv(fn2, index=False)
            fn2.close()

            def read_lines2():
                with open(ELEMENT_OUTPUT2) as file2:
                    reader2 = csv.reader(file2)
                    for row3 in reader2:
                        yield [int(kEleSet) for kEleSet in row3]

            elementSet = list(read_lines2())
            global elementDict
            # making elements as dictionary where elements are keys and corresponding nodes are values
            elementDict = {elekey[0]: elekey[1:] for elekey in elementSet}

        tk.Button(frame8, text="BC Elements ", command=bcElementDict, width=15, height=1).grid(row=2, column=3)
        tk.Label(frame8, width=15, text="BC Element File", anchor='e').grid(row=2, column=2, padx=5, pady=5)

        def shellElementDict():
            # noinspection PyGlobalUndefined
            global fbSE
            createFolder('./ElementFiles')
            SHELL_ELEMENT_OUTPUT = '/ElementFiles/Element3.csv'
            SHELL_ELEMENT_OUTPUT2 = '/ElementFiles/Element4.csv'
            with open(fbSE) as elementFile:
                strippedEle = (ele.strip() for ele in elementFile)
                elements = (ele.replace("\t", ",").split() for ele in strippedEle if ele)  # be noted that elimination is space here
                csv.reader(elementFile, delimiter=',')
                with open(SHELL_ELEMENT_OUTPUT, 'w', newline='') as outFile:
                    writer = csv.writer(outFile, quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerows(elements)

            dfE1 = pd.read_csv(SHELL_ELEMENT_OUTPUT)
            cS1 = dfE1.columns[0]
            cS2 = dfE1.columns[1]
            cS3 = dfE1.columns[7]

            fnSE = open(SHELL_ELEMENT_OUTPUT2, 'w', newline='')
            dfE1 = dfE1.drop([cS1, cS2, cS3], axis=1)
            dfE1.to_csv(fnSE, index=False)
            fnSE.close()

            def read_lines2():
                with open(SHELL_ELEMENT_OUTPUT2) as file3:
                    reader2 = csv.reader(file3)
                    for row3 in reader2:
                        yield [int(jSE) for jSE in row3]

            elementSet2 = list(read_lines2())
            # noinspection PyGlobalUndefined
            global elementDict2
            elementDict2 = {elekey[0]: elekey[1:] for elekey in elementSet2}

        tk.Button(frame8, text="Shell Element File", command=shellElementDict, width=15, height=1).grid(row=3, column=3)
        tk.Label(frame8, width=15, text="Create Shell Elements", anchor='e').grid(row=3, column=2, padx=5, pady=5)

        # noinspection PyGlobalUndefined,PyShadowingNames
        def output2():  # functions for Columns
            global location, iEntity, mesh, nodeSET, fireModel, heatFlux, htRecorder, meshBLK, blockEntity, iEle, jEle
            if clicked3.get() == "ADIABATIC SURFACE TEMPERATURE":
                if clicked4.get() == "Columns":
                    i = float(z.get())
                    m = float(z_max.get())
                    var = float(e.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i, m, var, 'AST', "'{0}'".format(clicked3.get()), float(x.get()), float(y.get()), ior.get())

                if clicked4.get() == "Longitudinal Beams":
                    i1 = float(x_int.get())
                    m1 = float(x_max.get())
                    var2 = float(e1.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i1, m1, var2, 'AST', "'{0}'".format(clicked3.get()), float(y2.get()), float(z2.get()), ior1.get())

                if clicked4.get() == "Transverse Beam":
                    i2 = float(y_int.get())
                    m2 = float(y_max.get())
                    var3 = float(e2.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i2, m2, var3, 'AST', "'{0}'".format(clicked3.get()), float(x2.get()), float(z3.get()), ior2.get())

                if clicked4.get() == "Longitudinal Truss":
                    iLT = float(xLT.get())
                    mLT = float(lenTruss.get())
                    varLT = float(incXT.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(iLT, mLT, varLT, 'AST', "'{0}'".format(clicked3.get()), float(yLT.get()), float(uLimit.get()),
                                     iorLT.get())

                if clicked4.get() == "Transverse Truss":
                    iTT = float(yLT.get())
                    mTT = float(lenTrussT.get())
                    varTT = float(incYT.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(iTT, mTT, varTT, 'AST', "'{0}'".format(clicked3.get()), float(xTT.get()), float(uLimitTT.get()),
                                     iorTT.get())

                if clicked4.get() == "Slabs":
                    yI = float(y3.get())
                    wI = float(yIncrement.get())
                    widSLB = float(widthSLB.get())
                    while yI < widSLB:
                        i3 = float(x1_int.get())
                        m3 = float(x1_max.get())
                        var4 = float(e3.get())
                        if choose1.get() == "Yes":
                            fdsFileMaker(i3, m3, var4, 'AST', "'{0}'".format(clicked3.get()), yI, float(z4.get()), ior3.get())
                        yI += wI

            if clicked3.get() == "HEAT FLUX":
                if clicked4.get() == "Columns":
                    i = float(z.get())
                    m = float(z_max.get())
                    var = float(e.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i, m, var, 'HF', "'{0}'".format(clicked3.get()), float(x.get()), float(y.get()), ior.get())

                if clicked4.get() == "Longitudinal Beams":
                    i1 = float(x_int.get())
                    m1 = float(x_max.get())
                    var2 = float(e1.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i1, m1, var2, 'HF', "'{0}'".format(clicked3.get()), float(y2.get()), float(z2.get()), ior1.get())

                if clicked4.get() == "Transverse Beam":
                    i2 = float(y_int.get())
                    m2 = float(y_max.get())
                    var3 = float(e2.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i2, m2, var3, 'HF', "'{0}'".format(clicked3.get()), float(x2.get()), float(z3.get()), ior2.get())

                if clicked4.get() == "Longitudinal Truss":
                    iLT = float(xLT.get())
                    mLT = float(lenTruss.get())
                    varLT = float(incXT.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(iLT, mLT, varLT, 'HF', "'{0}'".format(clicked3.get()), float(yLT.get()), float(uLimit.get()),
                                     iorLT.get())

                if clicked4.get() == "Transverse Truss":
                    iTT = float(yLT.get())
                    mTT = float(lenTrussT.get())
                    varTT = float(incYT.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(iTT, mTT, varTT, 'HF', "'{0}'".format(clicked3.get()), float(xTT.get()), float(uLimitTT.get()),
                                     iorTT.get())

                if clicked4.get() == "Slabs":
                    yI = float(y3.get())
                    wI = float(yIncrement.get())
                    widSLB = float(widthSLB.get())
                    while yI < widSLB:
                        i3 = float(x1_int.get())
                        m3 = float(x1_max.get())
                        var4 = float(e3.get())
                        if choose1.get() == "Yes":
                            fdsFileMaker(i3, m3, var4, 'HF', "'{0}'".format(clicked3.get()), yI, float(z4.get()), ior3.get())
                        yI += wI

            if clicked3.get() == "HEAT TRANSFER COEFFICIENT":
                if clicked4.get() == "Columns":
                    i = float(z.get())
                    m = float(z_max.get())
                    var = float(e.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i, m, var, 'HTC', "'{0}'".format(clicked3.get()), float(x.get()), float(y.get()), ior.get())

                if clicked4.get() == "Longitudinal Beams":
                    i1 = float(x_int.get())
                    m1 = float(x_max.get())
                    var2 = float(e1.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i1, m1, var2, 'HTC', "'{0}'".format(clicked3.get()), float(y2.get()), float(z2.get()), ior1.get())

                if clicked4.get() == "Transverse Beam":
                    i2 = float(y_int.get())
                    m2 = float(y_max.get())
                    var3 = float(e2.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(i2, m2, var3, 'HTC', "'{0}'".format(clicked3.get()), float(x2.get()), float(z3.get()), ior2.get())

                if clicked4.get() == "Longitudinal Truss":
                    iLT = float(xLT.get())
                    mLT = float(lenTruss.get())
                    varLT = float(incXT.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(iLT, mLT, varLT, 'HTC', "'{0}'".format(clicked3.get()), float(yLT.get()), float(uLimit.get()), iorLT.get())

                if clicked4.get() == "Transverse Truss":
                    iTT = float(yLT.get())
                    mTT = float(lenTrussT.get())
                    varTT = float(incYT.get())
                    if choose1.get() == "Yes":
                        fdsFileMaker(iTT, mTT, varTT, 'HTC', "'{0}'".format(clicked3.get()), float(xTT.get()), float(uLimitTT.get()), iorTT.get())

                if clicked4.get() == "Slabs":
                    yI = float(y3.get())
                    wI = float(yIncrement.get())
                    widSLB = float(widthSLB.get())
                    while yI < widSLB:
                        i3 = float(x1_int.get())
                        m3 = float(x1_max.get())
                        var4 = float(e3.get())
                        if choose1.get() == "Yes":
                            fdsFileMaker(i3, m3, var4, 'HTC', "'{0}'".format(clicked3.get()), yI, float(z4.get()), ior3.get())
                        yI += wI

            ###########################################-----functions for OpenSEES files---#######################

            if makeOpenSEES.get() == "Yes":
                def iEntity(intValue, maxL, incrementE, centroidX, centroidY, flangeWidth, flangeHeight,
                            webThick, flangeThick):
                    global j1
                    while intValue < maxL:  # entities
                        with open(osFile, 'a') as fileOS:
                            fileOS.writelines("HTEntity \t Isection \t {0}   \t {1} \t {2} \t {3} \t {4} \t {5} "
                                              "\t {6};\n".format(j1, centroidX, centroidY, flangeWidth, flangeHeight, webThick,
                                                                 flangeThick))
                            j1 += 1
                            intValue += incrementE
                    with open(osFile, 'a') as fileOS:
                        fileOS.writelines("\n")

                def mesh(intValue2, maxL2, increment2, phaseChange, meshFW, meshFT, meshWT, meshW, material):
                    global j2
                    while intValue2 < maxL2:   # creating mesh
                        with open(osFile, 'a') as fileOS:
                            fileOS.writelines("HTMesh \t {0}  \t {0}  \t {6} \t -phaseChange \t {1} \t -MeshCtrls \t {2} \t {3} \t "
                                              "{4} \t {5};\n".format(j2, phaseChange, meshFW, meshFT, meshWT, meshW, material))
                            j2 += 1
                            intValue2 += increment2
                    with open(osFile, 'a') as fileOS:
                        fileOS.writelines("\n")

                def nodeSET(intValue3, maxL3, increment3, faces):
                    global j3
                    while intValue3 < maxL3:   # creating Node Set
                        with open(osFile, 'a') as fileOS:
                            fileOS.writelines("HTNodeSet \t {0}  \t -Entity \t {0}  \t -face \t {1};\n".format(j3, faces))
                            j3 += 1
                            intValue3 += increment3
                    with open(osFile, 'a') as fileOS:
                        fileOS.writelines("\n")

                def fireModel(intValue4, maxL4, increment4, boundaryFile):
                    global j4
                    while intValue4 < maxL4:   # creating Fire Model
                        with open(osFile, 'a') as fileOS:
                            fileOS.writelines("FireModel \t UserDefined \t {0}  \t -file \t {1}{0}.dat;\n".format(j4, boundaryFile))
                            j4 += 1
                            intValue4 += increment4
                    with open(osFile, 'a') as fileOS:
                        fileOS.writelines("\n")

                def heatFlux(intValue5, maxL5, increment5, hfFaces, HTConstants):
                    global j5
                    while intValue5 < maxL5:   # creating Heat Flux
                        with open(osFile, 'a') as fileOS:
                            fileOS.writelines("HTPattern \t fire \t {0}  \t model \t {0}  \t HeatFluxBC \t -HTEntity \t {0}"
                                              "  \t -face {1} \t -type \t ConvecAndRad \t HTConstants {2};\n"
                                              .format(j5, hfFaces, HTConstants))
                            j5 += 1
                            intValue5 += increment5
                    with open(osFile, 'a') as fileOS:
                        fileOS.writelines("\n")

                def htRecorder(intValue6, maxL6, increment6):
                    global j6
                    while intValue6 < maxL6:   # creating recorder
                        with open(osFile, 'a') as fileOS:
                            fileOS.writelines("HTRecorder \t -file \t temp{0}.dat  \t -NodeSet \t {0};\n".format(j6))
                            j6 += 1
                            intValue6 += increment6

                def blockEntity(intValue7, maxL7, increment7, blkCentroidX, blkCentroidY, widthBLK, depthBLK):
                    global j1
                    while intValue7 < maxL7:  # entities
                        with open(osFile, 'a') as fileOS:
                            fileOS.writelines("HTEntity \t Block \t {0}   \t {1} \t {2} \t {3} "
                                              "\t {4};\n".format(j1, blkCentroidX, blkCentroidY, widthBLK, depthBLK))
                            j1 += 1
                            intValue7 += increment7
                    with open(osFile, 'a') as fileOS:
                        fileOS.writelines("\n")

                def meshBLK(intValue8, maxL8, increment8, material2, phaseChange2, meshWBLK, meshDepth):
                    global j2
                    while intValue8 < maxL8:   # creating mesh
                        with open(osFile, 'a') as fileOS:
                            fileOS.writelines("HTMesh \t {0}  \t {0}  \t {1} \t -phaseChange \t {2} \t -MeshCtrls \t {3} \t {4};\n"
                                              .format(j2, material2, phaseChange2, meshWBLK, meshDepth))
                            j2 += 1
                            intValue8 += increment8
                    with open(osFile, 'a') as fileOS:
                        fileOS.writelines("\n")

                if clicked4.get() == "Longitudinal Beams":     ###--writing files by using above methods
                    global ent
                    i1 = float(x_int.get())
                    m1 = float(x_max.get())
                    inc = float(e1.get())
                    with open(osFile, 'a') as f3:
                        f3.writelines("\n#This is Longitudinal Beam {0}\n\n".format(ent))
                    iEntity(i1, m1, inc, float(cX.get()), float(cy.get()), float(bf.get()), float(hf.get()),
                            float(tw.get()), float(tf.get()))
                    mesh(i1, m1, inc, float(pChange.get()), float(mFW.get()), float(mFT.get()), float(mWT.get()),
                         float(mW.get()), int(matT.get()))
                    nodeSET(i1, m1, inc, fNodeset.get())
                    fireModel(i1, m1, inc, fMBfile.get())
                    heatFlux(i1, m1, inc, hffaces.get(), htConst.get())
                    htRecorder(i1, m1, inc)
                    ent += 1

            if makeOpenSEES.get() == "Yes":
                if clicked4.get() == "Transverse Beam":
                    global ent2
                    i2 = float(y_int.get())
                    m2 = float(y_max.get())
                    inc2 = float(e2.get())
                    with open(osFile, 'a') as f3:
                        f3.writelines("\n#This is Transverse Beam {0}\n\n".format(ent2))
                    iEntity(i2, m2, inc2, float(cX.get()), float(cy.get()), float(bf.get()), float(hf.get()),
                            float(tw.get()), float(tf.get()))
                    mesh(i2, m2, inc2, float(pChange.get()), float(mFW.get()), float(mFT.get()), float(mWT.get()),
                         float(mW.get()), int(matT.get()))
                    nodeSET(i2, m2, inc2, fNodeset.get())
                    fireModel(i2, m2, inc2, fMBfile.get())
                    heatFlux(i2, m2, inc2, hffaces.get(), htConst.get())
                    htRecorder(i2, m2, inc2)
                    ent2 += 1

            if makeOpenSEES.get() == "Yes":
                if clicked4.get() == "Columns":
                    global ent3
                    iC = float(z.get())
                    mC = float(z_max.get())
                    inc3 = float(e.get())
                    with open(osFile, 'a') as f3:
                        f3.writelines("\n#This is Column {0}\n\n".format(ent3))
                    iEntity(iC, mC, inc3, float(cX.get()), float(cy.get()), float(bf.get()), float(hf.get()),
                            float(tw.get()), float(tf.get()))
                    mesh(iC, mC, inc3, float(pChange.get()), float(mFW.get()), float(mFT.get()), float(mWT.get()),
                         float(mW.get()), int(matT.get()))
                    nodeSET(iC, mC, inc3, fNodeset.get())
                    fireModel(iC, mC, inc3, fMBfile.get())
                    heatFlux(iC, mC, inc3, hffaces.get(), htConst.get())
                    htRecorder(iC, mC, inc3)
                    ent3 += 1

                if clicked4.get() == "Longitudinal Truss":     ###--writing files by using above methods
                    global entLT
                    iLTO = float(xLT.get())
                    mLTO = float(lenTruss.get())
                    incLTO = float(incXT.get())
                    with open(osFile, 'a') as f3:
                        f3.writelines("\n#This is Longitudinal Truss {0}\n\n".format(entLT))
                    iEntity(iLTO, mLTO, incLTO, float(cX.get()), float(cy.get()), float(bf.get()), float(hf.get()),
                            float(tw.get()), float(tf.get()))
                    mesh(iLTO, mLTO, incLTO, float(pChange.get()), float(mFW.get()), float(mFT.get()), float(mWT.get()),
                         float(mW.get()), int(matT.get()))
                    nodeSET(iLTO, mLTO, incLTO, fNodeset.get())
                    fireModel(iLTO, mLTO, incLTO, fMBfile.get())
                    heatFlux(iLTO, mLTO, incLTO, hffaces.get(), htConst.get())
                    htRecorder(iLTO, mLTO, incLTO)
                    entLT += 1

                if clicked4.get() == "Transverse Truss":
                    global entTT
                    iTTO = float(yTT.get())
                    mTTO = float(lenTrussT.get())
                    incTTO = float(incYT.get())
                    with open(osFile, 'a') as f3:
                        f3.writelines("\n#This is Transverse Truss {0}\n\n".format(entTT))
                    iEntity(iTTO, mTTO, incTTO, float(cX.get()), float(cy.get()), float(bf.get()), float(hf.get()),
                            float(tw.get()), float(tf.get()))
                    mesh(iTTO, mTTO, incTTO, float(pChange.get()), float(mFW.get()), float(mFT.get()), float(mWT.get()),
                         float(mW.get()), int(matT.get()))
                    nodeSET(iTTO, mTTO, incTTO, fNodeset.get())
                    fireModel(iTTO, mTTO, incTTO, fMBfile.get())
                    heatFlux(iTTO, mTTO, incTTO, hffaces.get(), htConst.get())
                    htRecorder(iTTO, mTTO, incTTO)
                    entTT += 1

                if clicked4.get() == "Slabs":   ####### functions for Slabs
                    global ent4
                    yStart = float(y3.get())
                    wIncrement = float(yIncrement.get())
                    totalWSLB = float(widthSLB.get())
                    while yStart < totalWSLB:
                        iBLK = float(x1_int.get())
                        mBLK = float(x1_max.get())
                        incBLK = float(e3.get())
                        with open(osFile, 'a') as f3:
                            f3.writelines("\n#This is Slab {0}\n\n".format(ent4))
                        blockEntity(iBLK, mBLK, incBLK, float(cBX.get()), float(cBy.get()), float(wB.get()), float(dB.get()))
                        meshBLK(iBLK, mBLK, incBLK, matT.get(), pChange.get(), float(mwB.get()), float(mdB.get()))
                        nodeSET(iBLK, mBLK, incBLK, fNodeset.get())
                        fireModel(iBLK, mBLK, incBLK, fMBfile.get())
                        heatFlux(iBLK, mBLK, incBLK, hffaces.get(), htConst.get())
                        htRecorder(iBLK, mBLK, incBLK)
                        ent4 += 1
                        yStart += wIncrement

            if elementSetGen.get() == "Yes":  ##  here we write a file for element generation
                global jEle
                global ELEMENT_SET
                global ELEMENT_SET2
                createFolder("./ElementSets")

                def ele_set_gen(counter, member):   # this method generate file  and write on the file, will take 2 items in each line
                    with open(ELEMENT_SET, 'a', newline='') as EleSet:
                        EleSet.write("\nThis is ElementSet{0} for {1}\n".format(counter, member))
                        writer = csv.writer(EleSet)
                        for iItem in range(0, len(elementList), 2):  # step by threes.
                            writer.writerow(elementList[iItem:iItem+2])

                def ele_set_gen2(counter1, member):   # this method generate file  and write on the file, will take 20 items in each line
                    with open("ElementSets/ElementSet{}.csv".format(counter1), 'w', newline='') as EleSetInd:
                        EleSetInd.write("\n#ElementSet{0} for {1}\n".format(counter1, member))
                        writerInd = csv.writer(EleSetInd)
                        for iItem in range(0, len(elementList), 1):  # step by threes.
                            writerInd.writerow(elementList[iItem:iItem+1])

                def ele_set_gen3(counter, member):   # this method generate file  and write on the file, will take 2 items in each line
                    with open(ELEMENT_SET, 'a', newline='') as EleSet2:
                        EleSet2.write("\n#This is ElementSet{0} for {1}\n".format(counter, member))
                        for iItem in range(0, len(elementList), 1):  # step by threes.
                            f = str(elementList[iItem:iItem+1])[1:-1]  # it removes the square brackets
                            EleSet2.write('\n eleLoad -ele  {0} -type -beamThermal -source "temp{1}.dat" {2}'.format(f, counter, sectionBC.get()))

                def ele_set_gen4(counter, member):   # this method generate file  and write on the file, will take 20 items in each line
                    with open("ElementSets/ElementSet{}.csv".format(counter), 'w', newline='') as EleSet2:
                        EleSet2.write("\n#This is ElementSet{0} for {1}\n".format(counter, member))
                        for iItem in range(0, len(elementList), 1):  # step by threes.
                            f = str(elementList[iItem:iItem+1])[1:-1]  # it removes the square brackets
                            EleSet2.write('\n eleLoad -ele  {0} -type -shellThermal -source "temp{1}.dat" {2}'.format(f, counter, sectionShell.get()))

                '''this step convert all nodes (value in Element dictionary) into set ,
                # which helps to find subset in the node set'''
                def eleDictionary(getClass):  # this method generate the element list which is copied in ele_set_gen method
                    # noinspection PyGlobalUndefined
                    global elementList
                    setX = getClass  # calling functions(methods) from the class
                    fullSet = set(setX)  # all nodes are changed into a set
                    elementList = [key for key, value in elementDict.items()
                                   if set(value).issubset(fullSet)]

                if clicked4.get() == "Columns":   #----------For Columns
                    global m1C, lowerL, upperL
                    m1C = float(z.get())
                    # if choose.get() == "X":
                    while m1C < float(z_max.get()):
                        lowerL = m1C - float(e.get())/2
                        upperL = m1C + float(e.get())/2
                        eleDictionary(nodes1())
                        ele_set_gen(iEle, "Columns")
                        ele_set_gen2(iEle, "Columns")
                        ele_set_gen3(iEle, "Columns")
                        m1C += float(e.get())
                        iEle += 1

                if clicked4.get() == "Longitudinal Beams":   #----------For Beams
                    # noinspection PyGlobalUndefined
                    global m2ES, lowerLB, upperLB
                    m2ES = float(x_int.get())
                    while m2ES < float(x_max.get()):
                        lowerLB = m2ES - float(e1.get())/2
                        upperLB = m2ES + float(e1.get())/2
                        eleDictionary(nodes4())
                        ele_set_gen(iEle, "Beams")
                        ele_set_gen2(iEle, "Beams")
                        ele_set_gen3(iEle, "Beams")
                        m2ES += float(e1.get())
                        iEle += 1

                if clicked4.get() == "Transverse Beam":   #----------For Beams
                    m2EST = float(y_int.get())
                    global M2EST, lowerLBT, upperLBT
                    while m2EST < float(y_max.get()):
                        lowerLBT = m2EST - float(e2.get())/2
                        upperLBT = m2EST + float(e2.get())/2
                        eleDictionary(nodes3())
                        ele_set_gen(iEle, "Beams")
                        ele_set_gen2(iEle, "Beams")
                        ele_set_gen3(iEle, "Beams")
                        m2EST += float(e2.get())
                        iEle += 1

                if clicked4.get() == "Longitudinal Truss":   #----------For Trusses
                    global mLTruss, trussEleL, trussEleU
                    mLTruss = float(xLT.get())
                    while mLTruss < float(lenTruss.get()):
                        trussEleL = mLTruss - float(incXT.get())/2
                        trussEleU = mLTruss + float(incXT.get())/2
                        eleDictionary(nodes5())
                        ele_set_gen(iEle, "Trusses")
                        ele_set_gen2(iEle, "Trusses")
                        ele_set_gen3(iEle, "Trusses")
                        mLTruss += float(incXT.get())
                        iEle += 1

                if clicked4.get() == "Transverse Truss":   #----------For Trusses
                    global mTTruss, trussTEleL, trussTEleU
                    mTTruss = float(yTT.get())
                    while mTTruss < float(lenTrussT.get()):
                        trussTEleL = mTTruss - float(incYT.get())/2
                        trussTEleU = mTTruss + float(incYT.get())/2
                        eleDictionary(nodes6())
                        ele_set_gen(iEle, "Trusses")
                        ele_set_gen2(iEle, "Trusses")
                        ele_set_gen3(iEle, "Trusses")
                        mTTruss += float(incYT.get())
                        iEle += 1

                if clicked4.get() == "Slabs":   #----------For Slabs
                    global mS4, slbF1, lowerSLW, upperSLW, lowerSLL, upperSLL
                    slbF1 = float(y3.get())
                    while slbF1 < float(widthSLB.get()):
                        lowerSLW = slbF1 - float(yIncrement.get())/2
                        upperSLW = slbF1 + float(yIncrement.get())/2
                        mS4 = float(x1_int.get())
                        while mS4 < float(x1_max.get()):
                            lowerSLL = mS4 - float(e3.get())/2
                            upperSLL = mS4 + float(e3.get())/2
                            eleDictionary(nodes7())
                            ele_set_gen(jEle, "Slabs")
                            ele_set_gen2(iEle, "Slabs")
                            ele_set_gen4(iEle, "Slabs")
                            mS4 += float(e3.get())
                            jEle += 1
                            iEle += 1
                        slbF1 += float(yIncrement.get())


        ################################################------OpenSEES File Entries-------#############################
        ##### I Beam Entries

        frame6 = tk.LabelFrame(window2, text="I Section Entities", padx=5, pady=5)
        frame6.grid(row=1, column=2, sticky="nsew")

        cX = tk.Entry(frame6, width=15)
        cX.grid(row=0, column=1)
        cX.insert(tk.END, "0")
        tk.Label(frame6, width=20, text="Centroid of X", anchor='e').grid(row=0, column=0)

        cy = tk.Entry(frame6, width=15)
        cy.grid(row=0, column=3)
        cy.insert(tk.END, "0.2")
        tk.Label(frame6, width=20, text="Centroid of Y", anchor='e').grid(row=0, column=2)

        bf = tk.Entry(frame6, width=15)
        bf.grid(row=1, column=1)
        bf.insert(tk.END, "0.4")
        tk.Label(frame6, width=20, text="Width of Flange", anchor='e').grid(row=1, column=0)

        hf = tk.Entry(frame6, width=15)
        hf.grid(row=1, column=3)
        hf.insert(tk.END, "0.4")
        tk.Label(frame6, width=20, text="Height of Beam", anchor='e').grid(row=1, column=2)

        tw = tk.Entry(frame6, width=15)
        tw.grid(row=2, column=1)
        tw.insert(tk.END, "0.4")
        tk.Label(frame6, width=20, text="Web Thickness", anchor='e').grid(row=2, column=0)

        tf = tk.Entry(frame6, width=15)
        tf.grid(row=2, column=3)
        tf.insert(tk.END, "0.4")
        tk.Label(frame6, width=20, text="Flange Thickness", anchor='e').grid(row=2, column=2)

        mFW = tk.Entry(frame6, width=15)
        mFW.grid(row=3, column=1)
        mFW.insert(tk.END, "0.4")
        tk.Label(frame6, width=20, text="Mesh flange width", anchor='e').grid(row=3, column=0)

        mFT = tk.Entry(frame6, width=15)
        mFT.grid(row=3, column=3)
        mFT.insert(tk.END, "0.4")
        tk.Label(frame6, width=20, text="Mesh flange thickness", anchor='e').grid(row=3, column=2)

        mWT = tk.Entry(frame6, width=15)
        mWT.grid(row=4, column=1)
        mWT.insert(tk.END, "0.4")
        tk.Label(frame6, width=20, text="Mesh web thickness", anchor='e').grid(row=4, column=0)

        mW = tk.Entry(frame6, width=15)
        mW.grid(row=4, column=3)
        mW.insert(tk.END, "0.4")
        tk.Label(frame6, width=20, text="Mesh web height", anchor='e').grid(row=4, column=2)

        ##### Block Entries
        frame7 = tk.LabelFrame(window2, text="Block Entities", padx=5, pady=5)
        frame7.grid(row=2, column=2, sticky="nsew")

        cBX = tk.Entry(frame7, width=15)
        cBX.grid(row=0, column=1)
        cBX.insert(tk.END, "0")
        tk.Label(frame7, width=20, text="Centroid of X", anchor='e').grid(row=0, column=0)

        cBy = tk.Entry(frame7, width=15)
        cBy.grid(row=0, column=3)
        cBy.insert(tk.END, "0")
        tk.Label(frame7, width=20, text="Centroid of Y", anchor='e').grid(row=0, column=2)

        wB = tk.Entry(frame7, width=15)
        wB.grid(row=1, column=1)
        wB.insert(tk.END, "0")
        tk.Label(frame7, width=20, text="Width of Block", anchor='e').grid(row=1, column=0)

        dB = tk.Entry(frame7, width=15)
        dB.grid(row=1, column=3)
        dB.insert(tk.END, "0")
        tk.Label(frame7, width=20, text="Depth of Block", anchor='e').grid(row=1, column=2)

        mwB = tk.Entry(frame7, width=15)
        mwB.grid(row=2, column=1)
        mwB.insert(tk.END, "0.01")
        tk.Label(frame7, width=20, text="Mesh along Width ", anchor='e').grid(row=2, column=0)

        mdB = tk.Entry(frame7, width=15)
        mdB.grid(row=2, column=3)
        mdB.insert(tk.END, "0.01")
        tk.Label(frame7, width=20, text="Mesh along Depth", anchor='e').grid(row=2, column=2)

        ### for beam and shell element sections
        sectionBC = tk.Entry(frame8, width=30)
        sectionBC.grid(row=4, column=1)
        sectionBC.insert(tk.END, "$y1 $y2 $z1 $z2")
        tk.Label(frame8, width=20, text="Section BC", anchor='e').grid(row=4, column=0)

        sectionShell = tk.Entry(frame8, width=30)
        sectionShell .grid(row=5, column=1)
        sectionShell .insert(tk.END, "$y1 $y2 $z1 $z2")
        tk.Label(frame8, width=20, text="Section Shell", anchor='e').grid(row=5, column=0)

        #####################---End of Entries

        tk.Button(window2, text="Save File", command=output2, width=15, height=1).grid(row=28, column=1, padx=5, pady=5)


    ############################################################--This is for module 4 : BatchFile for BNDF--#########

    if clicked.get() == "Batch File":
        window4 = tk.Tk()
        window4.title("Batch File Maker")
        window4.geometry("1200x600")
        # this is a frame for the entries of files and options for the user to chose the devices
        frame1 = tk.LabelFrame(window4, text="Basic Inputs", relief=tk.SUNKEN)
        frame1.grid(row=0, column=0, sticky="nsew")

        # label and button for location of the directory
        tk.Button(frame1, text="Directory", command=location, width=15, height=1).grid(row=0, column=1)
        tk.Label(frame1, width=20, text="Get Working Directory", anchor='e').grid(row=0, column=0, padx=5, pady=5)

        # dropbox for the structural components
        data = ["Columns", "Longitudinal Beams", "Transverse Beams", "Slabs"]
        clicked6 = tk.StringVar()
        clicked6.set(data[0])  # use variables as list
        dropStr = tk.OptionMenu(frame1, clicked6, *data)
        dropStr.config(width=12)
        dropStr.grid(row=3, column=5, padx=5, pady=5)
        tk.Label(frame1, width=20, text="Structural Components", anchor='e').grid(row=3, column=4, padx=5, pady=5)

        choose = tk.StringVar()
        choose.set("Yes")
        option = tk.OptionMenu(frame1, choose, "Yes", "No")
        option.config(width=12)
        option.grid(row=3, column=3, padx=5, pady=5)
        tk.Label(frame1, width=20, text="Devices to be installed", anchor='e').grid(row=3, column=2, padx=5, pady=5)

        ####################### Default Parameters
        fdsPr = "fds2ascii << EOF"  # to call fds2ascii
        bndf = 3  # data from BNDF file, it should be 2 for slice data
        SF = 1  # for all data
        domain = "y"  # all data to with in a range "n" for all data
        Var = 1  # change it according to the quantity required (Var represents the variable of the interest )
        EOF = "EOF"  # end of the command
        ###################---Entries Basic

        smv = tk.Entry(frame1, width=15)
        smv.grid(row=1, column=1)
        smv.insert(tk.END, "FDS")
        tk.Label(frame1, width=20, text="SMV File Name", anchor='e').grid(row=1, column=0)

        maxT = tk.Entry(frame1, width=15)
        maxT.grid(row=1, column=3)
        maxT.insert(tk.END, "300")
        tk.Label(frame1, width=20, text="Time of Simulation", anchor='e').grid(row=1, column=2)

        mesh = tk.Entry(frame1, width=15)
        mesh.grid(row=1, column=5)
        mesh.insert(tk.END, "0.1")
        tk.Label(frame1, width=20, text="Mesh Size in FDS", anchor='e').grid(row=1, column=4)

        BFI = tk.Entry(frame1, width=15)
        BFI.grid(row=2, column=1)
        BFI.insert(tk.END, "1")
        tk.Label(frame1, width=20, text="Mesh Index*", anchor='e').grid(row=2, column=0)

        x = tk.Entry(frame1, width=15)
        x.grid(row=2, column=3)
        x.insert(tk.END, "0")
        tk.Label(frame1, width=15, text="Initial Time", anchor='e').grid(row=2, column=2)

        y = tk.Entry(frame1, width=15)
        y.grid(row=2, column=5)
        y.insert(tk.END, "10")
        tk.Label(frame1, width=20, text="Time Interval", anchor='e').grid(row=2, column=4)

        ########################### Entries for Columns

        frame2 = tk.LabelFrame(window4, text="Columns Entries", padx=5, pady=5, relief=tk.SUNKEN)
        frame2.grid(row=1, column=0, sticky="nsew")

        x1 = tk.Entry(frame2, width=15)
        x1.grid(row=0, column=1)
        x1.insert(tk.END, "0")
        tk.Label(frame2, width=15, text="X Coordinate", anchor='e').grid(row=0, column=0)

        y1 = tk.Entry(frame2, width=15)
        y1.grid(row=0, column=3)
        y1.insert(tk.END, "0")
        tk.Label(frame2, width=15, text="Y Coordinate", anchor='e').grid(row=0, column=2)

        intZ = tk.Entry(frame2, width=15)
        intZ.grid(row=0, column=5)
        intZ.insert(tk.END, "0.5")
        tk.Label(frame2, width=15, text="Initial Z", anchor='e').grid(row=0, column=4)

        z_ran = tk.Entry(frame2, width=15)
        z_ran.grid(row=2, column=1)
        z_ran.insert(tk.END, "3")
        tk.Label(frame2, width=15, text="Total Height", anchor='e').grid(row=2, column=0)

        z_inc = tk.Entry(frame2, width=15)
        z_inc.grid(row=2, column=3)
        z_inc.insert(tk.END, "1")
        tk.Label(frame2, width=15, text="Increment", anchor='e').grid(row=2, column=2)

        IOR1 = tk.Entry(frame2, width=15)
        IOR1.grid(row=2, column=5)
        IOR1.insert(tk.END, "1")
        tk.Label(frame2, width=15, text="Orientation(IOR)", anchor='e').grid(row=2, column=4)

        ########################### Entries for Longitudinal Beams

        frame3 = tk.LabelFrame(window4, text="Longitudinal Beams Entries", padx=5, pady=5, relief=tk.SUNKEN)
        frame3.grid(row=2, column=0, sticky="nsew")

        x2 = tk.Entry(frame3, width=15)
        x2.grid(row=0, column=1)
        x2.insert(tk.END, "0")
        tk.Label(frame3, width=15, text="X Coordinate", anchor='e').grid(row=0, column=0)

        y2 = tk.Entry(frame3, width=15)
        y2.grid(row=0, column=3)
        y2.insert(tk.END, "0.5")
        tk.Label(frame3, width=15, text="Initial Y", anchor='e').grid(row=0, column=2)

        z2 = tk.Entry(frame3, width=15)
        z2.grid(row=0, column=5)
        z2.insert(tk.END, "0")
        tk.Label(frame3, width=15, text="Z Coordinate", anchor='e').grid(row=0, column=4)

        y_ran = tk.Entry(frame3, width=15)
        y_ran.grid(row=2, column=1)
        y_ran.insert(tk.END, "3")
        tk.Label(frame3, width=15, text="Total Length", anchor='e').grid(row=2, column=0)

        y_inc = tk.Entry(frame3, width=15)
        y_inc.grid(row=2, column=3)
        y_inc.insert(tk.END, "1")
        tk.Label(frame3, width=15, text="Increment", anchor='e').grid(row=2, column=2)

        IOR2 = tk.Entry(frame3, width=15)
        IOR2.grid(row=2, column=5)
        IOR2.insert(tk.END, "1")
        tk.Label(frame3, width=15, text="Orientation(IOR)", anchor='e').grid(row=2, column=4)

        ########################### Transverse Beams

        frame4 = tk.LabelFrame(window4, text="Transverse Beams Entries", padx=5, pady=5, relief=tk.SUNKEN)
        frame4.grid(row=3, column=0, sticky="nsew")

        x3 = tk.Entry(frame4, width=15)
        x3.grid(row=0, column=1)
        x3.insert(tk.END, "0.5")
        tk.Label(frame4, width=15, text="Initial X", anchor='e').grid(row=0, column=0)

        y3 = tk.Entry(frame4, width=15)
        y3.grid(row=0, column=3)
        y3.insert(tk.END, "0")
        tk.Label(frame4, width=15, text="Y Coordinate", anchor='e').grid(row=0, column=2)

        z3 = tk.Entry(frame4, width=15)
        z3.grid(row=0, column=5)
        z3.insert(tk.END, "0")
        tk.Label(frame4, width=15, text="Z Coordinate", anchor='e').grid(row=0, column=4)

        x_ran = tk.Entry(frame4, width=15)
        x_ran.grid(row=2, column=1)
        x_ran.insert(tk.END, "3")
        tk.Label(frame4, width=15, text="Total Length", anchor='e').grid(row=2, column=0)

        x_inc = tk.Entry(frame4, width=15)
        x_inc.grid(row=2, column=3)
        x_inc.insert(tk.END, "1")
        tk.Label(frame4, width=15, text="Increment", anchor='e').grid(row=2, column=2)

        IOR3 = tk.Entry(frame4, width=15)
        IOR3.grid(row=2, column=5)
        IOR3.insert(tk.END, "1")
        tk.Label(frame4, width=15, text="Orientation(IOR)", anchor='e').grid(row=2, column=4)

        ########################### Entries for Slabs

        frame5 = tk.LabelFrame(window4, text="Slab Entries", padx=5, pady=5, relief=tk.SUNKEN)
        frame5.grid(row=4, column=0, sticky="nsew")

        x4 = tk.Entry(frame5, width=15)
        x4.grid(row=0, column=1)
        x4.insert(tk.END, "0")
        tk.Label(frame5, width=15, text="X Coordinate", anchor='e').grid(row=0, column=0)

        y4 = tk.Entry(frame5, width=15)
        y4.grid(row=0, column=3)
        y4.insert(tk.END, "0.5")
        tk.Label(frame5, width=15, text="Initial Y", anchor='e').grid(row=0, column=2)

        z4 = tk.Entry(frame5, width=15)
        z4.grid(row=0, column=5)
        z4.insert(tk.END, "0")
        tk.Label(frame5, width=15, text="Z Coordinate", anchor='e').grid(row=0, column=4)

        s_ran = tk.Entry(frame5, width=15)
        s_ran.grid(row=2, column=1)
        s_ran.insert(tk.END, "3")
        tk.Label(frame5, width=15, text="Length oF the Slab", anchor='e').grid(row=2, column=0)

        s_inc = tk.Entry(frame5, width=15)
        s_inc.grid(row=2, column=3)
        s_inc.insert(tk.END, "1")
        tk.Label(frame5, width=15, text="Increment", anchor='e').grid(row=2, column=2)

        IOR4 = tk.Entry(frame5, width=15)
        IOR4.grid(row=2, column=5)
        IOR4.insert(tk.END, "1")
        tk.Label(frame5, width=15, text="Orientation(IOR)", anchor='e').grid(row=2, column=4)

        #########################################---END OF ENTRIES---#####################################################

        # this is the batch file added to the directory
        global iB
        iB = 1  # it gives index to the output files from fds2ascii if indexing is continuous

        # noinspection PyGlobalUndefined
        def output4():
            batchfile = "Batchfile.txt"

            # noinspection PyGlobalUndefined
            def batchFile(iX1, iX2, jY1, jY2, kZ1, kZ2, orientation):
                global iB
                t = int(x.get())
                dt = int(y.get())
                while t < int(maxT.get()):
                    with open(batchfile, 'a') as fb1:
                        t1 = t
                        t2 = t1 + dt
                        out = "test{}.csv".format(iB)  # file name which will come after the program run in FDS2ASCII
                        fb1.writelines("{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}\n{9}\n{10}\n{11}\n{12}\n{13}"
                                       "\n{14}\n{15}\n{16}\n{17}\n".format(fdsPr, smv.get(), bndf, SF, domain, iX1, iX2,
                                                                           jY1, jY2, kZ1, kZ2, t1, t2,
                                                                           orientation, Var, int(BFI.get()), out, EOF))
                        t += dt
                        iB += 1

            if choose.get() == "Yes":
                if clicked6.get() == "Columns":
                    kCol = float(intZ.get())
                    while kCol <= float(y_ran.get()):
                        xN = float(x1.get()) + float(mesh.get())/2
                        yN = float(y1.get()) + float(mesh.get())/2
                        zN = kCol + float(mesh.get()) / 2
                        batchFile(float(x1.get()), xN, float(y1.get()), yN, kCol, zN, IOR1.get())
                        kCol += float(z_inc.get())

                if clicked6.get() == "Longitudinal Beams":
                    k2 = float(y2.get())
                    while k2 <= float(y_ran.get()):
                        xN = float(x2.get()) + float(mesh.get())/2
                        yN = k2 + float(mesh.get())/2
                        zN = float(z2.get()) + float(mesh.get())/2
                        batchFile(float(x1.get()), xN, k2, yN, float(z2.get()), zN, IOR2.get())
                        k2 += float(y_inc.get())

                if clicked6.get() == "Transverse Beams":
                    k3 = float(x3.get())
                    while k3 <= float(x_ran.get()):
                        xN = k3 + float(mesh.get())/2
                        yN = float(y3.get()) + float(mesh.get())/2
                        zN = float(z3.get()) + float(mesh.get())/2
                        batchFile(k3, xN, float(y3.get()), yN, float(z3.get()), zN, IOR3.get())
                        k3 += float(x_inc.get())

                if clicked6.get() == "Slabs":
                    k4 = float(y4.get())
                    while k4 <= float(s_ran.get()):
                        xN = float(x4.get()) + float(mesh.get())/2
                        yN = k4 + float(mesh.get())/2
                        zN = float(z4.get()) + float(mesh.get())/2
                        batchFile(float(x4.get()), xN, k4, yN, float(z4.get()), zN, IOR4.get())
                        k4 += float(s_inc.get())

        tk.Button(window4, text="Generate Batch File", command=output4, width=15, height=1).grid(row=5, column=0,
                                                                                                 padx=5, pady=5)

        # this is a frame for the entries of files and options for the user to chose the devices
        infoFrame = tk.LabelFrame(window4, text="Information", relief=tk.SUNKEN)
        infoFrame.grid(row=8, column=0, sticky="nsew")

        tk.Label(infoFrame, width=140, text="Run in Terminal (Linux or MacOX), "
                                            "use (chmod +x BatchFile.command ) (name of command line) "
                                            "and in the next "
                                            "line run the batch file with "
                                            "(.\BatchFile.command))", anchor='w') \
            .grid(row=15, column=0, columnspan=4, padx=5, pady=5)

    #################################################-End of BatchFile Module--######################################

    if clicked.get() == "BNDF2OpenSEES":           ############### 5th Module BNDF to OpenSEES
        window5 = tk.Tk()
        window5.title("BNDF to OpenSEES")
        window5.geometry("400x300")

        # this is a frame for the entries of files and options for the user to chose the devices
        frame1 = tk.LabelFrame(window5, text="Basic Inputs", padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky="nsew")

        # button and label for the location
        tk.Button(frame1, text="Directory", command=location, width=15, height=1).grid(row=0, column=1)
        tk.Label(frame1, width=20, text="Get Working Directory", anchor='e').grid(row=0, column=0, padx=5, pady=5)

        sim_time = tk.Entry(frame1, width=10)
        sim_time.grid(row=1, column=1)
        sim_time.insert(tk.END, "300")
        tk.Label(frame1, width=20, text="Time of Simulation", anchor='e').grid(row=1, column=0)

        dT = tk.Entry(frame1, width=10)
        dT.grid(row=2, column=1)
        dT.insert(tk.END, "10")
        tk.Label(frame1, width=20, text="Time interval", anchor='e').grid(row=2, column=0)

        no_Devc = tk.Entry(frame1, width=10)
        no_Devc.grid(row=3, column=1)
        no_Devc.insert(tk.END, "5")
        tk.Label(frame1, width=20, text="Number of Devices", anchor='e').grid(row=3, column=0)

        global TIME
        TIME = []

        # noinspection PyGlobalUndefined
        def output5():
            createFolder('./Header/')
            createFolder("./Header/Values/")
            createFolder("./Header/Values/DAT")
            createFolder("./OpenSEES")
            global TIME
            time = int(dT.get())
            while time <= int(sim_time.get()):
                newTime = time
                time += int(dT.get())
                TIME += [newTime]

            # make a column from the list
            outfile = open("Time.csv", 'w', newline='')
            out = csv.writer(outfile)
            out.writerows(map(lambda t1: [t1], TIME))
            outfile.close()
            fName = []  # making a list of all files comes from the FDS2ASCII
            iT = 1
            numFiles = (int(sim_time.get()) * int(no_Devc.get()) / int(dT.get()))   # it will give the total number of files

            '''The name of the files should be the same as generated by BNDF script '''

            while iT <= numFiles:
                file = 'test{}.csv'.format(iT)
                fName += [file]
                iT += 1

            r = 1
            while r <= numFiles:
                for fname in fName:
                    with open("Header/FDS{}.csv".format(r), 'w') as outfile:
                        with open(fname) as infile:
                            next(infile)
                            next(infile)
                            next(infile)
                            csv.reader(infile, quoting=csv.QUOTE_NONNUMERIC)
                            for lines in infile:
                                outfile.writelines(lines)
                    r += 1

            CSV = []  # making the list of files after removing the headers from the file
            kCSV = 1  # increment counter for CSV files
            while kCSV <= numFiles:  # for all files
                f1 = 'Header/FDS{}.csv'.format(kCSV)
                CSV += [f1]
                kCSV += 1

            s = 1
            t = (int(sim_time.get())*int(no_Devc.get())/int(dT.get()))

            while s <= t:
                for p1 in CSV:
                    with open("Header/Values/FDS{}.csv".format(s), 'w') as out:
                        wtr = csv.writer(out, delimiter=' ', quoting=csv.QUOTE_NONNUMERIC)
                        with open(p1, newline='') as go:
                            thirdColumn = [line.split(',')[3] for line in go]  # keeping only the 4th column as
                            # first three columns contains the coordinates data
                            wtr.writerow(thirdColumn)
                    s += 1

            #################################################################################################
            '''combining all data from the files in one file (one more inside code in needed to achieve limited 
                number of files based on  time and sample size'''

            listF = []  # list of all files after removing coordinates data
            i1 = 1

            while i1 <= numFiles:
                file1 = 'Header/Values/FDS{}.csv'.format(i1)
                listF += [file1]
                i1 += 1

            # number of files taken in one time will depends upon simulation time and time interval
            '''Below is the list of all files, where each item has sub-list of all items at one location with total time history'''
            tt1 = int(sim_time.get())
            ti1 = int(dT.get())

            allFilesList = [listF[numFile:numFile + int(tt1 / ti1)] for numFile in range(0, len(listF), int(tt1 / ti1))]

            jB = 1
            while jB <= int(no_Devc.get()):
                for iFile in allFilesList:
                    oneFile = "Header/Values/AST{}.csv".format(jB)
                    with open(oneFile, 'w') as outf1:
                        for itemK2 in iFile:
                            with open(itemK2) as infile:
                                dataOut = csv.reader(infile, quoting=csv.QUOTE_NONNUMERIC)
                                for lines in dataOut:
                                    outf1.writelines(lines)

                    # making file in Time and Temperature history
                    df1 = pd.read_csv("Time.csv")
                    df2 = pd.read_csv("Header/Values/AST{}.csv".format(jB))

                    result = pd.concat([df1, df2], axis=1, sort=False)  # join two columns
                    result.to_csv("Header/Values/ASTX{}.csv".format(jB), mode='w', index=False)

                    # converting files to DAT format
                    inputPath = "Header/Values/ASTX{}.csv".format(jB)
                    outputPath = "Header/Values/DAT/AST{}.dat".format(jB)

                    with open(inputPath) as inputFile:
                        with open(outputPath, 'w', newline='') as outputFile:
                            reader = csv.DictReader(inputFile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
                            writer = csv.DictWriter(outputFile, reader.fieldnames, delimiter=' ')
                            writer.writeheader()
                            writer.writerows(reader)

                    jB += 1

            # adding first line at time 0
            m = 1
            while m <= int(no_Devc.get()):
                f = open('Header/Values/DAT/AST{}.dat'.format(m), 'r')
                newF = open('OpenSEES/AST{}.dat'.format(m), 'w')
                lines = f.readlines()  # read old content
                newF.write("0.0 20.0\n")  # write new content at the beginning
                for line in lines:  # write old content after new
                    newF.write(line)
                newF.close()
                f.close()
                m += 1

        tk.Button(window5, text="Save File", command=output5, width=15, height=1).grid(row=2, column=0, padx=5, pady=5)

    #####################################################################---6 Module Running FDS and OpenSEES--#############

    if clicked.get() == "Run FDS/OpenSEES":
        window6 = tk.Tk()
        window6.title("Running FDS and OpenSEES")
        window6.geometry("420x350")
        # this is a frame for the entries of files and options for the user to chose the devices
        frameFDS = tk.LabelFrame(window6, text="FDS Inputs", padx=5, pady=5)
        frameFDS.grid(row=0, column=0, sticky="nsew")

        tk.Button(frameFDS, text="Directory", command=location, width=15, height=1).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(frameFDS, width=20, text="Get Working Directory", anchor='e').grid(row=0, column=0, padx=5, pady=5)

        FDS_FILE = tk.Entry(frameFDS, width=20)
        FDS_FILE.grid(row=1, column=1)
        FDS_FILE.insert(tk.END, "SemiConfined_Case1")
        tk.Label(frameFDS, width=15, text="FDS File Name", anchor='e').grid(row=1, column=0)

        MPI = tk.Entry(frameFDS, width=20)
        MPI.grid(row=2, column=1)
        MPI.insert(tk.END, "4")
        tk.Label(frameFDS, width=15, text="MPI Processes", anchor='e').grid(row=2, column=0)

        CORES = tk.Entry(frameFDS, width=20)
        CORES.grid(row=3, column=1)
        CORES.insert(tk.END, "2")
        tk.Label(frameFDS, width=15, text="Assigned Cores", anchor='e').grid(row=3, column=0)

        frameOS = tk.LabelFrame(window6, text="OpenSEES Inputs", padx=5, pady=5)
        frameOS.grid(row=1, column=0, sticky="nsew")

        OpenSEES_FILE = tk.Entry(frameOS, width=20)
        OpenSEES_FILE.grid(row=0, column=1)
        OpenSEES_FILE.insert(tk.END, "htibeamast")
        tk.Label(frameOS, width=20, text="OpenSEES File Name", anchor='e').grid(row=0, column=0)

        OpenSEES_Program = tk.Entry(frameOS, width=20)
        OpenSEES_Program.grid(row=1, column=1)
        OpenSEES_Program.insert(tk.END, r"C:\Program Files\OpenSEES")
        tk.Label(frameOS, width=20, text="OpenSEES Saved Here", anchor='e').grid(row=1, column=0)

        def runFDS():
            FDS = 'cmd /k "fdsinit & fds_local -p {} -o {} {}.fds"'.format(MPI.get(), CORES.get(), FDS_FILE.get())
            os.system(FDS)

        tk.Button(window6, text="Run FDS", command=runFDS, width=15, height=1).grid(row=2, column=0, padx=5, pady=5)

        def runOpenSEES():
            process = subprocess.Popen(["{0}\OpenSees.exe".format(OpenSEES_Program.get())], stdin=subprocess.PIPE,
                                       text=True)
            process.communicate(os.linesep.join(["source {0}.tcl".format(OpenSEES_FILE.get())]))

        tk.Button(window6, text="Run OpenSEES", command=runOpenSEES, width=15, height=1).grid(row=3, column=0, padx=5,
                                                                                              pady=5)
    if clicked.get() == "HT_Plots":
        window7 = tk.Tk()
        window7.title("Plotting")
        window7.geometry("500x220")

        framePLT = tk.Label(window7, text="Files", padx=15, pady=10)
        framePLT.grid(row=1, column=0, sticky="nsew")

        tk.Button(framePLT, text="Directory", command=location, width=15, height=1).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(framePLT, width=20, text="Get Working Directory", anchor='e').grid(row=0, column=0, padx=5, pady=5)

        num_Devc = tk.Entry(framePLT, width=10)
        num_Devc.grid(row=1, column=1)
        num_Devc.insert(tk.END, "5")
        tk.Label(framePLT, width=20, text="Number of Entities", anchor='e').grid(row=1, column=0)

        # noinspection PyGlobalUndefined
        def dev():
            global iPLT
            global filenamePLT
            filenamePLT = []
            while iPLT <= int(num_Devc.get()):
                file = ("temp{}.dat".format(iPLT))
                filenamePLT += [file]
                iPLT += 1

            global modules
            modules = filenamePLT  # modules
            clickedPLT = tk.StringVar()
            clickedPLT.set(modules[0])  # use variables as list
            dropPLT = tk.OptionMenu(framePLT, clickedPLT, *modules)
            dropPLT.config(width=15)
            dropPLT.grid(row=2, column=1, padx=5, pady=5)
            tk.Label(framePLT, width=30, text="Plot for ....", anchor='e').grid(row=2, column=0, padx=5, pady=5)

            def plot():
                style.use('ggplot')
                x_axis = pd.read_csv(clickedPLT.get(), delimiter=' ', usecols=[0], header=None)
                y_axis = pd.read_csv(clickedPLT.get(), delimiter=' ', usecols=[1], header=None)
                plt.plot(x_axis, y_axis)
                plt.title(clickedPLT.get())
                plt.show()

            tk.Button(framePLT, text="Plot", command=plot, width=15, height=1).grid(row=3, column=1, padx=5, pady=5)

        def allPlots():
            incPLT = 0
            while incPLT < len(modules):
                x2_axis = pd.read_csv(modules[incPLT], delimiter=' ', usecols=[0], header=None)
                y2_axis = pd.read_csv(modules[incPLT], delimiter=' ', usecols=[1], header=None)
                style.use('ggplot')
                plt.plot(x2_axis, y2_axis, '.-', label=modules[incPLT])
                plt.xlabel('time (s)')
                plt.ylabel('Temperature')
                plt.legend(loc="upper left")
                incPLT += 1
            plt.show()

        tk.Button(framePLT, text="Plot All", command=allPlots, width=15, height=1).grid(row=4, column=1, padx=5, pady=5)
        tk.Button(framePLT, text="Generate", command=dev, width=15, height=1).grid(row=1, column=2, padx=5, pady=5)


save_Button = tk.Button(root, text="Proceed", command=mainOutput, width=15, height=1).grid(row=3, column=0, padx=5,
                                                                                           pady=5)
root.mainloop()
