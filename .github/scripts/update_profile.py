#!/usr/bin/env python3

import os
import random
import shutil
from datetime import datetime
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

def get_available_images():
    """Get list of available images in Waifu folder, excluding padoru unless it's December"""
    waifu_folder = "Waifu"
    current_month = datetime.now().month

    if not os.path.exists(waifu_folder):
        raise FileNotFoundError(f"Waifu folder not found at {waifu_folder}")

    # Get all image files
    image_files = []
    for file in os.listdir(waifu_folder):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Skip padoru unless it's December
            if file.lower() == 'padoru.png' and current_month != 12:
                continue
            image_files.append(file)

    return image_files

def extract_dominant_colors(image_path, num_colors=5):
    """Extract dominant colors from an image using K-means clustering"""
    # Open and convert image to RGB
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img = img.resize((150, 150))  # Resize for faster processing

        # Convert to numpy array
        data = np.array(img)
        data = data.reshape((-1, 3))

        # Use K-means to find dominant colors
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(data)

        # Get the colors
        colors = kmeans.cluster_centers_.astype(int)

        # Convert to hex
        hex_colors = ['#' + ''.join([format(int(c), '02x') for c in color]) for color in colors]

        return hex_colors

def create_color_image(hex_color, width=25, height=20):
    """Create a small colored image for the color palette"""
    # Remove # from hex color
    hex_color = hex_color.lstrip('#')

    # Convert hex to RGB
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Create image
    img = Image.new('RGB', (width, height), rgb)

    # Save to img folder
    os.makedirs('img', exist_ok=True)
    img_path = f'img/{hex_color}.png'
    img.save(img_path)

    return img_path

def update_readme(selected_image, colors):
    """Generate README.md from TEMPLATE.md with updated color palette"""
    template_path = "TEMPLATE.md"

    if not os.path.exists(template_path):
        raise FileNotFoundError("TEMPLATE.md not found")

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create color images and build the color palette HTML
    color_imgs = []
    for color in colors:
        create_color_image(color)
        hex_clean = color.lstrip('#')
        color_imgs.append(f'<img alt="{color}" src="https://raw.githubusercontent.com/TryKatChup/TryKatChup/main/img/{hex_clean}.png" width="25" height="20" />')

    new_color_line = ''.join(color_imgs)

    # Replace the color palette images in the template
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if '<p align="left">' in line:
            new_lines.append(line)
            i += 1
            # Skip existing content lines until </p>
            while i < len(lines) and '</p>' not in lines[i]:
                i += 1
            # Add spacing and new color images
            new_lines.append('  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;')
            new_lines.append(new_color_line)
            if i < len(lines):
                new_lines.append(lines[i])  # Add </p>
        else:
            new_lines.append(line)
        i += 1

    with open("README.md", 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

def copy_selected_image(selected_image, max_size=600):
    """Copy selected image to root as cropped.jpg, resized to consistent dimensions"""
    source_path = os.path.join("Waifu", selected_image)

    with Image.open(source_path) as img:
        # Convert to RGB (handles PNG with transparency, etc.)
        rgb_img = img.convert('RGB')

        # Resize maintaining aspect ratio, fitting within max_size x max_size
        rgb_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # Save as JPEG with good quality
        rgb_img.save("cropped.jpg", "JPEG", quality=85)
        print(f"Resized image to: {rgb_img.size}")

def main():
    try:
        print("Starting profile update...")

        # Get available images
        images = get_available_images()
        if not images:
            raise ValueError("No suitable images found in Waifu folder")

        print(f"Found {len(images)} available images")

        # Select random image
        selected_image = random.choice(images)
        print(f"Selected image: {selected_image}")

        # Copy selected image to root
        copy_selected_image(selected_image)

        # Extract colors from the selected image
        image_path = os.path.join("Waifu", selected_image)
        colors = extract_dominant_colors(image_path)
        print(f"Extracted colors: {colors}")

        # Update README with new image and colors
        update_readme(f"cropped.jpg", colors)

        print("Profile update completed successfully!")

    except Exception as e:
        print(f"Error during profile update: {e}")
        raise

if __name__ == "__main__":
    main()