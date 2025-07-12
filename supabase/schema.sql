-- WiseDesktopNoteApp Database Schema
-- Racing Notes and Media Management System

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tracks
CREATE TABLE track (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        TEXT NOT NULL,
  type        TEXT CHECK (type IN ('Superspeedway','Intermediate','Short Track','Road Course')) NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Series
CREATE TABLE series (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Drivers
CREATE TABLE driver (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        TEXT NOT NULL,
  series_id   UUID REFERENCES series(id),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Sessions
CREATE TYPE session_enum AS ENUM ('Practice','Qualifying','Race');
CREATE TABLE session (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date        DATE NOT NULL,
  session     session_enum NOT NULL,
  track_id    UUID REFERENCES track(id),
  series_id   UUID REFERENCES series(id),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Notes
CREATE TYPE note_category_enum AS ENUM ('General','Track Specific','Series Specific','Driver Specific');
CREATE TABLE note (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  body        TEXT NOT NULL,
  shared      BOOLEAN NOT NULL DEFAULT TRUE,
  driver_id   UUID REFERENCES driver(id),
  session_id  UUID REFERENCES session(id),
  category    note_category_enum NOT NULL DEFAULT 'General',
  created_by  TEXT NOT NULL DEFAULT 'anonymous',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Media
CREATE TYPE media_enum AS ENUM ('video','image','csv');
CREATE TABLE media (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  note_id     UUID REFERENCES note(id) ON DELETE CASCADE,
  file_url    TEXT NOT NULL,
  media_type  media_enum NOT NULL,
  size_mb     NUMERIC,
  filename    TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tags
CREATE TABLE tag (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  label       TEXT UNIQUE NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE note_tag (
  note_id UUID REFERENCES note(id) ON DELETE CASCADE,
  tag_id  UUID REFERENCES tag(id) ON DELETE CASCADE,
  PRIMARY KEY (note_id, tag_id)
);

-- Sample Data: NASCAR Series
INSERT INTO series (name) VALUES
('NASCAR Cup Series'),
('NASCAR Xfinity Series'),
('NASCAR Craftsman Truck Series'),
('INDYCAR Series'),
('Formula 1');

-- Sample Data: Default Tags
INSERT INTO tag (label) VALUES
('Qualifying'),
('Restart'),
('Entry'),
('Exit'),
('Min Speed'),
('Proximity'),
('Angle'),
('Shape'),
('Pass'),
('Aero'),
('Pit Road'),
('Green Pit Entry'),
('Green Pit Exit'),
('Setup'),
('Strategy'),
('Tire Wear'),
('Fuel'),
('Weather'),
('Incident'),
('Performance');

-- Sample Data: NASCAR Tracks (User will correct track types)
INSERT INTO track (name, type) VALUES
('Daytona International Speedway', 'Superspeedway'),
('Talladega Superspeedway', 'Superspeedway'),
('Atlanta Motor Speedway', 'Superspeedway'),
('Charlotte Motor Speedway', 'Intermediate'),
('Texas Motor Speedway', 'Intermediate'),
('Kansas Speedway', 'Intermediate'),
('Las Vegas Motor Speedway', 'Intermediate'),
('Michigan International Speedway', 'Intermediate'),
('Homestead-Miami Speedway', 'Intermediate'),
('Nashville Superspeedway', 'Intermediate'),
('Pocono Raceway', 'Intermediate'),
('Indianapolis Motor Speedway', 'Intermediate'),
('Darlington Raceway', 'Intermediate'),
('World Wide Technology Raceway', 'Intermediate'),
('New Hampshire Motor Speedway', 'Intermediate'),
('Martinsville Speedway', 'Short Track'),
('Bristol Motor Speedway', 'Short Track'),
('Phoenix Raceway', 'Short Track'),
('Richmond Raceway', 'Short Track'),
('North Wilkesboro Speedway', 'Short Track'),
('Iowa Speedway', 'Short Track'),
('Bowman Gray Stadium', 'Short Track'),
('Sonoma Raceway', 'Road Course'),
('Watkins Glen International', 'Road Course'),
('Circuit of the Americas', 'Road Course'),
('Chicago Street Course', 'Road Course'),
('Autodromo Hermanos Rodriguez', 'Road Course'),
('Lime Rock Park', 'Road Course');

-- Create indexes for performance
CREATE INDEX idx_note_created_at ON note(created_at DESC);
CREATE INDEX idx_note_driver_id ON note(driver_id);
CREATE INDEX idx_note_session_id ON note(session_id);
CREATE INDEX idx_media_note_id ON media(note_id);
CREATE INDEX idx_session_date ON session(date);

-- Enable Row Level Security (RLS) - Optional since no auth required
-- ALTER TABLE note ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE media ENABLE ROW LEVEL SECURITY;

-- Create a function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for note table
CREATE TRIGGER update_note_updated_at 
    BEFORE UPDATE ON note 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create a view for notes with related data
CREATE VIEW note_view AS
SELECT 
    n.id,
    n.body,
    n.shared,
    n.created_by,
    n.created_at,
    n.updated_at,
    d.name AS driver_name,
    s.date AS session_date,
    s.session AS session_type,
    t.name AS track_name,
    t.type AS track_type,
    ser.name AS series_name,
    array_agg(DISTINCT tag.label) AS tags,
    array_agg(DISTINCT m.file_url) AS media_urls
FROM note n
LEFT JOIN driver d ON n.driver_id = d.id
LEFT JOIN session s ON n.session_id = s.id
LEFT JOIN track t ON s.track_id = t.id
LEFT JOIN series ser ON s.series_id = ser.id
LEFT JOIN note_tag nt ON n.id = nt.note_id
LEFT JOIN tag ON nt.tag_id = tag.id
LEFT JOIN media m ON n.id = m.note_id
GROUP BY n.id, n.body, n.shared, n.created_by, n.created_at, n.updated_at,
         d.name, s.date, s.session, t.name, t.type, ser.name
ORDER BY n.created_at DESC; 