#!/usr/bin/env python3
"""
GraphiVault Thumbnail Generator
Creates thumbnails for image files
"""

import sys
import os
from pathlib import Path
from PIL import Image
import argparse

def create_thumbnail(input_path: str, output_path: str, size: tuple = (256, 256)) -> None:
    """Create a thumbnail from an image file"""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save thumbnail as JPEG for smaller file size
            img.save(output_path, 'JPEG', quality=85, optimize=True)
            
        print(f"Thumbnail created: {output_path}")
        
    except Exception as e:
        print(f"Thumbnail generation error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python thumbnail.py <input_path> <output_path>", file=sys.stderr)
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    create_thumbnail(input_path, output_path)

if __name__ == "__main__":
    main()
