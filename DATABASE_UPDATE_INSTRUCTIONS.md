# Database Update Instructions - Fix Video Display

## Issue
Videos and other media files are not displaying in the recent notes feed because the database view structure is outdated.

## Solution
You need to update the `note_view` in your Supabase database to use the new media structure.

### Steps:

1. **Log into your Supabase Dashboard**
   - Go to https://app.supabase.com
   - Navigate to your project
   - Go to the "SQL Editor" tab

2. **Run the Update Query**
   Copy and paste this SQL query into the SQL Editor and run it:

```sql
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
```

3. **Verify the Update**
   After running the query, you should see a success message. The view will now return `media_files` instead of `media_urls`.

### Alternative Method (if you have Supabase CLI):

If you have the Supabase CLI installed, you can run:
```bash
supabase db push
```

This will apply the `update_note_view_for_media.sql` file to your database.

### What This Fixes:
- Videos will now display properly in the notes feed
- All media types (images, videos, documents) will show with proper icons and metadata
- The X/Twitter-style media preview will work correctly

After updating the database view, restart your application and try adding a video file to a note. It should now display properly in the recent notes feed. 