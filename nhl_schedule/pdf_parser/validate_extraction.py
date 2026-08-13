from pathlib import Path
import json
import sys
sys.path.append('.')
import pdf_parser

with open(Path('../config/config.json'), encoding='utf-8') as f:
    teams = json.load(f)

names = ['Buffalo Sabres', 'Los Angeles Kings', 'Ottawa Senators']
for name in names:
    team = next(t for t in teams if t['team'] == name)
    text = pdf_parser.extract_text_from_page(team['page_index'])
    matches = list(pdf_parser.GAME_PATTERN.finditer(text))
    print(name, 'matches', len(matches))
    print('sample text:', repr(text[:300]))
    print('---')
