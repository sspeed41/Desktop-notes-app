-- Add NASCAR drivers to the database (no series association)
-- Run this in your Supabase SQL Editor

-- First, add unique constraint on driver names if it doesn't exist
ALTER TABLE driver ADD CONSTRAINT unique_driver_name UNIQUE (name);

-- Remove series_id constraint from existing drivers (if any exist)
UPDATE driver SET series_id = NULL;

-- Add drivers without series association (they can run in multiple series)
INSERT INTO driver (name) VALUES
('Kyle Larson'),
('Alex Bowman'),
('Ross Chastain'),
('Daniel Suarez'),
('Austin Dillon'),
('Connor Zilisch'),
('Carson Kvapil'),
('Austin Hill'),
('Jesse Love'),
('Nick Sanchez'),
('Daniel Dye'),
('Grant Enfinger'),
('Daniel Hemric'),
('Connor Mosack'),
('Kaden Honeycutt'),
('Rajah Caruth'),
('Andres Perez'),
('Matt Mills'),
('Dawson Sutton'),
('Tristan McKee'),
('Hailie Meza'),
('Corey Day'),
('Ben Maier'),
('Tyler Reif'),
('Brenden Queen')
ON CONFLICT (name) DO NOTHING;  -- Prevent duplicates if some drivers already exist

-- Update the note_view to include category field (was missing)
DROP VIEW IF EXISTS note_view;
CREATE VIEW note_view AS
SELECT 
    n.id,
    n.body,
    n.shared,
    n.created_by,
    n.created_at,
    n.updated_at,
    n.category,
    d.name AS driver_name,
    s.date AS session_date,
    s.session AS session_type,
    t.name AS track_name,
    t.type AS track_type,
    ser.name AS series_name,
    COALESCE(
        array_remove(array_agg(DISTINCT tag.label), NULL),
        ARRAY[]::text[]
    ) AS tags,
    COALESCE(
        array_remove(array_agg(DISTINCT m.file_url), NULL),
        ARRAY[]::text[]
    ) AS media_urls
FROM note n
LEFT JOIN driver d ON n.driver_id = d.id
LEFT JOIN session s ON n.session_id = s.id
LEFT JOIN track t ON s.track_id = t.id
LEFT JOIN series ser ON s.series_id = ser.id
LEFT JOIN note_tag nt ON n.id = nt.note_id
LEFT JOIN tag ON nt.tag_id = tag.id
LEFT JOIN media m ON n.id = m.note_id
GROUP BY n.id, n.body, n.shared, n.created_by, n.created_at, n.updated_at, n.category,
         d.name, s.date, s.session, t.name, t.type, ser.name
ORDER BY n.created_at DESC;

-- Verify the drivers were added
SELECT name FROM driver ORDER BY name; 