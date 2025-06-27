"""
AR Sticker Factory - ComfyUI Custom Node
Generate AR-ready stickers with FLUX.1-schnell and SAM2
"""

from .nodes.ar_sticker_generator import ARStickerGenerator
from .nodes.sam2_segmenter import SAM2Segmenter
from .nodes.usdz_exporter import USDZExporter

# ComfyUI Node Registration
NODE_CLASS_MAPPINGS = {
    "ARStickerGenerator": ARStickerGenerator,
    "SAM2Segmenter": SAM2Segmenter,
    "USDZExporter": USDZExporter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ARStickerGenerator": "AR Sticker Generator",
    "SAM2Segmenter": "SAM2 Background Removal",
    "USDZExporter": "USDZ AR Exporter",
}

# ComfyUI Web Extension Support
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
