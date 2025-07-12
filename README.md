# Wise Desktop Note App

A desktop note application for racing data and observations, built with PySide6 and Supabase.

## Features

- **Clean, minimalistic UI** inspired by X/Twitter design
- **Racing-focused data structure** with tracks, series, drivers, and sessions
- **Offline-first architecture** with local caching using TinyDB
- **Real-time synchronization** with Supabase backend
- **Flexible tagging system** for organizing notes
- **Media attachments** support for images, videos, and CSV files
- **Advanced filtering** by track type, series, drivers, and tags

## Tech Stack

- **Frontend**: PySide6 (Qt for Python)
- **Backend**: Supabase (PostgreSQL + Real-time)
- **Caching**: TinyDB (offline storage)
- **Models**: Pydantic (data validation)
- **Packaging**: Poetry + Briefcase

## Quick Start

### 1. Prerequisites

- Python 3.12+
- Poetry (for dependency management)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd CursorDesktopNotesV1.0

# Install dependencies
poetry install

# Copy environment configuration
cp .env.example .env
```

### 3. Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL from `supabase/schema.sql` in your Supabase SQL editor
3. Update `.env` with your Supabase URL and keys:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anonymous-key-here
SUPABASE_SERVICE_ROLE=your-service-role-key-here
ORG_ID=your-org-id
```

### 4. Run the Application

```bash
# Run the desktop app
poetry run python app/main.py

# Or use the development script
chmod +x scripts/dev_run.sh
./scripts/dev_run.sh
```

## Project Structure

```
CursorDesktopNotesV1.0/
├── app/                     # Python application
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── settings.py          # Configuration and constants
│   ├── ui/                  # User interface components
│   │   ├── main_window.py   # Main application window
│   │   ├── note_dialog.py   # New note creation dialog
│   │   ├── feed_view.py     # Notes timeline/feed
│   │   └── components/      # Reusable UI components
│   │       ├── note_card.py # Individual note display
│   │       └── filters.py   # Filter sidebar
│   └── data/                # Data layer
│       ├── models.py        # Pydantic data models
│       ├── supabase_client.py # Supabase API wrapper
│       └── cache.py         # Offline caching system
├── supabase/
│   └── schema.sql           # Database schema
├── scripts/
│   └── dev_run.sh           # Development runner script
├── pyproject.toml           # Poetry configuration
└── README.md
```

## Database Schema

The application uses the following main entities:

- **Tracks**: Racing venues with types (Superspeedway, Intermediate, Short Track, Road Course)
- **Series**: Racing series (NASCAR Cup, Xfinity, Truck, etc.)
- **Drivers**: Individual drivers associated with series
- **Sessions**: Practice, Qualifying, or Race sessions
- **Notes**: User observations and insights
- **Tags**: Categorization labels for notes
- **Media**: File attachments for notes

## Track Types

Based on the NASCAR schedule provided:

- **Superspeedway**: Daytona, Talladega
- **Intermediate**: Atlanta, Charlotte, Texas, Kansas, Las Vegas, etc.
- **Short Track**: Martinsville, Bristol, Phoenix, Richmond, etc.
- **Road Course**: Sonoma, Watkins Glen, COTA, Chicago Street Course

## Development

### Adding New Features

1. **UI Components**: Add new widgets in `app/ui/components/`
2. **Data Models**: Extend models in `app/data/models.py`
3. **Database Changes**: Update `supabase/schema.sql`
4. **Caching**: Modify `app/data/cache.py` for offline support

### Styling

The app uses a neutral, X/Twitter-inspired color scheme defined in `app/settings.py`:

- Primary: #1DA1F2 (Twitter Blue)
- Background: #FFFFFF (White)
- Surface: #F7F9FA (Light Gray)
- Text Primary: #14171A (Dark Gray)
- Border: #E1E8ED (Light Border)

### Building for Distribution

```bash
# Install briefcase
poetry add --group dev briefcase

# Create app bundle
poetry run briefcase create

# Build distributable
poetry run briefcase build

# Package for distribution (macOS)
poetry run briefcase package
```

## Environment Variables

Create a `.env` file with these variables:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anonymous-key-here
SUPABASE_SERVICE_ROLE=your-service-role-key-here
ORG_ID=your-organization-id
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please use the GitHub issue tracker. 