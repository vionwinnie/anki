# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from __future__ import annotations

from typing import Any, TextIO

from anki.collection import Collection
from anki.importing.noteimp import ForeignNote, NoteImporter


class TextVocabImporter(NoteImporter):
    """Importer for plain text vocabulary files.
    
    Supports:
    - One word per line
    - Optional definition/translation after tab or colon
    - Optional tags at the top of file
    - UTF-8 encoding
    """
    
    needDelimiter = False
    needMapper = True

    def __init__(self, col: Collection, file: str) -> None:
        NoteImporter.__init__(self, col, file)
        self.fileobj: TextIO | None = None
        self.tagsToAdd: list[str] = []
        self.lines: list[str] = []
        self.numFields = 2  # word and definition

    def foreignNotes(self) -> list[ForeignNote]:
        self.open()
        notes = []
        ignored = 0
        log = []

        for line in self.lines:
            line = line.strip()
            if not line:
                continue
                
            # Split on tab or colon
            parts = line.split("\t")
            if len(parts) == 1:
                parts = line.split(":", 1)
                
            if len(parts) == 1:
                # Only word, no definition
                word = parts[0].strip()
                definition = ""
            else:
                word = parts[0].strip()
                definition = parts[1].strip()
                
            if not word:
                ignored += 1
                continue
                
            note = ForeignNote()
            note.fields = [word, definition]
            note.tags.extend(self.tagsToAdd)
            notes.append(note)

        self.log = log
        self.ignored = ignored
        self.close()
        return notes

    def open(self) -> None:
        """Open and parse the text file."""
        self.fileobj = open(self.file, encoding="utf-8-sig")
        self.lines = self.fileobj.readlines()
        
        # Check for tags at the top
        if self.lines and self.lines[0].startswith("tags:"):
            tags = self.lines[0][5:].strip()
            self.tagsToAdd = tags.split()
            self.lines = self.lines[1:]

    def close(self) -> None:
        if self.fileobj:
            self.fileobj.close()
            self.fileobj = None

    def __del__(self):
        self.close()
        zuper = super()
        if hasattr(zuper, "__del__"):
            zuper.__del__(self)  # type: ignore

    def fields(self) -> int:
        """Number of fields."""
        return self.numFields 