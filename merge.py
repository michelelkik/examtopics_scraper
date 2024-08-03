
from PIL import Image


# Merge PNG files into a PDF
def merge_png_to_pdf(png_files, pdf_filename):
    images = [Image.open(png) for png in png_files]
    images[0].save(pdf_filename, save_all=True, append_images=images[1:])
    print(f"PDF file saved as '{pdf_filename}'")
