import os
import logging
from typing import List
import utils
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

def get_videos(input_folder: str) -> List[str]:
    """
    Get list of video files from input folder.
    
    Args:
        input_folder: Path to input folder
        
    Returns:
        List of video file paths
        
    Raises:
        FileNotFoundError: If input folder doesn't exist
    """
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Input folder not found: {input_folder}")
        
    videos = [f for f in os.listdir(input_folder) 
              if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    if not videos:
        logger.warning(f"No video files found in {input_folder}")
        
    return videos

def dedup_words(texts: List[str]) -> List[str]:
    """
    Remove duplicate words from a list of text strings.
    
    Args:
        texts: List of text strings
        
    Returns:
        List of unique words
    """
    wordSet = set()
    for text in texts:
        words = text.split()
        wordSet.update(words)
    return sorted(list(wordSet))

def process_video(video_path: str, config: Config) -> None:
    """
    Process a single video file.
    
    Args:
        video_path: Path to video file
        config: Configuration object
        
    Raises:
        Exception: If any step of processing fails
    """
    try:
        logger.info(f"Processing video: {video_path}")
        
        # get frames from video
        frames = utils.get_frames(video_path, config)
        
        # extract text from frames
        text = utils.extract_text(frames, config)
        
        # dedup words and output as text file
        words = dedup_words(text)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        utils.save_results(words, config.output_folder, video_name, config)
        
        logger.info(f"Successfully processed video: {video_path}")
        
    except Exception as e:
        logger.error(f"Error processing video {video_path}: {str(e)}")
        raise

def main():
    """
    Main entry point for the video processing application.
    """
    try:
        config = Config()
        logger.info("Starting video processing application")
        
        # get videos from input folder
        videos = get_videos(config.input_folder)
        
        if not videos:
            logger.error("No videos to process. Exiting.")
            return
            
        # Process each video
        for video in videos:
            video_path = os.path.join(config.input_folder, video)
            try:
                process_video(video_path, config)
            except Exception as e:
                logger.error(f"Failed to process video {video}: {str(e)}")
                # Continue with next video instead of failing completely
                continue
                
        logger.info("Video processing completed")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 