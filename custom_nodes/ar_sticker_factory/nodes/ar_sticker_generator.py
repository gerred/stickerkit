"""
AR Sticker Generator Node
Main generation node using SDXL for high-quality sticker creation
Optimized for fast, production-ready sticker generation on H100 GPUs
"""

import torch
import numpy as np
import time
from ..models.sdxl_loader import SDXLLoader
from .sam2_segmenter import SAM2Segmenter


class ARStickerGenerator:
    """
    ComfyUI node for generating stickers using SDXL
    Optimized for high-quality sticker generation with consistent results
    """

    # Sticker-optimized prompt templates
    STICKER_STYLE_PROMPTS = {
        "cartoon": "cartoon style, clean vector art, bold outlines, bright colors",
        "kawaii": "kawaii style, cute, pastel colors, soft shading, adorable",
        "pixel": "pixel art style, 8-bit, retro gaming, crisp pixels",
        "minimal": "minimalist design, simple shapes, clean lines, modern",
        "vibrant": "vibrant colors, high contrast, pop art style, bold",
    }

    STICKER_BACKGROUND_PROMPTS = {
        "clean_white": "clean white background, no shadows, pure white (#FFFFFF)",
        "transparent": "transparent background, cut-out style, no background",
        "subtle_shadow": "white background with subtle drop shadow",
        "gradient": "subtle gradient background, soft colors",
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "cute cartoon cat sticker, clean white background",
                    },
                ),
                "sticker_style": (
                    list(cls.STICKER_STYLE_PROMPTS.keys()),
                    {"default": "cartoon"},
                ),
                "background_style": (
                    list(cls.STICKER_BACKGROUND_PROMPTS.keys()),
                    {"default": "clean_white"},
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "blurry, low quality, photorealistic, realistic photo, human photo, messy background, cluttered, dark, muddy colors",
                    },
                ),
                "width": (
                    "INT",
                    {"default": 1024, "min": 512, "max": 1536, "step": 64},
                ),
                "height": (
                    "INT",
                    {"default": 1024, "min": 512, "max": 1536, "step": 64},
                ),
                "num_inference_steps": (
                    "INT",
                    {"default": 20, "min": 10, "max": 50, "step": 1},
                ),
                "guidance_scale": (
                    "FLOAT",
                    {"default": 7.5, "min": 1.0, "max": 15.0, "step": 0.5},
                ),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**32 - 1}),
                "remove_background": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "MASK")
    RETURN_NAMES = ("original_image", "sticker_with_alpha", "mask")
    FUNCTION = "generate_sticker"
    CATEGORY = "AR Sticker Factory"

    def __init__(self):
        self.sdxl_loader = SDXLLoader()
        self.sam2_segmenter = SAM2Segmenter()
        self.pipeline = None
        self.generation_count = 0

    def _enhance_sticker_prompt(self, base_prompt, sticker_style, background_style):
        """
        Enhance the base prompt with sticker-specific optimizations
        """
        style_addition = self.STICKER_STYLE_PROMPTS.get(sticker_style, "")
        background_addition = self.STICKER_BACKGROUND_PROMPTS.get(background_style, "")

        # Combine prompts with sticker-optimized keywords
        enhanced_prompt = f"{base_prompt}, {style_addition}, {background_addition}"
        enhanced_prompt += (
            ", sticker design, high quality, crisp details, vibrant, well-defined edges"
        )

        return enhanced_prompt.strip().replace(", ,", ",")

    def _validate_dimensions(self, width, height):
        """
        Ensure dimensions are optimal for SDXL and sticker generation
        """
        # SDXL works best with multiples of 64
        width = (width // 64) * 64
        height = (height // 64) * 64

        # Ensure minimum sticker quality
        width = max(width, 512)
        height = max(height, 512)

        return width, height

    def generate_sticker(
        self,
        prompt,
        sticker_style,
        background_style,
        negative_prompt,
        width,
        height,
        num_inference_steps,
        guidance_scale,
        seed,
        remove_background,
    ):
        """
        Generate a high-quality sticker image using SDXL
        """
        generation_start = time.time()

        try:
            # Load pipeline if not already loaded
            if self.pipeline is None:
                print("🚀 Loading SDXL pipeline...")
                self.pipeline = self.sdxl_loader.load_pipeline()

            # Validate and optimize dimensions
            width, height = self._validate_dimensions(width, height)

            # Enhance prompt for sticker generation
            enhanced_prompt = self._enhance_sticker_prompt(
                prompt, sticker_style, background_style
            )

            # Set seed for reproducibility
            if seed == -1:
                seed = torch.randint(0, 2**32 - 1, (1,)).item()

            device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=device).manual_seed(seed)

            print(f"🎨 Generating sticker {self.generation_count + 1}")
            print(f"📝 Enhanced prompt: {enhanced_prompt[:100]}...")
            print(f"📐 Dimensions: {width}x{height}")
            print(f"⚡ Steps: {num_inference_steps}")

            # Generate image with optimized parameters
            inference_start = time.time()

            result = self.pipeline(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
            )

            inference_time = time.time() - inference_start

            image = result.images[0]

            # Convert PIL to tensor format expected by ComfyUI
            image_array = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_array)[None,]

            # Store original image for return
            original_tensor = image_tensor

            # Apply background removal if requested
            if remove_background:
                print("🎭 Applying background removal...")
                bg_removal_start = time.time()
                
                sticker_with_alpha, mask = self.sam2_segmenter.segment_background(
                    image_tensor, 
                    confidence_threshold=0.5,
                    edge_smoothing=True,
                    padding=5
                )
                
                bg_removal_time = time.time() - bg_removal_start
                print(f"🎭 Background removal: {bg_removal_time:.2f}s")
            else:
                # No background removal - return original with dummy mask
                sticker_with_alpha = image_tensor
                mask = torch.ones(1, 1, image_tensor.shape[1], image_tensor.shape[2])

            total_time = time.time() - generation_start
            self.generation_count += 1

            print(f"✅ Sticker generated successfully!")
            print(f"⏱️  Inference time: {inference_time:.2f}s")
            print(f"🎯 Total time: {total_time:.2f}s")
            print(f"💾 GPU Memory: {self._get_memory_usage()}")

            return (original_tensor, sticker_with_alpha, mask)

        except Exception as e:
            print(f"❌ Error in ARStickerGenerator: {str(e)}")
            print(f"🔧 Debug info - Prompt: {prompt[:50]}...")
            print(f"🔧 Debug info - Dimensions: {width}x{height}")
            raise e

    def _get_memory_usage(self):
        """Get current GPU memory usage"""
        if not torch.cuda.is_available():
            return "CPU mode"

        allocated = torch.cuda.memory_allocated() / 1024**3
        return f"{allocated:.1f}GB"
