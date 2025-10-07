#!/usr/bin/env python3
# update_index.py
# Replaces the entire <div id="atis-message"> block in index.html
# with the updated version from atis_structured.html

import os
import re

def update_atis_message():
    try:
        # Read content of atis_structured.html
        with open("atis_structured.html", "r", encoding="utf-8") as atis_file:
            atis_content = atis_file.read().strip()

        # Read current index.html content
        with open("index.html", "r", encoding="utf-8") as index_file:
            index_content = index_file.read()

        # Use regex to replace the full <div id="atis-message"> ... </div>
        updated_content, count = re.subn(
            r'<div id="atis-message">.*?</div>',
            atis_content,
            index_content,
            flags=re.DOTALL
        )

        if count == 0:
            raise ValueError("No <div id='atis-message'> block found in index.html.")

        # Write the updated version back to index.html
        with open("index.html", "w", encoding="utf-8") as index_file:
            index_file.write(updated_content)

        print("✅ index.html successfully updated with new ATIS structure.")

    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e.filename}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    update_atis_message()
