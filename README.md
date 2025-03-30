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
- Configurable settings through a central configuration file
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

## Configuration

The project uses a central configuration file (`config.py`) where you can modify various settings:

```python
@dataclass
class Config:
    # Directory paths
    input_folder: str = 'input'
    output_folder: str = 'output'
    frames_folder: str = 'frames'
    text_folder: str = 'text'
    
    # Video processing settings
    frame_rate: int = 10  # Extract every Nth frame
    output_format: str = 'txt'
    
    # Logging settings
    log_level: str = 'INFO'
    log_file: str = 'video_processing.log'
    
    # OCR settings
    languages: List[str] = field(default_factory=lambda: ['eng'])  # List of languages to use
    tesseract_config: Optional[str] = None
```

### Language Configuration

You can specify multiple languages for OCR processing. The languages are processed in order, and results are combined. Available language codes:
- `eng`: English
- `chi_sim`: Simplified Chinese
- `chi_tra`: Traditional Chinese

Example configuration for multiple languages:
```python
config = Config(languages=['eng', 'chi_sim', 'chi_tra'])
```

## Usage

1. Place your video files in the `input` folder
2. Configure the desired languages in `config.py`
3. Run the script:
```bash
python main.py
```

4. The processed results will be saved in the `output` folder
5. Check the `video_processing.log` file for detailed processing information

### Output Structure

- `output/`: Contains the final word lists for each video
- `frames/`: Contains extracted video frames
- `text/`: Contains OCR results for each frame
- `video_processing.log`: Contains detailed processing logs

## Error Handling

The tool includes comprehensive error handling:
- Continues processing if individual frames fail
- Continues processing if individual videos fail
- Logs all errors and warnings
- Creates necessary directories automatically
- Validates input files and paths
- Handles language-specific OCR errors gracefully

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


