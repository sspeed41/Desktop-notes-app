-- Update note_view to include structured media information
CREATE OR REPLACE VIEW public.note_view AS
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
    sr.name AS series_name,
    COALESCE(
        (SELECT array_agg(tag.label)
         FROM note_tag
         JOIN tag ON note_tag.tag_id = tag.id
         WHERE note_tag.note_id = n.id),
        '{}'::text[]
    ) AS tags,
    COALESCE(
        (SELECT jsonb_agg(
            jsonb_build_object(
                'file_url', m.file_url,
                'media_type', m.media_type,
                'filename', m.filename
            )
        )
         FROM media m
         WHERE m.note_id = n.id),
        '[]'::jsonb
    ) AS media_files
FROM
    note n
LEFT JOIN driver d ON n.driver_id = d.id
LEFT JOIN session s ON n.session_id = s.id
LEFT JOIN track t ON s.track_id = t.id
LEFT JOIN series sr ON s.series_id = sr.id; 