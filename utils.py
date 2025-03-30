import os
import logging
import ffmpeg
import pytesseract
from PIL import Image
from typing import List, Optional
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# get frames from video (every 10 frames)
def get_frames(video_path: str, config: Config = Config()) -> List[str]:
    """
    Extract frames from a video file.
    
    Args:
        video_path: Path to the video file
        config: Configuration object containing settings
        
    Returns:
        List of paths to extracted frames
        
    Raises:
        FileNotFoundError: If video file doesn't exist
        ffmpeg.Error: If frame extraction fails
    """
    try:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        logger.info(f"Extracting frames from video: {video_path}")
        
        # get frames from video
        video = ffmpeg.input(video_path)
        output_pattern = os.path.join(config.frames_folder, '%04d.jpg')
        
        try:
            video.output(output_pattern, start_number=0, r=config.frame_rate).run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise

        # get frames from frames folder
        frames = [os.path.join(config.frames_folder, frame) 
                 for frame in os.listdir(config.frames_folder) 
                 if frame.endswith('.jpg')]
        
        logger.info(f"Successfully extracted {len(frames)} frames")
        return frames
        
    except Exception as e:
        logger.error(f"Error extracting frames: {str(e)}")
        raise

# extract text from frames
def extract_text(frames: List[str], config: Config = Config()) -> List[str]:
    """
    Extract text from frames using OCR.
    
    Args:
        frames: List of paths to frame images
        config: Configuration object containing settings
        
    Returns:
        List of extracted text strings
        
    Raises:
        FileNotFoundError: If frame files don't exist
        pytesseract.TesseractError: If OCR fails
    """
    text = []
    
    for frame in frames:
        try:
            if not os.path.exists(frame):
                raise FileNotFoundError(f"Frame file not found: {frame}")
                
            logger.info(f"Processing frame: {frame}")
            
            # Extract text using all configured languages
            frame_text = []
            for lang in config.languages:
                try:
                    lang_text = pytesseract.image_to_string(
                        Image.open(frame),
                        lang=lang,
                        config=config.tesseract_config
                    )
                    if lang_text.strip():  # Only add non-empty results
                        frame_text.append(lang_text)
                        logger.debug(f"Extracted text using {lang} for frame {frame}")
                except Exception as e:
                    logger.warning(f"Failed to extract text using {lang} for frame {frame}: {str(e)}")
                    continue
            
            if frame_text:
                # Combine text from all languages
                combined_text = '\n'.join(frame_text)
                text.append(combined_text)
                
                # output as text file with frame name
                frame_name = os.path.basename(frame)
                output_path = os.path.join(config.text_folder, f'{frame_name}.txt')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(combined_text)
                    
                logger.debug(f"Saved text to: {output_path}")
            else:
                logger.warning(f"No text extracted from frame {frame} using any language")
            
        except Exception as e:
            logger.error(f"Error processing frame {frame}: {str(e)}")
            # Continue with next frame instead of failing completely
            continue
            
    return text

# save results to output folder
def save_results(results: List[str], output_folder: str, video_name: str = 'results', config: Config = Config()) -> None:
    """
    Save results to output file.
    
    Args:
        results: List of results to save
        output_folder: Output directory path
        video_name: Name of the video file (without extension)
        config: Configuration object containing settings
        
    Raises:
        IOError: If file writing fails
    """
    try:
        output_path = os.path.join(output_folder, f'{video_name}.{config.output_format}')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))
            
        logger.info(f"Successfully saved results to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        raise

