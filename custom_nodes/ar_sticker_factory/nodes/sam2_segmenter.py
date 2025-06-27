"""
SAM2 Segmenter Node
Background removal using Meta's Segment Anything Model 2
"""

import torch
import numpy as np
from PIL import Image
from ..models.sam2_loader import SAM2Loader
from ..utils.image_processing import process_alpha_channel


class SAM2Segmenter:
    """
    ComfyUI node for automatic background removal using SAM2
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "confidence_threshold": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.05},
                ),
                "edge_smoothing": ("BOOLEAN", {"default": True}),
                "padding": ("INT", {"default": 10, "min": 0, "max": 50, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image_with_alpha", "mask")
    FUNCTION = "segment_background"
    CATEGORY = "AR Sticker Factory"

    def __init__(self):
        self.sam2_loader = SAM2Loader()
        self.predictor = None

    def segment_background(self, image, confidence_threshold, edge_smoothing, padding):
        """
        Remove background using SAM2 automatic segmentation with rembg fallback
        """
        try:
            # Try SAM2 first if available
            if self.sam2_loader and hasattr(self.sam2_loader, 'load_model'):
                result = self._try_sam2_segmentation(image, confidence_threshold, edge_smoothing, padding)
                if result is not None:
                    return result
                    
            # Fallback to rembg if SAM2 fails
            print("🔄 SAM2 unavailable, trying rembg background removal...")
            result = self._try_rembg_segmentation(image, edge_smoothing, padding)
            if result is not None:
                return result
                
            # Final fallback to geometric mask
            print("⚠️  All automatic methods failed, using geometric fallback")
            return self._fallback_segmentation(image, padding)

        except Exception as e:
            print(f"❌ Error in SAM2Segmenter: {str(e)}")
            return self._fallback_segmentation(image, padding)

    def _try_sam2_segmentation(self, image, confidence_threshold, edge_smoothing, padding):
        """Try SAM2 automatic segmentation"""
        try:
            from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
            
            # Load SAM2 model if not already loaded
            if self.predictor is None:
                self.predictor = self.sam2_loader.load_model()

            if self.predictor is None:
                return None

            # Convert ComfyUI tensor to numpy array
            image_np = (image.squeeze(0).numpy() * 255).astype(np.uint8)
            
            # Create automatic mask generator for better subject detection
            mask_generator = SAM2AutomaticMaskGenerator(
                model=self.predictor.model,
                points_per_side=32,  # Good for sticker subjects
                pred_iou_thresh=0.8,
                stability_score_thresh=0.9,
                crop_n_layers=1,
                crop_n_points_downscale_factor=2,
                min_mask_region_area=1000,  # Filter small regions
            )
            
            # Generate masks
            masks = mask_generator.generate(image_np)
            
            if not masks:
                print("No SAM2 masks generated")
                return None
                
            # Find the largest, most centered mask (likely the main subject)
            height, width = image_np.shape[:2]
            center_x, center_y = width // 2, height // 2
            
            best_mask = None
            best_score = 0
            
            for mask_data in masks:
                mask = mask_data['segmentation']
                stability_score = mask_data['stability_score']
                
                # Calculate mask center
                y_coords, x_coords = np.where(mask)
                if len(x_coords) == 0:
                    continue
                    
                mask_center_x = np.mean(x_coords)
                mask_center_y = np.mean(y_coords)
                
                # Score based on stability, size, and proximity to center
                area = np.sum(mask)
                max_area = height * width * 0.8  # Max 80% of image
                area_score = min(area / max_area, 1.0)
                
                center_distance = np.sqrt((mask_center_x - center_x)**2 + (mask_center_y - center_y)**2)
                max_distance = np.sqrt(center_x**2 + center_y**2)
                center_score = 1.0 - (center_distance / max_distance)
                
                combined_score = stability_score * 0.4 + area_score * 0.3 + center_score * 0.3
                
                if combined_score > best_score and stability_score > confidence_threshold:
                    best_score = combined_score
                    best_mask = mask
            
            if best_mask is None:
                print(f"No SAM2 mask met confidence threshold: {confidence_threshold}")
                return None
                
            print(f"✅ SAM2 segmentation successful (score: {best_score:.3f})")
            
            # Process mask
            if edge_smoothing:
                best_mask = process_alpha_channel(best_mask.astype(np.float32), padding)
            
            # Apply mask
            pil_image = Image.fromarray(image_np)
            image_with_alpha = self._apply_mask_to_image(pil_image, best_mask)
            
            # Convert to tensors
            result_array = np.array(image_with_alpha).astype(np.float32) / 255.0
            result_tensor = torch.from_numpy(result_array)[None,]
            mask_tensor = torch.from_numpy(best_mask.astype(np.float32))[None, None,]
            
            return (result_tensor, mask_tensor)
            
        except Exception as e:
            print(f"SAM2 segmentation failed: {str(e)}")
            return None

    def _try_rembg_segmentation(self, image, edge_smoothing, padding):
        """Try rembg background removal as fallback"""
        try:
            from rembg import remove, new_session
            
            # Convert tensor to PIL
            image_np = (image.squeeze(0).numpy() * 255).astype(np.uint8)
            pil_image = Image.fromarray(image_np)
            
            # Use u2net model (good for general objects)
            session = new_session('u2net')
            result_image = remove(pil_image, session=session)
            
            # Extract alpha channel as mask
            if result_image.mode == 'RGBA':
                alpha_channel = np.array(result_image)[:, :, 3]
                mask = (alpha_channel > 128).astype(np.float32)  # Binary threshold
                
                # Process mask if requested
                if edge_smoothing:
                    mask = process_alpha_channel(mask, padding)
                    
                print("✅ rembg background removal successful")
                
                # Convert to tensors
                result_array = np.array(result_image).astype(np.float32) / 255.0
                result_tensor = torch.from_numpy(result_array)[None,]
                mask_tensor = torch.from_numpy(mask)[None, None,]
                
                return (result_tensor, mask_tensor)
            else:
                print("rembg did not produce RGBA output")
                return None
                
        except ImportError:
            print("rembg not available, install with: pip install rembg")
            return None
        except Exception as e:
            print(f"rembg segmentation failed: {str(e)}")
            return None

    def _fallback_segmentation(self, image, padding):
        """
        Fallback segmentation when SAM2 is not available
        Creates a simple center-focused circular mask
        """
        print("Using fallback segmentation (circular mask)")

        # Get image dimensions
        batch_size, height, width, channels = image.shape

        # Create circular mask centered in the image
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 3

        y, x = torch.meshgrid(torch.arange(height), torch.arange(width), indexing="ij")
        mask = ((x - center_x) ** 2 + (y - center_y) ** 2) <= radius**2
        mask = mask.float()

        # Convert image to PIL for processing
        image_np = (image.squeeze(0).numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)

        # Apply mask
        image_with_alpha = self._apply_mask_to_image(pil_image, mask.numpy())

        # Convert back to tensors
        result_array = np.array(image_with_alpha).astype(np.float32) / 255.0
        result_tensor = torch.from_numpy(result_array)[None,]
        mask_tensor = mask[
            None,
            None,
        ]

        return (result_tensor, mask_tensor)

    def _apply_mask_to_image(self, image, mask):
        """Apply mask to create RGBA image with transparent background"""
        image_array = np.array(image)

        # Add alpha channel
        if image_array.shape[2] == 3:  # RGB
            alpha = mask.astype(np.uint8) * 255
            image_with_alpha = np.dstack([image_array, alpha])
        else:  # Already has alpha
            image_with_alpha = image_array.copy()
            image_with_alpha[:, :, 3] = mask.astype(np.uint8) * 255

        return Image.fromarray(image_with_alpha, "RGBA")
