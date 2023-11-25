import customtkinter as ctk
from binary import encode, decode, compare_files
from panel import SliderPanel, ConvertButton, DropdownPanel, SegmentedPanel, DecodeButton, TextPanel

class Menu(ctk.CTkTabview):
    def __init__(self, parent, fps, pixel_size, resolution, check_acc, status, converting_flag, convert_type, display_decoded, path):
        def update_state(*args):
            state = 'normal' if converting_flag.get() else 'disabled'
            self.configure(state=state)
            
        state = 'normal' if converting_flag.get() else 'disabled'
        
        super().__init__(master=parent, state=state)
        self.grid(row=0, column=0, sticky='snew', pady=10, padx=10)

        if path.split('.')[-1] != 'mp4':
            self.add('Encode')
            Encode(self.tab('Encode'), fps, pixel_size, resolution, check_acc, converting_flag, status, path)
        else:
            self.add('Decode')
            Decode(self.tab('Decode'), status, path, display_decoded)

        if convert_type:
            self.set('Encode')
        else:
            self.set('Decode')


        converting_flag.trace_add('write', update_state)

class Encode(ctk.CTkFrame):
    def __init__(self, parent, fps, pixel_size, resolution, check_acc, converting_flag, status, path):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
        self.can_change_settings = True
        self.check_acc = check_acc
        self.status = status
        self.path = path
        self.accuracy = ctk.BooleanVar(value=None)

        DropdownPanel(self, resolution, ['720p', '1080p', '1440p', '4K'], converting_flag)
        SliderPanel(self, 'FPS', fps, 10, 144, converting_flag)
        SliderPanel(self, 'Pixel Size', pixel_size, 2, 10, converting_flag)
        SegmentedPanel(self, 'Test Accuracy?', check_acc, ['Yes', 'No'], converting_flag)
        self.accuracy_panel = TextPanel(self, 'Accuracy (T/F)', self.accuracy, 'top')
        ConvertButton(self, self.status, self.encode, converting_flag)
        TextPanel(self, 'Status', status, 'bottom')

        check_acc.trace_add('write', lambda *args: self.update_field())

    def update_field(self):
        if self.check_acc.get() == 'Yes':
            self.accuracy_panel.pack(side='top', fill='x', pady=4, ipady=8)
        else:
            self.accuracy_panel.pack_forget()

    def encode(self):
        self.status.set('Encoding')
        encode(self.path)
        if self.check_acc.get() == 'Yes':
            self.status.set('Decoding')
            decode('video/' + self.path.split('/')[-1].split('.')[0] + '.mp4')
            self.status.set('Testing Accuracy')
            accuracy = compare_files(self.path, 'recovered/' + self.path.split('/')[-1].split('.')[0] + '-recovered.' + self.path.split('.')[-1])
            self.accuracy.set(accuracy)

class Decode(ctk.CTkFrame):
    def __init__(self, parent, status, path, display_decoded):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
        self.status = status
        self.path = path
        self.display_decoded = display_decoded

        DecodeButton(self, self.status, self.decode)
        TextPanel(self, 'Status', status, 'bottom')

    def decode(self):
        self.status.set('Decoding')
        decode('video/' + self.path.split('/')[-1].split('.')[0] + '.mp4')
        self.display_decoded.set(True)