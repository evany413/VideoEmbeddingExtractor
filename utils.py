import os
import logging
import ffmpeg
import pytesseract
import cv2
import numpy as np
from PIL import Image
from typing import List, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)

def calculate_frame_info(video_path: str, frame_gap: float) -> Tuple[float, int, int]:
    """
    Calculate video duration, number of frames, and required digits for frame filenames.
    
    Args:
        video_path: Path to the video file
        frame_gap: Time gap between frames in seconds
        
    Returns:
        Tuple containing (duration, num_frames, num_digits)
        
    Raises:
        FileNotFoundError: If video file doesn't exist
        ffmpeg.Error: If video probing fails
    """
    try:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        # Get video duration
        probe = ffmpeg.probe(video_path)
        duration = float(probe['streams'][0]['duration'])
        
        # Calculate number of frames
        num_frames = int(duration / frame_gap)
        
        # Calculate required number of digits for frame filenames
        num_digits = len(str(num_frames))
        
        logger.info(f"Video duration: {duration:.2f}s")
        logger.info(f"Number of frames to extract: {num_frames}")
        logger.info(f"Using {num_digits} digits for frame filenames")
        
        return duration, num_frames, num_digits
        
    except Exception as e:
        logger.error(f"Error calculating frame info: {str(e)}")
        raise

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
        logger.info(f"Extracting frames from video: {video_path}")
        
        # Calculate frame information
        duration, num_frames, num_digits = calculate_frame_info(video_path, config.frame_gap)
        
        # Create output pattern with calculated digits
        output_pattern = os.path.join(config.frames_folder, f'%0{num_digits}d.jpg')
        
        # get frames from video
        video = ffmpeg.input(video_path)
        
        try:
            # Calculate frame rate based on frame gap
            frame_rate = 1.0 / config.frame_gap
            video.output(output_pattern, start_number=0, r=frame_rate).run(capture_stdout=True, capture_stderr=True)
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
            
            # Preprocess the image
            processed_image = preprocess_image(frame, config)
            
            # Extract text using all configured languages
            frame_text = []
            for lang in config.languages:
                try:
                    lang_text = pytesseract.image_to_string(
                        processed_image,
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
                
                # Save frame text if enabled
                if config.save_frame_text:
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
def save_results(results: List[str], video_name: str) -> None:
    """
    Save results to output file in the root directory.
    
    Args:
        results: List of results to save
        video_name: Name of the video file (without extension)
        
    Raises:
        IOError: If file writing fails
    """
    try:
        # Save the deduplicated word list in the root directory
        output_path = f'{video_name}_words.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))
            
        logger.info(f"Successfully saved results to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        raise

def preprocess_image(image_path: str, config: Config = Config()) -> np.ndarray:
    """
    Preprocess the image for better OCR results.
    
    Args:
        image_path: Path to the input image
        config: Configuration object containing settings
        
    Returns:
        Preprocessed image as numpy array in RGB format
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image is invalid or processing fails
    """
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")
            
        # Save original image if debug mode is enabled
        if config.debug:
            debug_path = os.path.join(config.debug_folder, f"{os.path.basename(image_path)}_original.jpg")
            cv2.imwrite(debug_path, image)
            logger.debug(f"Saved original image to: {debug_path}")
            
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if config.debug:
            debug_path = os.path.join(config.debug_folder, f"{os.path.basename(image_path)}_gray.jpg")
            cv2.imwrite(debug_path, gray)
            logger.debug(f"Saved grayscale image to: {debug_path}")
        
        # Apply thresholding
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        if config.debug:
            debug_path = os.path.join(config.debug_folder, f"{os.path.basename(image_path)}_thresh.jpg")
            cv2.imwrite(debug_path, thresh)
            logger.debug(f"Saved thresholded image to: {debug_path}")
        
        # Apply dilation to remove noise
        kernel = np.ones((3,3), np.uint8)
        dilate = cv2.dilate(thresh, kernel, iterations=2)
        if config.debug:
            debug_path = os.path.join(config.debug_folder, f"{os.path.basename(image_path)}_dilate.jpg")
            cv2.imwrite(debug_path, dilate)
            logger.debug(f"Saved dilated image to: {debug_path}")
        
        # Find contours
        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours on original image
        image = cv2.drawContours(image, contours, -1, (0, 0, 255), 3)
        if config.debug:
            debug_path = os.path.join(config.debug_folder, f"{os.path.basename(image_path)}_contours.jpg")
            cv2.imwrite(debug_path, image)
            logger.debug(f"Saved image with contours to: {debug_path}")
        
        # Convert BGR to RGB for pytesseract
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if config.debug:
            debug_path = os.path.join(config.debug_folder, f"{os.path.basename(image_path)}_final.jpg")
            cv2.imwrite(debug_path, cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))  # Convert back to BGR for saving
            logger.debug(f"Saved final RGB image to: {debug_path}")
        
        return image_rgb
        
    except Exception as e:
        logger.error(f"Error preprocessing image {image_path}: {str(e)}")
        raise ValueError(f"Failed to preprocess image: {str(e)}")

