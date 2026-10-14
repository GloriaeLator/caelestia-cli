import json
import os
import socket


def get_monitor_sizes() -> list[tuple[int, int]] | None:
    """Return (width, height) of each Hyprland monitor, or None if Hyprland isn't running."""
    sig = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
    runtime = os.getenv("XDG_RUNTIME_DIR")
    if not sig or not runtime:
        return None

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(f"{runtime}/hypr/{sig}/.socket.sock")
            sock.send(b"j/monitors")
            resp = b""
            while chunk := sock.recv(8192):
                resp += chunk
        return [(m["width"], m["height"]) for m in json.loads(resp)]
    except (OSError, ValueError, KeyError):
        return None
