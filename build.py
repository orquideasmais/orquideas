
import json
import html
import shutil
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------

R = Path(__file__).resolve().parent
P = R / "public"
P.mkdir(parents=True, exist_ok=True)

MES = (
    "janeiro fevereiro março abril maio junho julho agosto "
    "setembro outubro novembro dezembro"
).split()

def carregar_json(nome, padrao=None):
    arquivo = R / f"{nome}.json"

    if not arquivo.exists():
        if padrao is not None:
            print(f"Aviso: {arquivo.name} não encontrado.")
            return padrao
        raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {arquivo}")

    try:
        with arquivo.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON inválido em {arquivo.name}, "
            f"linha {exc.lineno}, coluna {exc.colno}: {exc.msg}"
        ) from exc

def E(valor):
    return html.escape(str(valor or ""), quote=True)

cfg = carregar_json("config")
arts = carregar_json("artigos", [])

if not isinstance(cfg, dict):
    raise ValueError("config.json precisa conter um objeto JSON.")

if not isinstance(arts, list):
    raise ValueError("artigos.json precisa conter uma lista de matérias.")

# Verifica campos e datas das matérias.
slugs = set()

for i, a in enumerate(arts, start=1):
    if not isinstance(a, dict):
        raise ValueError(f"A matéria {i} não é um objeto JSON.")

    for campo in ("titulo", "slug", "data", "categoria", "resumo"):
        if not a.get(campo):
            raise ValueError(
                f"Matéria {i}: campo obrigatório ausente: {campo}"
            )

    try:
        datetime.date.fromisoformat(a["data"])
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Data inválida na matéria {a['titulo']!r}: {a['data']!r}. "
            "Use AAAA-MM-DD."
        ) from exc

    slug = a["slug"]
    if (
        not isinstance(slug, str)
        or slug in (".", "..")
        or "/" in slug
        or "\\" in slug
        or not slug.strip()
    ):
        raise ValueError(f"Slug inválido: {slug!r}")

    if slug in slugs:
        raise ValueError(f"Slug duplicado: {slug!r}")

    slugs.add(slug)

    if not isinstance(a.get("paragrafos", []), list):
        raise ValueError(
            f"'paragrafos' precisa ser uma lista em {a['titulo']!r}."
        )

arts.sort(key=lambda a: a["data"], reverse=True)

def dt(s):
    data = datetime.date.fromisoformat(s)
    return f"{data.day} de {MES[data.month - 1]} de {data.year}"

def mins(a):
    texto = " ".join(
        str(t) for t in a.get("paragrafos", [])
        if not str(t).startswith("## ")
    )
    return max(1, round(len(texto.split()) / 200))

def paras(a):
    resultado = []
    for t in a.get("paragrafos", []):
        t = str(t)
        if t.startswith("## "):
            resultado.append(f"<h2>{E(t[3:])}</h2>")
        else:
            resultado.append(f"<p>{E(t)}</p>")
    return "".join(resultado)

def write(path, txt):
    destino = P / path
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(str(txt), encoding="utf-8")

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------

NAV = [
    ("", "Matérias"),
    ("maranhao/", "Maranhão"),
    ("pesquisa-leo/", "Pesquisa do LEO"),
    ("quiz/", "Quiz"),
    ("glossario/", "Glossário"),
    ("linha-do-tempo/", "Linha do tempo"),
]

def page(titulo, desc, body, rel, main=False):
    nome = cfg.get("nome", "LEO")
    slogan = cfg.get("slogan", "")
    descricao = cfg.get("descricao", "")
    instagram = cfg.get("instagram", "#")

    titulo_completo = (
        f"{titulo} | {nome}" if titulo
        else f"{nome} | {slogan}"
    )

    nav = "".join(
        f'<a href="{rel}{u}">{E(n)}</a>'
        for u, n in NAV
    )

    conteudo = (
        f'<main class="p">{body}</main>'
        if main else f'<main class="w">{body}</main>'
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(titulo_completo)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(titulo_completo)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🌸%3C/text%3E%3C/svg%3E">
<link rel="alternate" type="application/rss+xml" href="{rel}feed.xml">
<link rel="stylesheet" href="{rel}assets/style.css">
</head>
<body>
<header>
<div class="w nav">
<a class="logo" href="{rel}">🌸 {E(nome[:-1])}<b>+</b></a>
<nav class="menu">{nav}</nav>
<a class="btn o" href="{E(instagram)}" target="_blank" rel="noopener">📷 @leo.ufma</a>
</div>
</header>
{conteudo}
<footer>
<div class="w">
<p>{E(descricao)}</p>
<p><a href="{E(instagram)}" target="_blank" rel="noopener">Instagram do Laboratório de Estudos sobre Orquídeas (LEO)</a> · <a href="{rel}feed.xml">RSS</a></p>
</div>
</footer>
<script src="{rel}assets/app.js"></script>
</body>
</html>"""

def cover(a, rel, big=False):
    hue = int(a.get("hue", 300))
    estilo = (
        f"background:linear-gradient(135deg,"
        f"hsl({hue % 360},70%,82%),"
        f"hsl({(hue + 40) % 360},65%,68%))"
    )

    imagem = a.get("imagem")
    if imagem:
        # Impede caminhos absolutos e referências que saiam da pasta.
        nome_imagem = Path(str(imagem))
        if nome_imagem.is_absolute() or ".." in nome_imagem.parts:
            raise ValueError(f"Caminho de imagem inválido: {imagem!r}")

        conteudo = (
            f'<img src="{rel}imagens/{E(imagem)}" '
            f'alt="{E(a.get("titulo", "Orquídea"))}">'
        )
    else:
        conteudo = E(a.get("emoji", "🌸"))

    classe = "cv big" if big else "cv"
    return f'<div class="{classe}" style="{estilo}">{conteudo}</div>'

def card(a, rel):
    busca = (a["titulo"] + " " + a["resumo"]).lower()
    return f"""<a class="card" href="{rel}materias/{E(a['slug'])}/"
data-c="{E(a['categoria'])}" data-t="{E(busca)}">
{cover(a, rel)}
<div class="cb">
<span class="tag">{E(a['categoria'])}</span>
<h3>{E(a['titulo'])}</h3>
<p>{E(a['resumo'])}</p>
<p class="meta" style="margin-top:8px">{dt(a['data'])} · ⏱ {mins(a)} min</p>
</div></a>"""

def listing(items, rel):
    return '<div class="grid">' + "".join(
        card(a, rel) for a in items
    ) + "</div>"

def nl():
    action = cfg.get("newsletter_action", "")
    campo = cfg.get("newsletter_campo_email", "email")

    if action:
        return (
            f'<form class="nl" action="{E(action)}" method="post" '
            f'target="_blank">'
            f'<input type="email" name="{E(campo)}" '
            f'placeholder="Seu melhor e-mail" required>'
            f'<button class="btn">Quero receber</button></form>'
        )

    return (
        '<p style="opacity:.85">(Cadastro de e-mail ainda não '
        'configurado: veja o LEIAME.)</p>'
    )

def newsbox(t="Receba cada nova matéria no seu e-mail"):
    return f'<div class="cta"><p><b>📬 {E(t)}</b></p>{nl()}</div>'

# --------------------------------------------------
# PÁGINA INICIAL
# --------------------------------------------------

categorias = ["Todas"] + list(dict.fromkeys(
    a["categoria"] for a in arts
))

chips = "".join(
    f'<button class="chip{" on" if c == "Todas" else ""}" '
    f'data-c="{E(c)}">{E(c)}</button>'
    for c in categorias
)

leo = [a for a in arts if a.get("leo")]

home = f"""
<div class="hero">
<h1>Orquídeas, <em>além do ornamental</em></h1>
<p>{E(cfg.get("descricao", ""))} Cada matéria se lê em poucos minutos e traz a fonte original.</p>
<div class="row c">
<a class="btn" href="quiz/">🧠 Teste-se no quiz</a>
<a class="btn o" href="{E(cfg.get('instagram', '#'))}" target="_blank" rel="noopener">Siga o LEO no Instagram</a>
</div>
</div>
<div class="row tools">
<input id="q" type="search" placeholder="Buscar nas matérias..." aria-label="Buscar">
</div>
<div class="row tools">{chips}</div>
{listing(arts, "")}
{newsbox()}
"""

write("index.html", page("", cfg.get("descricao", ""), home, ""))

# --------------------------------------------------
# PÁGINAS DAS MATÉRIAS
# --------------------------------------------------

for i, a in enumerate(arts):
    autor = a.get("autor", "")
    bio = cfg.get("autores", {}).get(autor, "")
    fonte = a.get("fonte") or {}

    if not isinstance(fonte, dict):
        fonte = {}

    byline = (
        f'<p class="meta">Por <b>{E(autor)}</b> · '
        f'{dt(a["data"])} · ⏱ {mins(a)} min</p>'
    )
    if bio:
        byline += f'<p class="meta">{E(bio)}</p>'

    credito = ""
    if a.get("imagem") and a.get("credito_imagem"):
        credito = f'<p class="cred">Foto: {E(a["credito_imagem"])}</p>'

    corpo_fonte = ""
    if fonte.get("url"):
        corpo_fonte = (
            f'<a class="btn" href="{E(fonte["url"])}" '
            'target="_blank" rel="noopener">Ler a pesquisa original ↗</a>'
        )

    proxima = ""
    if len(arts) > 1:
        n = arts[(i + 1) % len(arts)]
        proxima = (
            f'<p><a class="btn o" href="../{E(n["slug"])}/">'
            f'Próxima: {E(n.get("emoji", "🌸"))} '
            f'{E(n["titulo"])} →</a></p>'
        )

    body = f"""
<a href="../../">← Todas as matérias</a>
{cover(a, "../../", True)}
{credito}
<p class="tag" style="margin:16px 0 0">{E(a['categoria'])}</p>
<h1>{E(a['titulo'])}</h1>
<p class="lead">{E(a['resumo'])}</p>
{byline}
{paras(a)}
<div class="fx"><b>⚡ Fato relâmpago:</b> {E(a.get('fato', ''))}</div>
<div class="box">
<h4>Estudo em que esta matéria se baseia</h4>
<b>{E(fonte.get('titulo', 'Fonte não informada'))}</b><br>
{E(fonte.get('autores', ''))}<br>
<i>{E(fonte.get('revista', ''))}</i><br><br>
{corpo_fonte}
</div>
<div class="row">
<b>Compartilhar:</b>
<a class="btn" id="wa" href="#" target="_blank" rel="noopener">WhatsApp</a>
<button class="btn" id="ig">Instagram</button>
<button class="btn o" id="cp">🔗 Copiar link</button>
</div>
<div class="cta" style="margin-top:24px">
<p>Quer ver mais ciência sobre orquídeas? Acompanhe o Laboratório de Estudos sobre Orquídeas.</p>
<a class="btn" href="{E(cfg.get('instagram', '#'))}" target="_blank" rel="noopener">📷 @leo.ufma no Instagram</a>
</div>
{newsbox()}
{proxima}
"""

    write(
        f"materias/{a['slug']}/index.html",
        page(a["titulo"], a["resumo"], body, "../../", True)
    )

# --------------------------------------------------
# SEÇÕES
# --------------------------------------------------

mar = [
    a for a in arts
    if a.get("categoria") == "Maranhão"
    or a["slug"].startswith("brasil")
]

write(
    "maranhao/index.html",
    page(
        "Orquídeas do Maranhão",
        "Espécies, pesquisas e conservação das orquídeas do Maranhão.",
        '<div class="hero"><h1>Orquídeas do <em>Maranhão</em></h1>'
        '<p>Entre a Amazônia e o Cerrado, o estado guarda uma flora '
        'de orquídeas ainda pouco conhecida.</p></div>'
        + listing(mar, "../"),
        "../"
    )
)

write(
    "pesquisa-leo/index.html",
    page(
        "Pesquisa do LEO",
        "Estudos do Laboratório de Estudos sobre Orquídeas.",
        '<div class="hero"><h1>Pesquisa do <em>LEO</em></h1>'
        '<p>Estudos do Laboratório de Estudos sobre Orquídeas da '
        'UFMA, traduzidos para todo mundo.</p></div>'
        + (listing(leo, "../") if leo else "<p>Em breve.</p>")
        + f'<div class="cta"><p>Acompanhe o dia a dia do laboratório.</p>'
        f'<a class="btn" href="{E(cfg.get("instagram", "#"))}" '
        'target="_blank" rel="noopener">📷 @leo.ufma</a></div>',
        "../"
    )
)

# --------------------------------------------------
# QUIZ
# --------------------------------------------------

quiz = carregar_json("quiz", [])
quiz_json = json.dumps(
    quiz, ensure_ascii=False
).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")

write(
    "quiz/index.html",
    page(
        "Quiz: mito ou verdade?",
        "Teste o que você sabe sobre orquídeas.",
        f'<h1>Mito ou verdade? 🌸</h1>'
        f'<p class="lead">Teste o que você sabe sobre orquídeas.</p>'
        f'<div id="quiz"></div>'
        f'<p id="score" style="font-size:20px;font-weight:700"></p>'
        f'<script type="application/json" id="qdata">{quiz_json}</script>',
        "../",
        True
    )
)

# --------------------------------------------------
# GLOSSÁRIO
# --------------------------------------------------

glossario = carregar_json("glossario", [])

gl = "".join(
    f'<div><dt>{E(g["t"])}</dt><dd>{E(g["d"])}</dd></div>'
    for g in sorted(glossario, key=lambda g: g.get("t", "").lower())
)

write(
    "glossario/index.html",
    page(
        "Glossário",
        "Os principais termos sobre orquídeas.",
        '<h1>Glossário</h1>'
        '<p class="lead">Os termos que você vai encontrar nas matérias.</p>'
        '<input id="gq" type="search" placeholder="Buscar termo..." '
        'style="width:100%;padding:11px 14px;border-radius:99px;'
        'border:1.5px solid var(--bd);background:var(--sf);'
        'color:var(--tx);font:inherit">'
        f'<dl>{gl}</dl>',
        "../",
        True
    )
)

# --------------------------------------------------
# LINHA DO TEMPO
# --------------------------------------------------

timeline = carregar_json("linha-do-tempo", [])

tl = "".join(
    f'<div><span class="y">{E(t.get("a", ""))}</span>'
    f'<h3>{E(t.get("t", ""))}</h3>'
    f'<p>{E(t.get("d", ""))}</p></div>'
    for t in timeline
)

write(
    "linha-do-tempo/index.html",
    page(
        "Linha do tempo",
        "Marcos das pesquisas sobre orquídeas.",
        '<h1>Linha do tempo</h1>'
        '<p class="lead">Marcos das pesquisas sobre orquídeas.</p>'
        f'<div class="tl">{tl}</div>',
        "../",
        True
    )
)

# --------------------------------------------------
# RSS
# --------------------------------------------------

base = (
    cfg.get("url_do_site") or "https://SEU-SITE"
).rstrip("/")

rss = ET.Element("rss", {"version": "2.0"})
channel = ET.SubElement(rss, "channel")

def xml_text(pai, tag, texto):
    el = ET.SubElement(pai, tag)
    el.text = str(texto or "")
    return el

xml_text(channel, "title", cfg.get("nome", "LEO"))
xml_text(channel, "link", base + "/")
xml_text(channel, "description", cfg.get("descricao", ""))
xml_text(channel, "language", "pt-BR")

for a in arts:
    item = ET.SubElement(channel, "item")
    url = f"{base}/materias/{a['slug']}/"

    xml_text(item, "title", a["titulo"])
    xml_text(item, "link", url)
    xml_text(item, "guid", url)

    data = datetime.date.fromisoformat(a["data"])
    pubdate = datetime.datetime.combine(
        data, datetime.time(12, 0)
    ).strftime("%a, %d %b %Y 12:00:00 +0000")

    xml_text(item, "pubDate", pubdate)
    xml_text(item, "description", a["resumo"])

rss_xml = ET.tostring(
    rss, encoding="utf-8", xml_declaration=True
)
write("feed.xml", rss_xml.decode("utf-8"))

# --------------------------------------------------
# ARQUIVOS ESTÁTICOS
# --------------------------------------------------

for pasta in ("assets", "imagens"):
    origem = R / pasta
    destino = P / pasta

    if origem.is_dir():
        shutil.copytree(origem, destino, dirs_exist_ok=True)
    elif pasta == "assets":
        raise FileNotFoundError(
            f"A pasta obrigatória '{origem}' não existe."
        )
    else:
        print("Aviso: pasta de imagens não encontrada.")

# GitHub Pages: CNAME somente quando há domínio configurado.
dominio = str(cfg.get("dominio_proprio", "")).strip()
if dominio:
    write("CNAME", dominio + "\n")

print(f"OK: {len(arts)} matérias geradas.")
print(f"Site pronto em: {P}")
