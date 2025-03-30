# Video Embedding Extractor

A Python tool that extracts text from videos using OCR (Optical Character Recognition) and processes the extracted text to create unique word embeddings.

## Features

- Extracts frames from video files at configurable intervals
- Performs OCR on video frames to extract text
- Removes duplicate words and creates unique word lists
- Supports multiple video formats (MP4, AVI, MOV, MKV)
- Supports multiple languages:
  - English
  - Simplified Chinese
  - Traditional Chinese
- Comprehensive error handling and logging
- Configurable settings through command line arguments
- Cross-platform compatibility

## Prerequisites

- Python 3.7 or higher
- FFmpeg (for video processing)
- Tesseract OCR (for text extraction)

### Installing Prerequisites

#### macOS
```bash
# Install FFmpeg
brew install ffmpeg

# Install Tesseract with language data
brew install tesseract
brew install tesseract-lang  # This includes Chinese language data
```

#### Ubuntu/Debian
```bash
# Install FFmpeg
sudo apt-get update
sudo apt-get install ffmpeg

# Install Tesseract with language data
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # Simplified Chinese
sudo apt-get install tesseract-ocr-chi-tra  # Traditional Chinese
```

#### Windows
1. Download and install FFmpeg from [FFmpeg official website](https://ffmpeg.org/download.html)
2. Download and install Tesseract from [Tesseract GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
3. Download Chinese language data files:
   - [chi_sim.traineddata](https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata) (Simplified Chinese)
   - [chi_tra.traineddata](https://github.com/tesseract-ocr/tessdata/raw/main/chi_tra.traineddata) (Traditional Chinese)
4. Place the downloaded language files in the Tesseract tessdata directory (usually `C:\Program Files\Tesseract-OCR\tessdata`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/VideoEmbeddingExtractor.git
cd VideoEmbeddingExtractor
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The tool can be used from the command line with various options:

```bash
python main.py [video_path] [options]
```

### Basic Usage
```bash
python main.py video.mp4
```

### Advanced Options
```bash
python main.py video.mp4 --frame-gap 3.0 --languages eng chi_sim --save-frames --save-frame-text
```

### Command Line Arguments

- `video_path`: Path to the video file to process (required)
- `--video`: Alternative way to specify the video path
- `--frame-gap`: Time gap between frames in seconds (default: 5.0)
- `--save-frames`: Save frame screenshots (default: False)
- `--save-frame-text`: Save text for each frame (default: False)
- `--languages`: Languages to use for OCR (default: eng). Can be combined with +. Example: eng+chi_tra
- `--debug`: Show detailed debug information (default: False)

### Output

By default, the tool provides minimal console output:
```
Starting video processing...
Processing video: example.mp4
✓ Processing completed successfully
```

With `--debug` enabled, you'll see detailed information:
```
Starting video processing application
Frame gap: 5.0s
Save frames: False
Save frame text: False
Languages: eng
Debug mode: True
...
```

### Output Files

- `{video_name}_words.txt`: Contains the final deduplicated word list
- `video_processing.log`: Contains detailed processing logs (created in all cases)
- `frames/`: Contains extracted video frames (if --save-frames is enabled)
- `text/`: Contains OCR results for each frame (if --save-frame-text is enabled)
- `debug/`: Contains debug images for each processing step (if --debug is enabled)

## Error Handling

The tool includes comprehensive error handling:
- Continues processing if individual frames fail
- Continues processing if individual videos fail
- Logs all errors and warnings
- Creates necessary directories automatically
- Validates input files and paths
- Handles language-specific OCR errors gracefully

Error messages are displayed in a user-friendly format:
```
Error: Video file not found: example.mp4
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FFmpeg for video processing
- Tesseract OCR for text extraction
- Python community for various libraries used in this project


