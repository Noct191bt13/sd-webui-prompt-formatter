# Prompt Formatter

Auto-cleans prompt text before generation — removes extra spaces, fixes comma formatting, collapses newlines.

## Features

- Removes spaces before commas (`tag1 , tag2` → `tag1, tag2`)
- Normalizes to single space after each comma
- Collapses consecutive commas
- Replaces newlines with spaces
- Strips leading/trailing whitespace and commas
- Collapses multiple whitespace into single space
- **Preview button** — reads from the active prompt textbox
- **Manual test input** — type any text to see how it formats
- **XYZ Grid integration** — grid with `True`/`False` to compare formatted vs raw

## Usage

Enable the checkbox in the **Prompt Formatter** accordion. Use the Preview button to see how your current prompt will look, or use the manual test input to experiment.

### XYZ Grid

Select `[Prompt Formatter] Enabled` as an X/Y/Z axis with values `True` / `False`.
