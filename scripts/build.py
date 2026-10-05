"""Build static hint pages from chronological Excel batches, using only Python stdlib."""
import json, re, shutil, zipfile, math
from pathlib import Path
from xml.etree import ElementTree as ET
from urllib.parse import quote
ROOT = Path(__file__).resolve().parents[1]
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
HEADERS = ['页面操作', '关键词', '题目标题', '提示1', '提示2', '第一提示间隔时间', '第二提示间隔时间']

def read_rows(path):
    with zipfile.ZipFile(path) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in root.findall('.//s:row', NS):
            values = [''] * 7
            for cell in row.findall('s:c', NS):
                col = re.match(r'[A-Z]+', cell.get('r')).group()
                if col not in 'ABCDEFG' or len(col) != 1: continue
                if cell.find('s:f', NS) is not None: raise ValueError(f'{path.name} 第{row.get("r")}行不支持公式，请粘贴为文本或数字')
                v = cell.find('s:v', NS)
                value = v.text if v is not None and v.text else ''
                if cell.get('t') == 's': value = strings[int(value)]
                if cell.get('t') == 'inlineStr': value = ''.join(cell.find('s:is', NS).itertext())
                values[ord(col)-65] = value.strip()
            rows.append((int(row.get('r')), values))
        return rows

def seconds(value):
    if not value: return 180
    try: minutes = float(value)
    except ValueError: raise ValueError('间隔时间必须填写分钟数，例如 3 或 0.5')
    if not math.isfinite(minutes) or minutes <= 0 or minutes > 10080:
        raise ValueError('间隔时间必须大于 0 且不超过 10080 分钟')
    return max(1, round(minutes * 60))

def apply_rows(catalog, rows):
    if not rows or rows[0][1] != HEADERS: raise ValueError('Excel 表头必须与提供的七列模板一致')
    seen = set()
    for number, row in rows[1:]:
        if not any(row): continue
        op, key, title, h1, h2, d1, d2 = row
        try:
            if not all(row[:4]): raise ValueError('前四列为必填项（删除行也需要填写）')
            if key in seen: raise ValueError('同一批次关键词重复')
            seen.add(key)
            if key in {'.', '..', 'assets', 'data', 'index.html', '404.html'} or re.search(r'[/\\?#%\x00-\x1f]', key):
                raise ValueError('关键词不能包含 /、\\、?、#、% 或保留路径名称')
            if len(key) > 100: raise ValueError('关键词不能超过 100 个字符')
            if op == '删除': catalog.pop(key, None)
            elif op == '新增':
                catalog[key] = dict(keyword=key, title=title, hint1=h1, hint2=h2, delay1=seconds(d1), delay2=seconds(d2) if h2 else 180)
            else: raise ValueError('页面操作只能填写“新增”或“删除”')
        except ValueError as e: raise ValueError(f'第 {number} 行（{key or "无关键词"}）：{e}') from e
    return catalog

def build():
    catalog = {}
    for path in sorted((ROOT/'imports').glob('*.xlsx')):
        if path.name.startswith('~$'): continue
        try: apply_rows(catalog, read_rows(path))
        except ValueError as e: raise ValueError(f'{path.name}：{e}') from e
    out = ROOT/'dist'
    if out.exists(): shutil.rmtree(out)
    out.mkdir()
    shutil.copytree(ROOT/'assets', out/'assets')
    shell = (ROOT/'index.html').read_text()
    (out/'index.html').write_text(shell)
    (out/'404.html').write_text(shell)
    (out/'.nojekyll').touch()
    links = []
    for key, item in catalog.items():
        folder = out/key
        folder.mkdir()
        payload = json.dumps(item, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        page = shell.replace('href="assets/', 'href="../assets/').replace('src="assets/', 'src="../assets/')
        page = page.replace('<script id="question" type="application/json">null</script>', f'<script id="question" type="application/json">{payload}</script>')
        (folder/'index.html').write_text(page)
        links.append({'关键词': key, '题目标题': item['title'], '链接': 'https://george351419-sys.github.io/answer/'+quote(key)+'/'})
    (ROOT/'data'/'links.json').write_text(json.dumps(links, ensure_ascii=False, indent=2)+'\n')
    import csv
    with (ROOT/'data'/'页面链接.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=['关键词','题目标题','链接']);writer.writeheader();writer.writerows(links)
    print(f'已生成 {len(catalog)} 个题目页面，链接清单：data/页面链接.csv')
if __name__ == '__main__': build()
