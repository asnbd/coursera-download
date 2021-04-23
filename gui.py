# Import module
import tkinter as tk
from tkinter import ttk
from threading import Thread
import utils
import time
import numpy as np
from PIL import Image, ImageTk
import cv2 as cv


class App(tk.Tk):
    def __init__(self, title, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title(title)

        # Adjust size
        # self.geometry("400x200")
        self.maxsize(900, 600)
        self.minsize(600, 300)

        # Create left and right frames
        top_frame = self.createTopFrame()
        bottom_frame = self.createBottomFrame()

        # Create frames on top frame
        self.createInputFrame(top_frame)

        # Create frames on right frame

    ###################################################################################################################
    """" Frame Creation Functions """
    ###################################################################################################################
    def createTopFrame(self):
        top_frame = tk.Frame(self, width=650, height=200, bg='grey')
        top_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.N + tk.W + tk.E)

        return top_frame

    def createBottomFrame(self):
        bottom_frame = tk.Frame(self, width=650, height=400, bg='grey')
        bottom_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.N)

        return bottom_frame

    def createInputFrame(self, root):
        labelframe = tk.LabelFrame(root, text="Input", width=600, height=300)
        labelframe.pack(fill="x", expand="yes")

        course_link_label = tk.Label(labelframe, text="Course Link:")
        course_link_entry = tk.Entry(labelframe, width=100)

        self.refresh_button = tk.Button(labelframe, text="Load", width=8)
        self.refresh_button.config(command=self.refreshAllDeviceList)

        padding_y = 3

        course_link_label.grid(row=0, column=0, padx=5, pady=padding_y + 2, sticky=tk.E + tk.N)
        course_link_entry.grid(row=0, column=1, padx=5, pady=padding_y + 2, sticky=tk.E + tk.N)


if __name__ == "__main__":
    app = App("TEST GUI")
    app.mainloop()

    print("Finished")

