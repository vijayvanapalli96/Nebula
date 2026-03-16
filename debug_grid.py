"""Generate one grid image, save the full grid + 4 cropped quadrants locally."""
import asyncio
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

from io import BytesIO
from PIL import Image

async def main():
    from app.infrastructure.ai.gemini_story_generator import GeminiStoryGenerator
    from app.core.settings import Settings

    settings = Settings()
    gen = GeminiStoryGenerator(settings)

    prompts = [
        "A disillusioned corporate enforcer in a rain-soaked neon city",
        "A street-smart hacker navigating the digital underground",
        "A jaded private investigator in a smoky cyberpunk office",
        "A black market dealer in a grimy back-alley bazaar",
    ]

    print("Generating 2x2 grid image...")
    grid_bytes = await gen.generate_option_image_grid(prompts)

    out_dir = os.path.join(os.path.dirname(__file__), "grid_debug")
    os.makedirs(out_dir, exist_ok=True)

    # Save the full grid
    grid_path = os.path.join(out_dir, "full_grid.png")
    with open(grid_path, "wb") as f:
        f.write(grid_bytes)
    print(f"Saved full grid: {grid_path}")

    # Crop into quadrants
    grid_img = Image.open(BytesIO(grid_bytes))
    w, h = grid_img.size
    print(f"Grid dimensions: {w}x{h}")
    mid_x, mid_y = w // 2, h // 2

    labels = ["top_left", "top_right", "bottom_left", "bottom_right"]
    boxes = [
        (0, 0, mid_x, mid_y),
        (mid_x, 0, w, mid_y),
        (0, mid_y, mid_x, h),
        (mid_x, mid_y, w, h),
    ]

    for label, box in zip(labels, boxes):
        crop = grid_img.crop(box)
        crop_path = os.path.join(out_dir, f"crop_{label}.png")
        crop.save(crop_path)
        print(f"Saved {label} crop: {crop_path}  ({crop.size[0]}x{crop.size[1]})")

    print(f"\nAll files saved to: {out_dir}")
    print("Open full_grid.png to see the original, and the crop_*.png files for the quadrants.")

asyncio.run(main())
