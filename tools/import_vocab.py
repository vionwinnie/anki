#!/usr/bin/env python3
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import argparse
import csv
import sys
from pathlib import Path

# Add pylib and out/pylib to Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "out" / "pylib"))
sys.path.insert(0, str(root_dir / "pylib"))

from anki.collection import Collection
from anki.notes import Note


def is_kanji(char: str) -> bool:
    """Check if a character is a kanji."""
    return '\u4e00' <= char <= '\u9fff'


def is_kana(char: str) -> bool:
    """Check if a character is hiragana or katakana."""
    return ('\u3040' <= char <= '\u309f' or  # Hiragana
            '\u30a0' <= char <= '\u30ff')    # Katakana


def add_furigana(expression: str, reading: str) -> str:
    """Add furigana only to kanji characters in the expression.
    
    Example:
        expression: 食べる
        reading: たべる
        result: 食[た]べる
    """
    if not any(is_kanji(c) for c in expression):
        return reading
        
    result = []
    reading_pos = 0
    
    # Split the reading into kana segments
    kana_segments = []
    current_segment = []
    
    for char in reading:
        if is_kana(char):
            if current_segment:
                kana_segments.append(''.join(current_segment))
                current_segment = []
            kana_segments.append(char)
        else:
            current_segment.append(char)
    if current_segment:
        kana_segments.append(''.join(current_segment))
    
    # Match kana segments with expression
    kana_idx = 0
    for char in expression:
        if is_kanji(char):
            if kana_idx < len(kana_segments):
                result.append(f"{char}[{kana_segments[kana_idx]}]")
                kana_idx += 1
            else:
                result.append(char)
        else:
            result.append(char)
            if kana_idx < len(kana_segments) and char == kana_segments[kana_idx]:
                kana_idx += 1
    
    return ''.join(result)


def import_vocab(col_path: str, csv_path: str, deck_name: str, additional_tags: list[str] = None) -> None:
    """Import vocabulary from a CSV file into a specific deck.
    
    The CSV file should have the following columns:
    - Expression (Japanese word)
    - Reading (Furigana)
    - Meaning (English meaning)
    - Tags (optional, semicolon-separated)
    
    Args:
        col_path: Path to Anki collection file
        csv_path: Path to CSV file containing vocabulary
        deck_name: Name of the deck to import into
        additional_tags: List of additional tags to add to all notes
    """
    
    print(f"\nDebug: Starting import process")
    print(f"Debug: Collection path: {col_path}")
    print(f"Debug: CSV path: {csv_path}")
    print(f"Debug: Deck name: {deck_name}")
    print(f"Debug: Additional tags: {additional_tags}")
    
    # Open the collection
    print("\nDebug: Opening collection...")
    col = Collection(col_path)
    
    # Get the deck ID
    print("Debug: Getting deck ID...")
    deck_id = col.decks.id(deck_name)
    if not deck_id:
        print(f"Error: Deck '{deck_name}' not found")
        sys.exit(1)
    print(f"Debug: Found deck ID: {deck_id}")
    
    # Get the Japanese note type
    print("\nDebug: Getting note type...")
    notetype = col.models.by_name("Japanese (recognition)")
    if not notetype:
        print("Error: Japanese (recognition) note type not found")
        sys.exit(1)
    print(f"Debug: Found note type: {notetype['name']}")
    
    # Read the CSV file
    notes_added = 0
    notes_updated = 0
    notes_skipped = 0
    
    # Get existing notes in the deck to check for duplicates
    print("\nDebug: Getting existing notes...")
    existing_notes = {}
    for cid in col.decks.cids(deck_id):
        card = col.get_card(cid)
        note = col.get_note(card.nid)
        existing_notes[note.fields[0]] = note  # Use Expression field as key
    print(f"Debug: Found {len(existing_notes)} existing notes")
    
    print("\nDebug: Reading CSV file...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        print(f"Debug: CSV headers: {reader.fieldnames}")
        
        for row in reader:
            # Get the expression and reading
            expression = row.get('Expression', '').strip()
            reading = row.get('Reading', '').strip()
            
            print(f"\nDebug: Processing note: {expression}")
            print(f"Debug: Reading: {reading}")
            
            # Format the reading field with furigana only for kanji
            reading_with_furigana = add_furigana(expression, reading)
            print(f"Debug: Reading with furigana: {reading_with_furigana}")
            
            # Prepare fields
            fields = [
                expression,                                    # Expression
                row.get('Meaning', '').strip(),               # Meaning
                reading_with_furigana,                        # Reading with furigana (only for kanji)
            ]
            print(f"Debug: Fields: {fields}")
            
            # Prepare tags
            tags = []
            csv_tags = row.get('Tags', '').strip()
            if csv_tags:  # Only split if there are tags
                tags.extend([tag.strip() for tag in csv_tags.split(';')])
            if additional_tags:
                tags.extend(additional_tags)
            print(f"Debug: Tags: {tags}")
            
            # Check if note exists
            if expression in existing_notes:
                print(f"Debug: Note exists, updating...")
                # Update existing note
                note = existing_notes[expression]
                note.fields = fields
                note.tags = tags
                notes_updated += 1
            else:
                print(f"Debug: Note is new, creating...")
                # Create new note
                note = Note(col, notetype)
                note.fields = fields
                note.tags = tags
                try:
                    col.add_note(note, deck_id)
                    notes_added += 1
                except Exception as e:
                    print(f"Error adding note '{expression}': {str(e)}")
                    notes_skipped += 1
    
    # Save changes
    print("\nDebug: Saving changes...")
    col.save()
    
    print(f"\nImport complete:")
    print(f"Notes added: {notes_added}")
    print(f"Notes updated: {notes_updated}")
    print(f"Notes skipped (errors): {notes_skipped}")


def main():
    parser = argparse.ArgumentParser(description='Import vocabulary from CSV into Anki deck')
    parser.add_argument('collection', help='Path to Anki collection file (*.anki2)')
    parser.add_argument('csv_file', help='Path to CSV file containing vocabulary')
    parser.add_argument('deck', help='Name of the deck to import into')
    parser.add_argument('--tags', help='Additional tags to add to all notes (comma-separated)', type=str)
    
    args = parser.parse_args()
    
    # Check if collection file exists
    if not Path(args.collection).exists():
        print(f"Error: Collection file '{args.collection}' not found")
        sys.exit(1)
    
    # Check if CSV file exists
    if not Path(args.csv_file).exists():
        print(f"Error: CSV file '{args.csv_file}' not found")
        sys.exit(1)
    
    # Process tags
    additional_tags = None
    if args.tags:
        additional_tags = [tag.strip() for tag in args.tags.split(',')]
    
    try:
        import_vocab(args.collection, args.csv_file, args.deck, additional_tags)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main() 