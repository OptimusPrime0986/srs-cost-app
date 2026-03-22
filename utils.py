"""
Utility Functions Module
Common utility functions used across the application.
"""

import re
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


def format_inr(amount: float) -> str:
    """
    Format amount in Indian Rupee format with appropriate suffix.
    
    Args:
        amount: Amount in INR
        
    Returns:
        Formatted string with ₹ symbol
    """
    if amount >= 10000000:  # 1 Crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 Lakh
        return f"₹{amount/100000:.2f} L"
    elif amount >= 1000:
        return f"₹{amount/1000:.2f}K"
    else:
        return f"₹{amount:,.0f}"


def format_inr_full(amount: float) -> str:
    """
    Format amount in full Indian Rupee format with commas.
    
    Args:
        amount: Amount in INR
        
    Returns:
        Formatted string with ₹ symbol and commas
    """
    # Indian number formatting (e.g., 12,34,567.89)
    int_part = int(amount)
    dec_part = amount - int_part
    
    int_str = str(int_part)
    if len(int_str) <= 3:
        formatted = int_str
    else:
        # Add commas Indian style
        formatted = int_str[-3:]
        remaining = int_str[:-3]
        while remaining:
            formatted = remaining[-2:] + ',' + formatted
            remaining = remaining[:-2]
    
    if dec_part > 0:
        return f"₹{formatted}.{int(dec_part * 100):02d}"
    return f"₹{formatted}"


def parse_duration(weeks: int) -> str:
    """
    Convert weeks to human-readable duration.
    
    Args:
        weeks: Number of weeks
        
    Returns:
        Human-readable duration string
    """
    if weeks < 4:
        return f"{weeks} week{'s' if weeks > 1 else ''}"
    
    months = weeks / 4.33
    if months < 12:
        return f"{months:.1f} months"
    
    years = months / 12
    remaining_months = months % 12
    
    if remaining_months < 0.5:
        return f"{years:.0f} year{'s' if years > 1 else ''}"
    
    return f"{int(years)} year{'s' if years > 1 else ''} {int(remaining_months)} months"


def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:!?\-()\'\"]+', '', text)
    
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def get_risk_color(risk_level: str) -> str:
    """
    Get color code for risk level.
    
    Args:
        risk_level: low, medium, or high
        
    Returns:
        Color code
    """
    colors = {
        'low': '#28a745',      # Green
        'medium': '#ffc107',   # Yellow
        'high': '#dc3545'      # Red
    }
    return colors.get(risk_level, '#6c757d')  # Gray default


def get_complexity_color(complexity: str) -> str:
    """
    Get color code for complexity level.
    
    Args:
        complexity: low, medium, high, or very_high
        
    Returns:
        Color code
    """
    colors = {
        'low': '#28a745',       # Green
        'medium': '#17a2b8',    # Blue
        'high': '#ffc107',      # Yellow
        'very_high': '#dc3545'  # Red
    }
    return colors.get(complexity, '#6c757d')


def create_progress_bar(percentage: float, width: int = 20) -> str:
    """
    Create a text-based progress bar.
    
    Args:
        percentage: Progress percentage (0-100)
        width: Width of the progress bar
        
    Returns:
        Text progress bar string
    """
    filled = int(width * percentage / 100)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {percentage:.1f}%"


def estimate_reading_time(text: str, wpm: int = 200) -> str:
    """
    Estimate reading time for text.
    
    Args:
        text: Text content
        wpm: Words per minute reading speed
        
    Returns:
        Human-readable reading time
    """
    word_count = len(text.split())
    minutes = word_count / wpm
    
    if minutes < 1:
        return "< 1 min"
    elif minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = int(minutes / 60)
        remaining = int(minutes % 60)
        return f"{hours}h {remaining}m"


def generate_project_id() -> str:
    """
    Generate a unique project ID.
    
    Returns:
        Project ID string
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"PROJ-{timestamp}"


def export_to_json(data: Dict[str, Any]) -> str:
    """
    Export data to JSON string.
    
    Args:
        data: Dictionary to export
        
    Returns:
        JSON string
    """
    def json_serializer(obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    return json.dumps(data, indent=2, default=json_serializer)


def calculate_confidence_level(score: float) -> str:
    """
    Convert confidence score to descriptive level.
    
    Args:
        score: Confidence score (0-1)
        
    Returns:
        Descriptive confidence level
    """
    if score >= 0.8:
        return "High"
    elif score >= 0.6:
        return "Medium"
    elif score >= 0.4:
        return "Low"
    else:
        return "Very Low"


def format_list_as_bullet_points(items: List[str], bullet: str = "•") -> str:
    """
    Format a list as bullet points.
    
    Args:
        items: List of items
        bullet: Bullet character
        
    Returns:
        Formatted bullet point string
    """
    return '\n'.join(f"{bullet} {item}" for item in items)


class AnalysisCache:
    """
    Simple cache for analysis results.
    """
    
    def __init__(self, max_size: int = 100):
        self._cache: Dict[str, Any] = {}
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        if len(self._cache) >= self._max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = value
    
    def clear(self) -> None:
        self._cache.clear()