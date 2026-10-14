# caelestia-wallpaper

Standalone wallpaper engine extracted from [caelestia-cli](https://github.com/caelestia-dots/cli).
It tracks the current wallpaper, generates thumbnails, picks a light/dark mode and
Material You variant from the image, and extracts a colour palette.
It does **not** draw the wallpaper itself — use `postHook` to hand the image to your
renderer (swww, hyprpaper, swaybg, ...).

## Install

    pip install .        # needs Python >= 3.13

## Usage

    caelestia-wallpaper                  # print current wallpaper
    caelestia-wallpaper -f IMG           # set wallpaper
    caelestia-wallpaper -r [DIR]         # random wallpaper (default ~/Pictures/Wallpapers)
    caelestia-wallpaper -p [PATH]        # print extracted colour scheme as JSON
    caelestia-wallpaper -n / -t 0.8 / -N # no size filter / size threshold / no smart mode

Size filtering uses Hyprland monitors when available and is skipped otherwise.

## Post hook

`~/.config/caelestia/cli.json`:

    { "wallpaper": { "postHook": "swww img \"$WALLPAPER_PATH\"" } }

Env vars: `WALLPAPER_PATH`, `THUMBNAIL_PATH`, `SCHEME_NAME`, `SCHEME_FLAVOUR`,
`SCHEME_MODE`, `SCHEME_VARIANT`, `SCHEME_COLOURS` (JSON).

State lives in `~/.local/state/caelestia/wallpaper/`, caches in `~/.cache/caelestia/`.
