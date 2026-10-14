import json
import os
import random
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from materialyoucolor.hct import Hct
from materialyoucolor.utils.color_utils import argb_from_rgb
from PIL import Image

from caelestia.utils.colourfulness import get_variant
from caelestia.utils.material import get_colours_for_image
from caelestia.utils.monitors import get_monitor_sizes
from caelestia.utils.paths import (
    compute_hash,
    user_config_path,
    wallpaper_link_path,
    wallpaper_path_path,
    wallpaper_thumbnail_path,
    wallpapers_cache_dir,
)


@dataclass
class Scheme:
    mode: str = "dark"
    variant: str = "tonalspot"
    flavour: str = "default"


def get_config() -> dict:
    try:
        return json.loads(user_config_path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def is_valid_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".gif"]


def check_wall(wall: Path, filter_size: tuple[int, int], threshold: float) -> bool:
    with Image.open(wall) as img:
        width, height = img.size
        return width >= filter_size[0] * threshold and height >= filter_size[1] * threshold


def get_wallpaper() -> str | None:
    try:
        return wallpaper_path_path.read_text()
    except IOError:
        return None


def get_wallpapers(directory: Path | str, no_filter: bool, threshold: float) -> list[Path]:
    directory = Path(directory)
    if not directory.is_dir():
        return []

    walls = [f for f in directory.rglob("*") if is_valid_image(f)]

    monitors = None if no_filter else get_monitor_sizes()
    if not monitors:
        return walls

    filter_size = min(w for w, _ in monitors), min(h for _, h in monitors)
    return [f for f in walls if check_wall(f, filter_size, threshold)]


def get_thumb(wall: Path, cache: Path) -> Path:
    thumb = cache / "thumbnail.jpg"

    if not thumb.exists():
        with Image.open(wall) as img:
            img = img.convert("RGB")
            img.thumbnail((128, 128), Image.Resampling.NEAREST)
            thumb.parent.mkdir(parents=True, exist_ok=True)
            img.save(thumb, "JPEG")

    return thumb


def get_smart_opts(wall: Path, cache: Path) -> dict:
    opts_cache = cache / "smart.json"

    try:
        return json.loads(opts_cache.read_text())
    except (IOError, json.JSONDecodeError):
        pass

    opts = {}

    with Image.open(get_thumb(wall, cache)) as img:
        opts["variant"] = get_variant(img)
        img.thumbnail((1, 1), Image.Resampling.LANCZOS)

        # Cast the pixel to a tuple of 3 integers to safely unpack it
        pixel = cast(tuple[int, int, int], img.getpixel((0, 0)))
        hct = Hct.from_int(argb_from_rgb(*pixel))

        opts["mode"] = "light" if hct.tone > 60 else "dark"

    opts_cache.parent.mkdir(parents=True, exist_ok=True)
    with opts_cache.open("w") as f:
        json.dump(opts, f)

    return opts


def get_colours_for_wall(wall: Path | str, no_smart: bool) -> dict:
    wall = Path(wall)
    scheme = Scheme()
    cache = wallpapers_cache_dir / compute_hash(wall)

    if wall.suffix.lower() == ".gif":
        wall = convert_gif(wall)

    name = "dynamic"

    if not no_smart:
        smart_opts = get_smart_opts(wall, cache)
        scheme = Scheme(mode=smart_opts["mode"], variant=smart_opts["variant"], flavour=scheme.flavour)

    return {
        "name": name,
        "flavour": scheme.flavour,
        "mode": scheme.mode,
        "variant": scheme.variant,
        "colours": get_colours_for_image(get_thumb(wall, cache), scheme),
    }


def convert_gif(wall: Path) -> Path:
    cache = wallpapers_cache_dir / compute_hash(wall)
    output_path = cache / "first_frame.png"

    if not output_path.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(wall) as img:
            try:
                img.seek(0)
            except EOFError:
                pass

            img = img.convert("RGB")
            img.save(output_path, "PNG")

    return output_path


def set_wallpaper(wall: Path, no_smart: bool) -> None:
    # Make path absolute
    wall = Path(wall).resolve()

    if not is_valid_image(wall):
        raise ValueError(f'"{wall}" is not a valid image')

    # Use gif's 1st frame for thumb only
    wall_cache = convert_gif(wall) if wall.suffix.lower() == ".gif" else wall

    # Update files
    wallpaper_path_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_path_path.write_text(str(wall))
    wallpaper_link_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_link_path.unlink(missing_ok=True)
    wallpaper_link_path.symlink_to(wall)

    cache = wallpapers_cache_dir / compute_hash(wall_cache)

    # Generate thumbnail or get from cache
    thumb = get_thumb(wall_cache, cache)
    wallpaper_thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_thumbnail_path.unlink(missing_ok=True)
    wallpaper_thumbnail_path.symlink_to(thumb)

    scheme = Scheme()

    # Change mode and variant based on wallpaper colour
    if not no_smart:
        smart_opts = get_smart_opts(wall_cache, cache)
        scheme.mode = smart_opts["mode"]
        scheme.variant = smart_opts["variant"]

    colours = get_colours_for_image(thumb, scheme)

    # Run custom post-hook if configured
    cfg = get_config().get("wallpaper", {})
    if post_hook := cfg.get("postHook"):
        subprocess.run(
            post_hook,
            shell=True,
            env={
                **os.environ,
                "WALLPAPER_PATH": str(wall),
                "SCHEME_NAME": "dynamic",
                "SCHEME_FLAVOUR": scheme.flavour,
                "SCHEME_MODE": scheme.mode,
                "SCHEME_VARIANT": scheme.variant,
                "SCHEME_COLOURS": json.dumps(colours),
                "THUMBNAIL_PATH": str(thumb),
            },
            stderr=subprocess.DEVNULL,
        )


def set_random(directory: Path | str, no_filter: bool, threshold: float, no_smart: bool) -> None:
    wallpapers = get_wallpapers(directory, no_filter, threshold)

    if not wallpapers:
        raise ValueError("No valid wallpapers found")

    try:
        last_wall = wallpaper_path_path.read_text()
        wallpapers.remove(Path(last_wall))

        if not wallpapers:
            raise ValueError("Only valid wallpaper is current")
    except (FileNotFoundError, ValueError):
        pass

    set_wallpaper(random.choice(wallpapers), no_smart)
