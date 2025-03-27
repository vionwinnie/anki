#!/usr/bin/env python3
from anki.collection import Collection

def list_notetypes(col_path: str):
    col = Collection(col_path)
    
    print("\nAvailable Note Types:")
    print("=" * 50)
    
    for nt in col.models.all():
        print(f"\nNote Type: {nt['name']}")
        print("Fields:")
        for fld in nt['flds']:
            print(f"  - {fld['name']}")
        print("Templates:")
        for tmpl in nt['tmpls']:
            print(f"  - {tmpl['name']}")
        print("-" * 50)

if __name__ == '__main__':
    list_notetypes("/Users/manwaiwinnieyeung/Library/Application Support/Anki2/User 1/collection.anki2") 