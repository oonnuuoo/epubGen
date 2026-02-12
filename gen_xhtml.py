import sys
import os
from PIL import Image

TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="ja" class="hltr">
<head>
<meta charset="UTF-8"/>
<title>{title}</title>
<link rel="stylesheet" href="../style/book-style-prepaginated.css" type="text/css"/>
<meta name="viewport" content="width={width}, height={height}"/>
</head>
<body class="p-image">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink">
<image width="{width}" height="{height}" xlink:href="{image_path}"/>
</svg>
</body>
</html>
"""


def gen_xhtml(image_folder, output_folder, title, image_rel_prefix="../image"):
    os.makedirs(output_folder, exist_ok=True)

    jpg_files = sorted(
        f for f in os.listdir(image_folder) if f.lower().endswith(".jpg")
    )

    if not jpg_files:
        print("No .jpg files found in", image_folder)
        return

    for i, jpg_name in enumerate(jpg_files, start=1):
        img_path = os.path.join(image_folder, jpg_name)
        with Image.open(img_path) as img:
            width, height = img.size

        xhtml_name = f"p-{i:04d}.xhtml"
        xlink_href = f"{image_rel_prefix}/{jpg_name}"

        content = TEMPLATE.format(
            title=title,
            width=width,
            height=height,
            image_path=xlink_href,
        ).lstrip("\n")

        out_path = os.path.join(output_folder, xhtml_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  {xhtml_name}  ({width}x{height})  <- {jpg_name}")

    print(f"\nGenerated {len(jpg_files)} xhtml files in {output_folder}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python gen_xhtml.py <image_folder> <output_folder> [title] [image_rel_prefix]")
        print("  image_folder:     path to folder containing .jpg images")
        print("  output_folder:    path to output .xhtml files")
        print("  title:            book title (default: 'Untitled')")
        print("  image_rel_prefix: relative path prefix for xlink:href (default: '../image')")
        sys.exit(1)

    image_folder = sys.argv[1]
    output_folder = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "Untitled"
    image_rel_prefix = sys.argv[4] if len(sys.argv) > 4 else "../image"

    gen_xhtml(image_folder, output_folder, title, image_rel_prefix)
