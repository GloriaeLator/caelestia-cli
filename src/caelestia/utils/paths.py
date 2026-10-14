import hashlib
import os
from pathlib import Path

state_dir: Path = Path(os.getenv("XDG_STATE_HOME", Path.home() / ".local/state"))
cache_dir: Path = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
config_dir: Path = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
pictures_dir: Path = Path(os.getenv("XDG_PICTURES_DIR", Path.home() / "Pictures"))

c_state_dir: Path = state_dir / "caelestia"
c_cache_dir: Path = cache_dir / "caelestia"

user_config_path: Path = config_dir / "caelestia" / "cli.json"

wallpapers_dir: Path = Path(os.getenv("CAELESTIA_WALLPAPERS_DIR", pictures_dir / "Wallpapers"))
wallpaper_path_path: Path = c_state_dir / "wallpaper/path.txt"
wallpaper_link_path: Path = c_state_dir / "wallpaper/current"
wallpaper_thumbnail_path: Path = c_state_dir / "wallpaper/thumbnail.jpg"
wallpapers_cache_dir: Path = c_cache_dir / "wallpapers"
scheme_cache_dir: Path = c_cache_dir / "schemes"


def compute_hash(path: Path | str) -> str:
    sha = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)

    return sha.hexdigest()
