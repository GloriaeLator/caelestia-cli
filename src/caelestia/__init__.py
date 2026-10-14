import argparse
import json
import sys

from caelestia.utils.paths import wallpapers_dir
from caelestia.utils.wallpaper import get_colours_for_wall, get_wallpaper, set_random, set_wallpaper


def main() -> None:
    parser = argparse.ArgumentParser(prog="caelestia-wallpaper", description="Wallpaper engine")
    parser.add_argument("-p", "--print", nargs="?", const=get_wallpaper(), metavar="PATH", help="print the scheme for a wallpaper")
    parser.add_argument("-r", "--random", nargs="?", const=wallpapers_dir, metavar="DIR", help="switch to a random wallpaper")
    parser.add_argument("-f", "--file", help="the path to the wallpaper to switch to")
    parser.add_argument("-n", "--no-filter", action="store_true", help="do not filter by size")
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.8,
        help="the minimum percentage of the smallest monitor size the image must be greater than to be selected",
    )
    parser.add_argument(
        "-N", "--no-smart", action="store_true", help="do not automatically pick mode/variant from wallpaper colour"
    )
    args = parser.parse_args()

    try:
        if args.print:
            print(json.dumps(get_colours_for_wall(args.print, args.no_smart)))
        elif args.file:
            set_wallpaper(args.file, args.no_smart)
        elif args.random:
            set_random(args.random, args.no_filter, args.threshold, args.no_smart)
        else:
            print(get_wallpaper() or "No wallpaper set")
    except KeyboardInterrupt:
        pass
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
