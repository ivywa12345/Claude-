"""Check the Codex images against storyboard.json, build a contact sheet, and record approvals.

  python tools/review.py status                 # which frames are missing / pending / passed
  python tools/review.py sheet                  # write contact_sheet.html to look at every frame in order
  python tools/review.py approve 1-40 52 60     # mark frames you have actually looked at as passed
  python tools/review.py reject 17 --note "..." # mark a frame for regeneration
"""
import argparse, hashlib, html, json, os, struct, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.join(ROOT, 'storyboard.json')


def load():
    return json.load(open(SB, encoding='utf-8'))


def save(sb):
    tmp = SB + '.tmp'
    json.dump(sb, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    os.replace(tmp, SB)


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def png_size(path):
    with open(path, 'rb') as fh:
        head = fh.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    return struct.unpack('>II', head[16:24])


def ids(specs, n):
    out = set()
    for s in specs:
        if s == 'all':
            out.update(range(1, n + 1))
        elif '-' in s:
            a, b = map(int, s.split('-'))
            out.update(range(a, b + 1))
        else:
            out.add(int(s))
    return sorted(out)


def status(sb):
    missing, pending, passed, stale, rejected = [], [], [], [], []
    for f in sb['frames']:
        p = os.path.join(ROOT, f['image'])
        if not os.path.exists(p):
            missing.append(f['id'])
        elif f['image_review_status'] == 'passed':
            (passed if f['image_sha256'] == sha(p) else stale).append(f['id'])
        elif f['image_review_status'] == 'rejected':
            rejected.append(f['id'])
        else:
            pending.append(f['id'])
    for name, lst in (('missing', missing), ('pending review', pending), ('passed', passed),
                      ('changed after approval', stale), ('rejected', rejected)):
        print(f'{name:24s} {len(lst):4d}  {lst[:40]}{" ..." if len(lst) > 40 else ""}')


def sheet(sb):
    cells = []
    for f in sb['frames']:
        p = os.path.join(ROOT, f['image'])
        size = png_size(p) if os.path.exists(p) else None
        img = f'<img src="{html.escape(f["image"])}">' if size else '<div class="miss">MISSING</div>'
        cells.append(f'<figure class="{f["image_review_status"]}">{img}<figcaption><b>{f["id"]}</b> '
                     f'{f["start_ms"]/1000:.2f}s · {size[0]}x{size[1] if size else ""} · {f["image_review_status"]}<br>'
                     f'{html.escape(f["narration_fragment"])}</figcaption></figure>' if size else
                     f'<figure>{img}<figcaption><b>{f["id"]}</b> {html.escape(f["narration_fragment"])}</figcaption></figure>')
    page = ('<!doctype html><meta charset="utf-8"><title>Contact sheet</title><style>body{font:13px sans-serif;margin:16px}'
            'main{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}figure{margin:0}'
            'img,.miss{width:100%;aspect-ratio:16/9;object-fit:contain;background:#fff;border:1px solid #ccc}'
            '.miss{display:grid;place-items:center;color:#c00}.passed img{border-color:#2a2}.rejected img{border-color:#c00}'
            '</style><main>' + ''.join(cells) + '</main>')
    out = os.path.join(ROOT, 'contact_sheet.html')
    open(out, 'w', encoding='utf-8').write(page)
    print('wrote', out)


def mark(sb, specs, verdict, note):
    by_id = {f['id']: f for f in sb['frames']}
    for i in ids(specs, len(sb['frames'])):
        f = by_id[i]
        p = os.path.join(ROOT, f['image'])
        if not os.path.exists(p) or not png_size(p):
            print(f'frame {i}: no valid PNG at {f["image"]}, skipped')
            continue
        f['image_review_status'] = verdict
        f['image_sha256'] = sha(p) if verdict == 'passed' else None
        if note:
            f['review_note'] = note
    save(sb)
    status(sb)


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('cmd', choices=['status', 'sheet', 'approve', 'reject'])
ap.add_argument('frames', nargs='*')
ap.add_argument('--note')
a = ap.parse_args()
sb = load()
if a.cmd == 'status':
    status(sb)
elif a.cmd == 'sheet':
    sheet(sb)
else:
    if not a.frames:
        sys.exit('give frame ids, e.g. 1-40 52')
    mark(sb, a.frames, 'passed' if a.cmd == 'approve' else 'rejected', a.note)
