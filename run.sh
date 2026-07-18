#!/bin/bash
# Run the HTML Portal server

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PAGES="$SCRIPT_DIR/pages"

if [ ! -d "$PAGES" ]; then
  mkdir -p "$PAGES"
  echo "Created pages/ directory."
  echo ""
  echo "STRUCTURE:"
  echo "  $SCRIPT_DIR/"
  echo "  ├── server.py"
  echo "  ├── index.html"
  echo "  └── pages/"
  echo "      ├── <Directory Name A>/"
  echo "      │   ├── page1.html"
  echo "      │   └── page2.html"
  echo "      └── <Directory Name B>/"
  echo "          └── page3.html"
  echo ""
  exit 0
fi

echo "Starting HTML Portal at http://127.0.0.1:8080"
echo "Pages directory: $PAGES"
echo ""
echo "Directory:"
ls "$SCRIPT_DIR" | sed 's/^/  /'
echo ""
echo "Pages:"
find "$PAGES" -type f -name '*.html' | sed "s|$SCRIPT_DIR/||g" | sed 's/^/  /'
echo ""
echo "Press Ctrl+C to stop."
echo ""

python3 "$SCRIPT_DIR/server.py"
