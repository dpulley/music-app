"""Command-line player.

A prompt loop rather than one-shot flags: playback is stateful (play, then
pause, then stop), so a ``--play track.mp3`` invocation would exit before the
sound finished.

Input and output are injectable so the loop can be driven by tests with
scripted commands instead of a real terminal.
"""

import argparse
import sys

from src.audio_player import AudioPlayer
from src.database.library import scan_directory
from src.database.playlist import Playlist

HELP_TEXT = """Commands:
  list        show the numbered track list
  play N      play track number N
  pause       pause the current track
  resume      resume the current track
  stop        stop playback
  help        show this message
  quit        stop playback and exit"""


def format_track_list(playlist):
    """Render the playlist as 1-based numbered lines for display."""
    return "\n".join(
        f"{number:>3}. {track.name}"
        for number, track in enumerate(playlist, start=1)
    )


def run_session(playlist, player, read_command=input, write=print):
    """Run the interactive command loop until the user quits.

    Args:
        playlist: A :class:`~src.database.playlist.Playlist` of tracks.
        player: An :class:`~src.audio_player.AudioPlayer`.
        read_command: Callable returning the next command line. Defaults to
            :func:`input`; tests pass a scripted callable.
        write: Callable for output. Defaults to :func:`print`.

    Returns:
        0 on a clean exit.
    """
    write(HELP_TEXT)

    while True:
        try:
            raw = read_command("> ")
        except (EOFError, KeyboardInterrupt):
            # Piped input running out, or Ctrl-C, both mean "done" - treat
            # them like quit rather than dumping a traceback on the user.
            write("")
            break

        command, _, argument = raw.strip().partition(" ")
        command = command.lower()

        if not command:
            continue

        if command in ("quit", "exit", "q"):
            break

        if command in ("help", "?"):
            write(HELP_TEXT)

        elif command == "list":
            write(format_track_list(playlist))

        elif command == "play":
            _handle_play(playlist, player, argument, write)

        elif command in ("pause", "resume", "stop"):
            _handle_transport(player, command, write)

        else:
            write(f"Unknown command: {command!r}. Type 'help' for commands.")

    _stop_quietly(player)
    write("Goodbye.")
    return 0


def _handle_play(playlist, player, argument, write):
    try:
        number = int(argument.strip())
    except ValueError:
        write(f"Play needs a track number, e.g. 'play 1' (got {argument.strip()!r})")
        return

    try:
        track = playlist.select(number - 1)  # user-facing numbering is 1-based
    except IndexError:
        write(f"No track {number}. Choose 1-{len(playlist)}.")
        return

    try:
        player.load(track)
        player.play()
    except Exception as exc:  # noqa: BLE001
        # Broad by design: a corrupt or mislabeled file shouldn't end the
        # session. The backend can raise anything from OSError to a
        # miniaudio-specific error, and none of them are worth exiting over.
        write(f"Could not play {track.name}: {type(exc).__name__}: {exc}")
        return

    write(f"Playing: {track.name}")


def _handle_transport(player, command, write):
    try:
        getattr(player, command)()
    except RuntimeError:
        # AudioPlayer's own guard for "nothing loaded yet" - reuse it rather
        # than tracking loaded-ness a second time here.
        write("No track loaded. Use 'play N' first.")
        return

    write(f"{command.capitalize()}d." if command != "stop" else "Stopped.")


def _stop_quietly(player):
    """Stop playback on the way out, ignoring 'nothing was loaded'."""
    try:
        player.stop()
    except RuntimeError:
        pass


def build_parser():
    parser = argparse.ArgumentParser(
        prog="music-app",
        description="Play music files from a directory.",
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


def main(argv=None, write=print, read_command=input):
    """Entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)

    try:
        tracks = scan_directory(args.directory, recursive=not args.no_recursive)
    except NotADirectoryError as exc:
        write(f"Error: {exc}")
        return 1

    if not tracks:
        write(f"No playable audio files found in {args.directory}")
        return 0

    playlist = Playlist(tracks)
    write(f"Found {len(playlist)} track(s):")
    write(format_track_list(playlist))

    return run_session(playlist, AudioPlayer(), read_command=read_command, write=write)


if __name__ == "__main__":
    sys.exit(main())
