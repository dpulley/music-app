# music-library Specification

## Purpose
TBD - created by archiving change add-library-scan-and-cli. Update Purpose after archive.
## Requirements
### Requirement: Discover playable files in a directory
The system SHALL find audio files under a given directory, including nested
subdirectories by default, returning only files whose extensions are in the
project's supported-format list.

#### Scenario: Scanning a directory containing audio files
- **WHEN** `scan_directory()` is called on a folder holding `.mp3`, `.wav`,
  `.flac`, and `.ogg` files
- **THEN** all four files are returned

#### Scenario: Non-audio files are excluded
- **WHEN** a scanned folder also contains files such as `.txt`, `.jpg`, or
  `.pdf`
- **THEN** those files SHALL NOT appear in the result

#### Scenario: Nested directories are included by default
- **WHEN** audio files exist in subdirectories of the scanned folder
- **THEN** those files are included in the result

#### Scenario: Recursion can be disabled
- **WHEN** `scan_directory()` is called with recursion disabled
- **THEN** only audio files directly inside the given folder are returned

#### Scenario: Results are in a stable order
- **WHEN** the same directory is scanned twice without changes
- **THEN** the results SHALL be in the same, sorted order both times

#### Scenario: Scanning a folder with no audio files
- **WHEN** the scanned folder contains no supported audio files
- **THEN** an empty list is returned and no exception is raised

#### Scenario: Scanning a path that is not a directory
- **WHEN** `scan_directory()` is called with a path that does not exist or is
  a file
- **THEN** the system SHALL raise `NotADirectoryError`

### Requirement: Ordered playlist with a current-track cursor
The system SHALL hold discovered tracks as an ordered collection with a
notion of the currently selected track, and SHALL allow moving forward and
backward through it.

#### Scenario: Creating a playlist from scanned tracks
- **WHEN** a `Playlist` is created from a list of track paths
- **THEN** its length equals the number of tracks and its current track is
  the first one

#### Scenario: Advancing to the next track
- **WHEN** `next()` is called and a following track exists
- **THEN** the current track becomes that following track and it is returned

#### Scenario: Advancing past the last track
- **WHEN** `next()` is called while the last track is current
- **THEN** the system SHALL return `None` and the current track SHALL remain
  the last track

#### Scenario: Moving to the previous track
- **WHEN** `previous()` is called and a preceding track exists
- **THEN** the current track becomes that preceding track and it is returned

#### Scenario: Moving before the first track
- **WHEN** `previous()` is called while the first track is current
- **THEN** the system SHALL return `None` and the current track SHALL remain
  the first track

#### Scenario: Selecting a track by position
- **WHEN** `select()` is called with a valid index
- **THEN** the track at that index becomes current and is returned

#### Scenario: Selecting an out-of-range position
- **WHEN** `select()` is called with an index outside the playlist
- **THEN** the system SHALL raise `IndexError` and the current track SHALL be
  unchanged

#### Scenario: Querying an empty playlist
- **WHEN** a `Playlist` is created with no tracks
- **THEN** its current track SHALL be `None` and navigation SHALL return
  `None` without raising

