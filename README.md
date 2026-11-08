# Piano Lesson Notes System

A lightweight Streamlit application for recording piano lesson details and saving them into Google Sheets. It is designed for tracking:

- lesson number and date
- audio file name
- book and piece information
- practice page/measures
- lesson focus notes

The app writes records into four Google Sheets tabs:

- Books
- Pieces
- Lessons
- Lesson_Details

## Project structure

- `app.py` — main Streamlit UI and data writing logic
- `main.py` — starter script for the package entry point
- `pyproject.toml` — project metadata and Python dependencies

## Features

- Add lesson metadata such as class number, date, and recording filename
- Select existing books or add a new one inline
- Select existing pieces or add a new piece under the chosen book
- Save practice notes, page references, measures, and focus points
- Automatically maintain Google Sheets via `streamlit_gsheets`

## Tech stack

- Python 3.13+
- Streamlit
- pandas
- streamlit-gsheets-connection

## Setup

Using `uv` is recommended:

```bash
uv sync
```

Run the app:

```bash
uv run streamlit run app.py
```

## Important configuration

Before using the app, open `app.py` and update the `sheet_url` value to your real Google Sheets URL:

```python
sheet_url = "https://docs.google.com/spreadsheets/d/.../edit?gid=1003#gid=1003"
```

The app expects the spreadsheet to contain worksheet tabs named:

- `Books`
- `Pieces`
- `Lessons`
- `Lesson_Details`

If the spreadsheet is empty or missing tabs, the app should be initialized with the corresponding columns first.

## Data model

### Books
Typical fields:

- `book_id`
- `book_title`
- `original_title`
- `author_editor`
- `publisher`
- `series`
- `publish_date`
- `description`
- `isbn`

### Pieces
Typical fields:

- `piece_id`
- `book_id`
- `piece_name`

### Lessons
Typical fields:

- `class_id`
- `date`
- `audio_filename`

### Lesson_Details
Typical fields:

- `detail_id`
- `class_id`
- `piece_id`
- `page`
- `measures`
- `focus`

## Usage

1. Launch the app with Streamlit.
2. Fill in the lesson information.
3. Choose an existing book or add a new one.
4. Choose an existing piece or add a new one.
5. Enter page, measures, and focus notes.
6. Click `儲存筆記` to write data to the Google Sheet.

## Notes

This project currently uses a hardcoded Google Sheets connection and is best suited for a single, managed workbook. For production use, it would be a good idea to move the spreadsheet URL and connection details into environment variables or a configuration file.

## License

No explicit license has been set for this project yet.
