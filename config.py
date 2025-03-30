import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class Config:
    # OCR settings
    languages: List[str] = field(default_factory=lambda: ['eng'])
    tesseract_config: str = ''
    
    # Frame extraction settings
    frame_gap: float = 5.0  # seconds between frames
    save_frames: bool = False  # whether to save frame screenshots
    save_frame_text: bool = False  # whether to save text for each frame
    
    # Debug settings
    debug: bool = False  # whether to save debug images
    debug_folder: str = 'debug'  # folder for debug images
    
    # Logging
    log_file: str = 'video_processing.log'
    
    # Folder paths
    frames_folder: str = 'frames'
    text_folder: str = 'text'
    
    def __post_init__(self):
        # Create all necessary directories
        for folder in [self.frames_folder, self.text_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # Create debug folder if debug mode is enabled
        if self.debug:
            os.makedirs(self.debug_folder, exist_ok=True)
        
        # Validate languages
        self._validate_languages()
    
    def _validate_languages(self):
        """Validate that all specified languages are installed."""
        import pytesseract
        try:
            # Get list of installed languages
            installed_langs = pytesseract.get_languages()
            
            # Check each language
            for lang in self.languages:
                # Split combined language string and check each
                lang_parts = lang.split('+')
                missing_langs = [part for part in lang_parts if part not in installed_langs]
                if missing_langs:
                    raise ValueError(
                        f"Missing language data files for: {', '.join(missing_langs)}. "
                        f"Please install the required language data files for Tesseract."
                    )
        except Exception as e:
            raise ValueError(f"Error validating languages: {str(e)}") 