import os, filecmp
from shutil import rmtree
from PIL import Image
import cv2
from settings import video_settings

def file_to_binary(file_path):
    """
    Takes an input file of any type and converts it to a string of binary
    
    Parameters:
    - file_path: the source file that will be converted to binary

    Returns:
    A binary string with the data from the source file
    """

    try:
        with open(file_path, 'rb') as file:
            contents = file.read()
            # format(byte, '08b) is used to convert each byte to binary
            binary_data = ''.join(format(byte, '08b') for byte in contents)

            #with open(output_path, 'w') as output_file:
                #output_file.write(binary_data)

            print(f'File {file_path} has been successsfully converted to binary')

            return binary_data

    except FileNotFoundError:
        print(f'Error: file {file_path} not found')
    except Exception as e:
        print(f'An error hass occurred: {str(e)}')

def binary_to_file(bits, output_file):
    """
    Takes a text file of a binary string and converts it to the original format

    Parameters:
    - binary_path: the file holding the binary string
    """

    byte_data = bytes([int(''.join(map(str, bits[i:i+8])), 2) for i in range(0, len(bits), 8)])

    clear_folder('recovered')

    with open(output_file, 'wb') as output_file:
        output_file.write(byte_data)

def pixels_to_bits(pixels):
    bits = []
    for pixel in pixels:
        bits.append('1' if round_bit(pixel) == (0, 0, 0) else '0')

    return bits

def get_pixels(bits):
    """
    Converts the list of bits to a list of pixels

    Parameters:
    - bits: a list of bits

    Returns:
    A list of pixels
    """

    pixels = []

    for bit in bits:
        pixels.append((0, 0, 0) if bit == '1' else (255, 255, 255))
    
    return pixels

def pixels_to_png(pixels, path):
    """
    Takes a list of pixels and makes them into .png images, then stores them in images folder

    Parameters:
    - pixels: a list of pixels to be added to image
    - path: the filename for the output png
    """

    image = Image.new('RGB', (video_settings['width'] // video_settings['Pixel Size'], video_settings['height'] // video_settings['Pixel Size']))
    image.putdata(pixels)

    new_img = image.resize((video_settings['width'], video_settings['height']), Image.Resampling.NEAREST)

    clear_folder('recovered')

    new_img.save(path)

def png_to_pixels(image):
    """
    Extracts the pixels from a .png file and shrinks size back down to 1x1

    Parameters:
    - path: the path to the image file

    Returns:
    - a list of pixels per image
    """

    pixel_list = []
    pixels = image.load()
    width, height = image.size

    for row in range(height // video_settings['Pixel Size']):
        for col in range(width // video_settings['Pixel Size']):
            pixel_list.append(pixels[col * video_settings['Pixel Size'], row * video_settings['Pixel Size']])

    return pixel_list

def add_instructions(bits, filename):
    """
    Adds the filename and filetype of the original source file and adds it to the first 64 bits of the bit string

    Parameters:
    - bits: the string of bits retrieved from the source file
    - filename: the name of the original file

    Returns:
    The original bitstring with the instructions added as leading bits
    """

    # converts the filename to a binary string
    filename_bitstring = ''.join(format(ord(char), '08b') for char in filename)

    # the binary representation of the filename bitstring
    length_bitstring = "{0:b}".format(len(filename_bitstring))

    # pads the legnth bitstring to 16 characters
    while len(length_bitstring) < 16:
        length_bitstring = "0" + length_bitstring
        
    # concatenates the name of the file at the end of the bistring that represents the length of the file name
    filename_header = length_bitstring + filename_bitstring

    header_list = []
    for char in filename_header:
        header_list.append(char)

    payload_length = "{0:b}".format(len(bits))

    while len(payload_length) < 64:
        payload_length = "0" + payload_length

    for char in payload_length:
        header_list.append(char)

    header_list.extend(bits)

    return header_list

def decode_instructions(bits):
    # helper function to gets a string from binary
    def binary_code_string(str):
        return ''.join(chr(int(str[i*8:i*8 + 8], 2)) for i in range(len(str) // 8))
    
    # gets the first 16 bits of the bitstring -> the length of the file name
    filename_len_bitstr = ''.join(bits[:16])

    # converts the binary filename length to decimal
    filename_len = int(filename_len_bitstr, 2)

    # gets the bitstring representation of the filename
    filename_bitstring = ''.join(bits[16:16 + filename_len])

    # gets the filename
    filename = binary_code_string(filename_bitstring)

    # gets the payload and the length
    payload_len_bitstr = ''.join(bits[16 + filename_len:16 + filename_len + 64])
    payload_len = int(payload_len_bitstr, 2)

    return filename, bits[16 + filename_len + 64:16 + filename_len + 64 + payload_len]

def make_video(folder_path, output):
    """
    Creates an .mp4 video from the encoded images and stores it in 'video/{output}.mp4'

    Parameters:
    - folder_path: the folder holding all of the images
    - output: the name of the output file to be posted
    """

    # loops through the temporary images folder and appends each .png to image_list
    image_list = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith('.png'):
            file_path = os.path.join(folder_path, filename)
            img = cv2.imread(file_path)

            if img is not None:
                image_list.append(img)

    # clears the video folder
    clear_folder('video')

    # necessary objects to write to a video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output + '.mp4', fourcc, video_settings['FPS'], (video_settings['width'], video_settings['height']))

    # writing each frame to the video
    for image in image_list:
        video.write(image)

    # closing vc2 objects
    video.release()
    cv2.destroyAllWindows()

def get_frames(source):
    # opens the video
    video = cv2.VideoCapture(source)

    # gets the number of frames
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # goes through each frame and appends each frame object to frames
    frames = []
    for frame in range(total_frames):
        success, frame = video.read()

        if not success:
            print('Video finished.')
            break

        frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))

    # close vc2 objects
    video.release()
    cv2.destroyAllWindows()

    return frames

def round_bit(rgb):
    # reading pixels from compressed videos doesn't always return (0, 0, 0) or (255, 255, 255), so it must be rounded
    rgb = tuple(max(0, min(255, value)) for value in rgb)
    avg_value = sum(rgb) / 3
    rounded_rgb = tuple(0 if avg_value < 128 else 255 for _ in rgb)

    return rounded_rgb

def clear_folder(relative_path):
    """
    Clears the folder and recreates an empty folder with the same name

    Parameters:
    - relative_path: the relative path to the folder to be deleted
    """

    try:
        rmtree(relative_path)
    except:
        print(f'WARNING: Could not locate {relative_path} directory.')

    try:
        os.mkdir(relative_path)
    except:
        pass

def encode(source):
    """
    The main function that takes in a source file and encodes it into a video

    Parameters:
    - source: the file being encoded
    """

    # gets the bits from the source file
    bits = file_to_binary(source)

    # adds the length and filename to the beginning of the bitstring
    bits = add_instructions(bits, source.split('/')[-1])
    # converts the bits to pixels
    pixels = get_pixels(bits)

    # gets the number of pixels (not bits!) per image
    pixels_per_image = (video_settings['width'] * video_settings['height']) // (video_settings['Pixel Size'] ** 2)

    # gets the number of images needed to hold the pixels
    num_images = int(len(pixels) / pixels_per_image) + 1

    # gets the output name (i.e test.jpg)
    output_name = source.split('/')[-1]

    # clears the temporary images folder that holds the frames
    clear_folder('images')

    # loops through and gets the file name, the start index in the bitstring, the span of the pixels, the current pixels, and creates the .png image
    for i in range(num_images):
        curr_image_name = 'images/' + output_name + '-' + str(i).zfill(4) + '.png'
        curr_start_idx = i * pixels_per_image
        curr_span = min(pixels_per_image, len(pixels) - curr_start_idx)
        curr_pixels = pixels[curr_start_idx : curr_start_idx + curr_span]
        pixels_to_png(curr_pixels, curr_image_name)

    # makes the final video
    make_video('images', 'video/' + source.split('/')[-1].split('.')[0])

def decode(source):
    # gets every frame from the video
    frames = get_frames(source)

    # loops through the frames and gets the pixels, storing them in pixels
    pixels = []
    for frame in frames:
        frame_pixels = png_to_pixels(frame)
        pixels.extend(frame_pixels)

    # converts the pixels to bits
    bits = pixels_to_bits(pixels)

    # gets the filename and the payload from the bitstring
    filename, bits = decode_instructions(bits)

    # converts the binary into the final recovered file
    binary_to_file(bits, 'recovered/' + filename.split('.')[0] + '-recovered.' + filename.split('.')[1])

def compare_files(f1, f2):
    result = filecmp.cmp(f1, f2)
    print(result)
    return result