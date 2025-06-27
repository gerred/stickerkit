"""
AR Sticker Generator Node for ComfyUI
Created for NVIDIA x ComfyUI Hackathon 2025

This node generates AR-ready stickers from text prompts using:
1. Text-to-image generation (FLUX.1 or SDXL)
2. Background removal/segmentation (SAM2)
3. USDZ export for AR compatibility
"""

import torch
import numpy as np
from PIL import Image
import tempfile
import os
from typing import Dict, Any, Tuple, Optional


class ARStickerGenerator:
    """
    ComfyUI node for generating AR-ready stickers from text prompts.
    
    This node combines text-to-image generation with segmentation and 
    AR format export to create stickers suitable for AR applications.
    """
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models_loaded = False
        
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define the input interface for the ComfyUI node."""
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A cute cartoon sticker of a smiling cat with big eyes",
                    "placeholder": "Enter your sticker description..."
                }),
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": "background, blurry, low quality, watermark",
                    "placeholder": "What to avoid in the image..."
                }),
                "width": ("INT", {
                    "default": 512,
                    "min": 256,
                    "max": 2048,
                    "step": 64
                }),
                "height": ("INT", {
                    "default": 512,
                    "min": 256,
                    "max": 2048,
                    "step": 64
                }),
                "steps": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
                "cfg_scale": ("FLOAT", {
                    "default": 7.5,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.1
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 4294967295
                }),
                "model_type": (["flux", "sdxl"], {
                    "default": "flux"
                }),
                "export_format": (["png", "usdz", "both"], {
                    "default": "both"
                })
            },
            "optional": {
                "input_image": ("IMAGE",),
                "mask": ("MASK",)
            }
        }
    
    @classmethod
    def RETURN_TYPES(cls) -> Tuple[str, ...]:
        """Define what this node outputs."""
        return ("IMAGE", "MASK", "STRING", "STRING")
    
    @classmethod 
    def RETURN_NAMES(cls) -> Tuple[str, ...]:
        """Define names for the outputs."""
        return ("image", "mask", "png_path", "usdz_path")
    
    @classmethod
    def FUNCTION(cls) -> str:
        """Define the main function name."""
        return "generate_ar_sticker"
    
    @classmethod
    def CATEGORY(cls) -> str:
        """Define the category where this node appears in ComfyUI."""
        return "AR Sticker Factory"
    
    @classmethod
    def DESCRIPTION(cls) -> str:
        """Node description for ComfyUI UI."""
        return "Generate AR-ready stickers from text prompts with automatic background removal"
    
    def generate_ar_sticker(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg_scale: float,
        seed: int,
        model_type: str,
        export_format: str,
        input_image: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, str, str]:
        """
        Main execution function for the AR sticker generation pipeline.
        
        Args:
            prompt: Text description of the sticker
            negative_prompt: What to avoid in generation
            width, height: Output dimensions
            steps: Number of diffusion steps
            cfg_scale: Classifier-free guidance scale
            seed: Random seed (-1 for random)
            model_type: Which model to use (flux/sdxl)
            export_format: Output format (png/usdz/both)
            input_image: Optional input image for img2img
            mask: Optional mask for inpainting
            
        Returns:
            Tuple of (generated_image, mask, png_path, usdz_path)
        """
        try:
            # Handle seed
            if seed == -1:
                seed = torch.randint(0, 2**32 - 1, (1,)).item()
            
            # Set random seeds
            torch.manual_seed(seed)
            np.random.seed(seed)
            
            print(f"🎨 Generating AR sticker with prompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
            print(f"📐 Dimensions: {width}x{height}, Steps: {steps}, CFG: {cfg_scale}")
            print(f"🤖 Model: {model_type.upper()}, Format: {export_format}")
            
            # Step 1: Generate base image
            generated_image = self._generate_base_image(
                prompt, negative_prompt, width, height, steps, cfg_scale, seed, model_type, input_image
            )
            
            # Step 2: Remove background / create mask
            segmented_image, mask_tensor = self._remove_background(generated_image)
            
            # Step 3: Export in requested formats
            png_path, usdz_path = self._export_sticker(segmented_image, mask_tensor, export_format)
            
            print(f"✅ AR sticker generation complete!")
            print(f"📁 PNG: {png_path if png_path else 'Not exported'}")
            print(f"🥽 USDZ: {usdz_path if usdz_path else 'Not exported'}")
            
            return (segmented_image, mask_tensor, png_path or "", usdz_path or "")
            
        except Exception as e:
            print(f"❌ Error in AR sticker generation: {str(e)}")
            # Return error placeholders
            error_image = torch.zeros((1, height, width, 3))
            error_mask = torch.zeros((1, height, width))
            return (error_image, error_mask, f"Error: {str(e)}", "")
    
    def _generate_base_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg_scale: float,
        seed: int,
        model_type: str,
        input_image: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Generate the base image using the specified model.
        
        TODO: Implement actual model loading and generation
        Currently returns a placeholder for development.
        """
        print(f"🔄 Generating base image with {model_type.upper()} model...")
        
        # TODO: Load and use actual models (FLUX.1 or SDXL)
        # For now, create a placeholder image
        if input_image is not None:
            print("📸 Using input image for img2img generation")
            # Use input image as base
            return input_image
        else:
            # Create placeholder colored image for development
            print("🎲 Creating placeholder image for development")
            image_array = np.random.rand(height, width, 3) * 255
            image_array = image_array.astype(np.uint8)
            
            # Convert to ComfyUI tensor format (batch, height, width, channels)
            image_tensor = torch.from_numpy(image_array).float() / 255.0
            image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
            
            return image_tensor
    
    def _remove_background(self, image: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Remove background from the generated image using segmentation.
        
        TODO: Implement SAM2 or similar segmentation model
        Currently returns a placeholder mask.
        """
        print("🎭 Removing background with segmentation...")
        
        # TODO: Load and use SAM2 for background removal
        # For now, create a simple placeholder mask
        batch_size, height, width, channels = image.shape
        
        # Create a circular mask as placeholder
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 3
        
        y, x = torch.meshgrid(torch.arange(height), torch.arange(width), indexing='ij')
        mask = ((x - center_x) ** 2 + (y - center_y) ** 2) <= radius ** 2
        mask = mask.float().unsqueeze(0)  # Add batch dimension
        
        # Apply mask to image (set background to transparent)
        segmented_image = image.clone()
        # In a real implementation, we'd add an alpha channel here
        
        print("✂️ Background removal complete (placeholder)")
        return segmented_image, mask
    
    def _export_sticker(
        self,
        image: torch.Tensor,
        mask: torch.Tensor,
        export_format: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Export the sticker in the requested format(s).
        
        TODO: Implement actual USDZ export
        Currently creates placeholder files.
        """
        png_path = None
        usdz_path = None
        
        # Create output directory
        output_dir = "output/ar_stickers"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = torch.randint(10000, 99999, (1,)).item()
        
        if export_format in ["png", "both"]:
            png_path = self._export_png(image, mask, output_dir, timestamp)
        
        if export_format in ["usdz", "both"]:
            usdz_path = self._export_usdz(image, mask, output_dir, timestamp)
        
        return png_path, usdz_path
    
    def _export_png(self, image: torch.Tensor, mask: torch.Tensor, output_dir: str, timestamp: int) -> str:
        """Export as PNG with transparency."""
        print("💾 Exporting PNG with transparency...")
        
        # Convert tensor to PIL Image
        image_np = (image.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)
        
        # TODO: Apply mask as alpha channel
        # For now, save as regular PNG
        png_path = os.path.join(output_dir, f"ar_sticker_{timestamp}.png")
        pil_image.save(png_path)
        
        print(f"📁 PNG saved: {png_path}")
        return png_path
    
    def _export_usdz(self, image: torch.Tensor, mask: torch.Tensor, output_dir: str, timestamp: int) -> str:
        """Export as USDZ for AR applications."""
        print("🥽 Exporting USDZ for AR...")
        
        # TODO: Implement actual USDZ export with USD/MaterialX
        # For now, create a placeholder file
        usdz_path = os.path.join(output_dir, f"ar_sticker_{timestamp}.usdz")
        
        # Create placeholder file
        with open(usdz_path, 'wb') as f:
            f.write(b"USDZ placeholder - TODO: implement actual USDZ export")
        
        print(f"🥽 USDZ placeholder created: {usdz_path}")
        return usdz_path


# ComfyUI registration mappings
NODE_CLASS_MAPPINGS = {
    "ARStickerGenerator": ARStickerGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ARStickerGenerator": "AR Sticker Generator"
}
