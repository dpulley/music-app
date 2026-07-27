## ADDED Requirements

### Requirement: Load a validated audio file
The system SHALL validate a file path before loading it for playback,
rejecting paths that do not exist, are not files, or do not have a
supported extension (`.mp3`, `.wav`, `.flac`, `.ogg`).

#### Scenario: Loading a valid, existing audio file
- **WHEN** `AudioPlayer.load()` is called with a path to an existing
  `.wav` file
- **THEN** the file is loaded for playback and no exception is raised

#### Scenario: Loading a nonexistent path
- **WHEN** `AudioPlayer.load()` is called with a path that does not exist
  on disk
- **THEN** the system SHALL raise `FileNotFoundError` and SHALL NOT attempt
  to hand the path to the underlying playback engine

#### Scenario: Loading an unsupported file type
- **WHEN** `AudioPlayer.load()` is called with a path to an existing file
  whose extension is not `.mp3`, `.wav`, `.flac`, or `.ogg`
- **THEN** the system SHALL raise `ValueError` and SHALL NOT attempt to
  hand the path to the underlying playback engine

### Requirement: Transport controls
The system SHALL provide play, pause, resume, and stop operations on the
currently loaded audio file.

#### Scenario: Play starts audio from a loaded file
- **WHEN** `play()` is called after a file has been successfully loaded
- **THEN** the underlying playback engine's play operation is invoked
  exactly once

#### Scenario: Pause suspends playback
- **WHEN** `pause()` is called while playback is active
- **THEN** the underlying playback engine's pause operation is invoked and
  `AudioPlayer.paused` reports `True`

#### Scenario: Resume continues from a paused state
- **WHEN** `resume()` is called while playback is paused
- **THEN** the underlying playback engine's resume operation is invoked and
  `AudioPlayer.paused` reports `False`

#### Scenario: Stop halts playback completely
- **WHEN** `stop()` is called during active or paused playback
- **THEN** the underlying playback engine's stop operation is invoked and
  `AudioPlayer.playing` reports `False`

### Requirement: Seek and volume control
The system SHALL allow repositioning playback to a specific time and
adjusting output volume, and SHALL report current position, duration, and
volume via read-only properties.

#### Scenario: Seeking to a valid position
- **WHEN** `seek(seconds)` is called with a value between 0 and the loaded
  track's duration
- **THEN** the underlying playback engine's seek operation is invoked with
  that value and `AudioPlayer.curr_pos` reflects the new position

#### Scenario: Setting volume within range
- **WHEN** `set_volume(level)` is called with a value between 0.0 and 1.0
- **THEN** the underlying playback engine's volume is updated to that
  value and `AudioPlayer.volume` reports it

### Requirement: State reporting without a loaded file
The system SHALL report a safe, well-defined state when no file has been
loaded yet, rather than raising on state queries.

#### Scenario: Querying state before any file is loaded
- **WHEN** `AudioPlayer.playing`, `.paused`, `.curr_pos`, or `.duration` is
  read before `load()` has ever been called
- **THEN** the system SHALL return a falsy/zero default (no exception)
