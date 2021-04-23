# Import module
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from threading import Thread
import utils
import time
import numpy as np
from PIL import Image, ImageTk
import cv2 as cv
from tkinter import filedialog
from bot import Bot
from driver import Driver


class App(tk.Tk):
    bot = None
    driver = None

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
        self.createOutputFrame(top_frame)

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
        self.course_link_entry = tk.Entry(labelframe, width=100)

        self.load_button = tk.Button(labelframe, text="Load", width=8)
        self.load_button.config(command=self.loadButtonAction)

        self.get_video_check_var = tk.IntVar(value=1)
        self.get_reading_check_var = tk.IntVar(value=1)
        self.get_quiz_check_var = tk.IntVar(value=1)
        self.get_graded_check_var = tk.IntVar(value=1)

        checkboxes_frame = tk.Frame(labelframe)
        get_video_check_box = tk.Checkbutton(checkboxes_frame, text="Video", variable=self.get_video_check_var)
        get_reading_check_box = tk.Checkbutton(checkboxes_frame, text="Reading", variable=self.get_reading_check_var)
        get_quiz_check_box = tk.Checkbutton(checkboxes_frame, text="Quiz", variable=self.get_quiz_check_var)
        get_graded_check_box = tk.Checkbutton(checkboxes_frame, text="Peer Graded Assignment", variable=self.get_graded_check_var)

        padding_y = 3

        course_link_label.grid(row=0, column=0, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        self.course_link_entry.grid(row=0, column=1, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        self.load_button.grid(row=0, column=2, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)

        # Checkboxes Frame
        checkboxes_frame.grid(row=1, column=1, pady=padding_y + 2, sticky=tk.S + tk.N + tk.W)
        get_video_check_box.grid(row=0, column=0, padx=5, sticky=tk.S + tk.N + tk.W)
        get_reading_check_box.grid(row=0, column=1, padx=5, sticky=tk.S + tk.N + tk.W)
        get_quiz_check_box.grid(row=0, column=2, padx=5, sticky=tk.S + tk.N + tk.W)
        get_graded_check_box.grid(row=0, column=3, padx=5, sticky=tk.S + tk.N + tk.W)

    def createOutputFrame(self, root):
        labelframe = tk.LabelFrame(root, text="Output", width=600, height=300)
        labelframe.pack(fill="x", expand="yes")

        output_folder_label = tk.Label(labelframe, text="Output:")
        self.output_folder_var = tk.StringVar()
        output_folder_entry = tk.Entry(labelframe, textvariable=self.output_folder_var, width=100)

        def browseFolder():
            folder_selected = filedialog.askdirectory()
            if folder_selected != "":
                self.output_folder_var.set(folder_selected)

        browse_button = tk.Button(labelframe, text="Browse", width=8, command=browseFolder)
        download_button = tk.Button(labelframe, text="Download", width=8, command=self.downloadButtonAction)
        # browse_button.config(command=browseFolder)

        # self.get_video_check_var = tk.IntVar(value=1)
        # self.get_reading_check_var = tk.IntVar(value=1)
        # self.get_quiz_check_var = tk.IntVar(value=1)
        # self.get_graded_check_var = tk.IntVar(value=1)

        # checkboxes_frame = tk.Frame(labelframe)
        # get_video_check_box = tk.Checkbutton(checkboxes_frame, text="Video", variable=self.get_video_check_var)
        # get_reading_check_box = tk.Checkbutton(checkboxes_frame, text="Reading", variable=self.get_reading_check_var)
        # get_quiz_check_box = tk.Checkbutton(checkboxes_frame, text="Quiz", variable=self.get_quiz_check_var)
        # get_graded_check_box = tk.Checkbutton(checkboxes_frame, text="Peer Graded Assignment", variable=self.get_graded_check_var)

        padding_y = 3

        output_folder_label.grid(row=0, column=0, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        output_folder_entry.grid(row=0, column=1, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        browse_button.grid(row=0, column=2, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        download_button.grid(row=1, column=2, padx=5, pady=padding_y + 2, sticky=tk.N)

        # Checkboxes Frame
        # checkboxes_frame.grid(row=1, column=1, pady=padding_y + 2, sticky=tk.S + tk.N + tk.W)
        # get_video_check_box.grid(row=0, column=0, padx=5, sticky=tk.S + tk.N + tk.W)
        # get_reading_check_box.grid(row=0, column=1, padx=5, sticky=tk.S + tk.N + tk.W)
        # get_quiz_check_box.grid(row=0, column=2, padx=5, sticky=tk.S + tk.N + tk.W)
        # get_graded_check_box.grid(row=0, column=3, padx=5, sticky=tk.S + tk.N + tk.W)

    ###################################################################################################################
    """" Button Handler Functions """
    ###################################################################################################################
    def loadButtonAction(self):
        course_link = self.getCourseLink()

        if course_link == "":
            messagebox.showinfo(title="Information", message="Please enter course link")
            return

        download_topics = self.getDownloadTopics()

        if self.driver == None:
            self.driver = Driver("main")

        if self.bot == None:
            self.bot = Bot(self.driver, course_link, start_week=1)

        self.bot.setDownloadTopics(download_topics)

    def downloadButtonAction(self):
        output_folder = self.getOutputFolder()

        if output_folder == "":
            messagebox.showinfo(title="Information", message="Please choose output folder")
            return

        if self.bot:
            self.bot.setOutputRoot(output_folder)
        else:
            messagebox.showinfo(title="Information", message="Bot not loaded!")
        pass

    ###################################################################################################################
    """" Getter Functions """
    ###################################################################################################################
    def getCourseLink(self):
        return self.course_link_entry.get()

    def getOutputFolder(self):
        return self.output_folder_var.get()

    def getDownloadTopics(self):
        get_video = True if self.get_video_check_var.get() else False
        get_reading = True if self.get_reading_check_var.get() else False
        get_quiz = True if self.get_quiz_check_var.get() else False
        get_graded_assignment = True if self.get_graded_check_var.get() else False

        return get_video, get_reading, get_quiz, get_graded_assignment


if __name__ == "__main__":
    app = App("Coursera Downloader")
    app.mainloop()

    print("Finished")

