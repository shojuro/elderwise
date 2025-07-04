import logging
import base64
import io
from typing import Dict, List, Optional, Tuple
from PIL import Image
import numpy as np

try:
    from google.cloud import vision
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Google Cloud Vision not available. Install with: pip install google-cloud-vision")

from src.config.settings import settings

logger = logging.getLogger(__name__)


class GoogleVisionClient:
    """Client for Google Vision API integration"""
    
    def __init__(self):
        self.client = None
        self.api_key = settings.google_vision_api_key
        
        if GOOGLE_VISION_AVAILABLE and self.api_key:
            try:
                # Initialize client with API key
                self.client = vision.ImageAnnotatorClient(
                    client_options={"api_key": self.api_key}
                )
                logger.info("Google Vision API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Vision client: {e}")
                self.client = None
        else:
            if not GOOGLE_VISION_AVAILABLE:
                logger.warning("Google Cloud Vision library not installed")
            if not self.api_key:
                logger.warning("Google Vision API key not configured")
    
    async def extract_text(self, image_data: str) -> List[str]:
        """
        Extract text from image using OCR
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            List of detected text strings
        """
        if not self.client:
            return []
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = vision.Image(content=image_bytes)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                # First annotation contains all text
                full_text = texts[0].description if texts else ""
                
                # Extract individual words (skip first as it's full text)
                words = [text.description for text in texts[1:]]
                
                # Filter for potential imprints (alphanumeric, common patterns)
                imprints = self._filter_pill_imprints(words)
                
                logger.info(f"Detected text: {imprints}")
                return imprints
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return []
    
    async def detect_colors(self, image_data: str) -> List[Dict[str, any]]:
        """
        Detect dominant colors in image
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            List of color information
        """
        if not self.client:
            return []
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = vision.Image(content=image_bytes)
            
            # Perform image properties detection
            response = self.client.image_properties(image=image)
            props = response.image_properties_annotation
            
            colors = []
            for color in props.dominant_colors.colors:
                color_info = {
                    'rgb': {
                        'red': int(color.color.red),
                        'green': int(color.color.green),
                        'blue': int(color.color.blue)
                    },
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction,
                    'name': self._rgb_to_color_name(
                        int(color.color.red),
                        int(color.color.green),
                        int(color.color.blue)
                    )
                }
                colors.append(color_info)
            
            return colors
            
        except Exception as e:
            logger.error(f"Error detecting colors: {e}")
            return []
    
    def _filter_pill_imprints(self, texts: List[str]) -> List[str]:
        """
        Filter detected text to likely pill imprints
        
        Args:
            texts: List of detected text strings
            
        Returns:
            Filtered list of potential imprints
        """
        imprints = []
        
        for text in texts:
            # Clean and uppercase
            text = text.strip().upper()
            
            # Skip if too long (likely not an imprint)
            if len(text) > 10:
                continue
            
            # Check if it matches common imprint patterns
            # - Contains numbers and letters
            # - All numbers
            # - Common drug prefixes
            if any(c.isdigit() for c in text) or len(text) <= 5:
                # Remove special characters except spaces and hyphens
                cleaned = ''.join(c for c in text if c.isalnum() or c in ' -')
                if cleaned:
                    imprints.append(cleaned)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_imprints = []
        for imprint in imprints:
            if imprint not in seen:
                seen.add(imprint)
                unique_imprints.append(imprint)
        
        return unique_imprints
    
    def _rgb_to_color_name(self, r: int, g: int, b: int) -> str:
        """
        Convert RGB values to common color name
        
        Args:
            r, g, b: RGB values (0-255)
            
        Returns:
            Color name
        """
        # Simple color classification
        if r > 200 and g > 200 and b > 200:
            return "white"
        elif r < 50 and g < 50 and b < 50:
            return "black"
        elif r > 150 and g < 100 and b < 100:
            return "red"
        elif r < 100 and g < 100 and b > 150:
            return "blue"
        elif r < 100 and g > 150 and b < 100:
            return "green"
        elif r > 200 and g > 150 and b < 100:
            return "yellow"
        elif r > 200 and g > 100 and b < 100:
            return "orange"
        elif r > 150 and g < 100 and b > 150:
            return "purple"
        elif r > 150 and g > 100 and b > 100:
            return "pink"
        elif r > 100 and g > 50 and b < 50:
            return "brown"
        elif r > 150 and g > 150 and b > 150:
            return "gray"
        else:
            return "unknown"
    
    async def enhance_for_ocr(self, image_data: str) -> str:
        """
        Enhance image for better OCR results
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            Enhanced base64 encoded image
        """
        try:
            # Decode image
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to grayscale for better OCR
            if img.mode != 'L':
                img = img.convert('L')
            
            # Apply contrast enhancement
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Apply sharpness enhancement
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Convert back to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            enhanced_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image_data


# Singleton instance
google_vision_client = GoogleVisionClient()