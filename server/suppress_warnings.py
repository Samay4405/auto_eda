"""
Suppress common warnings from optional dependencies
"""
import warnings
import sys
import os

# Suppress HuggingFace Hub warnings
warnings.filterwarnings("ignore", message=".*huggingface_hub.*")

# Redirect stderr temporarily to suppress import errors
class SuppressStderr:
    def __enter__(self):
        self.old_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        return self
    
    def __exit__(self, *args):
        sys.stderr.close()
        sys.stderr = self.old_stderr

# Apply suppression
with SuppressStderr():
    pass  # Suppression active for imports
