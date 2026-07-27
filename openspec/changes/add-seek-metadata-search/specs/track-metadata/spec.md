## ADDED Requirements

### Requirement: Read track metadata with filename fallback
The system SHALL read title, artist, album, and duration from an audio
file's tags, and SHALL fall back to the filename when tags are missing or
unreadable rather than failing.

#### Scenario: Reading a file with complete tags
- **WHEN** metadata is read from a file carrying title, artist, and album
  tags
- **THEN** those values are returned

#### Scenario: Reading a file with no tags
- **WHEN** metadata is read from a file that carries no tags at all
- **THEN** the title SHALL be the filename without its extension, and
  artist and album SHALL be empty rather than absent

#### Scenario: Reading a file with unreadable tags
- **WHEN** the tag library raises while parsing a corrupt or malformed file
- **THEN** the system SHALL return filename-based metadata instead of
  propagating the error

#### Scenario: Reporting duration
- **WHEN** metadata is read from a playable audio file
- **THEN** the track's duration in seconds is reported

#### Scenario: Duration is unavailable
- **WHEN** the file's duration cannot be determined
- **THEN** the duration SHALL be reported as 0 rather than `None`

### Requirement: Human-readable track description
The system SHALL provide a single display string for a track, combining
artist and title where both are known.

#### Scenario: Describing a fully tagged track
- **WHEN** a track has both artist and title
- **THEN** the description combines them, artist first

#### Scenario: Describing an untagged track
- **WHEN** a track has only a filename-derived title
- **THEN** the description is that title alone, with no separator left
  dangling
