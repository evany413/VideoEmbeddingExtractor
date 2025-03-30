import os
import logging
import shutil
import sys
from typing import List
import utils
from config import Config
import argparse

def setup_logging(config: Config):
    """
    Set up logging configuration.
    
    Args:
        config: Configuration object containing logging settings
    """
    # Set log level based on debug mode
    log_level = logging.DEBUG if config.debug else logging.INFO
    
    # Create formatters
    debug_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    user_formatter = logging.Formatter('%(message)s')
    
    # Create handlers
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setFormatter(debug_formatter)
    file_handler.setLevel(logging.DEBUG)  # Always log everything to file
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(user_formatter)
    console_handler.setLevel(log_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def cleanup_folders(config: Config):
    """
    Clean up temporary folders if they're not needed.
    
    Args:
        config: Configuration object
    """
    try:
        if not config.save_frames and os.path.exists(config.frames_folder):
            shutil.rmtree(config.frames_folder)
        if not config.save_frame_text and os.path.exists(config.text_folder):
            shutil.rmtree(config.text_folder)
    except Exception as e:
        logging.warning(f"Failed to clean up folders: {str(e)}")

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
        if text.strip():  # Only process non-empty strings
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
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Processing video: {video_path}")
        
        # get frames from video
        frames = utils.get_frames(video_path, config)
        if not frames:
            raise ValueError("No frames were extracted from the video")
        
        # extract text from frames
        text = utils.extract_text(frames, config)
        if not text:
            logger.warning("No text was extracted from any frames")
            return
        
        # dedup words and output as text file
        words = dedup_words(text)
        if not words:
            logger.warning("No words were extracted after deduplication")
            return
            
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        utils.save_results(words, video_name)
        
        logger.info("✓ Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

def main():
    """
    Main entry point for the video processing application.
    """
    try:
        # Add command line argument parsing
        parser = argparse.ArgumentParser(description='Video text extraction and processing')
        
        # Create a mutually exclusive group for video path arguments
        video_group = parser.add_mutually_exclusive_group(required=True)
        video_group.add_argument('video_path', nargs='?', help='Path to video file to process')
        video_group.add_argument('--video', type=str, help='Path to video file to process')
        
        parser.add_argument('--frame-gap', 
                          type=float, 
                          default=5.0,
                          help='Gap between frames in seconds (default: 5.0)')
        parser.add_argument('--save-frames', 
                          action='store_true',
                          help='Save frame screenshots (default: False)')
        parser.add_argument('--save-frame-text',
                          action='store_true', 
                          help='Save text for each frame (default: False)')
        parser.add_argument('--languages',
                          type=str,
                          nargs='+',
                          default=['eng'],
                          help='Languages to use for OCR (default: eng). Can be combined with +. Example: eng+chi_tra')
        parser.add_argument('--debug',
                          action='store_true',
                          help='Show detailed debug information (default: False)')
        
        args = parser.parse_args()
        
        # Get video path from either argument
        video_path = args.video_path or args.video
        
        # Create config with all parameters at once
        config = Config(
            frame_gap=args.frame_gap,
            save_frames=args.save_frames,
            save_frame_text=args.save_frame_text,
            languages=args.languages,
            debug=args.debug
        )
        
        # Set up logging with file handler after config is created
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        if config.debug:
            logger.info("Starting video processing application")
            logger.info(f"Frame gap: {config.frame_gap}s")
            logger.info(f"Save frames: {config.save_frames}")
            logger.info(f"Save frame text: {config.save_frame_text}")
            logger.info(f"Languages: {', '.join(config.languages)}")
            logger.info(f"Debug mode: {config.debug}")
        else:
            logger.info("Starting video processing...")
        
        # Process video file
        if not os.path.exists(video_path):
            logger.error(f"Error: Video file not found: {video_path}")
            sys.exit(1)
        if not video_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            logger.error(f"Error: Invalid video file format: {video_path}")
            sys.exit(1)
            
        try:
            process_video(video_path, config)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            sys.exit(1)
        finally:
            # Clean up temporary folders
            cleanup_folders(config)
            
        if config.debug:
            logger.info("Video processing completed")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 