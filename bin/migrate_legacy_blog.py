#!/usr/bin/env python3
"""Restore the owner's Hexo HTML backup as Jekyll posts.

Usage: python migrate_legacy_blog.py /path/to/mtank-master.zip
Requires beautifulsoup4 and pandoc. Run from the site root.
Uses blog-source-inventory.json when available to prefer original Markdown.
Pass --overwrite to regenerate previously migrated posts.
The JSON report beside this script records original paths and validation counts.
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from zipfile import ZipFile

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / '_posts'
ASSETS = ROOT / 'assets/img/blog/mtank'
FORMAT = 'markdown_strict+pipe_tables+fenced_code_blocks+backtick_code_blocks+strikeout+startnum'


def quoted(value):
    return json.dumps(value, ensure_ascii=False)


def normalize_taxonomy(document):
    """Use two broad categories; retain former technical categories as tags."""
    match = re.match(r'\A---\n(.*?)\n---\n', document, re.S)
    assert match
    front = match[1]
    def values(key):
        found = re.search(r'^' + key + r':[^\S\n]*(.*)$', front, re.M)
        if not found or not found[1].strip():
            return []
        value = found[1].strip()
        if value.startswith('['):
            return [v.strip().strip('\"\'') for v in value[1:-1].split(',') if v.strip()]
        return [value.strip('\"\'')]
    categories, tags = values('categories'), values('tags')
    life = bool(set(categories) & {'杂谈', '生活随笔'}) or 'title: hello world' in front
    if not life:
        tags = list(dict.fromkeys(tags + [c for c in categories if c not in {'技术札记', '技术博客'}]))
    for key, value in [('tags', tags), ('categories', ['生活随笔' if life else '技术札记'])]:
        line = key + ': ' + quoted(value)
        pattern = r'^' + key + r':[^\S\n]*[^\n]*$'
        front = re.sub(pattern, lambda _: line, front, flags=re.M) if re.search(pattern, front, re.M) else front + '\n' + line
    return '---\n' + front + '\n---\n' + document[match.end():]


def code_text(node):
    # Hexo represents line breaks as <br>, and line numbers in a separate column.
    for br in node.find_all('br'):
        br.replace_with('\n')
    return node.get_text()


def migrate_markdown(path, record, redirects):
    text = Path(path).read_text(encoding='utf-8-sig')
    metadata = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    front = metadata[1] if metadata else None
    body = text[metadata.end():] if metadata else text
    if not metadata:
        body = re.sub(r'\A于\d+同步至[^\n]*\n+', '', body)
    # Leave code and inline literals byte-for-byte intact while adapting URLs/math.
    protected = []
    def protect(match):
        token = f'MTANKSOURCECODE{len(protected):04d}TOKEN'
        protected.append((token, match[0]))
        return token
    body = re.sub(r'(?m)^([ \t]*)(`{3,}|~{3,})[^\n]*\n[\s\S]*?^\1\2[ \t]*$', protect, body)
    body = re.sub(r'(`+)[^\n]*?\1', protect, body)

    original_images = [Path(unquote(i.get('src', ''))).name
                       for i in record['soup'].select('.markdown-body img')]
    image_count = 0
    def image_url(match):
        nonlocal image_count
        name = unquote(match[0].replace('\\', '/').split('/')[-1])
        if not (ASSETS / name).is_file():
            stem, suffix = Path(name).stem, Path(name).suffix
            candidates = [n for n in original_images
                          if Path(n).stem.startswith(stem + '-') and Path(n).suffix == suffix]
            assert len(candidates) == 1, (path, name, candidates)
            name = candidates[0]
        assert (ASSETS / name).is_file(), (path, name)
        image_count += 1
        return '/assets/img/blog/mtank/' + quote(name, safe='/')
    body = re.sub(r'(?:/pictures/|[A-Za-z]:[\\/]TieNotes[\\/]pictures[\\/])[^\s)\"\'<>]+', image_url, body)
    rewritten = 0
    def article_url(match):
        nonlocal rewritten
        parsed = urlsplit(match[0])
        key = unquote(parsed.path).removesuffix('index.html').rstrip('/')
        assert key in redirects, (path, match[0])
        rewritten += 1
        return urlunsplit(('', '', quote(redirects[key], safe='/'), parsed.query, parsed.fragment))
    body = re.sub(r'https?://mtank\.(?:gitee|github)\.io/[^\s)\"\'<>]+', article_url, body)
    math_count = 0
    def math(match):
        nonlocal math_count
        math_count += 1
        return '$$' + match[1] + '$$'
    # Existing display math stays unchanged; single-dollar inline math uses Kramdown syntax.
    body = re.sub(r'(?<![\\$])\$(?!\$)([^$\n]+?)(?<!\\)\$(?!\$)', math, body)
    for token, content in protected:
        assert body.count(token) == 1
        body = body.replace(token, content)
    code_count = len(re.findall(r'(?m)^[ \t]*(`{3,}|~{3,})[^\n]*$', body)) // 2
    return front, body, image_count, rewritten, code_count, math_count


def main(archive):
    z = ZipFile(archive)
    sources = [n for n in z.namelist()
               if re.fullmatch(r'mtank-master/\d{4}/\d{2}/\d{2}/.+/index.html', n)]
    records = []
    redirects = {}
    for source in sources:
        soup = BeautifulSoup(z.read(source), 'html.parser')
        old_path = '/' + source.removeprefix('mtank-master/').removesuffix('index.html')
        parts = old_path.strip('/').split('/')
        slug = re.sub(r'[^\w\-]+', '-', parts[-1], flags=re.UNICODE).strip('-').lower()
        slug = re.sub(r'-+', '-', slug)
        date = soup.select_one('time[datetime]')['datetime']
        filename = date[:10] + '-' + slug + '.md'
        url = f'/blog/{date[:4]}/{slug}/'
        if any(r['filename'] == filename or r['url'] == url for r in records):
            raise ValueError(f'Post path collision: {source}')
        records.append(dict(source=source, old_path=old_path, filename=filename,
                            url=url, date=date, soup=soup))
        redirects[old_path.rstrip('/')] = url

    copied = []
    for name in z.namelist():
        if name.startswith('mtank-master/pictures/') and not name.endswith('/'):
            relative = Path(name.removeprefix('mtank-master/pictures/'))
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError(f'Unsafe asset path: {name}')
            target = ASSETS / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
            copied.append(str(target.relative_to(ROOT)))

    POSTS.mkdir(exist_ok=True)
    inventory_path = ROOT / 'bin/blog-source-inventory.json'
    inventory = {r['archive_path']: r for r in json.loads(inventory_path.read_text())['posts']} if inventory_path.exists() else {}
    report = []
    for record in records:
        soup = record['soup']
        body = soup.select_one('.markdown-body')
        assert body is not None, record['source']
        title = soup.title.get_text().removesuffix(' - mtPage')
        categories = [a.get_text(strip=True) for a in soup.select('.post-metas a[href^="/categories/"]')]
        tags = [a.get_text(strip=True) for a in soup.select('.post-metas a[href^="/tags/"]')]
        for node in body.select('a.headerlink, script, style'):
            node.decompose()
        # Keep explicit old heading IDs so links with fragments still work.
        for heading in body.select('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]'):
            anchor = soup.new_tag('a', id=heading['id'])
            heading.insert_before(anchor)
            del heading['id']
        code_blocks = []
        for figure in body.select('figure.highlight'):
            source_code = figure.select_one('td.code pre code, td.code pre')
            assert source_code is not None, record['source']
            code = code_text(source_code)
            language = next((c for c in figure.get('class', []) if c != 'highlight'), '')
            language = {'c++': 'cpp', 'C++': 'cpp', 'shell': 'bash'}.get(language, language)
            pre = soup.new_tag('pre')
            node = soup.new_tag('code', attrs={'class': f'language-{language}'})
            node.string = code
            pre.append(node)
            figure.replace_with(pre)
        # Protect exact code contents from HTML-to-Markdown transformations.
        for pre in list(body.select('pre')):
            node = pre.find('code') or pre
            code = code_text(node)
            language = next((c.removeprefix('language-') for c in node.get('class', [])
                             if c.startswith('language-')), '')
            fence = '`' * max(3, max((len(m) for m in re.findall(r'`+', code)), default=0) + 1)
            token = f'MTANKCODEBLOCK{len(code_blocks):04d}TOKEN'
            code_blocks.append((token, f'{fence}{language}\n{code.rstrip(chr(10))}\n{fence}'))
            placeholder = soup.new_tag('p')
            placeholder.string = token
            pre.replace_with(placeholder)

        image_count = len(body.select('img'))
        for image in body.select('img'):
            src = image.get('src', '')
            if src.startswith('/pictures/'):
                relative = unquote(src.removeprefix('/pictures/'))
                assert (ASSETS / relative).is_file(), f'Missing image: {src}'
                image['src'] = '/assets/img/blog/mtank/' + quote(relative, safe='/')
            for attr in ['srcset', 'data-src', 'data-srcset', 'loading']:
                image.attrs.pop(attr, None)

        rewritten = 0
        for anchor in body.select('a[href]'):
            parsed = urlsplit(anchor['href'])
            if parsed.hostname in ('mtank.gitee.io', 'mtank.github.io') or not parsed.netloc:
                key = unquote(parsed.path).removesuffix('index.html').rstrip('/')
                if key in redirects:
                    anchor['href'] = urlunsplit(('', '', quote(redirects[key], safe='/'), parsed.query, parsed.fragment))
                    rewritten += 1
        # Kramdown's $$ syntax produces MathJax-compatible math spans/blocks.
        math_fragments = []
        for text in list(body.find_all(string=True)):
            if text.parent.name in ('code', 'pre'):
                continue
            def protect_math(match):
                token = f'MTANKMATH{len(math_fragments):04d}TOKEN'
                expression = match.group(1) if match.group(1) is not None else match.group(2)
                math_fragments.append((token, '$$' + expression + '$$'))
                return token
            replacement = re.sub(r'\$\$([\s\S]+?)\$\$|(?<!\\)\$([^$\n]+?)(?<!\\)\$', protect_math, str(text))
            if replacement != str(text):
                text.replace_with(replacement)
        rendered = subprocess.run(['pandoc', '-f', 'html', '-t', FORMAT, '--wrap=none'],
                                  input=body.decode_contents(), text=True, capture_output=True, check=True).stdout
        for token, content in code_blocks + math_fragments:
            assert rendered.count(token) == 1, (record['source'], token)
            rendered = rendered.replace(token, content)
        original = inventory.get(record['source'], {}).get('source')
        source_front = None
        if original:
            source_front, rendered, image_count, rewritten, code_count, math_count = migrate_markdown(original, record, redirects)
        else:
            code_count, math_count = len(code_blocks), len(math_fragments)
        # Literal C++/template braces must not be interpreted by Liquid.
        if '{{' in rendered or '{%' in rendered:
            rendered = '{% raw %}\n' + rendered + '{% endraw %}\n'
        front = ['---', 'layout: post', 'title: ' + quoted(title),
                 'date: ' + quoted(record['date'] + ':00 +0800'),
                 'tags: ' + quoted(tags), 'categories: ' + quoted(categories),
                 '---', '']
        if source_front:
            date_match = re.search(r'^date:\s*(.+)$', source_front, re.M)
            assert date_match, original
            source_date = date_match[1].strip().strip('\"\'')
            source_front = re.sub(r'^date:.*$', 'date: ' + quoted(source_date + ' +0800'), source_front, flags=re.M)
            front = ['---', source_front.strip(), 'layout: post', '---', '']
        target = POSTS / record['filename']
        if target.exists() and '--overwrite' not in sys.argv[2:]:
            raise FileExistsError(f'Refusing to overwrite {target}')
        target.write_text(normalize_taxonomy('\n'.join(front) + '\n' + rendered), encoding='utf-8')
        record.pop('soup')
        report.append(dict(**record, title=title, categories=categories, tags=tags,
                           original_markdown=original, migration='markdown' if original else 'html',
                           images=image_count, code_blocks=code_count,
                           math_fragments=math_count, rewritten_links=rewritten))
    result = dict(archive=Path(archive).name, posts=report, assets=copied)
    (ROOT / 'bin/blog-migration-report.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Migrated {len(report)} posts, {len(copied)} assets; '
          f'{sum(p["code_blocks"] for p in report)} code blocks, '
          f'{sum(p["rewritten_links"] for p in report)} internal links.')


if __name__ == '__main__':
    main(sys.argv[1])
