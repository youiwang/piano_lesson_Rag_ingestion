# Piano Lesson Notes System

A Streamlit-based piano teaching notebook that stores lesson records in a Google Sheet. It helps piano teachers or students track lesson history, repertoire, and practice notes in one place.

## Overview

The app manages four worksheet tabs in a shared spreadsheet:

- `Books`
- `Pieces`
- `Lessons`
- `Lesson_Details`

It supports:

- creating a new lesson record
- selecting or creating a book
- selecting or creating a piece for that book
- logging page numbers, measures, and practice focus notes
- reviewing historical notes by book or piece
- editing lesson metadata and individual piece notes

## Project structure

- `app.py` — Streamlit UI and Google Sheets write/read logic
- `main.py` — simple starter entry point
- `pyproject.toml` — Python project metadata and dependencies
- `README.md` — project documentation

## Features

- Add a new lesson with `class_id`, date, and recording filename
- Create a book record inline when needed
- Create a new piece inside a book or select an existing one
- Prevent duplicate entries for the same lesson and piece combination
- Save practice details such as page, measures, and focus notes
- View a filtered historical overview of all lesson records
- Update lesson metadata and existing lesson details directly in the app

## Tech stack

- Python 3.13+
- Streamlit
- pandas
- `st-gsheets-connection`

## Installation

Using `uv` is recommended:

```bash
uv sync
```

## Run the app

```bash
uv run streamlit run app.py
```

## Google Sheets configuration

Before using the app, update the `sheet_url` in `app.py` to the real spreadsheet URL:

```python
sheet_url = "https://docs.google.com/spreadsheets/d/.../edit?gid=1002#gid=1002"
```

The workbook should contain the following tabs:

- `Books`
- `Pieces`
- `Lessons`
- `Lesson_Details`

If the spreadsheet is empty, initialize each tab with the required columns before first use.

## Recommended data model

### Books

Typical columns:

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

Typical columns:

- `piece_id`
- `book_id`
- `piece_name`

### Lessons

Typical columns:

- `class_id`
- `date`
- `audio_filename`

### Lesson_Details

Typical columns:

- `detail_id`
- `class_id`
- `piece_id`
- `page`
- `measures`
- `focus`

## Usage

1. Start the app with Streamlit.
2. Enter the lesson number and lesson date.
3. Choose an existing book or add a new one.
4. Choose an existing piece or add a new one.
5. Fill in page number, measures, and the lesson focus notes.
6. Click `💾 儲存新筆記` to save the record.
7. Use the overview tab to browse historical notes and apply filters.
8. Use the edit tab to update lesson metadata or a specific piece note.

## Notes

This project currently uses a hardcoded Google Sheets URL, so it is best suited for a single managed workbook. For production use, consider moving the spreadsheet URL into an environment variable or configuration file.

## License

No explicit license has been set for this project yet.
