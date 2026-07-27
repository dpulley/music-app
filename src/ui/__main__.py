"""GUI entry point: ``python -m src.ui <directory>``.

Mirrors the CLI's invocation shape so the two surfaces feel like the same
app. One deliberate difference: an empty directory still opens the window
(showing the empty-library state) rather than exiting, because a GUI user
expects a window to appear - being dropped straight back to a prompt reads
as a crash.
"""

import argparse
import sys

from src.database.library import scan_directory
from src.ui.app import MusicAppWindow


def build_parser():
    parser = argparse.ArgumentParser(
        prog="python -m src.ui",
        description="Open the graphical music player.",
    )
    parser.add_argument(
        "directory",
        help="Folder to scan for audio files (searched recursively)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only look at files directly inside the folder",
    )
    return parser


def main(argv=None, write=print, window_factory=MusicAppWindow):
    """Entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)

    try:
        tracks = scan_directory(args.directory, recursive=not args.no_recursive)
    except NotADirectoryError as exc:
        write(f"Error: {exc}")
        return 1

    if not tracks:
        write(f"No playable audio files found in {args.directory}")

    window = window_factory(tracks=tracks)
    window.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
