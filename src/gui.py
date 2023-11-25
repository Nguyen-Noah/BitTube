import customtkinter as ctk
import cv2
from os import path, listdir
from tkinter import Canvas
from menu import Menu
from settings import *
from PIL import Image, ImageTk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')
        self.title('BitTube')
        self.geometry('1000x600')
        self.minsize(800, 500)
        self.init_parameters()
        self.display_decoded.trace_add('write', self.display_decoded_image)

        # layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform='a')
        self.columnconfigure(1, weight=6, uniform='a')

        # widgets
        self.image_import = FileSelect(self, self.import_file)

        # run
        self.mainloop()

    def init_parameters(self):
        self.fps = ctk.IntVar(value=video_settings['FPS'])
        self.pixel_size = ctk.IntVar(value=video_settings['Pixel Size'])
        self.resolution = ctk.StringVar(value='720p')
        self.check_acc = ctk.StringVar(value='Yes')
        self.status = ctk.StringVar(value='Idle')
        self.allow_changes = ctk.BooleanVar(value=True)
        self.display_decoded = ctk.BooleanVar(value=False)

    def import_file(self, path):
        self.path = path
        # can open PNG, JPEG, PPM, GIF, TIFF, BMP
        if path.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
            self.image = Image.open(self.path)
            self.image_ratio = self.image.size[0] / self.image.size[1]
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.convert_type = True
        elif path.split('.')[-1] in ['mp4', 'avi', 'mkv', 'mov', 'mpeg']:
            self.image = self.get_video_thumbnail(self.path)
            self.image_ratio = self.image.size[0] / self.image.size[1]
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.convert_type = False
        else:
            self.image = None
            self.image_ratio = 0
            self.image_tk = None
            self.convert_type = True

        self.image_output = ImageOutput(self, self.resize_image)
        self.image_import.grid_forget()
        self.close_button = CloseOutput(self, self.close_edit, self.allow_changes)

        self.menu = Menu(self, 
                         self.fps, 
                         self.pixel_size, 
                         self.resolution, 
                         self.check_acc, 
                         self.status, 
                         self.allow_changes, 
                         self.convert_type, 
                         self.display_decoded, 
                         path)

    def get_video_thumbnail(self, video_path):
        video = cv2.VideoCapture(video_path)
        success, frame = video.read()
        if not success:
            print('Error reading video')
            return None
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        thumbnail = Image.fromarray(frame_rgb)

        video.release()

        return thumbnail

    def close_edit(self):
        self.image_output.grid_forget()
        self.close_button.place_forget()
        self.menu.grid_forget()
        self.image_import = FileSelect(self, self.import_file)
        
    def display_decoded_image(self, *args):
        recovery_path = path.abspath(path.join(self.path, '../..')) + '/recovered'
        recovered_file = listdir(recovery_path)[0]
        if recovered_file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
            self.image = Image.open(recovery_path + '/' + recovered_file)
            self.image_ratio = self.image.size[0] / self.image.size[1]
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.image_output = ImageOutput(self, self.resize_image)
            self.close_button = CloseOutput(self, self.close_edit, self.allow_changes)
            self.allow_changes.set(True)

    def resize_image(self, event):
        canvas_ratio = event.width / event.height

        if canvas_ratio > self.image_ratio:
            image_height = event.height
            image_width = image_height * self.image_ratio
        else:
            image_width = event.width
            image_height = image_width / self.image_ratio

        self.image_output.delete('all')
        if self.image_tk:
            resized_image = self.image.resize((int(image_width), int(image_height)))
            self.image_tk = ImageTk.PhotoImage(resized_image)
            self.image_output.create_image(event.width / 2, event.height / 2, image=self.image_tk)

class FileSelect(ctk.CTkFrame):
    def __init__(self, parent, import_func):
        super().__init__(master=parent)
        self.grid(column=0, columnspan=2, row=0, sticky='nsew')
        self.import_func = import_func

        ctk.CTkButton(self, text='Open File', command=self.open_dialogue).pack(expand=True, side='left')

    def open_dialogue(self):
        path = ctk.filedialog.askopenfile().name
        self.import_func(path)

class ImageOutput(Canvas):
    def __init__(self, parent, resize_image):
        super().__init__(master=parent, background=BG_COLOR, bd=0, highlightthickness=0, relief='ridge')
        self.grid(row=0, column=1, sticky='snew', pady=10, padx=10)
        self.bind('<Configure>', resize_image)

class CloseOutput(ctk.CTkButton):
    def __init__(self, parent, close_func, converting_flag):
        
        def update_state(*args):
            state = 'normal' if converting_flag.get() else 'disabled'
            self.configure(state=state)

        state = 'normal' if converting_flag.get() else 'disabled'

        super().__init__(
            master=parent, 
            command=close_func,
            text='x', 
            text_color=WHITE, 
            fg_color='transparent', 
            width=40, height=40,
            corner_radius=5,
            state=state,
            hover_color=CLOSE)
        self.place(relx=0.99, rely=0.01, anchor='ne')

        converting_flag.trace_add('write', update_state)