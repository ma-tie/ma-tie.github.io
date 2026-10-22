#!/usr/bin/env python3
"""Import only articles from a Zhi-dang export, leaving answers untouched.
Usage: python3 bin/migrate_zhihu_articles.py /path/to/export
Existing unrelated posts are never overwritten. Requires only Python stdlib.
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SITE = Path(__file__).resolve().parents[1]
ASSETS = SITE / 'assets/img/blog/zhihu'


def quoted(value):
    return json.dumps(value, ensure_ascii=False)


def main(source):
    root = Path(source).resolve()
    index = json.loads((root / 'index.json').read_text())
    articles = [i for i in index['items'] if i['kind'] == 'article']
    manifest = []
    assets = set()
    for item in articles:
        source_file = (root / item['file']).resolve()
        assert source_file.is_relative_to(root / 'articles')
        text = source_file.read_text(encoding='utf-8-sig')
        match = re.match(r'\A---\n.*?\n---\n', text, re.S)
        assert match, source_file
        body = text[match.end():].lstrip('\n')
        # The export repeats its title in the body; Jekyll renders it in the header.
        heading = body.split('\n', 1)
        if heading[0] == '# ' + item['title']:
            body = heading[1].lstrip('\n')
        created = datetime.fromtimestamp(item['created'], ZoneInfo('Asia/Shanghai'))
        updated = datetime.fromtimestamp(item['updated'], ZoneInfo('Asia/Shanghai'))
        filename = f'{created:%Y-%m-%d}-zhihu-{item["id"]}.md'
        tags = ['网络领域顶会追踪', '计算机网络', '论文阅读']
        conference = re.search(r'\[(NSDI|SIGCOMM|ATC)[\'’](\d{2})\]', item['title'])
        if conference:
            tags.append(conference[1])
        def local_image(value):
            origin = (source_file.parent / value).resolve()
            assert origin.is_relative_to(root / 'images'), value
            assert origin.is_file(), value
            ASSETS.mkdir(parents=True, exist_ok=True)
            destination = ASSETS / origin.name
            if destination.exists():
                assert destination.read_bytes() == origin.read_bytes()
            else:
                shutil.copy2(origin, destination)
            assets.add(str(destination.relative_to(SITE)))
            return '/' + str(destination.relative_to(SITE))
        body = re.sub(r'\.\./images/[^\s)\"\'<>]+', lambda m: local_image(m[0]), body)
        original_url = item['url'].replace('http://', 'https://', 1)
        body = body.replace(item['url'], original_url)
        front = ['---', 'layout: post', 'title: ' + quoted(item['title']),
                 'date: ' + quoted(created.strftime('%Y-%m-%d %H:%M:%S %z')),
                 'last_updated: ' + quoted(updated.isoformat()),
                 'categories: [技术札记]', 'tags: ' + quoted(tags),
                 'original_url: ' + quoted(original_url),
                 'zhihu_id: ' + quoted(item['id'])]
        if item.get('cover'):
            cover = local_image('../' + item['cover'])
            front.append('cover: ' + quoted(cover))
        if '{{' in body or '{%' in body:
            body = '{% raw %}\n' + body + '\n{% endraw %}\n'
        document = '\n'.join(front + ['---', '', body.rstrip(), ''])
        target = SITE / '_posts' / filename
        if target.exists():
            assert 'zhihu_id: ' + quoted(item['id']) in target.read_text(), target
        target.write_text(document)
        manifest.append(dict(id=item['id'], title=item['title'], source=item['file'],
                             file=str(target.relative_to(SITE)),
                             url=f'/blog/{created:%Y}/zhihu-{item["id"]}/',
                             original_url=original_url,
                             source_sha256=hashlib.sha256(source_file.read_bytes()).hexdigest()))
    report = dict(article_count=len(manifest), excluded_answer_count=sum(i['kind']=='answer' for i in index['items']),
                  posts=manifest, assets=sorted(assets))
    (SITE / 'bin/zhihu-migration-report.json').write_text(quoted(report) + '\n')
    print(f'Imported {len(manifest)} articles; excluded {report["excluded_answer_count"]} answers; copied {len(assets)} cover images.')


if __name__ == '__main__':
    main(sys.argv[1])
