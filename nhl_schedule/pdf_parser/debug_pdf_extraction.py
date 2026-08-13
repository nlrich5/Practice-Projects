from pathlib import Path
import json
import re
from pypdf import PdfReader

GAME_PATTERN = re.compile(
    r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\."
    r"\s+"
    r"([A-Za-z]+\.?\s+\d+)"
    r"\s+"
    r"(\d+:\d+\s+[AP]M)"
    r"\s+"
    r"(AT\s+)?"
    r"([A-Za-z][A-Za-z0-9 .]+?)"
    r"(?=\s+(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.|\s*$|\s*\n)"
)

pdf = PdfReader(Path('schedule.pdf'))
config = json.loads(Path('../config/config.json').read_text(encoding='utf-8'))
for team in config:
    if team['team'] == 'Buffalo Sabres':
        idx = team['page_index']
        text = pdf.pages[idx].extract_text() or ''
        matches = list(GAME_PATTERN.finditer(text))
        print(team['team'], 'page', idx, 'len', len(text), 'matches', len(matches))
        print('--- raw text sample ---')
        lines = text.splitlines()
        for i, line in enumerate(lines[:30]):
            print(i, repr(line))
        print('--- matched lines ---')
        for i, m in enumerate(matches[:60], 1):
            print(i, repr(m.group(0)))
        break
