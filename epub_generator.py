#!/usr/bin/env python3
"""
EPUB Generator from Images
Generates an EPUB file from images in a specified folder.
Images are sorted by filename in ascending order.
"""

import os
import sys
import argparse
from pathlib import Path
from ebooklib import epub


# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


def get_image_files(folder_path: str) -> list[Path]:
    """
    Get all image files from the specified folder, sorted by filename.

    Args:
        folder_path: Path to the folder containing images

    Returns:
        List of image file paths sorted by filename in ascending order
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder_path}")

    image_files = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    # Sort by filename in ascending order
    image_files.sort(key=lambda x: x.name.lower())

    return image_files


def get_media_type(file_path: Path) -> str:
    """Get the MIME type for an image file."""
    extension = file_path.suffix.lower()
    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
    }
    return media_types.get(extension, 'image/jpeg')


def create_epub(image_folder: str, output_path: str, title: str = "Image Book",
                author: str = "Unknown") -> None:
    """
    Create an EPUB file from images in the specified folder.

    Args:
        image_folder: Path to folder containing images
        output_path: Output path for the EPUB file
        title: Book title
        author: Book author
    """
    # Get sorted image files
    image_files = get_image_files(image_folder)

    if not image_files:
        raise ValueError(f"No image files found in: {image_folder}")

    print(f"Found {len(image_files)} images")

    # Create EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('id_' + title.replace(' ', '_'))
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    chapters = []

    # Add each image as a chapter
    for index, image_path in enumerate(image_files, start=1):
        print(f"  Adding: {image_path.name}")

        # Read image data
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()

        # Create image item
        image_name = f"image_{index:04d}{image_path.suffix.lower()}"
        epub_image = epub.EpubImage()
        epub_image.file_name = f"images/{image_name}"
        epub_image.media_type = get_media_type(image_path)
        epub_image.content = image_data
        book.add_item(epub_image)

        # Create HTML chapter for this image
        chapter = epub.EpubHtml(
            title=f"Page {index}",
            file_name=f"page_{index:04d}.xhtml",
            lang='en'
        )

        # HTML content with the image
        chapter.content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Page {index}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            text-align: center;
        }}
        img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
    </style>
</head>
<body>
    <img src="images/{image_name}" alt="Page {index}"/>
</body>
</html>'''

        book.add_item(chapter)
        chapters.append(chapter)

    # Add navigation
    book.toc = [(epub.Section('Pages'), chapters)]
    book.spine = ['nav'] + chapters

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Write EPUB file
    epub.write_epub(output_path, book, {})
    print(f"\nEPUB created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate EPUB from images in a folder'
    )
    parser.add_argument(
        'input_folder',
        help='Path to folder containing images'
    )
    parser.add_argument(
        '-o', '--output',
        default='output.epub',
        help='Output EPUB file path (default: output.epub)'
    )
    parser.add_argument(
        '-t', '--title',
        default='Image Book',
        help='Book title (default: Image Book)'
    )
    parser.add_argument(
        '-a', '--author',
        default='Unknown',
        help='Book author (default: Unknown)'
    )

    args = parser.parse_args()

    try:
        create_epub(
            image_folder=args.input_folder,
            output_path=args.output,
            title=args.title,
            author=args.author
        )
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
