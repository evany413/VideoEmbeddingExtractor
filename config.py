import os
from dataclasses import dataclass, field
from typing import List, Optional

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
    tesseract_config: Optional[str] = None  # Additional Tesseract configuration options
    
    def __post_init__(self):
        # Create all necessary directories
        for folder in [self.input_folder, self.output_folder, 
                      self.frames_folder, self.text_folder]:
            os.makedirs(folder, exist_ok=True)
            
        # Validate languages
        valid_languages = {'eng', 'chi_sim', 'chi_tra'}
        invalid_languages = set(self.languages) - valid_languages
        if invalid_languages:
            raise ValueError(f"Invalid language codes: {invalid_languages}. "
                           f"Valid codes are: {valid_languages}") 