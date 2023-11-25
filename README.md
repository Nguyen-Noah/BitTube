# BitTube

BitTube is a Python application that converts files to binary black and white pixel videos. [**DOWNLOAD HERE**](https://github.com/Nguyen-Noah/BitTube/blob/main/BitTube.rar)

## The Idea

YouTube allows for 256GB uploads with unlimited posts, completely free of cost. If users can encode their data as .mp4 files, they could use YouTube as a means of backing up whatever files they want. At 4K 60FPS, a 1-second video can hold up to 62 million characters if each pixel represents a bit. 

## Installation

The application can either be used from the source code using ```git clone``` or using the executable file.

### Instructions

1. Clone the repository:

```bash
git clone https://github.com/Nguyen-Noah/BitTube.git
```

2. Install the required dependencies

```bash
pip install -r requirements.txt
```

## Example

Below is the output .mp4 file (converted to gif) from encoding an .mp3 file of [December, 1963 (Oh What A Night!) - The Four Seasons](https://www.youtube.com/watch?v=mTUhnIY3oRM).

The `encode()` function takes in a file and converts the contents to bits. It will then map the bits to a png of black for ```1``` and white for ```0```. It then produces a series of .png files that are stored in the ```/images/``` directory, which are made into an .mp4 video.

![Alt text](https://github.com/Nguyen-Noah/BitTube/blob/main/example.gif)

The video consists of 177 images at 720p 60FPS. Each pixel is at minimum 2x2 to compensate for video compression at higher resolutions. To increase the bitrate, the settings go from 720p to 4K at a frame rate of 10FPS to 144FPS. It is important to note there is a 64 bit header that has the filename, filetype, and payload length.

To convert the .mp4 file back to the original file, the `decode()` function is called. This function gets each frame from the video, reads the pixels, and translates it into a binary string. The first 64 bits are read to get the original file name and uses the payload to recover the file.

## Usage

1. Extract the BitTube.zip file
2. Run the executable
3. Choose the file you would like to encode/decode (.mp4 files will not allow encoding as it is less efficient to convert video files to binary)
4. Choose the settings for the output video
![Alt text](https://github.com/Nguyen-Noah/BitTube/blob/main/image.png)
(Art by [SamDoesArts](https://www.youtube.com/@samdoesarts))
6. Upload the video to YouTube (preferably on unlisted)
7. Download the YouTube video and select it to decode
8. Retrieve the recovered file in the ```/recovered/``` directory

## Roadmap
- Refactor the tkinter spaghetti code
- Implement threading in decoding process

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
