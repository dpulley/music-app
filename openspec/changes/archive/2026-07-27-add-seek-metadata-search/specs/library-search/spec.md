## ADDED Requirements

### Requirement: Filter the library by a text query
The system SHALL narrow the visible track list to tracks matching a
case-insensitive query against title, artist, album, or filename, without
altering the underlying library.

#### Scenario: Matching by title or filename
- **WHEN** a query matching part of a track's title or filename is entered
- **THEN** only matching tracks are visible

#### Scenario: Matching by artist or album
- **WHEN** a query matching part of a track's artist or album is entered
- **THEN** that track is visible

#### Scenario: Matching is case-insensitive
- **WHEN** a query differs from the track's text only in letter case
- **THEN** the track still matches

#### Scenario: No matches
- **WHEN** a query matches nothing in the library
- **THEN** the visible list is empty and no error is raised

#### Scenario: Clearing the search
- **WHEN** the query is cleared
- **THEN** every track in the library is visible again

#### Scenario: Searching does not disturb playback
- **WHEN** a query is entered while a track is playing
- **THEN** playback SHALL continue uninterrupted and the current track
  SHALL remain current, even if it is filtered out of view
