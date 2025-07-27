import re
import csv
from pathlib import Path

def srt_to_csv(srt_path, csv_path=None):
    srt_path = Path(srt_path)
    if csv_path is None:
        csv_path = srt_path.with_suffix('.csv')
    else:
        csv_path = Path(csv_path)

    with open(srt_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split into subtitle blocks
    blocks = re.split(r'\n\s*\n', content.strip())

    data = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # Extract timing
            timing = lines[1]
            match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', timing)
            if match:
                start, end = match.groups()

                # Merge all text lines
                text = ' '.join(lines[2:]).strip()
                data.append((start, end, text))

    # Save to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['start_time', 'end_time', 'text'])
        writer.writerows(data)

    print(f"Converted '{srt_path.name}' to '{csv_path.name}' successfully!")

def clean_text(text):
    if not isinstance(text, str):
        return ""

    # Remove musical symbols
    text = re.sub(r'[♫♪]', '', text)

    # Remove dash-prefixed sound cues like "-(DING)" or "- (LAUGHING)"
    text = re.sub(r'-\s*\(.*?\)', '', text)
    text = re.sub(r'-\s*\[.*?\]', '', text)

    # Remove any remaining bracketed sound descriptions
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)

    # Replace newlines with space
    text = text.replace('\n', ' ')

    # Remove extra dashes left behind if surrounded by whitespace
    text = re.sub(r'\s*-\s*', ' ', text)

    # Remove extra dashes left behind if surrounded by whitespace
    text = re.sub(r'\<*i\>*', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

