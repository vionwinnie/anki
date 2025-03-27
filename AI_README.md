
Add this to your zshell dot file to run the import conveniently 

```
# Anki vocabulary import function
anki-import() {
    # Check if required arguments are provided
    if [ "$#" -lt 2 ]; then
        echo "Usage: anki-import <csv_file> <deck_name> [--tags \"tag1,tag2\"]"
        echo "Example: anki-import ~/test_vocab.csv \"Daily New Phrases\" --tags \"imported,basic-verbs\""
        return 1
    fi

    # Get the CSV file path and deck name
    local csv_file="$1"
    local deck_name="$2"
    local additional_tags="$3"

    # Check if CSV file exists
    if [ ! -f "$csv_file" ]; then
        echo "Error: CSV file '$csv_file' not found"
        return 1
    fi

    # Get the Anki collection path
    local collection="$HOME/Library/Application Support/Anki2/User 1/collection.anki2"

    # Check if collection exists
    if [ ! -f "$collection" ]; then
        echo "Error: Anki collection not found at '$collection'"
        return 1
    }

    # Run the import script
    ./out/pyenv/bin/python tools/import_vocab.py "$collection" "$csv_file" "$deck_name" $additional_tags
}
```

