import base64, pathlib

root = pathlib.Path(__file__).parent
fonts = {
    'PF600': 'fonts/playfair-display/files/playfair-display-latin-600-normal.woff2',
    'PF700': 'fonts/playfair-display/files/playfair-display-latin-700-normal.woff2',
    'IN400': 'fonts/inter/files/inter-latin-400-normal.woff2',
    'IN500': 'fonts/inter/files/inter-latin-500-normal.woff2',
    'IN600': 'fonts/inter/files/inter-latin-600-normal.woff2',
}
html = (root / 'video_template.html').read_text()
for key, path in fonts.items():
    b64 = base64.b64encode((root / path).read_bytes()).decode()
    html = html.replace('{{' + key + '}}', b64)
(root / 'index.html').write_text(html)
print('index.html written,', len(html) // 1024, 'KB')
