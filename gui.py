# Import module
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from threading import Thread
import utils
import time
import os
from tkinter import filedialog
from bot import Bot
from driver import Driver
from file_downloader import FileDownloader


class App(tk.Tk):
    bot = None
    driver = None
    meta_data = None
    download_queue = None
    external_exercise_queue = None
    file_downloader = None

    def __init__(self, title, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title(title)

        # Adjust size
        # self.geometry("400x200")
        self.maxsize(800, 600)
        self.minsize(800, 470)

        # Create left and right frames
        top_frame = self.createTopFrame()
        bottom_frame = self.createBottomFrame()

        # Create frames on top frame
        self.createInputFrame(top_frame)
        self.createOutputFrame(top_frame)

        # Create frames on right frame
        # self.createStatusFrame(bottom_frame)
        self.createFileDownloaderFrame(bottom_frame)

    ###################################################################################################################
    """" Frame Creation Functions """
    ###################################################################################################################
    def createTopFrame(self):
        top_frame = tk.Frame(self, width=650, height=200, bg='grey')
        top_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.N + tk.W + tk.E)

        return top_frame

    def createBottomFrame(self):
        bottom_frame = tk.Frame(self, width=650, height=400, bg='grey')
        bottom_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.N + tk.W + tk.E)

        return bottom_frame

    def createInputFrame(self, root):
        labelframe = tk.LabelFrame(root, text="Input", width=600, height=300)
        labelframe.pack(fill="x", expand="yes")

        course_link_label = tk.Label(labelframe, text="Course Link:")
        self.course_link_entry = tk.Entry(labelframe, width=100)

        self.load_button = tk.Button(labelframe, text="Load", width=8)
        self.load_button.config(command=self.loadButtonAction)

        self.input_status_label = tk.Label(labelframe, text="", fg="green")

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

        course_link_label.grid(row=0, column=0, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        self.course_link_entry.grid(row=0, column=1, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        self.load_button.grid(row=0, column=2, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        self.input_status_label.grid(row=1, column=1, padx=5, pady=padding_y - 3, sticky=tk.W + tk.S + tk.N)

        # Checkboxes Frame
        # checkboxes_frame.grid(row=1, column=1, pady=padding_y + 2, sticky=tk.S + tk.N + tk.W)
        # get_video_check_box.grid(row=0, column=0, padx=5, sticky=tk.S + tk.N + tk.W)
        # get_reading_check_box.grid(row=0, column=1, padx=5, sticky=tk.S + tk.N + tk.W)
        # get_quiz_check_box.grid(row=0, column=2, padx=5, sticky=tk.S + tk.N + tk.W)
        # get_graded_check_box.grid(row=0, column=3, padx=5, sticky=tk.S + tk.N + tk.W)

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

        # browse_button.config(command=browseFolder)

        self.get_video_check_var = tk.IntVar(value=1)
        self.get_reading_check_var = tk.IntVar(value=1)
        self.get_quiz_check_var = tk.IntVar(value=1)
        self.get_graded_check_var = tk.IntVar(value=1)
        self.get_external_check_var = tk.IntVar(value=1)

        checkboxes_frame = tk.Frame(labelframe)
        get_video_check_box = tk.Checkbutton(checkboxes_frame, text="Video", variable=self.get_video_check_var)
        get_reading_check_box = tk.Checkbutton(checkboxes_frame, text="Reading", variable=self.get_reading_check_var)
        get_quiz_check_box = tk.Checkbutton(checkboxes_frame, text="Quiz", variable=self.get_quiz_check_var)
        get_graded_check_box = tk.Checkbutton(checkboxes_frame, text="Peer Graded", variable=self.get_graded_check_var)
        get_external_check_box = tk.Checkbutton(checkboxes_frame, text="External Exercise", variable=self.get_external_check_var)

        # Button Group
        buttons_frame = tk.Frame(labelframe)
        self.scrape_button = tk.Button(buttons_frame, text="Scrape", state=tk.DISABLED, width=8, command=self.scrapeButtonAction)
        self.download_video_button = tk.Button(buttons_frame, text="Download Video", state=tk.DISABLED, command=self.downloadVideoButtonAction)
        self.download_external_button = tk.Button(buttons_frame, text="External Exercise", state=tk.DISABLED, command=self.downloadExternalButtonAction)
        self.download_resource_button = tk.Button(buttons_frame, text="Resource", command=self.downloadResourceButtonAction)
        self.download_image_button = tk.Button(buttons_frame, text="Image", command=self.downloadImageButtonAction)

        # Status
        self.output_status_label = tk.Label(labelframe, text="", fg="green")

        padding_y = 3

        output_folder_label.grid(row=0, column=0, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        output_folder_entry.grid(row=0, column=1, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        browse_button.grid(row=0, column=2, padx=5, pady=padding_y + 2, sticky=tk.S + tk.N)
        checkboxes_frame.grid(row=1, column=1, pady=padding_y + 2, sticky=tk.S + tk.N + tk.W)
        buttons_frame.grid(row=2, column=1, padx=5, pady=padding_y, sticky=tk.W)
        self.output_status_label.grid(row=3, column=1, padx=5, pady=0, sticky=tk.W)

        # Checkboxes Frame
        get_video_check_box.grid(row=0, column=0, padx=5, sticky=tk.S + tk.N + tk.W)
        get_reading_check_box.grid(row=0, column=1, padx=5, sticky=tk.S + tk.N + tk.W)
        get_quiz_check_box.grid(row=0, column=2, padx=5, sticky=tk.S + tk.N + tk.W)
        get_graded_check_box.grid(row=0, column=3, padx=5, sticky=tk.S + tk.N + tk.W)
        get_external_check_box.grid(row=0, column=4, padx=5, sticky=tk.S + tk.N + tk.W)

        # Buttons Frame
        self.scrape_button.grid(row=0, column=0, padx=5, pady=padding_y, sticky=tk.N)
        self.download_video_button.grid(row=0, column=1, padx=5, pady=padding_y, sticky=tk.W)
        self.download_external_button.grid(row=0, column=2, padx=5, pady=padding_y, sticky=tk.W)
        self.download_resource_button.grid(row=0, column=3, padx=5, pady=padding_y, sticky=tk.W)
        self.download_image_button.grid(row=0, column=4, padx=5, pady=padding_y, sticky=tk.W)

    def createStatusFrame(self, root):
        labelframe = tk.LabelFrame(root, text="Status", width=600, height=100)
        labelframe.pack(fill="x", expand="yes")

        self.status_label_line_1 = tk.Label(labelframe, text="Downloading")
        self.status_label_line_2 = tk.Label(labelframe, text="Data")

        padding_y = 0

        self.status_label_line_1.grid(row=0, column=0, padx=5, pady=padding_y, sticky=tk.W)
        self.status_label_line_2.grid(row=1, column=0, padx=5, pady=padding_y, sticky=tk.W)


    def createFileDownloaderFrame(self, root):
        labelframe = tk.LabelFrame(root, text="File Downloader", width=600, height=500)
        labelframe.pack(fill="x", expand="yes")

        self.week_label = tk.Label(labelframe, text="", fg="green")
        self.topic_label = tk.Label(labelframe, text="", fg="green")

        filename_label = tk.Label(labelframe, text="Filename: ")
        self.filename_val_label = tk.Label(labelframe, text="")

        url_label = tk.Label(labelframe, text="Url: ")
        self.url_val_label = tk.Label(labelframe, text="")

        output_label = tk.Label(labelframe, text="Output: ")
        self.output_val_label = tk.Label(labelframe, text="")

        downloaded_label = tk.Label(labelframe, text="Downloaded: ")
        self.downloaded_val_label = tk.Label(labelframe, text="")
        size_label = tk.Label(labelframe, text="Size: ")
        self.size_val_label = tk.Label(labelframe, text="")

        speed_label = tk.Label(labelframe, text="Speed: ")
        self.speed_val_label = tk.Label(labelframe, text="")
        time_label = tk.Label(labelframe, text="Time left: ")
        self.time_val_label = tk.Label(labelframe, text="")

        total_label = tk.Label(labelframe, text="Total: ")
        self.total_val_label = tk.Label(labelframe, text="")

        # Progress bar widget
        self.progress_bar = ttk.Progressbar(labelframe, length=100, orient=tk.HORIZONTAL, mode='determinate')
        self.total_progress_bar = ttk.Progressbar(labelframe, length=100, orient=tk.HORIZONTAL, mode='determinate')

        # Button Group
        button_group_frame = tk.Frame(labelframe)
        self.pause_resume_btn = tk.Button(button_group_frame, text="Pause", width=8, state=tk.DISABLED, command=self.pauseDownloadButtonAction)
        self.skip_btn = tk.Button(button_group_frame, text="Skip", width=8, state=tk.DISABLED, command=self.skipDownloadButtonAction)
        self.cancel_btn = tk.Button(button_group_frame, text="Cancel", width=8, state=tk.DISABLED, command=self.cancelDownloadButtonAction)

        padding_y = 0

        self.week_label.grid(row=0, column=0, padx=5, pady=padding_y, sticky=tk.W)
        self.topic_label.grid(row=0, column=1, columnspan=3, padx=5, pady=padding_y, sticky=tk.W)

        filename_label.grid(row=1, column=0, padx=5, pady=padding_y, sticky=tk.W)
        self.filename_val_label.grid(row=1, column=1, columnspan=3, padx=5, pady=padding_y, sticky=tk.W)

        url_label.grid(row=2, column=0, padx=5, pady=padding_y, sticky=tk.W)
        self.url_val_label.grid(row=2, column=1, columnspan=3, padx=5, pady=padding_y, sticky=tk.W)

        output_label.grid(row=3, column=0, padx=5, pady=padding_y, sticky=tk.W)
        self.output_val_label.grid(row=3, column=1, columnspan=3, padx=5, pady=padding_y, sticky=tk.W)

        downloaded_label.grid(row=4, column=0, padx=5, pady=padding_y, sticky=tk.W)
        self.downloaded_val_label.grid(row=4, column=1, padx=5, pady=padding_y, sticky=tk.W)
        size_label.grid(row=4, column=2, padx=5, pady=padding_y, sticky=tk.W)
        self.size_val_label.grid(row=4, column=3, padx=5, pady=padding_y, sticky=tk.W)

        speed_label.grid(row=5, column=0, padx=5, pady=padding_y, sticky=tk.W)
        self.speed_val_label.grid(row=5, column=1, padx=5, pady=padding_y, sticky=tk.W)
        time_label.grid(row=5, column=2, padx=5, pady=padding_y, sticky=tk.W)
        self.time_val_label.grid(row=5, column=3, padx=5, pady=padding_y, sticky=tk.W)

        self.progress_bar.grid(row=6, column=0, columnspan=4, padx=5, pady=padding_y + 8, sticky=tk.W + tk.E)

        total_label.grid(row=7, column=0, padx=5, pady=padding_y, sticky=tk.W)
        self.total_val_label.grid(row=7, column=1, padx=5, pady=padding_y, sticky=tk.W)

        self.total_progress_bar.grid(row=8, column=0, columnspan=4, padx=5, pady=padding_y + 3, sticky=tk.W + tk.E)

        # Button Group Frame
        button_group_frame.grid(row=9, column=3, padx=5, pady=padding_y + 3, sticky=tk.E)
        self.pause_resume_btn.grid(row=0, column=0, padx=5, pady=padding_y, sticky=tk.E)
        self.skip_btn.grid(row=0, column=1, padx=5, pady=padding_y, sticky=tk.E)
        self.cancel_btn.grid(row=0, column=2, padx=5, pady=padding_y, sticky=tk.E)

        labelframe.columnconfigure(1, weight=1)
        labelframe.columnconfigure(3, weight=2)

    ###################################################################################################################
    """" Button Handler Functions """
    ###################################################################################################################
    def loadButtonAction(self):
        course_link = self.getCourseLink()

        if course_link == "":
            messagebox.showinfo(title="Information", message="Please enter course link")
            return

        if self.driver == None:
            self.driver = Driver("main")

        if self.bot == None:
            self.bot = Bot(self.driver, start_week=1, gui=self)

        self.bot.setCourseUrl(course_link)

        download_topics = self.getDownloadTopics()
        self.bot.setDownloadTopics(download_topics)

        Thread(target=self.runLoadMetaThread).start()

    def scrapeButtonAction(self):
        output_folder = self.getOutputFolder()

        if output_folder == "":
            messagebox.showinfo(title="Information", message="Please choose output folder")
            return

        if self.bot:
            self.bot.setOutputRoot(output_folder)
        else:
            messagebox.showinfo(title="Information", message="Bot not loaded!")

        download_topics = self.getDownloadTopics()
        self.bot.setDownloadTopics(download_topics)

        if self.meta_data:
            Thread(target=self.runDownloadHtmlAndGetVideoQueue).start()
        else:
            messagebox.showinfo(title="Information", message="Meta Data not loaded. Please load again")

    def downloadVideoButtonAction(self):
        if self.getOutputFolder() == "":
            messagebox.showinfo(title="Information", message="Please choose output folder")
            return

        if not self.download_queue:
            messagebox.showinfo(title="Information", message="Download Queue is Empty!")
            return

        Thread(target=self.runVideoDownloader).start()

    def downloadExternalButtonAction(self):
        output_folder = self.getOutputFolder()

        if output_folder == "":
            messagebox.showinfo(title="Information", message="Please choose output folder")
            return

        if not self.external_exercise_queue:
            messagebox.showinfo(title="Information", message="External Exercise Queue is Empty!")
            return

        Thread(target=self.runExternalExerciseDownloader).start()

    def downloadImageButtonAction(self):
        output_folder = self.getOutputFolder()

        if output_folder == "":
            messagebox.showinfo(title="Information", message="Please choose output folder")
            return

        if self.bot == None:
            self.bot = Bot(self.driver, gui=self)

        self.bot.setOutputRoot(output_folder)

        Thread(target=self.runImageDownloader).start()

    def downloadResourceButtonAction(self):
        course_link = self.getCourseLink()

        if course_link == "":
            messagebox.showinfo(title="Information", message="Please enter course link")
            return

        output_folder = self.getOutputFolder()

        if output_folder == "":
            messagebox.showinfo(title="Information", message="Please choose output folder")
            return

        if self.driver == None:
            self.driver = Driver("main")

        if self.bot == None:
            self.bot = Bot(self.driver, course_url=course_link, gui=self)

        self.bot.setOutputRoot(output_folder)

        # self.disableSkipButton(False)
        # self.disablePauseButton(False)
        # self.disableCancelButton(False)
        # self.disableDownloadVideoButton(True)

        Thread(target=self.runResourceDownloader).start()
        # self.downloadStatusLoop()

    def pauseDownloadButtonAction(self):
        if self.file_downloader:
            if self.file_downloader.pause():
                self.pause_resume_btn.config(text="Resume")
                self.pause_resume_btn.config(command=self.resumeDownloadButtonAction)

    def resumeDownloadButtonAction(self):
        if self.file_downloader:
            if self.file_downloader.resume():
                self.pause_resume_btn.config(text="Pause")
                self.pause_resume_btn.config(command=self.pauseDownloadButtonAction)

    def skipDownloadButtonAction(self):
        if self.file_downloader:
            self.file_downloader.stop()

    def cancelDownloadButtonAction(self):
        if self.file_downloader:
            if self.file_downloader.stopQueue():
                self.disablePauseButton(True)
                self.disableCancelButton(True)
                self.disableSkipButton(True)
                self.resetFileDownloaderInfo()
                self.disableDownloadVideoButton(False)

    ###################################################################################################################
    """" Getter Functions """
    ###################################################################################################################
    def getCourseLink(self):
        return self.course_link_entry.get()

    def getOutputFolder(self):
        return os.path.normpath(self.output_folder_var.get()) if self.output_folder_var.get() != "" else ""

    def getDownloadTopics(self):
        get_video = True if self.get_video_check_var.get() else False
        get_reading = True if self.get_reading_check_var.get() else False
        get_quiz = True if self.get_quiz_check_var.get() else False
        get_graded_assignment = True if self.get_graded_check_var.get() else False
        get_external_exercise = True if self.get_external_check_var.get() else False

        return get_video, get_reading, get_quiz, get_graded_assignment, get_external_exercise

    ###################################################################################################################
    """" Thread Functions """
    ###################################################################################################################
    def runLoadMetaThread(self):
        # Disable Buttons
        self.disableIOButtons()
        self.disableDownloadButtons()

        self.setInputStatus("Loading Metadata...", color="red")
        self.meta_data = self.bot.loadMeta()

        if not self.meta_data:
            messagebox.showwarning("Warning", "Course URL not set")
            return
        print(self.meta_data)

        item_count = 0

        for week in self.meta_data:
            for topic in week['topics']:
                item_count += len(topic['items'])

        # self.scrape_button.config(state="normal")
        self.disableButtons(self.scrape_button, self.load_button, val=False)

        self.setInputStatus("Loaded {} weeks with {} topics..".format(len(self.meta_data), item_count))

        messagebox.showinfo(title="Information", message="Meta data loaded!")

        # Enable Buttons
        self.disableButtons(self.load_button, self.scrape_button, self.download_resource_button, val=False)

    def runDownloadHtmlAndGetVideoQueue(self):
        self.setOutputStatus("Scraping...", color="red")

        # Disable Buttons
        self.disableIOButtons()
        self.disableDownloadButtons()

        self.download_queue, self.external_exercise_queue = self.bot.downloadHtmlAndGetVideoQueue(self.meta_data)
        print(self.download_queue)

        self.setOutputStatus("Downloaded HTMLs & Loaded {} videos in the queue".format(len(self.download_queue)), color="green")

        # Enable Buttons
        self.disableIOButtons(False)

        messagebox.showinfo(title="Information", message="HTML Downloaded and Video Download Queue Generated")

    def runVideoDownloader(self):
        # Disable Buttons
        self.disableIOButtons()
        self.disableDownloadButtons(False)

        # root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\Test"
        root = self.getOutputFolder()
        if self.file_downloader == None:
            self.file_downloader = FileDownloader(root)

        self.file_downloader.attachGUI(self)
        # self.file_downloader.loadQueueFromJson("data/log_20210424_031453/download_queue.json")
        self.file_downloader.loadQueueFromList(self.download_queue)
        self.file_downloader.startDownloadGui()

    def runResourceDownloader(self):
        # Disable Buttons
        self.disableIOButtons()
        self.disableDownloadButtons()

        self.bot.downloadResources()

        messagebox.showinfo(title="Information", message="Resource Download Complete!")

        # Enable Buttons
        self.disableIOButtons(False)

    def runExternalExerciseDownloader(self):
        # Disable Buttons
        self.disableIOButtons()
        self.disableDownloadButtons()

        self.bot.downloadExternalExercise()

        messagebox.showinfo(title="Information", message="External Exercise Download Complete!")

        # Enable Buttons
        self.disableIOButtons(False)

    def runImageDownloader(self):
        # Disable Buttons
        self.disableIOButtons()
        self.disableDownloadButtons()

        self.bot.downloadImages()

        messagebox.showinfo(title="Information", message="Images Download Complete!")

        # Enable Buttons
        self.disableIOButtons(False)

    ###################################################################################################################
    """" Looper Functions """
    ###################################################################################################################
    def downloadStatusLoop(self):
        if self.file_downloader:
            total_files, self.current_download_no, self.current_download_item, download_info = self.file_downloader.getDownloadInfo()

            if download_info:
                self.progress_bar['value'] = download_info['progress']
            # self.total_progress_bar['value'] = 1

        self.after(100, self.downloadStatusLoop)

    ###################################################################################################################
    """" GUI Functions """
    ###################################################################################################################
    def setScrapProgress(self, download_info):
        item = download_info['item']

        progress = download_info['progress']

        current_no = download_info['current_no']
        total_files = download_info['total_files']

        week = item['path'].split("\\")[0]
        topic_text = "Topic: {}".format(item['path'].split("\\")[1])
        filename = item['filename']
        url = item['url']
        output = download_info['full_path']

        eta = download_info['eta']
        speed = download_info['speed']

        dl_size = download_info['dl_size']
        file_size = download_info['total_size']

        self.setFileDownloaderInfo(week=week, topic=topic_text, filename=filename, url=url, output=output,
                                   eta=eta, speed=speed, dl_size=dl_size, file_size=file_size,
                                   progress=progress, current_no=current_no, total_files=total_files)

    def setVideoDownloadProgress(self, download_info):
        item = download_info['item']

        progress = download_info['progress']

        current_no = download_info['current_no']
        total_files = download_info['total_files']

        week = item['path'].split("\\")[0]
        topic_text = "Topic: {}".format(item['path'].split("\\")[1])
        filename = item['filename']
        url = item['url']
        output = download_info['full_path']

        eta = download_info['eta']
        speed = download_info['speed']

        dl_size = download_info['dl_size']
        file_size = download_info['total_size']

        self.setFileDownloaderInfo(week=week, topic=topic_text, filename=filename, url=url, output=output,
                                   eta=eta, speed=speed, dl_size=dl_size, file_size=file_size,
                                   progress=progress, current_no=current_no, total_files=total_files)

    def setFileDownloaderInfo(self, week=None, topic=None, filename=None, url=None, output=None,
                              eta=None, speed=None, dl_size=None, file_size=None,
                              progress=None, current_no=0, total_files=0):
        total_text = ""
        total_progress = 0

        if current_no > 0 and total_files > 0:
            prev_progress = (current_no - 1) / total_files * 100
            single_progress = 1 / total_files * 100
            total_progress = prev_progress + (single_progress * progress / 100)
            total_text = "{} of {} ( {:.2f} % )".format(current_no, total_files, total_progress)

        if week is not None: self.week_label.config(text=week)
        if topic is not None: self.topic_label.config(text=self.fitText(topic, 70))
        if filename is not None: self.filename_val_label.config(text=self.fitText(filename))
        if url is not None: self.url_val_label.config(text=self.fitText(url))
        if output is not None: self.output_val_label.config(text=self.fitText(output))

        if eta is not None: self.time_val_label.config(text=eta)
        if speed is not None: self.speed_val_label.config(text=speed)

        if dl_size is not None:
            downloaded_text = "{} ( {:.2f} % )".format(dl_size, progress) if dl_size != "" else ""
            self.downloaded_val_label.config(text=downloaded_text)

        if file_size is not None: self.size_val_label.config(text=file_size)
        if total_text is not None: self.total_val_label.config(text=total_text)

        if progress is not None: self.progress_bar['value'] = progress
        if total_progress is not None: self.total_progress_bar['value'] = total_progress

    def resetFileDownloaderInfo(self):
        self.setFileDownloaderInfo(week="", topic="", filename="", url="", output="",
                                   eta="", speed="", dl_size="", file_size="",
                                   progress=0, current_no=0, total_files=0)

    # Button Disable
    def disableButton(self, button, val=True):
        if val:
            button.config(state="disabled")
        else:
            button.config(state="normal")

    def disableButtons(self, *argv, val=True):
        for button in argv:
            if val:
                button.config(state="disabled")
            else:
                button.config(state="normal")

    def disableDownloadVideoButton(self, val):
        if val:
            self.download_video_button.config(state="disabled")
        else:
            self.download_video_button.config(state="normal")

    def disablePauseButton(self, val):
        if val:
            self.pause_resume_btn.config(state="disabled")
        else:
            self.pause_resume_btn.config(state="normal")

    def disableSkipButton(self, val):
        if val:
            self.skip_btn.config(state="disabled")
        else:
            self.skip_btn.config(state="normal")

    def disableCancelButton(self, val):
        if val:
            self.cancel_btn.config(state="disabled")
        else:
            self.cancel_btn.config(state="normal")

    def disableIOButtons(self, val=True):
        self.disableButtons(self.load_button, self.scrape_button, self.download_video_button,
                            self.download_external_button, self.download_resource_button, val=val)

    def disableDownloadButtons(self, val=True):
        self.disableButtons(self.pause_resume_btn, self.skip_btn, self.cancel_btn, val=val)

    # Show Dialogs
    def showDownloadCompleteDialog(self, msg=None):
        if msg is None:
            msg = "Download complete!"

        messagebox.showinfo(title="Information", message=msg)

        self.disableIOButtons(False)
        self.disableDownloadButtons(True)

    # Set Status
    def setInputStatus(self, text, color="green"):
        self.input_status_label.config(text=text, fg=color)

    def setOutputStatus(self, text, color="green"):
        self.output_status_label.config(text=text, fg=color)

    ###################################################################################################################
    """" Utility Functions """
    ###################################################################################################################
    def fitText(self, text, width=100):
        if text and width and len(text) > width:
            text = text[:width - 3] + '...'

        return text

    ###################################################################################################################
    """" Other Functions """
    ###################################################################################################################
    def destroy(self):
        super().destroy()
        if self.driver is not None:
            print("Closing Browser...")
            self.driver.closeBrowser()
            print("Closed Browser")

if __name__ == "__main__":
    app = App("Coursera Downloader")
    app.mainloop()

    print("Finished")
