# AR Sticker Export Guide

Complete guide for exporting AR-ready stickers for iOS QuickLook and AR apps.

## 🎯 Overview

The AR Sticker Factory now includes comprehensive AR export functionality with:
- **USDZ export** for iOS AR QuickLook (preferred)
- **PNG/OBJ fallback** for broader AR app compatibility  
- **Automatic optimization** for mobile AR performance
- **Multiple AR behaviors** (billboard, fixed, physics)

## 📱 Export Formats

### USDZ (iOS AR QuickLook)
- **Best for**: iPhone/iPad AR viewing
- **Features**: Native iOS AR support, Material properties, Lighting
- **Sharing**: AirDrop, Messages, Mail, Safari
- **Requirements**: USD library (conda install -c conda-forge usd-core)

### PNG + OBJ (Universal Fallback)
- **Best for**: Android AR apps, 3D viewers
- **Features**: Transparent PNG + 3D geometry
- **Compatibility**: Google Lens, AR Core apps, Blender
- **Requirements**: None (always available)

## 🚀 Usage

### Basic AR Export
```python
# In ComfyUI workflow
ARStickerGenerator -> USDZExporter -> SaveImage
```

### USDZExporter Node Parameters
```
image: Generated sticker (IMAGE)
scale: Real-world size in meters (0.01-2.0)
filename: Output filename (STRING)
material_type: matte | glossy | metallic
ar_behavior: billboard | fixed | physics
optimize_mobile: Enable mobile optimizations (BOOLEAN)
```

### AR Behaviors
- **Billboard**: Always faces camera (best for stickers)
- **Fixed**: Maintains world orientation
- **Physics**: Can interact with AR surfaces

## 📂 Output Files

### USDZ Export Success
```
output/ar_stickers/
├── sticker.usdz              # Main AR file
├── sticker_ar_info.json      # AR metadata
└── sticker_texture.png       # Source texture
```

### PNG/OBJ Fallback
```
output/ar_stickers/
├── sticker_ar.png            # Optimized PNG
├── sticker.obj               # 3D geometry
├── sticker.mtl               # Material definition
└── sticker_ar_instructions.json # Usage guide
```

## 🎯 iOS AR QuickLook Usage

### Viewing USDZ Files
1. **Open** the .usdz file on iPhone/iPad
2. **Tap AR** to enter AR mode
3. **Point camera** at flat surface
4. **Tap to place** sticker in AR
5. **Pinch to resize**, drag to move

### Sharing AR Stickers
- **AirDrop**: Send directly to other iOS devices
- **Messages**: Share in conversations (shows AR preview)
- **Mail**: Attach to emails with AR preview
- **Safari**: View from web links

## 📱 Android & Universal AR

### Google Lens / AR Core
1. **Import PNG** into AR apps
2. **Use transparent background** for clean placement
3. **Scale appropriately** for real-world viewing

### 3D Model Viewers
1. **Open OBJ file** in Blender, Meshlab, or online viewers
2. **Preview 3D geometry** and materials
3. **Export to preferred AR format**

## ⚙️ Optimization Settings

### Mobile Performance
- **Resolution limit**: Max 1024x1024 for performance
- **Power-of-2 dimensions**: GPU-optimized sizes
- **PNG compression**: Reduced file sizes
- **Texture clamping**: Prevents AR artifacts

### Material Properties
```python
matte:    roughness=0.8, metallic=0.0  # Soft, non-reflective
glossy:   roughness=0.1, metallic=0.0  # Shiny plastic
metallic: roughness=0.3, metallic=0.8  # Realistic metal
```

## 🧪 Testing AR Export

### Quick Test
```bash
python test_ar_export.py
```

### Manual Testing
1. **Generate sticker** with ARStickerGenerator
2. **Export with USDZExporter** 
3. **Check output directory** for files
4. **Test on device** (iPhone/iPad for USDZ)

## 🔧 Troubleshooting

### USD Library Not Available
- **Symptom**: "USD library not available" message
- **Solution**: Install with `conda install -c conda-forge usd-core`
- **Fallback**: Automatic PNG/OBJ export

### Large File Sizes
- **Enable mobile optimization** (optimize_mobile=True)
- **Reduce scale** for smaller textures
- **Use matte materials** (less complex shading)

### AR Placement Issues
- **Use billboard behavior** for stickers
- **Set appropriate scale** (0.05-0.2m typical)
- **Test on real devices** for best results

## 📋 Example Workflows

### Complete AR Pipeline
```json
{
  "workflow": "workflows/examples/complete_ar_sticker_pipeline.json",
  "description": "Full sticker generation -> AR export pipeline"
}
```

### AR Export Test
```json  
{
  "workflow": "workflows/examples/ar_sticker_export_test.json",
  "description": "Test AR export with sample image"
}
```

## 🎯 Production Ready

The AR export system is production-ready with:
- ✅ **Robust fallback** handling
- ✅ **Mobile optimization**
- ✅ **Cross-platform compatibility**
- ✅ **Comprehensive error handling**
- ✅ **Detailed usage instructions**

Ready for demo and real-world AR sticker creation! 🚀
