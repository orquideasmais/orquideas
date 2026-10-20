# Orquídeas+ — guia para os editores

Site estático e gratuito. Tudo o que aparece nele está em arquivos de texto na pasta `dados/`. Ao salvar uma alteração, o site se reconstrói sozinho.

## 0. Atalho: o site já está em HTML pronto
A pasta `public/` contém o site completo em HTML. Qualquer hospedagem de arquivos estáticos serve: basta enviar o conteúdo dessa pasta. O arquivo `orquideas-site-pronto.zip` traz só essa pasta. Para editar depois, use o projeto completo (`orquideas-mais.zip`): ao mudar os arquivos de `dados/`, rode `python build.py` (ou deixe o GitHub fazer isso) para gerar o HTML de novo.

## 1. Publicar o site (uma vez só)
**Opção A — GitHub Pages (recomendada, grátis)**
1. Crie uma conta em github.com com um e-mail do grupo (assim todos os editores compartilham o acesso, ou adicione cada pessoa em *Settings → Collaborators*).
2. Crie um repositório novo (ex.: `orquideas-mais`) e envie todos os arquivos desta pasta (*Add file → Upload files*).
3. Vá em *Settings → Pages → Source* e escolha **GitHub Actions**.
4. Aguarde 1 a 2 minutos. O endereço será `https://SEU-USUARIO.github.io/orquideas-mais/`.

**Opção B — Netlify ou Cloudflare Pages (grátis)**: conecte o repositório e use *build command* `python build.py` e *publish directory* `public`.
**Opção mais simples ainda**: arraste a pasta `public` para o Netlify Drop. Funciona, mas cada alteração exige refazer o upload.

## 2. Passar o site para os estudantes
O site fica no repositório, não na conta de quem o criou. Basta criar a conta/organização do grupo no GitHub e convidar os editores como colaboradores (ou transferir o repositório em *Settings → Transfer*).

## 3. Adicionar uma matéria
1. Abra `dados/artigos.json` no GitHub e clique no lápis (editar).
2. Copie um bloco `{ ... }` inteiro, cole no fim da lista (com vírgula entre os blocos) e troque os textos.
2b. Em `paragrafos`, uma linha que começa com `## ` vira subtítulo (ex.: `"## Por que isso importa"`). As demais linhas são parágrafos. O tempo de leitura é calculado sozinho (cerca de 200 palavras por minuto): 400 palavras dão 2 min, 1.000 dão 5 min.
3. Campos: `slug` (endereço, só letras minúsculas e hífen), `titulo`, `categoria`, `emoji`, `resumo`, `paragrafos` (lista), `fato`, `fonte` (estudo, autores, revista, link), `autor`, `data` (AAAA-MM-DD), `leo` (true para aparecer em "Pesquisa do LEO").
4. Salve (*Commit changes*). Em 1 a 2 minutos a matéria está no ar, com página própria.

## 4. Trocar fotos
1. Envie a foto para a pasta `imagens/` (*Add file → Upload files*).
2. No bloco da matéria, preencha `"imagem": "nome-do-arquivo.jpg"` e `"credito_imagem": "Nome de quem fez a foto"`.
Use fotos próprias ou com licença livre. Imagens leves (até 300 KB) deixam o site rápido.

## 5. Editar o restante
- `dados/config.json`: nome, slogan, Instagram, mini-bios dos autores, domínio, newsletter.
- `dados/quiz.json`, `dados/glossario.json`, `dados/linha-do-tempo.json`: edite ou acrescente itens no mesmo formato.
- Visual: `assets/style.css`.

## 6. E-mail para os leitores
1. Crie uma conta gratuita em um serviço de newsletter (Buttondown, MailerLite, Brevo etc.) e gere o formulário de inscrição.
2. Copie o endereço `action` do formulário para `newsletter_action` e o nome do campo de e-mail para `newsletter_campo_email` em `config.json`.
3. O site gera o arquivo `feed.xml` (RSS) com todas as matérias. Alguns serviços enviam e-mail automático a cada novo item do RSS; confira se o plano gratuito inclui isso. Se não incluir, o envio é feito manualmente em poucos cliques a cada matéria nova.
4. Preencha `url_do_site` em `config.json` com o endereço final, para o RSS ter os links certos.
Atenção: guardar e-mails de leitores exige respeitar a LGPD. Os serviços acima trazem consentimento e descadastro prontos.

## 7. Domínio próprio
Domínio como `orquideasmais.com.br` é pago (cerca de R$ 40 por ano no Registro.br). Depois de comprar: escreva o domínio em `dominio_proprio` no `config.json` e siga a configuração de DNS indicada em *Settings → Pages → Custom domain*. Sem domínio próprio, o endereço gratuito do GitHub Pages já dá a cada matéria uma página própria.

## 8. Conteúdo pendente
- Datas de floração das orquídeas do Maranhão: faltam dados dos estudos do LEO.
- Conferir quais estudos são do LEO (campo `leo`) e se o link do estudo da matéria 2 (Darwin) pode ser trocado pelo DOI oficial.
- Revisão científica dos textos pela autora antes da divulgação ampla.
