"""
USDZ Creation Utilities
Create AR-ready USDZ files from images
"""

import os
import tempfile
from PIL import Image
import numpy as np

try:
    from pxr import Usd, UsdGeom, Sdf, UsdShade, Gf

    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("USD not available. Install with: conda install -c conda-forge usd-core")


def create_usdz_from_image(image, output_path, scale=0.1, material_type="matte", ar_behavior="billboard"):
    """
    Create USDZ file from PIL Image for AR viewing with AR-specific optimizations

    Args:
        image: PIL Image (RGB or RGBA)
        output_path: Output path for USDZ file
        scale: Scale factor for AR object (in meters)
        material_type: Material type (matte, glossy, metallic)
        ar_behavior: AR behavior (billboard, fixed, physics)

    Returns:
        Boolean indicating success
    """
    if not USD_AVAILABLE:
        print("USD library not available for USDZ export")
        return False

    try:
        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save image as optimized PNG
            image_path = os.path.join(temp_dir, "texture.png")
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            # Optimize image for AR
            image = _optimize_image_for_ar(image)
            image.save(image_path, "PNG", optimize=True)

            # Create USD stage directly  
            stage = Usd.Stage.CreateNew(output_path)
            stage.SetStartTimeCode(1)
            stage.SetEndTimeCode(1)
            
            # Set up root prim with AR metadata
            root_prim = stage.DefinePrim("/Root", "Xform")
            stage.SetDefaultPrim(root_prim)
            
            # Add AR QuickLook metadata
            root_prim.SetMetadata("customData", {
                "arQuickLookCompatible": True,
                "realWorldScale": scale,
                "behavior": ar_behavior
            })

            # Create mesh geometry
            mesh_prim = stage.DefinePrim("/Root/Sticker", "Mesh")
            mesh = UsdGeom.Mesh(mesh_prim)

            # Define quad geometry optimized for AR
            width, height = image.size
            aspect_ratio = height / width

            # Create geometry with correct Y-up orientation for AR
            if ar_behavior == "billboard":
                # Billboard: Y-up, faces camera (AR Quick Look compatible)
                points = [
                    (-scale, 0, -scale * aspect_ratio),  # Bottom-left
                    (scale, 0, -scale * aspect_ratio),   # Bottom-right  
                    (scale, 0, scale * aspect_ratio),    # Top-right
                    (-scale, 0, scale * aspect_ratio),   # Top-left
                ]
                # Add billboard constraint
                mesh_prim.SetMetadata("customData", {"billboard": True})
            else:
                # Fixed: maintain Y-up standard orientation
                points = [
                    (-scale, -scale * aspect_ratio, 0),  # Bottom-left
                    (scale, -scale * aspect_ratio, 0),   # Bottom-right
                    (scale, scale * aspect_ratio, 0),    # Top-right
                    (-scale, scale * aspect_ratio, 0),   # Top-left
                ]

            # Set mesh attributes
            mesh.CreatePointsAttr(points)
            mesh.CreateFaceVertexCountsAttr([4])  # Quad
            mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
            
            # Normals for proper AR lighting (Y-up compatible)
            if ar_behavior == "billboard":
                # Billboard faces up (+Y normal)
                normals = [(0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)]
            else:
                # Fixed faces viewer (+Z normal)
                normals = [(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)]
            mesh.CreateNormalsAttr(normals)
            mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)

            # UV coordinates (flipped for AR compatibility)
            texCoords = [(0, 1), (1, 1), (1, 0), (0, 0)]
            texCoordsPrimvar = UsdGeom.PrimvarsAPI(mesh_prim).CreatePrimvar(
                "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex
            )
            texCoordsPrimvar.Set(texCoords)

            # Create AR-optimized material
            material_prim = stage.DefinePrim("/Root/Material", "Material")
            material = UsdShade.Material(material_prim)

            # Create surface shader with AR settings
            shader_prim = stage.DefinePrim("/Root/Material/Shader", "Shader")
            shader = UsdShade.Shader(shader_prim)
            shader.CreateIdAttr("UsdPreviewSurface")

            # Set material properties for AR
            diffuse_color = shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
            roughness = shader.CreateInput("roughness", Sdf.ValueTypeNames.Float)
            metallic = shader.CreateInput("metallic", Sdf.ValueTypeNames.Float)
            opacity = shader.CreateInput("opacity", Sdf.ValueTypeNames.Float)
            
            # Enable alpha blending for transparency
            shader.CreateInput("useSpecularWorkflow", Sdf.ValueTypeNames.Int).Set(1)

            # Set material properties based on type
            if material_type == "matte":
                roughness.Set(0.8)  # Slightly less rough for AR
                metallic.Set(0.0)
            elif material_type == "glossy":
                roughness.Set(0.1)
                metallic.Set(0.0)
            elif material_type == "metallic":
                roughness.Set(0.3)  # More realistic metallic
                metallic.Set(0.8)

            # Create texture reader with AR optimization
            tex_reader_prim = stage.DefinePrim("/Root/Material/TextureReader", "Shader")
            tex_reader = UsdShade.Shader(tex_reader_prim)
            tex_reader.CreateIdAttr("UsdUVTexture")

            # Set texture file with wrap mode
            tex_file_input = tex_reader.CreateInput("file", Sdf.ValueTypeNames.Asset)
            tex_file_input.Set(image_path)
            
            # Set texture wrapping for AR
            tex_reader.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("clamp")
            tex_reader.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("clamp")

            # Connect texture to material
            tex_output = tex_reader.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
            diffuse_color.ConnectToSource(tex_output)

            # Handle alpha channel for AR transparency
            if image.mode == "RGBA":
                alpha_output = tex_reader.CreateOutput("a", Sdf.ValueTypeNames.Float)
                opacity.ConnectToSource(alpha_output)
                
                # Enable transparency in AR
                shader.CreateInput("opacityThreshold", Sdf.ValueTypeNames.Float).Set(0.01)

            # Connect shader to material
            surface_output = material.CreateSurfaceOutput()
            shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
            surface_output.ConnectToSource(shader_output)

            # Bind material to mesh
            UsdShade.MaterialBindingAPI(mesh_prim).Bind(material)
            
            # Add physics if requested
            if ar_behavior == "physics":
                # Add collision shape
                mesh_prim.GetAttribute("physics:collisionEnabled").Set(True)
                mesh_prim.GetAttribute("physics:rigidBodyEnabled").Set(True)

            # Save stage with AR optimization
            stage.GetRootLayer().Save()

            print(f"✅ AR-optimized USDZ created: {output_path}")
            return True

    except Exception as e:
        print(f"❌ Error creating USDZ: {str(e)}")
        return False


def _optimize_image_for_ar(image):
    """Optimize image specifically for AR viewing"""
    # Ensure power-of-2 dimensions for GPU efficiency
    width, height = image.size
    
    # Find next power of 2
    def next_power_of_2(x):
        return 1 << (x - 1).bit_length()
    
    # Limit to reasonable AR sizes
    max_dimension = 1024
    if width > max_dimension or height > max_dimension:
        ratio = min(max_dimension / width, max_dimension / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Make power of 2
        new_width = min(next_power_of_2(new_width), max_dimension)
        new_height = min(next_power_of_2(new_height), max_dimension)
        
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return image


def create_fallback_obj(image, output_path, scale=0.1):
    """
    Create OBJ file as fallback when USD is not available

    Args:
        image: PIL Image
        output_path: Output path (will be changed to .obj)
        scale: Scale factor

    Returns:
        Boolean indicating success
    """
    try:
        # Change extension to .obj
        obj_path = output_path.replace(".usdz", ".obj")
        mtl_path = output_path.replace(".usdz", ".mtl")
        texture_path = output_path.replace(".usdz", "_texture.png")

        # Save texture
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        image.save(texture_path, "PNG")

        # Create OBJ file
        width, height = image.size
        aspect_ratio = height / width

        with open(obj_path, "w") as f:
            f.write("# AR Sticker OBJ\n")
            f.write(f"mtllib {os.path.basename(mtl_path)}\n")
            f.write("o Sticker\n")

            # Vertices
            f.write(f"v -{scale} -{scale * aspect_ratio} 0\n")
            f.write(f"v {scale} -{scale * aspect_ratio} 0\n")
            f.write(f"v {scale} {scale * aspect_ratio} 0\n")
            f.write(f"v -{scale} {scale * aspect_ratio} 0\n")

            # Texture coordinates
            f.write("vt 0 0\n")
            f.write("vt 1 0\n")
            f.write("vt 1 1\n")
            f.write("vt 0 1\n")

            # Face
            f.write("usemtl sticker_material\n")
            f.write("f 1/1 2/2 3/3 4/4\n")

        # Create MTL file
        with open(mtl_path, "w") as f:
            f.write("# AR Sticker Material\n")
            f.write("newmtl sticker_material\n")
            f.write("Ka 1.0 1.0 1.0\n")
            f.write("Kd 1.0 1.0 1.0\n")
            f.write("Ks 0.0 0.0 0.0\n")
            f.write("Ns 0.0\n")
            f.write("d 1.0\n")
            f.write(f"map_Kd {os.path.basename(texture_path)}\n")

        print(f"OBJ created as fallback: {obj_path}")
        return True

    except Exception as e:
        print(f"Error creating OBJ fallback: {str(e)}")
        return False
