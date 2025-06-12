#!/usr/bin/env python3
"""
GraphiVault Image Processor
Handles image validation, thumbnail generation, and metadata extraction
Supports multiple formats with security-first processing
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json

try:
    from PIL import Image, ImageOps, ExifTags
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ImageProcessor:
    """
    Image Processor - The guardian of image operations
    
    Features:
    - Secure image validation and format detection
    - High-quality thumbnail generation
    - EXIF metadata extraction and sanitization
    - Format conversion and optimization
    - Security-focused image processing (prevents malicious files)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize image processor"""
        self.config = {
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
            'thumbnail_size': (256, 256),
            'thumbnail_quality': 85,
            'extract_metadata': True,
            'sanitize_metadata': True,
            **config
        }
        
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL/Pillow is required for image processing")
    
    def validate_image(self, file_path: Path) -> bool:
        """
        Validate image file for security and format compliance
        """
        try:
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.config['max_file_size']:
                return False
            
            # Check file extension
            file_ext = file_path.suffix.lower().lstrip('.')
            if file_ext not in self.config['supported_formats']:
                return False
            
            # Validate MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type or not mime_type.startswith('image/'):
                return False
            
            # Try to open and validate image with PIL
            with Image.open(file_path) as img:
                # Verify image format
                if img.format is None:
                    return False
                
                # Check image dimensions (prevent extremely large images)
                width, height = img.size
                if width > 50000 or height > 50000:
                    return False
                
                # Verify image integrity by loading a small portion
                img.load()
                
                # Additional security checks
                if not self._security_check(img):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_mime_type(self, file_path: Path) -> str:
        """Get MIME type of image file"""
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return mime_type or 'application/octet-stream'
        except Exception:
            return 'application/octet-stream'
    
    def create_thumbnail(self, input_path: str, output_path: str, 
                        size: Optional[Tuple[int, int]] = None) -> bool:
        """
        Create high-quality thumbnail from image
        """
        try:
            thumbnail_size = size or self.config['thumbnail_size']
            
            with Image.open(input_path) as img:
                # Convert to RGB if necessary (for PNG with transparency, etc.)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Apply EXIF orientation
                img = ImageOps.exif_transpose(img)
                
                # Create thumbnail with high-quality resampling
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Ensure output directory exists
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Save thumbnail as JPEG for smaller file size
                img.save(
                    output_path, 
                    'JPEG', 
                    quality=self.config['thumbnail_quality'],
                    optimize=True,
                    progressive=True
                )
            
            return True
            
        except Exception:
            return False
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract and sanitize image metadata
        """
        metadata = {
            'format': None,
            'mode': None,
            'size': None,
            'file_size': 0,
            'has_transparency': False,
            'color_profile': None,
            'exif': {},
            'creation_date': None,
            'camera_info': {}
        }
        
        try:
            # Basic file information
            metadata['file_size'] = file_path.stat().st_size
            
            with Image.open(file_path) as img:
                # Basic image properties
                metadata['format'] = img.format
                metadata['mode'] = img.mode
                metadata['size'] = img.size
                metadata['has_transparency'] = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                
                # Color profile information
                if hasattr(img, 'info') and 'icc_profile' in img.info:
                    metadata['color_profile'] = 'ICC'
                
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif_data = img._getexif()
                    metadata['exif'] = self._process_exif_data(exif_data)
                    
                    # Extract specific camera and date information
                    metadata['camera_info'] = self._extract_camera_info(metadata['exif'])
                    metadata['creation_date'] = self._extract_creation_date(metadata['exif'])
            
            # Sanitize metadata if enabled
            if self.config['sanitize_metadata']:
                metadata = self._sanitize_metadata(metadata)
            
            return metadata
            
        except Exception:
            return metadata
    
    def optimize_image(self, input_path: str, output_path: str, 
                      quality: int = 90, max_dimension: int = 2048) -> bool:
        """
        Optimize image for storage (optional feature)
        """
        try:
            with Image.open(input_path) as img:
                # Apply EXIF orientation
                img = ImageOps.exif_transpose(img)
                
                # Resize if too large
                if max(img.size) > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Save optimized image
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                img.save(
                    output_path,
                    'JPEG',
                    quality=quality,
                    optimize=True,
                    progressive=True
                )
            
            return True
            
        except Exception:
            return False
    
    def _security_check(self, img: Image.Image) -> bool:
        """
        Perform additional security checks on image
        """
        try:
            # Check for suspicious metadata
            if hasattr(img, 'info'):
                # Check for potentially malicious metadata
                suspicious_keys = ['comment', 'software', 'artist', 'copyright']
                for key in suspicious_keys:
                    if key in img.info:
                        value = str(img.info[key])
                        # Check for script-like content
                        if any(tag in value.lower() for tag in ['<script', 'javascript:', 'data:']):
                            return False
            
            # Check image dimensions ratio (prevent zip bombs)
            width, height = img.size
            if width * height > 100_000_000:  # 100 megapixels
                return False
            
            # Additional format-specific checks
            if img.format == 'GIF':
                # Check for excessive frame count
                if hasattr(img, 'n_frames') and img.n_frames > 100:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _process_exif_data(self, exif_data: Dict) -> Dict[str, Any]:
        """
        Process and clean EXIF data
        """
        processed_exif = {}
        
        try:
            for tag_id, value in exif_data.items():
                # Get tag name
                tag_name = TAGS.get(tag_id, str(tag_id))
                
                # Skip binary data and GPS coordinates (privacy)
                if isinstance(value, bytes) or tag_name in ['GPSInfo', 'MakerNote']:
                    continue
                
                # Convert value to string and limit length
                str_value = str(value)
                if len(str_value) > 256:
                    str_value = str_value[:256] + '...'
                
                processed_exif[tag_name] = str_value
            
        except Exception:
            pass
        
        return processed_exif
    
    def _extract_camera_info(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract camera-specific information from EXIF
        """
        camera_info = {}
        
        try:
            # Camera make and model
            if 'Make' in exif_data:
                camera_info['make'] = exif_data['Make']
            if 'Model' in exif_data:
                camera_info['model'] = exif_data['Model']
            
            # Lens information
            if 'LensModel' in exif_data:
                camera_info['lens'] = exif_data['LensModel']
            
            # Camera settings
            settings = {}
            if 'FNumber' in exif_data:
                settings['aperture'] = exif_data['FNumber']
            if 'ExposureTime' in exif_data:
                settings['shutter_speed'] = exif_data['ExposureTime']
            if 'ISOSpeedRatings' in exif_data:
                settings['iso'] = exif_data['ISOSpeedRatings']
            if 'FocalLength' in exif_data:
                settings['focal_length'] = exif_data['FocalLength']
            
            if settings:
                camera_info['settings'] = settings
                
        except Exception:
            pass
        
        return camera_info
    
    def _extract_creation_date(self, exif_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract image creation date from EXIF
        """
        try:
            # Try different date fields
            date_fields = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
            
            for field in date_fields:
                if field in exif_data:
                    date_str = exif_data[field]
                    # Basic validation of date format
                    if len(date_str) >= 19 and ':' in date_str:
                        return date_str
            
        except Exception:
            pass
        
        return None
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata to remove potentially sensitive information
        """
        sanitized = metadata.copy()
        
        try:
            # Remove GPS and location data
            if 'exif' in sanitized:
                exif_copy = sanitized['exif'].copy()
                
                # Remove privacy-sensitive fields
                sensitive_fields = [
                    'GPSInfo', 'GPSLatitude', 'GPSLongitude', 'GPSAltitude',
                    'UserComment', 'Artist', 'Copyright', 'Software',
                    'HostComputer', 'OwnerName', 'CameraOwnerName'
                ]
                
                for field in sensitive_fields:
                    exif_copy.pop(field, None)
                
                sanitized['exif'] = exif_copy
            
            # Remove potentially sensitive camera info
            if 'camera_info' in sanitized:
                camera_copy = sanitized['camera_info'].copy()
                # Keep only basic technical information
                allowed_fields = ['make', 'model', 'lens', 'settings']
                sanitized['camera_info'] = {
                    k: v for k, v in camera_copy.items() 
                    if k in allowed_fields
                }
            
        except Exception:
            pass
        
        return sanitized
