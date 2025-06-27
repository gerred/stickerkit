"""
AR Sticker Factory - Custom ComfyUI Nodes
Created for NVIDIA x ComfyUI Hackathon 2025
"""

# Import from both the standalone node and the factory package
try:
    from .ar_sticker_generator import (
        NODE_CLASS_MAPPINGS as STANDALONE_MAPPINGS
    )
    from .ar_sticker_generator import (
        NODE_DISPLAY_NAME_MAPPINGS as STANDALONE_DISPLAY_MAPPINGS
    )
except ImportError:
    STANDALONE_MAPPINGS = {}
    STANDALONE_DISPLAY_MAPPINGS = {}

try:
    from .ar_sticker_factory import (
        NODE_CLASS_MAPPINGS as FACTORY_MAPPINGS
    )
    from .ar_sticker_factory import (
        NODE_DISPLAY_NAME_MAPPINGS as FACTORY_DISPLAY_MAPPINGS
    )
except ImportError:
    FACTORY_MAPPINGS = {}
    FACTORY_DISPLAY_MAPPINGS = {}

# Combine all mappings
NODE_CLASS_MAPPINGS = {**STANDALONE_MAPPINGS, **FACTORY_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {
    **STANDALONE_DISPLAY_MAPPINGS, **FACTORY_DISPLAY_MAPPINGS
}

# Export the mappings for ComfyUI registration
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Ensure ComfyUI can find our web resources
WEB_DIRECTORY = "./web"
