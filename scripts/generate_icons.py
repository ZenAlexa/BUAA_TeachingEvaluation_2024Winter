#!/usr/bin/env python3
"""
Icon generation script
Creates platform-specific icons from source PNG
"""

import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image


def generate_icons(source_path: Path, output_dir: Path) -> None:
    """Generate icons for all platforms from source PNG"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load source image
    img = Image.open(source_path)

    # Ensure RGBA mode
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Standard sizes for different platforms
    sizes = [16, 32, 48, 64, 128, 256, 512, 1024]

    # Generate PNG icons at various sizes
    print("Generating PNG icons...")
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(output_dir / f"icon_{size}x{size}.png", "PNG")

    # Copy original as icon.png
    img.save(output_dir / "icon.png", "PNG")

    # Generate ICO for Windows (multiple sizes embedded)
    print("Generating Windows ICO...")
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = []
    for size in ico_sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        ico_images.append(resized)

    ico_images[0].save(
        output_dir / "icon.ico",
        format="ICO",
        sizes=ico_sizes,
        append_images=ico_images[1:]
    )

    # Generate ICNS for macOS
    print("Generating macOS ICNS...")
    iconset_dir = output_dir / "icon.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # macOS iconset requires specific naming
    iconset_sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    for size, name in iconset_sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(iconset_dir / name, "PNG")

    # Try to create .icns using iconutil (macOS only)
    try:
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_dir / "icon.icns")],
            check=True,
            capture_output=True
        )
        print("Created icon.icns successfully")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Note: iconutil not available, skipping .icns generation")
        print("On macOS, run: iconutil -c icns assets/icons/icon.iconset -o assets/icons/icon.icns")

    print(f"\nIcons generated in: {output_dir}")
    print("Files created:")
    for f in sorted(output_dir.glob("*")):
        if f.is_file():
            print(f"  - {f.name}")


def main():
    """Entry point"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    source = project_root / "logo.png"
    output = project_root / "assets" / "icons"

    if not source.exists():
        print(f"Error: Source image not found: {source}")
        sys.exit(1)

    generate_icons(source, output)
    print("\nIcon generation complete!")


if __name__ == "__main__":
    main()
