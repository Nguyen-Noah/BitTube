import customtkinter as ctk
import threading, queue, os
from settings import *
from binary import encode, decode, compare_files

class Panel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=DARK_GREY)
        self.pack(fill='x', pady=4, ipady=8)

class DropdownPanel(ctk.CTkOptionMenu):
    def __init__(self, parent, data_var, options, converting_flag):
        def change_setting(selection):
            width, height = resolution_map[selection]
            set_setting('width', width)
            set_setting('height', height)

        def update_state(*args):
            state = 'normal' if converting_flag.get() else 'disabled'
            self.configure(state=state)

        state = 'normal' if converting_flag.get() else 'disabled'

        super().__init__(
            master=parent,
            values=options,
            variable=data_var,
            command=change_setting,
            state=state,
            fg_color=DARK_GREY,
            button_color=DROPDOWN_MAIN_COLOR,
            button_hover_color=DROPDOWN_HOVER_COLOR,
            dropdown_fg_color=DROPDOWN_MENU_COLOR)
        self.pack(fill='x', pady=4)

        converting_flag.trace_add('write', update_state)

class SliderPanel(Panel):
    def __init__(self, parent, text, param, min_value, max_value, converting_flag):
        super().__init__(parent=parent)

        def on_change(selection):
            set_setting(text, round(selection))

        def update_state(*args):
            state = 'normal' if converting_flag.get() else 'disabled'
            slider.configure(state=state)

        state = 'normal' if converting_flag.get() else 'disabled'

        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self, text=text).grid(column=0, row=0, sticky='W', padx=5)
        ctk.CTkLabel(self, textvariable=param).grid(column=1, row=0, sticky='E', padx=5)
        slider = ctk.CTkSlider(self, 
                      fg_color=SLIDER_BG, 
                      variable=param,
                      command=on_change,
                      from_=min_value,
                      to=max_value,
                      state=state
                      )
        slider.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        converting_flag.trace_add('write', update_state)

class SegmentedPanel(Panel):
    def __init__(self, parent, text, data_var, options, converting_flag):
        super().__init__(parent=parent)

        def update_state(*args):
            state = 'normal' if converting_flag.get() else 'disabled'
            panel.configure(state=state)

        state = 'normal' if converting_flag.get() else 'disabled'

        ctk.CTkLabel(self, text=text).pack()
        panel = ctk.CTkSegmentedButton(self, 
                                       variable=data_var, 
                                       values=options,
                                       state=state)
        panel.pack(expand=True, fill='both', padx=4, pady=4)
        
        converting_flag.trace_add('write', update_state)

class TextPanel(Panel):
    def __init__(self, parent, text, status, side):
        super().__init__(parent=parent)
        self.pack(side=side)
        label = ctk.CTkLabel(self, text=f'{text}: {status.get()}')
        label.pack(side='top', pady=5)

        def update_label(*args):
            label.configure(text=f'{text}: {status.get()}')
        
        status.trace_add('write', update_label)

class ConvertButton(ctk.CTkButton):
    def __init__(self, parent, status, encode_func, converting_flag):
        def on_click():
            self.configure(state='disabled')
            self.queue = queue.Queue()
            ThreadedTask(self.queue, status, encode_func).start()
            converting_flag.set(False)
            parent.after(100, process_queue)

        def process_queue():
            try:
                msg = self.queue.get_nowait()
                self.configure(state='normal')
                converting_flag.set(True)
            except queue.Empty:
                parent.after(100, process_queue)

        super().__init__(master=parent, text='Encode', command=on_click)
        self.pack(side='bottom', pady=10)

# thread to run binary conversion process
class ThreadedTask(threading.Thread):

    def __init__(self, queue, status, threaded_func):
        super().__init__()
        self.queue = queue
        self.status = status
        self.threaded_func = threaded_func
    
    def run(self):
        self.threaded_func()
        self.status.set('Done!')
        self.queue.put('task finished')

# --------------------------------------------------------------- #
class DecodeButton(ctk.CTkButton):
    def __init__(self, parent, status, decode_func):
        def on_click():
            self.configure(state='disabled')
            self.queue = queue.Queue()
            ThreadedTask(self.queue, status, decode_func).start()
            parent.after(100, process_queue)

        def process_queue():
            try:
                msg = self.queue.get_nowait()
            except queue.Empty:
                parent.after(100, process_queue)

        super().__init__(master=parent, text='Decode', command=on_click)
        self.pack(side='bottom', pady=10)