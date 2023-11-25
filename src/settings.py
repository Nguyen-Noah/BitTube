# FRONTEND SETTINGS
BG_COLOR = '#242424'
WHITE = '#FFF'
DARK_GREY = '#4a4a4a'
CLOSE = '#8a0606'
SLIDER_BG = '#64686b'
DROPDOWN_MAIN_COLOR = '#444'
DROPDOWN_HOVER_COLOR = '#333'
DROPDOWN_MENU_COLOR = '#666'

video_settings = {
    'width': 1280,
    'height': 720,
    'FPS': 60,
    'Pixel Size': 2
}

resolution_map = {
    '720p': (1280, 720),
    '1080p': (1920, 1080),
    '1440p': (2560, 1440),
    '4K': (3840, 2160)
}

def set_setting(setting, new):
    video_settings[setting] = new