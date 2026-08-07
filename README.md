# Amar Vacinas — Landing Page 2 (adultos e idosos)

Segunda landing page da **Amar Vacinas** (clínica particular de vacinação,
Parnaíba-PI). A [LP1](https://github.com/AK-Media-LPs/amar-vacinas-lp) fala com mães
de crianças; esta fala com **adultos e idosos**. Objetivo: gerar conversas no
WhatsApp. Ângulo: cuidado com a própria saúde, sem infantilização e sem alarmismo.

**Site estático puro** — HTML + CSS + um arquivo de JS inline. Sem build, sem
dependências, sem framework. O Vercel serve os arquivos como estão.

## Estrutura

```
index.html                 LP completa (HTML + CSS + JS inline)
build/build.py             converte o handoff de design nesta página
build/runtime.js           animações (entra inline no index.html)
assets/img/*.webp          imagens servidas na página
assets/img/*.png|jpg       originais (fonte; não referenciados pela página)
assets/fonts/*.woff2       Bricolage Grotesque + Plus Jakarta Sans (self-hosted)
favicon.ico · favicon.svg · site.webmanifest · robots.txt · vercel.json
docs/HANDOFF.md            briefing de design original
```

## Regerar a partir de um handoff novo

```
python3 build/build.py "~/Downloads/design_handoff_amar_vacinas_lp2/site/index.html"
```

O handoff chega como um bundle auto-extraível que monta a página em runtime com
React. O script desempacota tudo, converte o template em HTML final, gera as
imagens em WebP, o favicon e a og:image, e reaplica os ajustes de copy feitos
depois da entrega do design (lista `COPY_FIXES` no topo do `build.py`) — se o
designer alterar um desses trechos, o build para em vez de descartar o ajuste
em silêncio.

## Deploy

Projeto Vercel próprio (separado da LP1, para medir as duas em paralelo).
**Framework Preset: Other**, sem build command, output na raiz. Todo push na
`main` publica automaticamente.

## Conversão / rastreamento

- **GTM `GTM-T88KB8FV`** no `<head>` + `<noscript>` no início do `<body>` — o
  mesmo container da LP1, então separe as duas por página nos gatilhos.
- Os 3 CTAs + a barra fixa mobile apontam para `https://wa.me/558699334058` com a
  mensagem pré-preenchida "Olá, vim do site e gostaria de mais informações."
- Cada CTA carrega `data-cta` (`hero`, `meio`, `final`, `sticky`) e dispara um
  evento `clique_whatsapp` no `dataLayer` com `cta_local`.
- Não há formulário: lead = clique no WhatsApp. Não coleta dado de saúde (LGPD).

## O que muda em relação à LP1

- Hero em `#22317E` com texto branco e foto da Enf. Antonia ancorada na base;
  Autoridade invertida para fundo claro.
- Corpo de texto base 18px, botões ≥60px, contraste WCAG AA.
- Mascote discreto (canto do hero e trilha da Solução), sem elementos infantis.
- Copy adulta: nenhuma menção a criança, brinquedoteca, abelhinha ou caderneta.
- 10 dobras (a LP1 tem 9): entram Destaques e o bloco de **atendimento domiciliar**.

## Compliance aplicado (do briefing)

- Sem promessa de proteção, sem alarmismo, sem superlativo.
- Sem pergunta em segunda pessoa sobre status de saúde (política de saúde da Meta).
- "Atendimento particular" visível em várias dobras; nenhuma menção negativa à
  rede pública.
- Responsável técnica identificada: Enf. Antonia de Maria — **sem referência a
  COREN**, por decisão do cliente (difere da LP1).
- Endereço: Praça Santo Antônio, 1020 · Centro · Parnaíba (PI).

## Decisões tomadas na implementação

As duas tarjas amarelas `CONFIRMAR` do FAQ não podiam ir ao ar. Respostas
definidas pelo cliente em 07/08/2026 e aplicadas via `COPY_FIXES`:

- **"É atendimento particular?"** → "Sim, o atendimento é particular. A equipe
  informa valores e formas de pagamento pelo WhatsApp, de acordo com a vacina que
  você precisa." (evita divulgação de preço, conforme regras do conselho)
- **"Precisa agendar?"** → "O agendamento é feito pelo WhatsApp: você combina o
  horário que cabe na sua rotina e é atendido na hora marcada, sem fila."

## Pendências antes de rodar tráfego

- [ ] **Depoimentos** — os 3 da dobra Prova social são fictícios plausíveis,
      herdados do protótipo. Substituir por reais.
- [ ] **Foto da dobra Autoridade** — hoje reusa o retrato da Antonia; o ideal é
      uma foto real da equipe.
- [ ] **Domínio** — ao apontar o domínio final, preencher `og:image` com URL
      absoluta e adicionar `<link rel="canonical">` no `<head>`.

## Notas técnicas

O handoff original entregava um bundle auto-extraível de 4 MB que montava a
página em runtime com React + ReactDOM + um runtime de design. Esta versão
desempacota tudo em HTML estático: mesmo resultado visual (validado pixel a pixel
contra o protótipo), sem JS de framework, com imagens em WebP e fontes
self-hosted.

As animações (reveals no scroll, trilha da Solução, parallax) foram portadas para
JS vanilla no fim do `index.html` e respeitam `prefers-reduced-motion`.
