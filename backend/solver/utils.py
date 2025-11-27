"""
Utility functions
Logging, timeout management, data cleaning
"""
import time
import logging
import sys
from typing import Any, Optional


def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('quiz_bot.log')
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('playwright').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


class TimeoutManager:
    """Manages timeout for quiz processing"""
    
    def __init__(self, max_seconds: int):
        self.max_seconds = max_seconds
        self.start_time = time.time()
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time
    
    def remaining(self) -> float:
        """Get remaining time in seconds"""
        return max(0, self.max_seconds - self.elapsed())
    
    def is_expired(self) -> bool:
        """Check if timeout is expired"""
        return self.elapsed() >= self.max_seconds
    
    def check_timeout(self, buffer: float = 10.0):
        """Raise exception if approaching timeout"""
        if self.remaining() < buffer:
            raise TimeoutError(f"Approaching timeout limit ({self.max_seconds}s)")


def sanitize_string(s: str) -> str:
    """Sanitize string for safe processing"""
    if not isinstance(s, str):
        return str(s)
    
    # Remove control characters
    sanitized = ''.join(char for char in s if char.isprintable() or char.isspace())
    
    # Limit length
    max_length = 10000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def safe_float(value: Any) -> Optional[float]:
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int(value: Any) -> Optional[int]:
    """Safely convert value to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def extract_numbers(text: str) -> list:
    """Extract all numbers from text"""
    import re
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def clean_dataframe_columns(df):
    """Clean DataFrame column names"""
    import pandas as pd
    
    # Remove whitespace
    df.columns = df.columns.str.strip()
    
    # Replace special characters
    df.columns = df.columns.str.replace(r'[^\w\s]', '', regex=True)
    
    # Replace spaces with underscores
    df.columns = df.columns.str.replace(' ', '_')
    
    # Convert to lowercase
    df.columns = df.columns.str.lower()
    
    return df


def detect_encoding(content: bytes) -> str:
    """Detect encoding of byte content"""
    import chardet
    
    try:
        result = chardet.detect(content)
        return result.get('encoding', 'utf-8')
    except:
        return 'utf-8'
