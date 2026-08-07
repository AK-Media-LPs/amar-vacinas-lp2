#!/usr/bin/env python3
"""Desempacota o bundle do handoff e gera um site estatico puro (sem React)."""
import base64, gzip, hashlib, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)          # raiz do repo

if len(sys.argv) != 2:
    sys.exit("uso: python3 build/build.py <handoff>/site/index.html")
SRC = sys.argv[1]

CTA = ("https://wa.me/558699334058?text="
       "Ol%C3%A1%2C%20vim%20do%20site%20e%20gostaria%20de%20mais%20"
       "informa%C3%A7%C3%B5es.")

# Ajustes de copy pedidos depois do handoff. Ficam aqui (e nao so no HTML
# gerado) para sobreviverem ao reprocessamento de uma versao nova do design.
TARJA = ('<span style="display:inline-flex;align-items:flex-start;gap:9px;'
         'background:#FFF3C4;border:1px dashed #E5A800;border-radius:10px;'
         'padding:8px 12px;color:#6B4E00;font-weight:600;">'
         '<span style="flex:none;font-size:0.6875rem;font-weight:800;'
         'letter-spacing:0.08em;background:#E5A800;color:#22190A;'
         'border-radius:4px;padding:3px 6px;">CONFIRMAR</span><span>%s</span></span>')

COPY_FIXES = [
    # 07/08/2026 — respostas do cliente para as duas tarjas CONFIRMAR do FAQ
    ("Sim, o atendimento é particular. " + TARJA % (
        "informar se há orientação sobre valores, convênios ou formas de "
        "pagamento — respeitar as regras do conselho sobre divulgação de preço"),
     "Sim, o atendimento é particular. A equipe informa valores e formas de "
     "pagamento pelo WhatsApp, de acordo com a vacina que você precisa."),
    (TARJA % "agendamento obrigatório ou atende por ordem de chegada também",
     "O agendamento é feito pelo WhatsApp: você combina o horário que cabe na "
     "sua rotina e é atendido na hora marcada, sem fila."),
]

# ---------------------------------------------------------------- 1. unpack
raw = open(SRC, encoding="utf-8").read()


def island(kind):
    m = re.search(r'<script type="__bundler/%s">(.*?)</script>' % kind, raw, re.S)
    return m.group(1).strip()


manifest = json.loads(island("manifest"))
template = json.loads(island("template"))

# O bundler regera todos os UUIDs a cada export, entao as imagens sao
# identificadas pelo md5 do conteudo. Se o design trocar uma imagem, o build
# para e avisa qual hash novo precisa de nome.
IMG_NAMES = {
    "97346d856dbe1a43f7280b66491a5bf9": "logo-amar-azul.png",
    "e80b5fad93918ef1b18c8994f4ad8c7b": "logo-amar-branca.png",
    "5835d60287ff94759045b4bf681d790b": "mascote-hero.png",
    "42c1ec569840ee4872feaa6cf8627613": "mascote-apresentando.png",
    "c3d99958967b92aa5063cd6b65ea33bd": "mascote-pulando.png",
    "0befea5b60233dfaa99725befdfbd491": "antonia-sentada.png",
    "196b0c7c3cf1cad102e4255e5a46889d": "foto-antonia.jpg",
    "bcc64e89d338c71ad38b8690566f69e9": "antonia-frasco.png",
}

# nomes das fontes: derivados do comentario /* subset */ que precede cada @font-face
font_names = {}
for block in re.finditer(
    r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", template, re.S
):
    subset, body = block.group(1), block.group(2)
    fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    style = re.search(r"font-style:\s*(\w+)", body).group(1)
    uuid = re.search(r'url\("([^"]+)"\)', body).group(1)
    slug = fam.split()[0].lower()
    if style != "normal":
        slug += "-" + style
    font_names[uuid] = "%s-%s.woff2" % (slug, subset)

os.makedirs(os.path.join(OUT, "assets/img"), exist_ok=True)
os.makedirs(os.path.join(OUT, "assets/fonts"), exist_ok=True)

from PIL import Image
import io as _io

url_of = {}
dims = {}
for uuid, entry in manifest.items():
    data = base64.b64decode(entry["data"])
    if entry.get("compressed"):
        data = gzip.decompress(data)

    if uuid in font_names:
        rel = "assets/fonts/" + font_names[uuid]
        open(os.path.join(OUT, rel), "wb").write(data)
        url_of[uuid] = rel
        continue
    if not entry["mime"].startswith("image/"):
        continue  # runtimes React / dc-runtime / image-slot: descartados

    digest = hashlib.md5(data).hexdigest()
    if digest not in IMG_NAMES:
        sys.exit("Imagem desconhecida no bundle (%s, %d bytes, md5 %s) — "
                 "adicione um nome em IMG_NAMES." % (entry["mime"], len(data), digest))
    name = IMG_NAMES[digest]
    # original preservado no repo; a pagina serve WebP (~5x menor)
    open(os.path.join(OUT, "assets/img", name), "wb").write(data)
    im = Image.open(_io.BytesIO(data))
    webp = os.path.splitext(name)[0] + ".webp"
    im.save(os.path.join(OUT, "assets/img", webp), "webp", quality=88, method=6)
    rel = "assets/img/" + webp
    url_of[uuid] = rel
    dims[rel] = im.size

# ---------------------------------------------------------------- 2. head/body
helmet = re.search(r"<helmet>(.*?)</helmet>", template, re.S).group(1)
body = template[template.index("</helmet>") + len("</helmet>"):]
body = body[: body.rindex("<script type=\"text/x-dc\"")]
body = body.replace("</x-dc>", "").strip()

# o <noscript> do GTM vive fora do helmet, no topo do body: fica onde esta.

# ---------------------------------------------------------------- 3. limpeza
def clean(s):
    # runtimes do prototipo (dc-runtime, image-slot) nao existem em producao
    s = re.sub(r'<script src="[0-9a-f-]{36}"></script>\s*', "", s)
    s = re.sub(r'\sdata-screen-label="[^"]*"', "", s)
    s = s.replace("sc-camel-view-box", "viewBox")
    s = s.replace("sc-camel-preserve-aspect-ratio", "preserveAspectRatio")
    s = s.replace('ref="{{ rv }}"', "")
    s = s.replace('ref="{{ rMas }}"', "data-mas")
    s = re.sub(r'ref="\{\{ r(\w+) \}\}"',
               lambda m: 'data-ref="%s%s"' % (m.group(1)[0].lower(), m.group(1)[1:]), s)
    s = s.replace("{{ ctaLink }}", CTA)
    for uuid, rel in url_of.items():
        s = s.replace(uuid, rel)
    return s


helmet, body = clean(helmet), clean(body)

# <image-slot> -> <img>
def slot_to_img(m):
    attrs = m.group(1)
    src = re.search(r'src="([^"]*)"', attrs).group(1)
    alt = "Enf. Antonia de Maria, responsavel tecnica da Amar Vacinas"
    return ('<img src="%s" alt="%s" width="1400" height="1865" loading="lazy" '
            'decoding="async" style="display:block;width:100%%;height:100%%;'
            'object-fit:cover;">' % (src, alt))


body = re.sub(r"<image-slot([^>]*)></image-slot>", slot_to_img, body)
assert "image-slot" not in body

# width/height (evita layout shift) + lazy-loading abaixo da dobra
seen = {"count": 0}


def fiximg(m):
    tag = m.group(0)
    seen["count"] += 1
    src = re.search(r'src="([^"]*)"', tag)
    add = ""
    if src and src.group(1) in dims and "width=" not in tag:
        w, h = dims[src.group(1)]
        add += ' width="%d" height="%d"' % (w, h)
    if seen["count"] > 2 and "loading=" not in tag:   # lockup + mascote do hero
        add += ' loading="lazy" decoding="async"'
    elif seen["count"] <= 2:
        add += ' fetchpriority="high" decoding="async"'
    return tag[:-1].rstrip() + add + ">"


body = re.sub(r"<img\b[^>]*>", fiximg, body)

for old, new in COPY_FIXES:
    if old not in body:
        sys.exit("Ajuste de copy nao encontrado no handoff — o design mudou "
                 "esse trecho, revise COPY_FIXES:\n  %s" % old)
    body = body.replace(old, new)

# ---------------------------------------------------------------- 4. head novo
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")

# title/description vem do proprio handoff; as duas primeiras imagens do body
# sao o logo do lockup e a imagem grande do hero (o que preload e og usam).
TITLE = re.search(r"<title>(.*?)</title>", helmet, re.S).group(1).strip()
DESCRIPTION = re.search(r'<meta name="description" content="(.*?)"', helmet,
                        re.S).group(1).strip()
hero_imgs = re.findall(r'<img[^>]*src="(assets/img/[^"]+)"', body)[:2]
LOGO_IMG, HERO_IMG = hero_imgs[0], hero_imgs[1]

extra_head = """<meta name="theme-color" content="#3C5DFA">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Amar Vacinas">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESCRIPTION}">
<meta property="og:image" content="{URL}/assets/img/og-amar-vacinas.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/bricolage-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/plus-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{HERO}" as="image" type="image/webp" fetchpriority="high">"""

extra_head = (extra_head.replace("{TITLE}", TITLE)
                        .replace("{DESCRIPTION}", DESCRIPTION)
                        .replace("{HERO}", HERO_IMG))

if SITE_URL:
    extra_head = extra_head.replace("{URL}", SITE_URL)
    extra_head += '\n<link rel="canonical" href="%s/">' % SITE_URL
else:  # sem dominio definido ainda: og:image relativa (a maioria dos scrapers resolve)
    extra_head = extra_head.replace("{URL}/", "")

# preconnects para o Google Fonts nao servem mais (fontes sao locais)
helmet = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", helmet)

# ---------------------------------------------------------------- 5. runtime
runtime = open(os.path.join(HERE, "runtime.js"), encoding="utf-8").read()

html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
%s
%s
</head>
<body>
%s
<script>
%s
</script>
</body>
</html>
""" % (helmet.strip(), extra_head, body, runtime.strip())

# o helmet ja trazia title/description/viewport; remove o viewport duplicado dele
html = html.replace(
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<!-- Google Tag Manager -->',
    "<!-- Google Tag Manager -->", 1)

open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)

# ------------------------------------------------- 6. og:image (1200x630 JPG)
# Monta com o logo e a imagem do hero desta LP; o fundo acompanha a versao do
# logo (branca -> faixa escura, como o hero da LP2).
def _orig(rel):
    return os.path.join(OUT, "assets/img",
                        os.path.splitext(os.path.basename(rel))[0]) + ".png"


escuro = "branca" in LOGO_IMG
og = Image.new("RGB", (1200, 630), (34, 49, 126) if escuro else (228, 233, 255))
hero = Image.open(_orig(HERO_IMG)).convert("RGBA")
hh = 560
hero = hero.resize((round(hero.width * hh / hero.height), hh), Image.LANCZOS)
og.paste(hero, (1200 - hero.width - 90, 630 - hh + 30), hero)
logo = Image.open(_orig(LOGO_IMG)).convert("RGBA")
lw = 420
logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
og.paste(logo, (72, 150), logo)
og.save(os.path.join(OUT, "assets/img/og-amar-vacinas.jpg"), quality=86, optimize=True)

# ------------------------------------------------------- 7. favicon e ícones
# Símbolo da marca (o "M" com a carinha do logo AMAR) em branco sobre o azul
# do logo. A geometria foi medida no PNG do logo em alta resolução; validada
# contra ele com 1px de folga (antialiasing) em todo o contorno.
AZUL_LOGO = (0, 51, 152)          # #003398
SYM_W, SYM_H = 245.0, 165.0       # caixa do símbolo
BARS = [(1, 18, 24, 164), (221, 18, 244, 164)]        # hastes verticais
DOTS = [(91.5, 10.5), (154.5, 10.5)]                  # olhos
DOT_R = 10.5
STROKE = 23
SMILE = ((12.5, 18), (12.5, 99), (64, 152), (122.5, 152),
         (181, 152), (232.5, 99), (232.5, 18))        # duas cúbicas
SYM_FRAC = 0.72                   # largura do símbolo sobre a do ícone


def _bezier(p0, p1, p2, p3, steps=80):
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        yield (u * u * u * p0[0] + 3 * u * u * t * p1[0]
               + 3 * u * t * t * p2[0] + t * t * t * p3[0],
               u * u * u * p0[1] + 3 * u * u * t * p1[1]
               + 3 * u * t * t * p2[1] + t * t * t * p3[1])


def icon(size, ss=4):
    """Ícone quadrado de `size`px, desenhado em `ss`x e reduzido (antialiasing)."""
    from PIL import ImageDraw
    px = size * ss
    img = Image.new("RGB", (px, px), AZUL_LOGO)
    d = ImageDraw.Draw(img)
    k = SYM_FRAC * px / SYM_W                       # escala símbolo -> ícone
    ox = (px - SYM_W * k) / 2
    oy = (px - SYM_H * k) / 2
    T = lambda x, y: (ox + x * k, oy + y * k)

    # traço do sorriso: círculos ao longo da curva (line+joint do PIL serrilha)
    r = STROKE * k / 2
    pts = ([T(*p) for p in _bezier(*SMILE[:4], steps=400)]
           + [T(*p) for p in _bezier(SMILE[3], *SMILE[4:], steps=400)])
    for x, y in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill="white")
    # as pontas arredondadas sobrariam acima do topo das hastes: recorta
    for x0, x1 in ((0, 30), (215, 245)):
        d.rectangle([T(x0, 0), T(x1, 18)], fill=AZUL_LOGO)
    for x0, y0, x1, y1 in BARS:
        d.rectangle([T(x0, y0), T(x1, y1)], fill="white")
    for cx, cy in DOTS:
        x, y = T(cx, cy)
        r = DOT_R * k
        d.ellipse([x - r, y - r, x + r, y + r], fill="white")
    return img.resize((size, size), Image.LANCZOS)


def _path_d():
    a = "M12.5,18 C 12.5,99 64,152 122.5,152 C 181,152 232.5,99 232.5,18"
    return a


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#003398"/>
  <g transform="translate(71.68,131.87) scale(1.5045)">
    <g fill="none" stroke="#FFFFFF" stroke-width="23">
      <path d="M12.5,18 V164"/>
      <path d="M232.5,18 V164"/>
      <path d="%s"/>
    </g>
    <circle cx="91.5" cy="10.5" r="10.5" fill="#FFFFFF"/>
    <circle cx="154.5" cy="10.5" r="10.5" fill="#FFFFFF"/>
  </g>
</svg>
""" % _path_d()
open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8").write(FAVICON)

icon(180).save(os.path.join(OUT, "assets/img/apple-touch-icon.png"))
icon(192).save(os.path.join(OUT, "assets/img/favicon-192.png"))
icon(512).save(os.path.join(OUT, "assets/img/favicon-512.png"))
icon(48).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
    "User-agent: *\nAllow: /\n")

MANIFEST = {
    "name": "Amar Vacinas",
    "short_name": "Amar Vacinas",
    "icons": [
        {"src": "assets/img/favicon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "assets/img/favicon-512.png", "sizes": "512x512", "type": "image/png"},
    ],
    "theme_color": "#3C5DFA",
    "background_color": "#FFFFFF",
}
open(os.path.join(OUT, "site.webmanifest"), "w", encoding="utf-8").write(
    json.dumps(MANIFEST, indent=2, ensure_ascii=False) + "\n")

VERCEL = {
    "cleanUrls": True,
    "headers": [
        {"source": "/assets/(.*)",
         "headers": [{"key": "Cache-Control",
                      "value": "public, max-age=31536000, immutable"}]},
        {"source": "/(.*)",
         "headers": [
             {"key": "X-Content-Type-Options", "value": "nosniff"},
             {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
             {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
         ]},
    ],
}
open(os.path.join(OUT, "vercel.json"), "w", encoding="utf-8").write(
    json.dumps(VERCEL, indent=2, ensure_ascii=False) + "\n")

open(os.path.join(OUT, ".gitignore"), "w", encoding="utf-8").write(
    ".DS_Store\n.vercel/\n")

print("index.html:", len(html), "bytes")
print("assets:", len(url_of))
