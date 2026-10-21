import json,html,os,shutil,datetime
R=os.path.dirname(os.path.abspath(__file__));P=R+"/public"
L=lambda n:json.load(open(f"{R}/{n}.json",encoding="utf-8"))
E=html.escape;cfg=L("config");arts=sorted(L("artigos"),key=lambda a:a["data"],reverse=True)
MES="janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()
def dt(s):y,m,d=map(int,s.split("-"));return f"{d} de {MES[m-1]} de {y}"
def mins(a):return max(1,round(len(" ".join(t for t in a["paragrafos"] if not t.startswith("## ")).split())/200))
def paras(a):return "".join(f"<h2>{E(t[3:])}</h2>" if t.startswith("## ") else f"<p>{E(t)}</p>" for t in a["paragrafos"])
def write(path,txt):
    os.makedirs(os.path.dirname(f"{P}/{path}"),exist_ok=True);open(f"{P}/{path}","w",encoding="utf-8").write(txt)
NAV=[("","Matérias"),("maranhao/","Maranhão"),("pesquisa-leo/","Pesquisa do LEO"),("quiz/","Quiz"),("glossario/","Glossário"),("linha-do-tempo/","Linha do tempo")]
def page(titulo,desc,body,rel,main=False):
    nav="".join(f'<a href="{rel}{u}">{n}</a>' for u,n in NAV)
    t=f"{titulo} | {cfg['nome']}" if titulo else f"{cfg['nome']} | {cfg['slogan']}"
    return f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(t)}</title><meta name="description" content="{E(desc)}"><meta property="og:title" content="{E(t)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🌸%3C/text%3E%3C/svg%3E">
<link rel="alternate" type="application/rss+xml" href="{rel}feed.xml"><link rel="stylesheet" href="{rel}assets/style.css"></head><body>
<header><div class="w nav"><a class="logo" href="{rel}">🌸 {E(cfg['nome'][:-1])}<b>+</b></a><nav class="menu">{nav}</nav>
<a class="btn o" href="{cfg['instagram']}" target="_blank" rel="noopener">📷 @leo.ufma</a></div></header>
{'<main class="p">'+body+'</main>' if main else '<main class="w">'+body+'</main>'}
<footer><div class="w"><p>{E(cfg['descricao'])}</p><p><a href="{cfg['instagram']}" target="_blank" rel="noopener">Instagram do Laboratório de Estudos sobre Orquídeas (LEO)</a> · <a href="{rel}feed.xml">RSS</a></p></div></footer>
<script src="{rel}assets/app.js"></script></body></html>'''
def cover(a,rel,big=False):
    st=f"background:linear-gradient(135deg,hsl({a['hue']},70%,82%),hsl({a['hue']+40},65%,68%))"
    inner=f'<img src="{rel}imagens/{E(a["imagem"])}" alt="{E(a["titulo"])}">' if a.get("imagem") else a["emoji"]
    return f'<div class="cv{" big" if big else ""}" style="{st}">{inner}</div>'
def card(a,rel):
    return f'<a class="card" href="{rel}materias/{a["slug"]}/" data-c="{E(a["categoria"])}" data-t="{E((a["titulo"]+" "+a["resumo"]).lower())}">{cover(a,rel)}<div class="cb"><span class="tag">{E(a["categoria"])}</span><h3>{E(a["titulo"])}</h3><p>{E(a["resumo"])}</p><p class="meta" style="margin-top:8px">{dt(a["data"])} · ⏱ {mins(a)} min</p></div></a>'
def nl():
    if cfg["newsletter_action"]:
        return f'<form class="nl" action="{E(cfg["newsletter_action"])}" method="post" target="_blank"><input type="email" name="{E(cfg["newsletter_campo_email"])}" placeholder="Seu melhor e-mail" required><button class="btn">Quero receber</button></form>'
    return '<p style="opacity:.85">(Cadastro de e-mail ainda não configurado: veja o LEIAME.)</p>'
def newsbox(t="Receba cada nova matéria no seu e-mail"):return f'<div class="cta"><p><b>📬 {t}</b></p>{nl()}</div>'
def listing(items,rel):return '<div class="grid">'+"".join(card(a,rel) for a in items)+'</div>'
# home
cats=["Todas"]+[c for c in dict.fromkeys(a["categoria"] for a in arts)]
chips="".join(f'<button class="chip{" on" if c=="Todas" else ""}" data-c="{E(c)}">{E(c)}</button>' for c in cats)
leo=[a for a in arts if a.get("leo")]
home=f'''<div class="hero"><h1>Orquídeas, <em>além do ornamental</em></h1><p>{E(cfg["descricao"])} Cada matéria se lê em poucos minutos e traz a fonte original.</p>
<div class="row c"><a class="btn" href="quiz/">🧠 Teste-se no quiz</a><a class="btn o" href="{cfg['instagram']}" target="_blank" rel="noopener">Siga o LEO no Instagram</a></div></div>
<div class="row tools"><input id="q" type="search" placeholder="Buscar nas matérias..." aria-label="Buscar"></div><div class="row tools">{chips}</div>{listing(arts,"")}
{newsbox()}'''
write("index.html",page("",cfg["descricao"],home,""))
# materias
for i,a in enumerate(arts):
    n=arts[(i+1)%len(arts)];au=a.get("autor","");bio=cfg["autores"].get(au,"");f=a["fonte"]
    byline=f'<p class="meta">Por <b>{E(au)}</b> · {dt(a["data"])} · ⏱ {mins(a)} min</p>'+(f'<p class="meta">{E(bio)}</p>' if bio else "")
    cr=f'<p class="cred">Foto: {E(a["credito_imagem"])}</p>' if a.get("imagem") and a.get("credito_imagem") else ""
    body=f'''<a href="../../">← Todas as matérias</a>{cover(a,"../../",True)}{cr}<p class="tag" style="margin:16px 0 0">{E(a["categoria"])}</p><h1>{E(a["titulo"])}</h1><p class="lead">{E(a["resumo"])}</p>{byline}
{paras(a)}<div class="fx"><b>⚡ Fato relâmpago:</b> {E(a["fato"])}</div>
<div class="box"><h4>Estudo em que esta matéria se baseia</h4><b>{E(f["titulo"])}</b><br>{E(f["autores"])}<br><i>{E(f["revista"])}</i><br><br><a class="btn" href="{E(f["url"])}" target="_blank" rel="noopener">Ler a pesquisa original ↗</a></div>
<div class="row"><b>Compartilhar:</b><a class="btn" id="wa" href="#" target="_blank" rel="noopener">WhatsApp</a><button class="btn" id="ig">Instagram</button><button class="btn o" id="cp">🔗 Copiar link</button></div>
<div class="cta" style="margin-top:24px"><p>Quer ver mais ciência sobre orquídeas? Acompanhe o Laboratório de Estudos sobre Orquídeas.</p><a class="btn" href="{cfg["instagram"]}" target="_blank" rel="noopener">📷 @leo.ufma no Instagram</a></div>{newsbox()}
<p><a class="btn o" href="../{n["slug"]}/">Próxima: {n["emoji"]} {E(n["titulo"])} →</a></p>'''
    write(f"materias/{a['slug']}/index.html",page(a["titulo"],a["resumo"],body,"../../",True))
# secoes
mar=[a for a in arts if a["categoria"]=="Maranhão" or a["slug"].startswith("brasil")]
write("maranhao/index.html",page("Orquídeas do Maranhão","Espécies, pesquisas e conservação das orquídeas do Maranhão.",'<div class="hero"><h1>Orquídeas do <em>Maranhão</em></h1><p>Entre a Amazônia e o Cerrado, o estado guarda uma flora de orquídeas ainda pouco conhecida.</p></div>'+listing(mar,"../"),"../"))
write("pesquisa-leo/index.html",page("Pesquisa do LEO","Estudos do Laboratório de Estudos sobre Orquídeas.",'<div class="hero"><h1>Pesquisa do <em>LEO</em></h1><p>Estudos do Laboratório de Estudos sobre Orquídeas da UFMA, traduzidos para todo mundo.</p></div>'+(listing(leo,"../") if leo else "<p>Em breve.</p>")+f'<div class="cta"><p>Acompanhe o dia a dia do laboratório.</p><a class="btn" href="{cfg["instagram"]}" target="_blank" rel="noopener">📷 @leo.ufma</a></div>',"../"))
qz=json.dumps(L("quiz"),ensure_ascii=False).replace("</","<\\/")
write("quiz/index.html",page("Quiz: mito ou verdade?","Teste o que você sabe sobre orquídeas.",f'<h1>Mito ou verdade? 🌸</h1><p class="lead">Teste o que você sabe sobre orquídeas.</p><div id="quiz"></div><p id="score" style="font-size:20px;font-weight:700"></p><script type="application/json" id="qdata">{qz}</script>',"../",True))
gl="".join(f'<div><dt>{E(g["t"])}</dt><dd>{E(g["d"])}</dd></div>' for g in sorted(L("glossario"),key=lambda g:g["t"]))
write("glossario/index.html",page("Glossário","Os principais termos sobre orquídeas.",f'<h1>Glossário</h1><p class="lead">Os termos que você vai encontrar nas matérias.</p><input id="gq" type="search" placeholder="Buscar termo..." style="width:100%;padding:11px 14px;border-radius:99px;border:1.5px solid var(--bd);background:var(--sf);color:var(--tx);font:inherit"><dl>{gl}</dl>',"../",True))
tl="".join(f'<div><span class="y">{E(t["a"])}</span><h3>{E(t["t"])}</h3><p>{E(t["d"])}</p></div>' for t in L("linha-do-tempo"))
write("linha-do-tempo/index.html",page("Linha do tempo","Marcos das pesquisas sobre orquídeas.",f'<h1>Linha do tempo</h1><p class="lead">Marcos das pesquisas sobre orquídeas.</p><div class="tl">{tl}</div>',"../",True))
# feed, assets, dominio
base=(cfg["url_do_site"] or "https://SEU-SITE").rstrip("/")
items="".join(f'<item><title>{E(a["titulo"])}</title><link>{base}/materias/{a["slug"]}/</link><guid>{base}/materias/{a["slug"]}/</guid><pubDate>{datetime.datetime.strptime(a["data"],"%Y-%m-%d").strftime("%a, %d %b %Y 12:00:00 GMT")}</pubDate><description>{E(a["resumo"])}</description></item>' for a in arts)
write("feed.xml",f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{E(cfg["nome"])}</title><link>{base}/</link><description>{E(cfg["descricao"])}</description><language>pt-BR</language>{items}</channel></rss>')
shutil.copytree(R+"/assets",P+"/assets",dirs_exist_ok=True);os.makedirs(P+"/imagens",exist_ok=True)
if os.path.isdir(R+"/imagens"):shutil.copytree(R+"/imagens",P+"/imagens",dirs_exist_ok=True)
if cfg["dominio_proprio"]:write("CNAME",cfg["dominio_proprio"])
print("OK:",len(arts),"matérias")
