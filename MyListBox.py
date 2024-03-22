import tkinter as tk
from tkinter import ttk

class MyListBox(tk.Listbox):

    def __init__(self, container):
        super().__init__(container)

    def getSelectedFile(self):
        if(self.curselection()):
            return self.get(self.curselection())
        else:
            return -1

    def getSelectedFileId(self):
        if(self.curselection()):
            for item in self.curselection():
                return item
        else:
            return -1

    def removeSelectedFile(self):
        id = self.getSelectedFileId()

        if(id >= 0):
            self.delete(id, id)

    def addFileToList(self, newFile):
        self.insert(self.size(), newFile)

    def updateList(self, lista):
        self.delete(0, tk.END)
        for i in range(len(lista)):
            self.insert(i, lista[i])