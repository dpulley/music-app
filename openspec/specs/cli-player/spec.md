# cli-player Specification

## Purpose
TBD - created by archiving change add-library-scan-and-cli. Update Purpose after archive.
## Requirements
### Requirement: List discovered tracks
The command-line interface SHALL scan a directory given by the user and
present the tracks it finds as a numbered list, so a track can be chosen by
number.

#### Scenario: Listing tracks found in a directory
- **WHEN** the CLI is started against a directory containing audio files
- **THEN** each track is displayed with a 1-based number and its filename

#### Scenario: Starting against a directory with no audio files
- **WHEN** the CLI is started against a directory containing no supported
  audio files
- **THEN** the user is told that no tracks were found, and the program exits
  without error

#### Scenario: Starting against an invalid directory
- **WHEN** the CLI is started against a path that does not exist or is not a
  directory
- **THEN** the user is shown an error message and the program exits with a
  non-zero status

### Requirement: Select and play a track
The command-line interface SHALL let the user choose a listed track by
number and play it, and SHALL control playback of the selected track.

#### Scenario: Playing a track by number
- **WHEN** the user enters the play command with a valid track number
- **THEN** that track is loaded and playback starts

#### Scenario: Choosing a number that is not in the list
- **WHEN** the user enters the play command with a number outside the
  listed range
- **THEN** the user is shown an error message and the session continues

#### Scenario: Controlling playback of the current track
- **WHEN** the user enters the pause, resume, or stop command while a track
  is loaded
- **THEN** the corresponding playback operation is performed

#### Scenario: Issuing a playback command with nothing loaded
- **WHEN** the user enters a playback command before any track has been
  played
- **THEN** the user is told that no track is loaded, and the session
  continues rather than crashing

#### Scenario: A track that cannot be decoded
- **WHEN** loading a selected track fails because the file is unreadable or
  corrupt
- **THEN** the error is reported for that track and the session continues

#### Scenario: Leaving the session
- **WHEN** the user enters the quit command
- **THEN** playback stops and the program exits cleanly

