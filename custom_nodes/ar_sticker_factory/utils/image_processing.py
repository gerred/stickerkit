"""
Image Processing Utilities
Alpha channel processing and image manipulation utilities
"""

import numpy as np
import cv2
from PIL import Image, ImageFilter
from scipy import ndimage


def process_alpha_channel(mask, padding=10, blur_radius=2):
    """
    Process mask to create smooth alpha channel for AR stickers

    Args:
        mask: Binary mask array
        padding: Padding around the mask edges
        blur_radius: Gaussian blur radius for edge smoothing

    Returns:
        Processed alpha channel as numpy array
    """
    try:
        # Convert to uint8 if needed
        if mask.dtype != np.uint8:
            mask = (mask * 255).astype(np.uint8)

        # Apply morphological operations to clean up mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Add padding
        if padding > 0:
            mask = cv2.copyMakeBorder(
                mask, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=0
            )

        # Apply Gaussian blur for smooth edges
        mask = cv2.GaussianBlur(mask, (blur_radius * 2 + 1, blur_radius * 2 + 1), 0)

        # Normalize to 0-1 range
        mask = mask.astype(np.float32) / 255.0

        # Remove padding if it was added
        if padding > 0:
            mask = mask[padding:-padding, padding:-padding]

        return mask

    except Exception as e:
        print(f"Error processing alpha channel: {str(e)}")
        return mask


def create_feathered_mask(image_size, feather_radius=20):
    """
    Create a feathered mask for smoother alpha transitions

    Args:
        image_size: Tuple of (width, height)
        feather_radius: Radius for feathering effect

    Returns:
        Feathered mask as numpy array
    """
    width, height = image_size

    # Create base mask
    mask = np.ones((height, width), dtype=np.float32)

    # Apply distance transform for feathering
    dist_transform = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)

    # Create feathered edges
    feathered = np.clip(dist_transform / feather_radius, 0, 1)

    return feathered


def enhance_sticker_for_ar(image, enhance_contrast=True, enhance_saturation=True):
    """
    Enhance image properties for better AR appearance

    Args:
        image: PIL Image
        enhance_contrast: Whether to enhance contrast
        enhance_saturation: Whether to enhance saturation

    Returns:
        Enhanced PIL Image
    """
    try:
        if enhance_contrast:
            from PIL import ImageEnhance

            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # 20% more contrast

        if enhance_saturation:
            from PIL import ImageEnhance

            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)  # 10% more saturation

        return image

    except Exception as e:
        print(f"Error enhancing image: {str(e)}")
        return image


def resize_for_ar(image, max_size=1024):
    """
    Resize image for optimal AR performance

    Args:
        image: PIL Image
        max_size: Maximum dimension size

    Returns:
        Resized PIL Image
    """
    width, height = image.size

    # Calculate scaling factor
    scale = min(max_size / width, max_size / height)

    if scale < 1:
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return image
