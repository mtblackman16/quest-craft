#!/usr/bin/env python3
"""
Split multi-object artwork images into individual cropped images.
Uses only PIL and numpy (no scipy dependency).
"""

from PIL import Image
import numpy as np
from pathlib import Path

UPLOAD_DIR = Path("/home/mark/quest-craft/assets/images/Upload")
PLAYER_DIR = Path("/home/mark/quest-craft/assets/images/player")
ENEMIES_DIR = Path("/home/mark/quest-craft/assets/images/enemies")
ITEMS_DIR = Path("/home/mark/quest-craft/assets/images/items")

# Create items directory
ITEMS_DIR.mkdir(parents=True, exist_ok=True)


def find_content_mask(img):
    """Create a boolean mask of non-background pixels."""
    arr = np.array(img.convert("RGBA"))
    is_white = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    is_transparent = arr[:, :, 3] < 20
    is_background = is_white | is_transparent
    return ~is_background


def find_regions_1d(has_content, gap_threshold):
    """Find contiguous regions in a 1D boolean array, splitting on gaps >= threshold."""
    regions = []
    in_region = False
    start = 0

    for i, val in enumerate(has_content):
        if val and not in_region:
            start = i
            in_region = True
        elif not val and in_region:
            regions.append((start, i))
            in_region = False

    if in_region:
        regions.append((start, len(has_content)))

    # Merge regions with small gaps
    if len(regions) <= 1:
        return regions

    merged = [regions[0]]
    for start, end in regions[1:]:
        prev_start, prev_end = merged[-1]
        if start - prev_end < gap_threshold:
            merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))

    return merged


def find_objects_grid(img, h_gap=40, v_gap=40, min_size=30):
    """
    Find objects by looking for horizontal and vertical gaps in content.
    Returns list of (x1, y1, x2, y2) bounding boxes.
    """
    content = find_content_mask(img)
    if not content.any():
        return []

    # Find horizontal strips (rows of content separated by gaps)
    row_has_content = content.any(axis=1)
    h_regions = find_regions_1d(row_has_content, h_gap)

    objects = []
    for y_start, y_end in h_regions:
        # Within this horizontal strip, find vertical columns of content
        strip_content = content[y_start:y_end, :]
        col_has_content = strip_content.any(axis=0)
        v_regions = find_regions_1d(col_has_content, v_gap)

        for x_start, x_end in v_regions:
            # Refine: find tight bounding box within this region
            region = content[y_start:y_end, x_start:x_end]
            rows = np.where(region.any(axis=1))[0]
            cols = np.where(region.any(axis=0))[0]
            if len(rows) >= min_size and len(cols) >= min_size:
                obj_y1 = y_start + rows.min()
                obj_y2 = y_start + rows.max() + 1
                obj_x1 = x_start + cols.min()
                obj_x2 = x_start + cols.max() + 1
                objects.append((obj_x1, obj_y1, obj_x2, obj_y2))

    return objects


def crop_with_padding(img, bbox, padding=10):
    """Crop image to bounding box with padding."""
    x1, y1, x2, y2 = bbox
    w, h = img.size
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)
    return img.crop((x1, y1, x2, y2))


def make_transparent_bg(img):
    """Convert near-white background to transparent."""
    arr = np.array(img.convert("RGBA"))
    is_white = (arr[:, :, 0] > 245) & (arr[:, :, 1] > 245) & (arr[:, :, 2] > 245)
    arr[is_white, 3] = 0
    return Image.fromarray(arr)


def process_image0():
    """image0.png: 3 objects - jello cube front, jelly powder bag, jello cube 3/4 view"""
    print("Processing image0.png (3 objects)...")
    img = Image.open(UPLOAD_DIR / "image0.png").convert("RGBA")
    print(f"  Image size: {img.size}")

    objects = find_objects_grid(img, h_gap=40, v_gap=40, min_size=30)
    print(f"  Found {len(objects)} objects")

    for i, bbox in enumerate(objects):
        x1, y1, x2, y2 = bbox
        print(f"  Object {i}: ({x1},{y1})-({x2},{y2}) size={x2 - x1}x{y2 - y1}")

    if len(objects) == 3:
        # Sort by center-Y to find top 2 vs bottom 1
        sorted_by_cy = sorted(objects, key=lambda b: (b[1] + b[3]) / 2)
        # Top 2 objects (smallest center Y), bottom 1 (largest center Y)
        top_objs = sorted(sorted_by_cy[:2], key=lambda b: b[0])  # sort left-to-right
        bot_objs = [sorted_by_cy[2]]

        # Top-left = jello cube front view
        cropped = crop_with_padding(img, top_objs[0], padding=15)
        cropped = make_transparent_bg(cropped)
        cropped.save(PLAYER_DIR / "jello-cube-front.png")
        print(f"  -> player/jello-cube-front.png ({cropped.size})")

        # Top-right = jelly powder bag
        cropped = crop_with_padding(img, top_objs[1], padding=15)
        cropped = make_transparent_bg(cropped)
        cropped.save(ITEMS_DIR / "jelly-powder-bag.png")
        print(f"  -> items/jelly-powder-bag.png ({cropped.size})")

        # Bottom = jello cube 3/4 view
        cropped = crop_with_padding(img, bot_objs[0], padding=15)
        cropped = make_transparent_bg(cropped)
        cropped.save(PLAYER_DIR / "jello-cube-three-quarter.png")
        print(f"  -> player/jello-cube-three-quarter.png ({cropped.size})")

    elif len(objects) == 2:
        print("  Only found 2 objects, trying with smaller gap threshold...")
        objects = find_objects_grid(img, h_gap=20, v_gap=20, min_size=20)
        print(f"  Retry found {len(objects)} objects")
        for i, bbox in enumerate(objects):
            x1, y1, x2, y2 = bbox
            print(f"  Object {i}: ({x1},{y1})-({x2},{y2}) size={x2 - x1}x{y2 - y1}")
        # If still not 3, handle the 2-object case
        if len(objects) >= 3:
            return process_image0_with_objects(img, objects)
        else:
            print("  Falling back to manual regions based on visual analysis...")
            process_image0_manual(img)
    else:
        print(f"  Unexpected count ({len(objects)}), using manual regions...")
        process_image0_manual(img)


def process_image0_manual(img):
    """Fallback: manually crop image0 based on known layout."""
    w, h = img.size
    # Top-left quadrant: jello cube front
    cropped = img.crop((0, 0, w * 55 // 100, h * 55 // 100))
    cropped = make_transparent_bg(cropped)
    cropped.save(PLAYER_DIR / "jello-cube-front.png")
    print(f"  -> player/jello-cube-front.png ({cropped.size}) [manual]")

    # Top-right area: jelly powder bag
    cropped = img.crop((w * 50 // 100, 0, w, h * 45 // 100))
    cropped = make_transparent_bg(cropped)
    cropped.save(ITEMS_DIR / "jelly-powder-bag.png")
    print(f"  -> items/jelly-powder-bag.png ({cropped.size}) [manual]")

    # Bottom-center: jello cube 3/4 view
    cropped = img.crop((w * 15 // 100, h * 45 // 100, w * 85 // 100, h))
    cropped = make_transparent_bg(cropped)
    cropped.save(PLAYER_DIR / "jello-cube-three-quarter.png")
    print(f"  -> player/jello-cube-three-quarter.png ({cropped.size}) [manual]")


def process_image0_with_objects(img, objects):
    """Process image0 when we have the right number of objects."""
    sorted_objs = sorted(objects, key=lambda b: (b[1], b[0]))
    mid_y = img.size[1] // 2

    top_objs = sorted([o for o in sorted_objs if o[1] < mid_y], key=lambda b: b[0])
    bot_objs = [o for o in sorted_objs if o[1] >= mid_y]

    if not bot_objs:
        bot_objs = [sorted_objs[-1]]
        top_objs = sorted(sorted_objs[:-1], key=lambda b: b[0])

    cropped = crop_with_padding(img, top_objs[0], padding=15)
    cropped = make_transparent_bg(cropped)
    cropped.save(PLAYER_DIR / "jello-cube-front.png")
    print(f"  -> player/jello-cube-front.png ({cropped.size})")

    cropped = crop_with_padding(img, top_objs[1] if len(top_objs) > 1 else top_objs[0], padding=15)
    cropped = make_transparent_bg(cropped)
    cropped.save(ITEMS_DIR / "jelly-powder-bag.png")
    print(f"  -> items/jelly-powder-bag.png ({cropped.size})")

    cropped = crop_with_padding(img, bot_objs[0], padding=15)
    cropped = make_transparent_bg(cropped)
    cropped.save(PLAYER_DIR / "jello-cube-three-quarter.png")
    print(f"  -> player/jello-cube-three-quarter.png ({cropped.size})")


def process_image1():
    """image1.png: 2 objects - hand sanitizer front and back views"""
    print("Processing image1.png (2 objects)...")
    img = Image.open(UPLOAD_DIR / "image1.png").convert("RGBA")
    print(f"  Image size: {img.size}")

    objects = find_objects_grid(img, h_gap=30, v_gap=30, min_size=30)
    print(f"  Found {len(objects)} objects")

    for i, bbox in enumerate(objects):
        x1, y1, x2, y2 = bbox
        print(f"  Object {i}: ({x1},{y1})-({x2},{y2}) size={x2 - x1}x{y2 - y1}")

    if len(objects) >= 2:
        sorted_objs = sorted(objects, key=lambda b: b[0])

        cropped = crop_with_padding(img, sorted_objs[0], padding=15)
        cropped = make_transparent_bg(cropped)
        cropped.save(ITEMS_DIR / "hand-sanitizer-front.png")
        print(f"  -> items/hand-sanitizer-front.png ({cropped.size})")

        cropped = crop_with_padding(img, sorted_objs[1], padding=15)
        cropped = make_transparent_bg(cropped)
        cropped.save(ITEMS_DIR / "hand-sanitizer-back.png")
        print(f"  -> items/hand-sanitizer-back.png ({cropped.size})")
    else:
        print("  Falling back to manual split...")
        w, h = img.size
        left = img.crop((0, 0, w // 2, h))
        left = make_transparent_bg(left)
        left.save(ITEMS_DIR / "hand-sanitizer-front.png")
        print(f"  -> items/hand-sanitizer-front.png ({left.size}) [manual]")

        right = img.crop((w // 2, 0, w, h))
        right = make_transparent_bg(right)
        right.save(ITEMS_DIR / "hand-sanitizer-back.png")
        print(f"  -> items/hand-sanitizer-back.png ({right.size}) [manual]")


def process_single_images():
    """Process single-object images (image2-6): add transparency and save to correct folders."""
    print("Processing single-object images...")

    mappings = {
        "image2.png": (ENEMIES_DIR, "sanitizer-warrior-rear-view.png"),
        "image3.png": (ENEMIES_DIR, "sanitizer-warrior-side-view.png"),
        "image4.png": (ITEMS_DIR, "dropped-items-in-puddle.png"),
        "image5.png": (ENEMIES_DIR, "sanitizer-warrior-equipment-spread.png"),
        "image6.png": (ENEMIES_DIR, "sanitizer-warrior-front-view.png"),
    }

    for src_name, (dest_dir, dest_name) in mappings.items():
        src = UPLOAD_DIR / src_name
        img = Image.open(src).convert("RGBA")
        img = make_transparent_bg(img)
        dest = dest_dir / dest_name
        img.save(dest)
        print(f"  {src_name} -> {dest_dir.name}/{dest_name} ({img.size})")


if __name__ == "__main__":
    print("=" * 60)
    print("Andrew's Artwork Processing Pipeline")
    print("=" * 60)
    print()

    process_image0()
    print()
    process_image1()
    print()
    process_single_images()

    print()
    print("=" * 60)
    print("COMPLETE! All images processed.")
    print("=" * 60)

    # Print summary
    print()
    print("Output Summary:")
    for d in [PLAYER_DIR, ENEMIES_DIR, ITEMS_DIR]:
        files = sorted(d.glob("*.png"))
        files = [f for f in files if f.name != ".gitkeep"]
        if files:
            print(f"\n  {d.relative_to(d.parent.parent.parent)}/ ({len(files)} files):")
            for f in files:
                size = Image.open(f).size
                print(f"    {f.name} ({size[0]}x{size[1]})")
