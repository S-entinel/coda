# coda

*a quiet place for quiet thoughts*

A minimal terminal-based journal app written in Python. Write daily entries, track your mood, and look back on past days — all from the command line.

This project started as a small learning exercise (built step by step while learning file I/O, functions, and error handling) and grew into a fully featured journaling tool.

## Features

- **Write entries** with a timestamp and a mood rating (1–5, shown as ♦ glyphs)
- **Read** all past entries
- **Search** by keyword, mood, or date
- **Edit** existing entries (text and/or mood), with an "edited" timestamp
- **Delete** entries, with a confirmation step
- **Mood summary** — entry count, average mood, and your best and hardest days
- Entries stored as JSON for easy backup or future extension
- Optional colour output (degrades gracefully if `colorama` isn't installed)

## Requirements

- Python 3.x
- [`colorama`](https://pypi.org/project/colorama/) (optional — used for colour output; the app falls back to plain text if it's not installed)

## Installation

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install -r requirements.txt   # optional, for colour output
```

## Usage

Run the app with:

```bash
python journal.py
```

You'll be shown a menu with the following options:

| Key | Action |
|-----|--------|
| `w` | Write a new entry |
| `r` | Read all entries |
| `s` | Search entries |
| `e` | Edit an entry |
| `d` | Delete an entry |
| `m` | Mood summary |
| `q` | Quit |

## Data storage

Entries are saved to `journal.json` in the same directory as `journal.py`. This file is created automatically the first time you write an entry, and is excluded from version control via `.gitignore` to keep your personal entries private.

Each entry is stored as:

```json
{
  "timestamp": "10/06/2026 14:32:10",
  "mood": 4,
  "text": "Today was a good day.",
  "edited_at": null
}
```
