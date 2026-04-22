"""
Load an agenda HTML onto the macOS clipboard AS FORMATTED HTML
(not plain text), so you can paste directly into Google Sites and
keep bold + bullets + paragraph structure.

Usage:
    python3 copy_agenda_to_clipboard.py autos
    python3 copy_agenda_to_clipboard.py metals
    python3 copy_agenda_to_clipboard.py <path/to/any.html>

After running: go to the Google Sites edit URL for the right page,
double-click into the text block, press Cmd+V. The formatting carries.

Why this exists: pbcopy and "Copy" from a PDF put plain text on the
clipboard, which loses every bold and bullet when pasted into Sites.
This script uses AppleScript to set the clipboard with type
"public.html" so the paste target recognizes it as real HTML.
"""
import os
import re
import subprocess
import sys

EXPORTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")

SHORTCUTS = {
    "autos":  os.path.join(EXPORTS, "autos_agenda_04_20_paste.html"),
    "metals": os.path.join(EXPORTS, "metals_agenda_04_20_paste.html"),
}


def read_html(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def html_to_plain(html_str):
    """Strip HTML tags for the plain-text clipboard fallback."""
    # Replace block-level tags with newlines so paragraphs stay readable.
    s = re.sub(r"(?i)<br\s*/?>", "\n", html_str)
    s = re.sub(r"(?i)</p\s*>", "\n\n", s)
    s = re.sub(r"(?i)</li\s*>", "\n", s)
    # Strip remaining tags.
    s = re.sub(r"<[^>]+>", "", s)
    # Collapse 3+ blank lines and trim.
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s


def set_clipboard_html(html_str):
    """Write HTML + plain-text fallback onto the macOS clipboard.

    Google Sites reads the HTML flavor and keeps bold + bullets. Other
    paste targets (Notes, Mail, TextEdit) see the plain text flavor and
    get something sensible instead of nothing.
    """
    hex_html = html_str.encode("utf-8").hex().upper()
    plain = html_to_plain(html_str)
    # Escape backslashes and quotes for AppleScript string literal.
    escaped = plain.replace("\\", "\\\\").replace("\"", "\\\"")
    # Set the clipboard to a record carrying both flavors. The HTML
    # flavor uses «data HTMLxxxx»; the text flavor is a plain string.
    script = (
        'set the clipboard to {'
        f'«class HTML»:«data HTML{hex_html}», '
        f'string:"{escaped}"'
        '}'
    )
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"osascript failed ({result.returncode}): {result.stderr.strip()}"
        )


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    arg = sys.argv[1]
    path = SHORTCUTS.get(arg.lower(), arg)
    if not os.path.isfile(path):
        print(f"ERROR: file not found: {path}")
        print("Known shortcuts: " + ", ".join(SHORTCUTS.keys()))
        sys.exit(1)

    html = read_html(path)
    set_clipboard_html(html)

    kb = len(html.encode("utf-8")) // 1024
    print(f"Clipboard loaded with HTML from: {path}")
    print(f"Size: ~{kb} KB of formatted HTML.")
    print()
    print("Next step:")
    if "autos" in path.lower():
        print(
            "  Open Autos Schedule edit URL:\n"
            "  https://sites.google.com/d/1MefkDWwf6SfuedKjgxgf0VjcUlIOTC_g/"
            "p/16h8vCKuyIjN2IIEkY6mF3TlPjQ7Y_Z1x/edit"
        )
    elif "metals" in path.lower():
        print(
            "  In Google Sites, click Pages panel on the right,\n"
            "  pick Metals Schedule, click Edit."
        )
    print("  Double-click into the text block, press Home, then Cmd+V.")
    print("  The old agendas stay; new one lands on top.")


if __name__ == "__main__":
    main()
