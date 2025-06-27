"""
USDZ Exporter Node
Export images as AR-ready USDZ files for iOS QuickLook with fallback support
"""

import numpy as np
from PIL import Image
import os
import json
from ..utils.usdz_creation import (
    create_usdz_from_image, 
    create_fallback_obj, 
    USD_AVAILABLE
)


class USDZExporter:
    """
    ComfyUI node for exporting images as USDZ AR files with fallback to OBJ/PNG
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "scale": (
                    "FLOAT",
                    {"default": 0.1, "min": 0.01, "max": 2.0, "step": 0.01},
                ),
                "filename": ("STRING", {"default": "sticker", "multiline": False}),
                "material_type": (
                    ["matte", "glossy", "metallic"],
                    {"default": "matte"},
                ),
                "ar_behavior": (
                    ["billboard", "fixed", "physics"],
                    {"default": "billboard"},
                ),
                "optimize_mobile": (
                    "BOOLEAN",
                    {"default": True},
                ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_path", "format_type", "ar_instructions")
    FUNCTION = "export_ar_sticker"
    CATEGORY = "AR Sticker Factory"
    OUTPUT_NODE = True

    def export_ar_sticker(self, image, scale, filename, material_type, ar_behavior, optimize_mobile):
        """
        Export image as AR-ready file (USDZ preferred, OBJ/PNG fallback)
        """
        try:
            # Convert ComfyUI tensor to PIL Image
            image_np = (image.squeeze(0).numpy() * 255).astype(np.uint8)

            # Handle RGBA if present, ensure transparency
            if image_np.shape[2] == 4:
                pil_image = Image.fromarray(image_np, "RGBA")
            else:
                # Convert RGB to RGBA for AR transparency support
                pil_image = Image.fromarray(image_np, "RGB").convert("RGBA")

            # Optimize for mobile if requested
            if optimize_mobile:
                pil_image = self._optimize_for_mobile(pil_image)

            # Create output directories
            output_dir = os.path.join(os.getcwd(), "output", "ar_stickers")
            os.makedirs(output_dir, exist_ok=True)

            # Try USDZ export first
            if USD_AVAILABLE:
                output_path = os.path.join(output_dir, f"{filename}.usdz")
                success = create_usdz_from_image(
                    image=pil_image,
                    output_path=output_path,
                    scale=scale,
                    material_type=material_type,
                )
                
                if success:
                    # Add AR metadata for iOS QuickLook
                    self._create_ar_metadata(output_path, ar_behavior, scale)
                    
                    ar_instructions = self._generate_ar_instructions("usdz", filename)
                    print(f"✅ USDZ AR file created: {output_path}")
                    return (output_path, "usdz", ar_instructions)

            # Fallback to OBJ + PNG export
            print("📱 Using OBJ/PNG fallback for AR compatibility")
            
            # Save optimized PNG
            png_path = os.path.join(output_dir, f"{filename}_ar.png")
            pil_image.save(png_path, "PNG", optimize=True)
            
            # Create OBJ for 3D viewers
            obj_path = os.path.join(output_dir, f"{filename}.obj")
            obj_success = create_fallback_obj(pil_image, obj_path, scale)
            
            # Create AR instruction file
            instructions_path = os.path.join(output_dir, f"{filename}_ar_instructions.json")
            ar_data = {
                "format": "png_obj",
                "png_file": os.path.basename(png_path),
                "obj_file": os.path.basename(obj_path) if obj_success else None,
                "scale": scale,
                "behavior": ar_behavior,
                "instructions": self._generate_ar_instructions("png", filename)
            }
            
            with open(instructions_path, 'w') as f:
                json.dump(ar_data, f, indent=2)
            
            ar_instructions = self._generate_ar_instructions("png", filename)
            print(f"✅ AR-ready PNG created: {png_path}")
            return (png_path, "png", ar_instructions)

        except Exception as e:
            print(f"❌ Error in USDZExporter: {str(e)}")
            return (f"Error: {str(e)}", "error", "Export failed")

    def _optimize_for_mobile(self, image):
        """Optimize image for mobile AR performance"""
        # Limit resolution for mobile performance
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Optimize PNG compression
        return image

    def _create_ar_metadata(self, usdz_path, behavior, scale):
        """Create AR metadata for iOS QuickLook"""
        metadata_path = usdz_path.replace('.usdz', '_ar_info.json')
        metadata = {
            "ar_quicklook_compatible": True,
            "behavior": behavior,
            "scale": scale,
            "real_world_scale": f"{scale}m",
            "placement": "horizontal" if behavior == "physics" else "any",
            "instructions": {
                "ios": "Tap to place in AR, pinch to resize",
                "android": "Use AR Core compatible viewer"
            }
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _generate_ar_instructions(self, format_type, filename):
        """Generate AR viewing instructions"""
        if format_type == "usdz":
            return f"""🎯 AR Instructions for {filename}.usdz:

iOS (QuickLook):
1. Open {filename}.usdz on iPhone/iPad
2. Tap 'AR' to enter AR mode
3. Point camera at flat surface
4. Tap to place sticker
5. Pinch to resize, drag to move

Sharing:
• AirDrop to other iOS devices
• Works in Messages, Mail, Safari
• Compatible with AR Quick Look"""
        
        else:  # PNG fallback
            return f"""📱 AR Instructions for {filename}_ar.png:

iOS AR Apps:
1. Use AR apps like 'AR Stickers' or 'Holos'
2. Import the PNG file
3. Place on flat surfaces
4. Transparent background preserved

Android:
1. Use Google Lens or AR Core apps
2. Import PNG for AR overlay
3. Works with most AR camera apps

3D Viewers:
• Open {filename}.obj in 3D model viewers
• Blender, Meshlab, or online viewers"""
