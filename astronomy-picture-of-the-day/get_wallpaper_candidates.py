import os
from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Iterable, List
import tkinter as tk

import cv2


WALLPAPER_LIST_FILE = "wallpaper_candidates.txt"
WALLPAPER_COPY_DIR = "wallpapers"


def find_images(
    root_dir: str | Path,
    extensions: Iterable[str] = (
        ".jpg",
        ".jpeg",
        ".png",
    ),
) -> List[str]:
    """
    Recursively find all image files under root_dir.

    Args:
        root_dir: Root directory to search.
        extensions: Iterable of allowed file extensions (case-insensitive).

    Returns:
        List of absolute file paths to image files.
    """
    root = Path(root_dir).expanduser().resolve()
    exts = {e.lower() for e in extensions}

    return [str(p) for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts]


@dataclass
class Size2D:
    height: int
    width: int


def get_screen_size() -> Size2D:
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return Size2D(width=width, height=height)


def get_image_size(path: str) -> Size2D:
    if (img := cv2.imread(path, 0)) is None:
        raise ValueError(f"Invalid image at path {path}")
    height, width = img.shape[:2]
    return Size2D(height=height, width=width)


def is_candidate_by_absolute_size(img_size: Size2D, screen_size: Size2D) -> bool:
    return img_size.width >= screen_size.width and img_size.height >= screen_size.height


def is_candidate_by_screen_ratio(
    img_size: Size2D, screen_size: Size2D, ratio_bound: float
) -> bool:
    screen_ratio = screen_size.width / screen_size.height
    img_ratio = img_size.width / img_size.height
    min_size, max_size = 1 - ratio_bound, 1 + ratio_bound
    return min_size <= screen_ratio / img_ratio <= max_size


def is_candidate(
    img_size: Size2D,
    screen_size: Size2D,
    *,
    absolute_size: bool = True,
    screen_ratio: bool = True,
    ratio_bound: float = 0.05,
) -> bool:
    _is_candidate = True
    if absolute_size:
        _is_candidate = _is_candidate and is_candidate_by_absolute_size(
            img_size, screen_size
        )
    if screen_ratio:
        _is_candidate = _is_candidate and is_candidate_by_screen_ratio(
            img_size, screen_size, ratio_bound
        )
    return _is_candidate


def main():
    current_dir = os.path.dirname(__file__)
    images = find_images(current_dir)
    screen_size = get_screen_size()
    candidates = [
        img for img in images if is_candidate(get_image_size(img), screen_size)
    ]

    wallpaper_list = os.path.join(current_dir, WALLPAPER_LIST_FILE)
    print("Writing candidate list to", wallpaper_list)
    with open(wallpaper_list, "w+") as f:
        f.writelines(candidates)

    out_dir = os.path.join(current_dir, WALLPAPER_COPY_DIR)
    os.makedirs(out_dir, exist_ok=True)
    match input("Copy wallpaper candidate images to new directory? (Y/n): ").lower():
        case "y" | "yes":
            print("Copying image files to", out_dir)
            for wallpaper in candidates:
                try:
                    shutil.copy2(wallpaper, out_dir)
                except shutil.SameFileError:
                    ...
    print("Done.")


if __name__ == "__main__":
    main()
