#!/usr/bin/env python3
import re
import hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TEMPLATES = BASE / 'home' / 'templates'
STATIC_CSS_DIR = BASE / 'static' / 'home'
CSS_OUTPUT = STATIC_CSS_DIR / 'csp-inline-fixes.css'

STYLE_ATTR_RE = re.compile(r'style\s*=\s*"([^"]+)"')

# Gather all files
files = list(TEMPLATES.rglob('*.html'))

style_map = {}  # style_text -> class_name

for f in files:
    text = f.read_text(encoding='utf-8')
    for m in STYLE_ATTR_RE.finditer(text):
        style_text = m.group(1).strip()
        # normalize spaces
        normalized = '; '.join(p.strip() for p in style_text.split(';') if p.strip())
        if normalized and normalized not in style_map:
            h = hashlib.sha1(normalized.encode('utf-8')).hexdigest()[:10]
            cls = f'csp-{h}'
            style_map[normalized] = cls

if not style_map:
    print('No inline style attributes found.')
    exit(0)

# Ensure static css dir exists
STATIC_CSS_DIR.mkdir(parents=True, exist_ok=True)

# Append CSS rules
css_lines = []
for style, cls in style_map.items():
    css_lines.append(f'.{cls} ' + '{ ' + style + ' }')

existing = ''
if CSS_OUTPUT.exists():
    existing = CSS_OUTPUT.read_text(encoding='utf-8')

new_css = existing + '\n/* CSP inline style fixes auto-generated */\n' + '\n'.join(css_lines) + '\n'
CSS_OUTPUT.write_text(new_css, encoding='utf-8')
print(f'Wrote {len(css_lines)} classes to {CSS_OUTPUT}')

# Replace style="..." with class additions
for f in files:
    text = f.read_text(encoding='utf-8')
    modified = False
    # (older, more complex replacer removed; using two-pass replacements below)

    # Because replacing while needing to manipulate the element head is tricky, we'll do a simpler approach:
    # Replace occurrences of style="..." where class exists first
    # 1) handle elements with class attribute: class="..." ... style="..."
    text2 = text
    # pattern: class="..." (any attrs) style="..."
    pattern = re.compile(r'(class\s*=\s*"(?P<cls>[^\"]*)"[^>]*?)style\s*=\s*"(?P<style>[^"]+)"')
    def repl2(m):
        old_classes = m.group('cls')
        style_text = m.group('style').strip()
        normalized = '; '.join(p.strip() for p in style_text.split(';') if p.strip())
        cls = style_map.get(normalized)
        if not cls:
            return m.group(0)
        new_classes = (old_classes + ' ' + cls).strip()
        return m.group(1).replace(f'class="{old_classes}"', f'class="{new_classes}"')
    text2 = pattern.sub(repl2, text2)

    # 2) handle elements without class attribute: insert class before style
    pattern2 = re.compile(r'<(?P<tag>\w+)(?P<attrs>[^>]*)\sstyle\s*=\s*"(?P<style>[^"]+)"')
    def repl3(m):
        style_text = m.group('style').strip()
        normalized = '; '.join(p.strip() for p in style_text.split(';') if p.strip())
        cls = style_map.get(normalized)
        if not cls:
            return m.group(0)
        return f'<{m.group("tag")}{m.group("attrs")} class="{cls}"'
    text3 = pattern2.sub(repl3, text2)

    if text3 != text:
        f.write_text(text3, encoding='utf-8')
        print(f'Modified {f}')

print('Done.')
