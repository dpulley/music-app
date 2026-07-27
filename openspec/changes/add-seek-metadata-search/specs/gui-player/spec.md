## ADDED Requirements

### Requirement: Seekable progress display
The graphical player SHALL show how far through the current track playback
has reached, and SHALL let the user move playback to any point in the track
by dragging that control.

#### Scenario: Progress advances during playback
- **WHEN** a track is playing
- **THEN** the progress control advances toward the end of the track as
  playback proceeds

#### Scenario: Dragging to a new position
- **WHEN** the user drags the progress control to a position and releases it
- **THEN** playback moves to the corresponding point in the track

#### Scenario: Progress is not fought while dragging
- **WHEN** the user is dragging the progress control
- **THEN** automatic position updates SHALL NOT move the control out from
  under them

#### Scenario: Elapsed and total time are shown
- **WHEN** a track is loaded
- **THEN** the elapsed position and the track's total duration are displayed
  in minutes and seconds

#### Scenario: Progress with nothing loaded
- **WHEN** no track has been loaded
- **THEN** the progress control sits at the start and the time display shows
  zero rather than a blank or an error

### Requirement: Search field
The graphical player SHALL provide a text field that filters the visible
track list as the user types.

#### Scenario: Typing filters the visible list
- **WHEN** the user types into the search field
- **THEN** the sidebar shows only tracks matching the query

#### Scenario: Emptying the field restores the library
- **WHEN** the user clears the search field
- **THEN** the sidebar shows every track again

## MODIFIED Requirements

### Requirement: Present the library as a selectable track list
The graphical player SHALL display the discovered tracks as a list the user
can browse and select from, SHALL indicate which track is currently
selected, and SHALL label each track using its metadata where available.

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

#### Scenario: Labelling tracks with metadata
- **WHEN** a listed track carries artist and title tags
- **THEN** the list shows those rather than the raw filename

### Requirement: Now-playing display
The graphical player SHALL show which track is currently loaded, described
by its metadata where available, and whether it is playing, paused, or
stopped.

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

#### Scenario: Naming a tagged track
- **WHEN** the loaded track carries artist and title tags
- **THEN** the display uses those rather than the raw filename
