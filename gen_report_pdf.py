# -*- coding: utf-8 -*-
"""调研报告 md -> PDF -> 小红书图片。
流程：md 解析成每页 HTML -> Edge 逐页 print-to-pdf -> pypdf 合并成整本 PDF -> PyMuPDF 拆成 PNG。
用法: python gen_report_pdf.py <md路径> <pdf输出路径> <图片输出目录>
"""
import io, re, os, sys, html, subprocess, shutil
import fitz
from pypdf import PdfWriter, PdfReader

EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
UD = r'C:\Users\zhuan\AppData\Local\Temp\edge_pdf'

def esc(s): return html.escape(s).replace('\n', '<br>')

def md_inline(s):
    s = html.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    return s

# 1080x1440 px 对应 285.75mm x 381mm (96dpi)
CSS = '''
@page { size: 285.75mm 381mm; margin: 0; }
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1440px;overflow:hidden;font-family:"Microsoft YaHei","PingFang SC",sans-serif;background:#fff;color:#1a1a1a;padding:64px 72px}
.cover-tag{display:inline-block;background:#1a1a1a;color:#fff;font-size:26px;padding:10px 24px;border-radius:999px;margin-bottom:36px}
h1{font-size:52px;line-height:1.35;font-weight:700;margin-bottom:32px}
.meta{font-size:23px;color:#555;line-height:1.85;margin-bottom:36px}
h2{font-size:34px;margin:24px 0 16px}
p.body{font-size:26px;line-height:1.85;color:#222}
.en{font-size:38px;line-height:1.45;font-weight:700;margin-bottom:14px}
.zh{font-size:30px;line-height:1.5;color:#444;font-weight:600;margin-bottom:24px}
.metaline{font-size:22px;color:#666;line-height:1.9;margin-bottom:24px}
.sec{margin-bottom:22px}
.label{display:block;font-size:26px;font-weight:700;color:#1a1a1a;margin-bottom:8px}
.ptext{font-size:25px;line-height:1.8;color:#222}
.deep-en{font-size:30px;font-weight:700;line-height:1.45;margin-bottom:10px}
.deep-p{font-size:25px;line-height:1.8;color:#222}
.deep-item{margin-bottom:36px}
.foot{margin-top:40px;padding-top:20px;border-top:2px solid #eee;font-size:20px;color:#999}
'''
MEASURE = '''<script>
window.addEventListener('load',function(){document.title='H'+document.body.scrollHeight;});
</script>'''

def page(inner, extra_css='', script=''):
    return '<!DOCTYPE html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body>%s</html>' % (CSS, extra_css, inner, script)

def build(md_path):
    md = io.open(md_path, encoding='utf-8').read()
    title = re.search(r'^# (.+)$', md, re.M).group(1)
    meta = re.findall(r'^((?:📅|📂|🔍|⏰).+)$', md, re.M)
    kw = re.search(r'^🔍 检索关键词：(.+)$\n((?:\d+\. .+\n?)+)', md, re.M)
    if kw:
        meta = [m if not m.startswith('🔍') else m + '\n' + kw.group(2).strip() for m in meta]
    ov = re.search(r'## 📊 概览\n\n(.+?)\n\n---', md, re.S).group(1)
    papers = re.findall(r'### \d+\. (.+?)\n- \*\*🏷️ 中文标题：\*\*\s*(.+?)\n- \*\*👤 作者：\*\*(.+?)\n- \*\*📅 发布日期：\*\*(.+?)\n- \*\*📂 分类：\*\*(.+?)\n- \*\*🔗 链接：\*\*(.+?)\n\n\*\*📝 中文摘要：\*\*\n(.+?)\n\n\*\*💬 通俗解读：\*\*\n(.+?)\n\n\*\*🔎 点评：\*\*\n(.+?)(?=\n\n---)', md, re.S)
    deep_sec = md[md.index('## ⭐ 精读推荐'):]
    deep_sec = deep_sec[:deep_sec.index('---\n\nskill来源')]
    deeps = re.findall(r'### 🌟 (.+?)（(.+?)）\s*\n+(.+?)(?=\n+### 🌟|\Z)', deep_sec, re.S)
    print('papers:', len(papers), 'deeps:', len(deeps), 'meta:', len(meta))

    pages = []
    inner = '<div class="cover-tag">arXiv 前沿文献追踪</div><h1>%s</h1><div class="meta">%s</div><h2>📊 概览</h2><p class="body">%s</p>' % (
        esc(title), '<br>'.join(esc(m) for m in meta), esc(ov))
    pages.append(('01_封面', inner))
    for i, (en, zh, au, date, cats, link, abs_, pop, com) in enumerate(papers):
        com_html = md_inline(com)
        com_html = com_html.replace('- 💡', '💡').replace('- ⚠️', '⚠️')
        com_html = re.sub(r'(?<!<br>)\s*⚠️', '<br>⚠️', com_html, count=1)
        inner = ('<div class="en">%d. %s</div><div class="zh">%s</div>'
                 '<div class="metaline">👤 %s<br>📅 %s · 📂 %s<br>🔗 %s</div>'
                 '<div class="sec"><span class="label l-abs">📝 中文摘要</span><p class="ptext">%s</p></div>'
                 '<div class="sec"><span class="label l-pop">💬 通俗解读</span><p class="ptext">%s</p></div>'
                 '<div class="sec"><span class="label l-com">🔎 点评</span><p class="ptext">%s</p></div>'
                 ) % (i + 1, esc(en.strip()), esc(zh.strip()), esc(au.strip()), esc(date.strip()),
                      esc(cats.strip()), esc(link.strip()), md_inline(abs_), md_inline(pop), com_html)
        pages.append(('%02d_论文%d' % (i + 2, i + 1), inner))
    items = ''.join('<div class="deep-item"><div class="deep-en">🌟 %s（%s）</div><div class="deep-p">%s</div></div>'
                    % (esc(e), esc(z), md_inline(b.strip())) for e, z, b in deeps)
    pages.append(('%02d_精读推荐' % (len(pages) + 1), '<h2 style="font-size:44px">⭐ 精读推荐</h2>' + items))
    return pages

def main():
    md_path, pdf_path, imgdir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(imgdir, exist_ok=True)
    tmpdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf_tmp')
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir)

    pages = build(md_path)

    # 第一遍：去掉固定高度，测出每页内容的自然高度；放不下的页单独等比缩小
    zooms = []
    for name, inner in pages:
        html_path = os.path.join(tmpdir, name + '_m.html')
        io.open(html_path, 'w', encoding='utf-8').write(
            page(inner, extra_css='body{height:auto;overflow:visible}', script=MEASURE))
        url = 'file:///' + html_path.replace(os.sep, '/')
        h = 1440
        try:
            r = subprocess.run([EDGE, '--headless', '--disable-gpu', '--dump-dom',
                                '--virtual-time-budget=4000', '--user-data-dir=' + UD,
                                url], capture_output=True, timeout=240)
            dom = r.stdout.decode('utf-8', errors='replace')
            m = re.search(r'<title>H(\d+)</title>', dom)
            if m:
                h = int(m.group(1))
        except Exception as e:
            print('MEASURE ERR', name, str(e)[:80])
        z = 1.0 if h <= 1440 else max(1440 / h * 0.995, 0.7)
        zooms.append(z)
        if z < 1.0:
            print('shrink %s: natural %dpx -> zoom %.3f' % (name, h, z))

    pdfs = []
    for (name, inner), z in zip(pages, zooms):
        html_path = os.path.join(tmpdir, name + '.html')
        io.open(html_path, 'w', encoding='utf-8').write(
            page(inner, extra_css='body{zoom:%.4f}' % z))
        pout = os.path.join(tmpdir, name + '.pdf')
        url = 'file:///' + html_path.replace(os.sep, '/')
        try:
            subprocess.run([EDGE, '--headless', '--disable-gpu',
                            '--no-pdf-header-footer', '--print-to-pdf=' + pout,
                            '--virtual-time-budget=4000', '--user-data-dir=' + UD,
                            url], capture_output=True, timeout=240)
        except Exception as e:
            print('ERR', name, str(e)[:80])
            continue
        ok = os.path.exists(pout)
        print(('OK   ' if ok else 'FAIL ') + name)
        if ok:
            pdfs.append(pout)

    writer = PdfWriter()
    for p in pdfs:
        for pg in PdfReader(p).pages[:1]:
            writer.add_page(pg)
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    print('PDF merged:', pdf_path, len(pdfs), 'pages')

    doc = fitz.open(pdf_path)
    scale = 1080 / (285.75 / 25.4 * 72)
    mat = fitz.Matrix(scale, scale)
    for i, pg in enumerate(doc):
        pix = pg.get_pixmap(matrix=mat)
        name = pages[i][0] + '.png'
        pix.save(os.path.join(imgdir, name))
    print('images written:', len(doc), '->', imgdir)

if __name__ == '__main__':
    main()
