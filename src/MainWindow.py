import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
from MyListBox import *
from conversionFn import *
import threading as T
from tkinter import messagebox
import os
from os.path import exists
import platform

class MainWindow():

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("From Webp Converter V1.0.1")
        self.window.resizable(False, False)
        self.PrintWindowInTheCenter()
        
        """
        try:
            self.window.iconphoto(True, tk.Image("photo", file="../assets/icon.icns"))  # tkinter only supports .ico and .png files for icons, icon will be set in the app bundle using py2app
        except:
            pass
        """
            
        self.listBox = MyListBox(self.window)
        self.listScrollbarY = tk.Scrollbar(self.window)
        self.listScrollbarX = tk.Scrollbar(self.window,orient='horizontal')
        self.chooseFilesBtn = ttk.Button(self.window, text='Select Files', command=self.chooseFilesBtnDialogAction)
        self.removeBtn = ttk.Button(self.window, text='Remove', command=self.removeFileFromListAction)
        self.removeAllBtn = ttk.Button(self.window, text='Remove All', command=self.removeAllFileFromListAction)
        self.convertBtn = ttk.Button(self.window, text='Convert', command=self.convertAction)
        self.chooseDestinationEntryVar = tk.StringVar()
        self.chooseDestinationEntry = ttk.Entry(textvariable=self.chooseDestinationEntryVar, state=tk.DISABLED, foreground="black")
        self.chooseDestinationBtn = ttk.Button(self.window, text='Select Destination', command=self.chooseDestinationPathAction)
        self.progressBar = ttk.Progressbar(self.window, orient='horizontal', mode='indeterminate', length=280)
        self.statusBar = tk.Label(self.window, bd=1, relief=tk.GROOVE, text='from Webp Converter')

        self.listBox.config(yscrollcommand = self.listScrollbarY.set)
        self.listBox.config(xscrollcommand = self.listScrollbarX.set)
        self.listScrollbarY.config(command = self.listBox.yview)
        self.listScrollbarX.config(command = self.listBox.xview)

        # Default destination path
        if platform.system() == 'Darwin' or platform.system() == 'Linux':
            self.chooseDestinationEntryVar.set(os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop'))
        elif platform.system() == 'Windows':
            self.chooseDestinationEntryVar.set(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))

        self.setStateButtons(state="off", howMany="essentials")

        self.fileList = []

    # ~~~~~~~~ ACTIONS FUNCTIONS ~~~~~~~~

    def chooseFilesBtnDialogAction(self):
        filetypes = (('webp files', '*.webp'), ('all files', '*.*'))
        
        appoList = fd.askopenfilenames(parent=self.window, title='Choose files', filetypes=filetypes)

        if appoList:
            appoList = self.removeAlreadySelectedFiles(appoList)
            
            for i in range(len(appoList)):
                if(appoList[i].split(".")[1] != "webp"):
                    appoList.pop(i)
            
            if appoList:
                for i in range(len(appoList)):
                    self.fileList.append(appoList[i])
        
                self.listBox.updateList(self.fileList)
                self.setStateButtons(state="on", howMany="essentials")

    def removeFileFromListAction(self):
        if len(self.fileList) > 0 and self.listBox.getSelectedFile() != -1:
            self.fileList.remove(self.listBox.getSelectedFile())
            self.listBox.updateList(self.fileList)
            if not self.fileList:
                self.setStateButtons(state="off", howMany="essentials")

    def removeAllFileFromListAction(self):
        if len(self.fileList) > 0:
            self.fileList.clear()
            self.listBox.updateList(self.fileList)
            self.setStateButtons(state="off", howMany="essentials")

    def chooseDestinationPathAction(self):
        pathBackup = self.chooseDestinationEntryVar.get()
        self.chooseDestinationEntryVar.set(fd.askdirectory(initialdir=self.chooseDestinationEntryVar.get()))
        
        if self.chooseDestinationEntryVar.get() == "":      # if the user open the dialog but doesn't choose a folder
            self.chooseDestinationEntryVar.set(pathBackup)

    def convertAction(self):
        if(len(self.fileList) > 0):
            self.progressBar.grid(row=4, column=2, columnspan=1, sticky=(tk.W, tk.E))
            self.progressBar.start()
            self.setStateButtons(state="off", howMany="all")
            
            T.Thread(target=self.ConversionThread).start()

    def ConversionThread(self):
        counter = 0
        self.statusBar.config(fg="black")
        
        for i in range(len(self.fileList)):
            try:
                answer = True
                fileName = str(extractFileName(self.fileList[i]))
                filePath = str(self.chooseDestinationEntryVar.get()) + "/" + str(fileName)

                if exists(filePath + ".jpg") or exists(filePath + ".jpeg") or exists(filePath + ".png") or exists(filePath + ".gif"):
                    question = "A converted file of \"" + fileName + "\" could already exists here, proceed anyway?"
                    answer = messagebox.askyesno(title="Watch out!", message=question)

                if answer == True:
                    message = "Converting... " + str(counter + 1) + " / " + str(len(self.fileList))
                    self.statusBar.config(text=message)
                    self.listBox.itemconfig(i, {'bg': 'orange'})
                    convertFile(self.fileList[i], self.chooseDestinationEntryVar.get())
                    counter = counter + 1
                    self.listBox.itemconfig(i, {'bg': 'green'})
            except:
                self.statusBar.config(text = "Error!")
                self.listBox.itemconfig(i, {'bg': 'red'})
        
        self.statusBar.config(text = "Converted " + str(counter) + " / " + str(len(self.fileList)))
        if counter == len(self.fileList):
            self.statusBar.config(fg="green")
        else:
            self.statusBar.config(fg="red")
        self.progressBar.stop()
        self.progressBar.grid_remove()
        self.fileList.clear()
        self.listBox.updateList(self.fileList)
        self.setStateButtons(state="on", howMany="all")
        self.setStateButtons(state="off", howMany="essentials") # not so sophisticated, must be updated with automatic system

    # ~~~~~~~~ WINDOW FUNCTIONS ~~~~~~~~

    def gridAll(self):

        self.window.columnconfigure(0, weight=2)
        self.window.columnconfigure(1, weight=2)
        self.window.columnconfigure(2, weight=3)

        self.chooseFilesBtn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=(10, 0), columnspan=3)
        self.listBox.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0), padx=(10, 0))
        self.listScrollbarY.grid(row=1, column=3, sticky=(tk.W, tk.N, tk.S), pady=5, padx=(0, 1))
        self.listScrollbarX.grid(row=2, column=0, sticky=(tk.E, tk.W, tk.N), pady=(0, 5), columnspan=3, padx=(10, 0))
        self.chooseDestinationEntry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.chooseDestinationBtn.grid(row=3, column=2, pady=5, sticky=(tk.W, tk.E))
        self.removeBtn.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=(10, 0))
        self.removeAllBtn.grid(row=4, column=1, sticky=(tk.W, tk.E))
        self.convertBtn.grid(row=4, column=2, sticky=(tk.W, tk.E))
        self.statusBar.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.S), columnspan=3, padx=(10,0), pady=(10, 0))

    def appStart(self):
        self.window.mainloop()

    def PrintWindowInTheCenter(self):
        windowHeight = 340
        windowWidth = 650

        screenWidth = self.window.winfo_screenwidth()
        screenHeight = self.window.winfo_screenheight()

        x_cordinate = int((screenWidth/2) - (windowWidth/2))
        y_cordinate = int((screenHeight/2) - (windowHeight/2)) - 100 # slightly upper than center

        self.window.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, x_cordinate, y_cordinate))

    # ~~~~~~~~ UTILITY FUNCTIONS ~~~~~~~~

    def removeAlreadySelectedFiles(self, appoTuple):

        appoList = []

        for k in range(len(appoTuple)):
            appoList.append(appoTuple[k])

        for i in range(len(self.fileList)):
            for j in range(len(appoList)):
                if appoList[j] == self.fileList[i]:
                    appoList.pop(j)
                    break
        return appoList

    def setStateButtons(self, state, howMany="essentials"):

        if state == "off":
            self.removeBtn.config(state=tk.DISABLED)
            self.removeAllBtn.config(state=tk.DISABLED)
            self.convertBtn.config(state=tk.DISABLED)
            if howMany == "all":
                self.chooseDestinationBtn.config(state=tk.DISABLED)
                self.chooseFilesBtn.config(state=tk.DISABLED)
        
        elif state == "on":
            self.removeBtn.config(state=tk.ACTIVE)
            self.removeAllBtn.config(state=tk.ACTIVE)
            self.convertBtn.config(state=tk.ACTIVE)
            if howMany == "all":
                self.chooseDestinationBtn.config(state=tk.ACTIVE)
                self.chooseFilesBtn.config(state=tk.ACTIVE)