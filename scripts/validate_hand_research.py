"""Check publication integrity and independently aggregate the gallery scores."""
import collections
import hashlib
import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'docs'


def read(name):
    return json.loads((SITE / name).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ['src', 'href']:
            if key in attrs:
                self.links.append(attrs[key])


data, manifest = read('data.json'), read('publication-manifest.json')
assets = {a['path']: a for a in manifest['assets']}
assert len(assets) == len(manifest['assets']) == 565
assert set(assets) == {str(p.relative_to(SITE)) for p in (SITE/'assets').iterdir() if p.is_file()}
for name, item in assets.items():
    path = SITE / name
    assert path.stat().st_size == item['bytes'], name
    assert digest(path) == item['sha256'], name
assert data['sources'] == manifest['sources']
assert len(data['sources']) == 31
for source in data['sources']:
    assert digest(SITE/source['path']) == source['public_sha256'], source['id']
    assert read(source['path'])['source_sha256'] == source['source_sha256']
for route in data['routes']:
    assert route['source'] in {s['id'] for s in data['sources']}

parser = Links()
parser.feed((SITE/'index.html').read_text())
assert len(set(parser.ids)) == len(parser.ids), 'Duplicate HTML IDs'
for link in parser.links:
    parts = urlsplit(link)
    if parts.scheme or parts.netloc:
        continue
    if parts.path:
        path = (SITE/unquote(parts.path)).resolve()
        assert path.is_relative_to(ROOT/'docs'), link
        assert path.exists(), link
    elif parts.fragment:
        assert parts.fragment in parser.ids, link

assert data['dataset']['accepted_pairs'] == sum(data['dataset']['methods'].values()) == 4454
counts = collections.Counter()
group_counts = collections.Counter()
paired = []
for group in data['gallery']:
    split = group['split']
    group_counts[split] += 1
    records = group['records']
    identity = [(r['variant'], r['seed']) for r in records]
    assert len(set(identity)) == len(identity), (split, group['group'])
    for r in records:
        counts[split+':'+r['variant']] += 1
        for name in [r['review_assets']['full'], *r['review_assets']['crops']]:
            assert name in assets, name
        assert math.isfinite(r['score']['quality_score'])
    bases = {r['seed']: r for r in records if r['variant'] == 'base'}
    finals = {r['seed']: r for r in records if r['variant'] == 'step00512'}
    assert set(bases) == set(finals)
    for r in records:
        if r['variant'].startswith('step'):
            assert r['seed'] in bases
    report_group = next(g for g in data['score_groups'] if g['split'] == split and g['group'] == group['group'])
    base_mean = sum(r['score']['quality_score'] for r in bases.values())/len(bases)
    lora_mean = sum(r['score']['quality_score'] for r in finals.values())/len(finals)
    assert math.isclose(base_mean, report_group['mean_base'], abs_tol=1e-8)
    assert math.isclose(lora_mean, report_group['mean_lora'], abs_tol=1e-8)
    if split == 'dev8':
        for seed, final in finals.items():
            paired.append((bases[seed]['score']['quality_score'], final['score']['quality_score']))
assert dict(group_counts) == {'dev8': 8, 'train8': 8}
assert counts['dev8:base'] == counts['dev8:step00512'] == 80
assert counts['dev8:step00128'] == counts['dev8:step00256'] == 16
assert counts['train8:base'] == counts['train8:step00512'] == 16
assert sum(n for k,n in counts.items() if not k.endswith('reference')) == 224
assert sum(b > a for a,b in paired) == 54
means = [sum(p[i] for p in paired)/len(paired) for i in (0,1)]
assert round(means[0],2) == 24.15 and round(means[1],2) == 29.51
conf = data['scorer']['all_modules']['classification']['all']
assert conf['tp']+conf['fn'] == 312 and conf['tn']+conf['fp'] == 132
assert math.isclose((conf['tp']/312+conf['tn']/132)/2, conf['balanced_accuracy'])

# The publication should contain research, not machine paths or authentication.
patterns = [r'/root/', r'/home/', r'connect\.[^\s]+seetacloud',
            r'(?i)(?:password|passwd|token|api_key)\s*[=:]\s*["\x27]?[^\s"\x27,}]{8,}',
            r'gh[pousr]_[A-Za-z0-9]{20,}', r'-----BEGIN .*PRIVATE KEY-----']
for path in SITE.rglob('*'):
    if path.suffix in {'.json', '.html', '.js', '.css', '.md'}:
        content = path.read_text()
        for pattern in patterns:
            assert not re.search(pattern, content), f'Privacy pattern matched in {path.name}'

result = {
    'status': 'passed', 'report_date': data['report_date'],
    'checks': ['All 565 preview sizes and SHA256 hashes', '31 public evidence hashes and source references',
               'Static local links and anchor IDs', 'All gallery image references and matched seeds',
               'Independent aggregation of per-group and full development scores',
               '444-label confusion matrix and balanced accuracy', 'Machine-path and credential-pattern scan'],
    'routes': len(data['routes']), 'gallery_groups': dict(group_counts), 'record_counts': dict(counts),
    'evaluation_records_excluding_references': 224,
    'development_score_mean_base': means[0], 'development_score_mean_lora': means[1],
    'development_same_seed_score_increases': 54,
    'note': 'Website publication checks only; not a new model evaluation or anatomical success measure.'
}
(SITE/'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(result, ensure_ascii=False))
