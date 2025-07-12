-- Update Racing Notes Tags
-- Remove: Setup, Strategy, Tire Wear, Fuel, Weather, Incident, Performance
-- Add: Crash, Tactical, Technical
-- Note: Practice and Race are session types, not tags

-- First, remove any note_tag associations for tags being deleted
-- This ensures referential integrity
DELETE FROM note_tag 
WHERE tag_id IN (
    SELECT id FROM tag 
    WHERE label IN ('Setup', 'Strategy', 'Tire Wear', 'Fuel', 'Weather', 'Incident', 'Performance')
);

-- Remove the tags themselves
DELETE FROM tag 
WHERE label IN ('Setup', 'Strategy', 'Tire Wear', 'Fuel', 'Weather', 'Incident', 'Performance');

-- Add the new tags
INSERT INTO tag (label) VALUES
('Crash'),
('Tactical'),
('Technical');

-- Display the updated tag list
SELECT label FROM tag ORDER BY label; 