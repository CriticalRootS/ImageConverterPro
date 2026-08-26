import importlib
import os

try:
    Image = importlib.import_module("PIL.Image")
except ImportError as e:
    raise ImportError(
        "Pillow is required to convert images. Install it with: pip install Pillow"
    ) from e

class ImageConverter:
    def __init__(self):
        pass

    def convert(self, input_path, output_path, output_format=None):
        """Convert a single image."""
        try:
            with Image.open(input_path) as img:
                if output_format is None:
                    output_format = os.path.splitext(output_path)[1][1:].upper()
                    if output_format == 'JPG':
                        output_format = 'JPEG'
                img.save(output_path, format=output_format)
                print(f"[OK] {input_path} → {output_path} ({output_format})")
        except Exception as e:
            print(f"[ERROR] {input_path}: {e}")

    def batch_convert(self, input_folder, output_folder, output_format=None):
        """Convert all images in a folder."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for filename in os.listdir(input_folder):
            input_path = os.path.join(input_folder, filename)
            if not os.path.isfile(input_path):
                continue
            name, ext = os.path.splitext(filename)
            output_ext = output_format.lower() if output_format else ext[1:]
            output_path = os.path.join(output_folder, f"{name}.{output_ext}")
            self.convert(input_path, output_path, output_format)