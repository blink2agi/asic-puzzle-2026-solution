"""Minimal markdown -> HTML for the writeup (known subset)."""
import re, html, sys
src = open(sys.argv[1]).read()
lines = src.split('\n')
out=[]; i=0
def inl(s):
    s = html.escape(s)
    # protect inline code from the emphasis passes (it can contain * and _)
    spans=[]
    def keep(m):
        spans.append(m.group(1)); return f'\x00{len(spans)-1}\x00'
    s = re.sub(r'`([^`]+)`', keep, s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<i>\1</i>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', s)
    s = re.sub(r'\x00(\d+)\x00', lambda m: '<code>'+spans[int(m.group(1))]+'</code>', s)
    return s
while i < len(lines):
    l = lines[i]
    if l.startswith('```'):
        i+=1; buf=[]
        while i < len(lines) and not lines[i].startswith('```'):
            buf.append(html.escape(lines[i])); i+=1
        i+=1
        out.append('<pre>'+'\n'.join(buf)+'</pre>')
        continue
    if l.startswith('|'):
        rows=[]
        while i < len(lines) and lines[i].startswith('|'):
            rows.append(lines[i]); i+=1
        cells=[[c.strip() for c in r.strip('|').split('|')] for r in rows]
        body=[c for c in cells if not set(''.join(c)) <= set('-: ')]
        t=['<table border="1" cellspacing="0" cellpadding="6">']
        for n,row in enumerate(body):
            tag='th' if n==0 else 'td'
            t.append('<tr>'+''.join(f'<{tag}>{inl(c)}</{tag}>' for c in row)+'</tr>')
        t.append('</table>')
        out.append('\n'.join(t)); continue
    if re.match(r'^#{1,6} ', l):
        n=len(l)-len(l.lstrip('#')); out.append(f'<h{n}>{inl(l[n+1:])}</h{n}>'); i+=1; continue
    if l.strip()=='---': out.append('<hr>'); i+=1; continue
    if l.startswith('> '):
        buf=[]
        while i<len(lines) and lines[i].startswith('>'):
            buf.append(lines[i].lstrip('>').strip()); i+=1
        out.append('<p><i>'+inl(' '.join(buf))+'</i></p>'); continue
    if re.match(r'^\s*[-*] ', l):
        buf=[]
        while i<len(lines) and (re.match(r'^\s*[-*] ', lines[i]) or (lines[i].startswith('  ') and lines[i].strip() and buf)):
            if re.match(r'^\s*[-*] ', lines[i]): buf.append(re.sub(r'^\s*[-*] ','',lines[i]))
            else: buf[-1]+=' '+lines[i].strip()
            i+=1
        out.append('<ul>'+''.join(f'<li>{inl(b)}</li>' for b in buf)+'</ul>'); continue
    if not l.strip(): i+=1; continue
    buf=[]
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','> ','---')) and not re.match(r'^\s*[-*] ',lines[i]):
        buf.append(lines[i]); i+=1
    out.append('<p>'+inl(' '.join(buf))+'</p>')
body='\n'.join(out)
print(f'''<html><head><meta charset="utf-8"><style>
pre{{font-family:"Courier New";font-size:9pt;line-height:1.25;white-space:pre;
     background:#f4f4f6;padding:8pt;border:1px solid #ddd}}
code{{font-family:"Courier New";font-size:10pt}}
table{{border-collapse:collapse;font-size:10pt}} th{{background:#eee;text-align:left}}
</style></head><body>
{body}
</body></html>''')
