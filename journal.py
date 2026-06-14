"""
coda — a minimal terminal journal.

Entries are stored as JSON (see JOURNAL_FILE) with timestamp, mood (1-5),
text, and an optional edited_at timestamp.

colorama is optional — if it's not installed, the app falls back to
plain text via the HAS_COLOR flag.
"""

import datetime
import json
import os
import random
import re


try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

JOURNAL_FILE = "journal.json"
WIDTH = 60

# Random closing message shown on quit — a small personal touch
# matching the journal's reflective tone.

CLOSING_LINES = [
    "some things are better left as memories.",
    "the snow keeps falling, regardless.",
    "you can't replay it. but you can remember it.",
    "it's okay not to have the words right now.",
    "whatever you're carrying — set it down for tonight.",
    "the melody stays, even after the song ends.",
]

# ── colour helpers ────────────────────────────────────────────

# Each function wraps text in an ANSI colour code if colorama is available,
# otherwise returns the text unchanged.

def dim(text):
    return (Style.DIM + text + Style.RESET_ALL) if HAS_COLOR else text

def soft(text):
    return ("\x1b[38;2;160;180;200m" + text + Style.RESET_ALL) if HAS_COLOR else text

def warm(text):
    return ("\x1b[38;2;200;170;170m"+ text + Style.RESET_ALL) if HAS_COLOR else text

def bright(text):
    return (Fore.WHITE + Style.BRIGHT + text + Style.RESET_ALL) if HAS_COLOR else text

# Higher moods get a cool/blue tint, lower moods a warm/muted tint —
# a subtle emotional cue rather than literal "good/bad" colours.

def mood_color(mood, text):
    if not HAS_COLOR:
        return text
    if mood >= 4:
        return "\x1b[38;2;160;180;200m" + text + Style.RESET_ALL
    elif mood <= 2:
        return "\x1b[38;2;200;170;170m" + text + Style.RESET_ALL
    return text

# ── layout primitives ─────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def rule(char="─"):
    return dim(char * WIDTH)

def box_top():
    return dim("┌" + "─" * (WIDTH - 2) + "┐")

def box_bottom():
    return dim("└" + "─" * (WIDTH - 2) + "┘")

def box_row(text="", align="left"):
    """
    Return one row of a box, padded to WIDTH.

    Colour codes add invisible characters that would otherwise throw off
    the padding calculation, so we strip them before measuring length.
    """
    inner = WIDTH - 4
    plain = re.sub(r'\x1b\[[0-9;]*m', '', text)
    padding = inner - len(plain)

    if align == "center":
        left_pad = padding // 2
        right_pad = padding - left_pad
        padded = " " * left_pad + text + " " * right_pad
    else:
        padded = text + " " * padding

    return dim("│") + " " + padded + " " + dim("│")

def blank_row():
    return dim("│") + " " * (WIDTH - 2) + dim("│")

# ── header ────────────────────────────────────────────────────

def print_header():
    print()
    print(soft("  c o d a"))
    print(dim("  a quiet place for quiet thoughts"))
    print()

# ── mood glyph ────────────────────────────────────────────────

def mood_glyph(mood):
    filled = "♦" * mood
    empty = "♢" * (5 - mood)
    return mood_color(mood, filled) + dim(empty)

# ── entry formatting ──────────────────────────────────────────

def format_entry(entry, index=None):
    """
    Render a single journal entry as a multi-line string.

    If index is given, the entry is numbered (used by pick_entry).
    Shows an '· edited <date>' tag if the entry has been edited.
    """
    prefix = f"{index}.  " if index is not None else "    "
    edited = dim(f"  · edited {entry['edited_at']}") if entry.get("edited_at") else ""
    timestamp = dim(entry["timestamp"])
    glyph = mood_glyph(entry["mood"])
    text = bright(entry["text"])
    return f"{dim(prefix)}{timestamp}  {glyph}\n    {text}{edited}"

# ── data layer ────────────────────────────────────────────────

def load_entries():
    """Load all entries from JOURNAL_FILE, or None if it doesn't exist yet."""
    try:
        with open(JOURNAL_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_entries(entries):
    """Write the full list of entries back to JOURNAL_FILE as JSON."""
    with open(JOURNAL_FILE, "w") as f:
        json.dump(entries, f, indent=2)

# ── shared interaction ────────────────────────────────────────

def pick_entry(entries, prompt="which entry? "):
    """
    Display all entries numbered, then ask the user to pick one.
    Returns the zero-based index, or None if the choice was invalid.
    """
    for i, entry in enumerate(entries, start=1):
        print(format_entry(entry, index=i))
        print()
    try:
        choice = int(input(soft(f"\n  {prompt}")))
        if 1 <= choice <= len(entries):
            return choice - 1
        print(dim("  that entry doesn't exist."))
    except ValueError:
        print(dim("  please enter a number."))
    return None

def ask(prompt, default=None):
    """Styled input prompt. If default is given, shows it in brackets."""
    suffix = dim(f" [{default}]") if default else ""
    return input(soft(f"  {prompt}") + suffix + soft(" › ")).strip()

def confirm(prompt):
    """Ask a yes/no question, returns True only if the answer is 'y'."""
    ans = ask(f"{prompt} (y/n)")
    return ans.lower() == "y"

def pause():
    """Wait for the user to press enter before continuing."""
    input(dim("\n  ↩  press enter to continue"))

# ── screens ───────────────────────────────────────────────────

def screen_write():
    """Prompt for a new entry and mood, then save it to the journal."""
    clear()
    print_header()
    print(rule())
    print()
    text = ask("what's on your mind?")
    if not text:
        print(dim("\n  nothing written. returning."))
        pause()
        return
    print()
    while True:
        try:
            mood = int(ask("how are you feeling?  ♦ = 1 · ♦♦♦♦♦ = 5"))
        except ValueError:
            print(dim("  please type a number."))
            continue
        if 1 <= mood <= 5:
            break
        print(dim("  between 1 and 5, please."))

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    entries = load_entries() or []
    entries.append({"timestamp": now, "mood": mood, "text": text, "edited_at": None})
    save_entries(entries)

    print()
    print(rule())
    print()
    print(f"  {dim(now)}  {mood_glyph(mood)}")
    print(f"  {bright(text)}")
    print()
    print(dim("  saved.  ◆"))
    pause()


def screen_read():
    """Display every journal entry in order."""
    clear()
    print_header()
    print(rule())
    entries = load_entries()
    if not entries:
        print()
        print(dim("  no entries yet — perhaps today is a good day to begin."))
        pause()
        return
    print()
    for entry in entries:
        print(format_entry(entry))
        print()
    print(rule())
    pause()


def screen_search():
    """
    Search entries by keyword.

    Matches against the entry text, mood number, and timestamp,
    so searching '5' would find both mood-5 entries and dates containing '5'.
    """
    clear()
    print_header()
    print(rule())
    print()
    keyword = ask("search for").lower()
    entries = load_entries()
    if not entries:
        print(dim("\n  nothing here yet."))
        pause()
        return

    results = [
        e for e in entries
        if keyword in e["text"].lower()
        or keyword in str(e["mood"])
        or keyword in e["timestamp"].lower()
    ]

    print()
    if results:
        print(dim(f"  {len(results)} result{'s' if len(results) != 1 else ''} for \"{keyword}\""))
        print()
        for entry in results:
            print(format_entry(entry))
            print()
    else:
        print(dim(f"  nothing found for \"{keyword}\"."))
    print(rule())
    pause()


def screen_delete():
    """Let the user pick an entry and delete it after confirmation."""
    clear()
    print_header()
    print(rule())
    entries = load_entries()
    if not entries:
        print()
        print(dim("  no entries yet."))
        pause()
        return

    print()
    idx = pick_entry(entries, "which entry to delete? ")
    if idx is None:
        pause()
        return

    print()
    print(format_entry(entries[idx]))
    print()
    if confirm("remove this entry permanently?"):
        entries.pop(idx)
        save_entries(entries)
        print()
        print(dim("  entry removed."))
    else:
        print(dim("  cancelled."))
    pause()


def screen_edit():
    """Let the user pick an entry and update its text and/or mood."""
    clear()
    print_header()
    print(rule())
    entries = load_entries()
    if not entries:
        print()
        print(dim("  no entries yet."))
        pause()
        return

    print()
    idx = pick_entry(entries, "which entry to edit? ")
    if idx is None:
        pause()
        return

    entry = entries[idx]
    print()
    print(format_entry(entry))
    print()
    print(rule())
    print()

    new_text = ask("new text", default="keep")
    if new_text and new_text != "keep":
        entry["text"] = new_text

    while True:
        mood_input = ask("new mood 1–5", default="keep")
        if not mood_input or mood_input == "keep":
            break
        try:
            val = int(mood_input)
            if 1 <= val <= 5:
                entry["mood"] = val
                break
            print(dim("  between 1 and 5, please."))
        except ValueError:
            print(dim("  please type a number."))

    entry["edited_at"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    save_entries(entries)
    print()
    print(dim("  updated.  ◆"))
    pause()


def screen_summary():
    """Show entry count, average mood, and the best/worst single-day moods."""
    clear()
    print_header()
    print(rule())
    entries = load_entries()
    if not entries:
        print()
        print(dim("  no entries yet."))
        pause()
        return

    total = sum(e["mood"] for e in entries)
    avg = total / len(entries)
    best = max(entries, key=lambda e: e["mood"])
    worst = min(entries, key=lambda e: e["mood"])

    print()
    print(box_top())
    print(blank_row())
    print(box_row(bright(f"{len(entries)}  entries"), align="center"))
    print(box_row(dim(f"average mood  {avg:.2f}"), align="center"))
    print(blank_row())
    print(box_row(dim("best day"), align="center"))
    print(box_row(f"{dim(best['timestamp'])}  {mood_glyph(best['mood'])}", align="center"))
    print(blank_row())
    print(box_row(dim("hardest day"), align="center"))
    print(box_row(f"{dim(worst['timestamp'])}  {mood_glyph(worst['mood'])}", align="center"))
    print(blank_row())
    print(box_bottom())
    pause()

# ── menu ──────────────────────────────────────────────────────

# (key, label) pairs for the menu — key is what the user types,
# label is the display text. 'q' (quit) is handled separately in main().

MENU_ITEMS = [
    ("w", "write"),
    ("r", "read"),
    ("s", "search"),
    ("e", "edit"),
    ("d", "delete"),
    ("m", "mood summary"),
    ("q", "quit"),
]

def show_menu():
    """Clear the screen, print the menu, and return the user's chosen key (lowercased)."""
    clear()
    print_header()
    print(rule())
    print()
    for key, label in MENU_ITEMS:
        print(f"  {soft(key)}  {dim(label)}")
    print()
    print(rule())
    print()
    return ask("").lower()

# ── main ──────────────────────────────────────────────────────

def main():
    """
    Run the main menu loop.

    Maps menu keys to their screen functions via `actions`, except 'q'
    which exits the app with a random closing message.
    """
    actions = {
        "w": screen_write,
        "r": screen_read,
        "s": screen_search,
        "e": screen_edit,
        "d": screen_delete,
        "m": screen_summary,
    }

    while True:
        choice = show_menu()
        if choice == "q":
            clear()
            print()
            print(soft("  c o d a  ◆"))
            print()
            print(dim(f"  {random.choice(CLOSING_LINES)}"))
            print()
            break
        elif choice in actions:
            actions[choice]()
        else:
            pass 


if __name__ == "__main__":
    main()