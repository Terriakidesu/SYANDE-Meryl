import os
from fastapi import UploadFile
from PIL import Image
from ..Settings import Settings


def create_square_image(shoe_id: int, file: UploadFile):

    shoe_dir = os.path.join(
        Settings.shoes.path, f"shoe-{shoe_id:05d}")

    os.makedirs(shoe_dir, exist_ok=True)

    # Process image
    image = Image.open(file.file)
    if image.mode in ('RGBA', 'P'):
        image = image.convert("RGB")

    # Resize to fit within target size while maintaining aspect ratio (fit-to-screen)
    target_size = Settings.shoes.size
    image.thumbnail((target_size, target_size),
                    Image.Resampling.LANCZOS)

    # Create square canvas and center the image (fit-to-screen in square)
    square_image = Image.new(
        'RGB', (target_size, target_size), (255, 255, 255))

    # Calculate position to center the image

    aspect_ratio = image.width / image.height
    if aspect_ratio > 1:
        new_width = target_size
        new_height = int(target_size / aspect_ratio)
    else:
        new_height = target_size
        new_width = int(target_size * aspect_ratio)

    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    x = (target_size - image.width) // 2
    y = (target_size - image.height) // 2

    # Paste the resized image onto the square canvas
    square_image.paste(image, (x, y))

    return square_image, shoe_dir


def create_profile_image(user_id: int, file: UploadFile):

    user_dir = os.path.join(
        Settings.profiles.path, f"user-{user_id:05d}")

    os.makedirs(user_dir, exist_ok=True)

    # Process image
    image = Image.open(file.file)
    if image.mode in ('RGBA', 'P'):
        image = image.convert("RGB")

    # Resize to target size
    target_size = Settings.profiles.size
    image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)

    return image, user_dir
