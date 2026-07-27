## ADDED Requirements

### Requirement: Present the library as a selectable track list
The graphical player SHALL display the discovered tracks as a list the user
can browse and select from, and SHALL indicate which track is currently
selected.

#### Scenario: Opening the window with a scanned library
- **WHEN** the graphical player is opened against a directory containing
  audio files
- **THEN** every discovered track is listed, and the first track is selected

#### Scenario: Selecting a track without starting playback
- **WHEN** the user selects a track in the list while another track is
  playing
- **THEN** the selection moves to that track and the currently playing audio
  SHALL NOT be interrupted

#### Scenario: Opening against a directory with no audio
- **WHEN** the graphical player is opened against a directory containing no
  supported audio files
- **THEN** the user is shown an empty-library message and the transport
  controls are unavailable rather than erroring

### Requirement: Transport controls
The graphical player SHALL provide controls to play or pause the selected
track, stop playback, and move to the previous or next track.

#### Scenario: Playing the selected track
- **WHEN** the user activates the play control with a track selected
- **THEN** that track is loaded and playback starts

#### Scenario: Pausing and resuming with one control
- **WHEN** the user activates the play/pause control while audio is playing
- **THEN** playback pauses; activating it again resumes from the same
  position

#### Scenario: Stopping playback
- **WHEN** the user activates the stop control
- **THEN** playback halts

#### Scenario: Skipping to the next track
- **WHEN** the user activates the next control and a following track exists
- **THEN** that track becomes current and starts playing

#### Scenario: Skipping past the last track
- **WHEN** the user activates the next control while the last track is
  current
- **THEN** playback of the current track is unaffected and no error is shown

#### Scenario: Returning to the previous track
- **WHEN** the user activates the previous control and a preceding track
  exists
- **THEN** that track becomes current and starts playing

### Requirement: Now-playing display
The graphical player SHALL show which track is currently loaded and whether
it is playing, paused, or stopped.

#### Scenario: Showing a playing track
- **WHEN** a track is playing
- **THEN** the display names that track and indicates it is playing

#### Scenario: Showing a paused track
- **WHEN** playback is paused
- **THEN** the display names the track and indicates it is paused

#### Scenario: Showing no track
- **WHEN** nothing has been played yet
- **THEN** the display indicates that no track is loaded rather than showing
  a blank or placeholder name

### Requirement: Playback failures do not close the window
The graphical player SHALL report a track that cannot be played and remain
usable.

#### Scenario: Selecting an unplayable file
- **WHEN** loading the chosen track fails because the file is unreadable or
  corrupt
- **THEN** the failure is reported in the now-playing display and the window
  stays open and responsive
