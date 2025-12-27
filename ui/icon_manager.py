from PIL import Image, ImageOps
import customtkinter as ctk
import os

class IconManager:
    @staticmethod
    def load_icon(path, size, color=None):
        """
        Loads an icon, resizes it, and optionally tints it.
        Returns a CTkImage.
        """
        if not path or not os.path.exists(path):
            return None
            
        try:
            pil_img = Image.open(path).convert("RGBA")
            
            # Resize uses high quality downsampling
            pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
            
            if color:
                # Tinting logic: preserving alpha, filling color
                # Create a solid color image
                r, g, b = IconManager.hex_to_rgb(color)
                color_img = Image.new('RGB', pil_img.size, (r, g, b))
                
                # Use the alpha channel of the icon as a mask
                mask = pil_img.split()[3]
                
                # Composite
                pil_img = Image.composite(color_img, Image.new('RGB', pil_img.size, (255, 255, 255)), mask)
                
                # Restore alpha to make background transparent again if needed, 
                # but CTkImage dark/light mode usually handles simple RGBA.
                # Actually for CTkImage we want RGBA.
                pil_img = pil_img.convert("RGBA")
                pil_img.putalpha(mask)

            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            
        except Exception as e:
            print(f"Error loading icon {path}: {e}")
            return None

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
