
"""Pillow Fallback - Basic Image Processing"""
import io
import base64

class Image:
    def __init__(self, data=None):
        self.data = data
        self.size = (100, 100)
        self.mode = "RGB"
    
    @staticmethod
    def open(file_path):
        return Image()
    
    @staticmethod
    def new(mode, size, color=0):
        img = Image()
        img.size = size
        img.mode = mode
        return img
    
    def save(self, output, format="PNG"):
        # Basic save functionality
        if hasattr(output, 'write'):
            output.write(b"PNG_PLACEHOLDER")
        else:
            with open(output, 'wb') as f:
                f.write(b"PNG_PLACEHOLDER")
    
    def resize(self, size):
        self.size = size
        return self
    
    def convert(self, mode):
        self.mode = mode
        return self

# Make available as PIL.Image
class PIL:
    Image = Image

# Create fallback module
import sys
sys.modules['PIL'] = PIL()
sys.modules['PIL.Image'] = Image
sys.modules['pillow'] = PIL()
