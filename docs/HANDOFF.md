# LP2 Amar Vacinas — adultos e idosos

Segunda versão da landing page. A **LP1** fala com mães de crianças; esta fala com **adultos e idosos**.

## Deploy (GitHub → Vercel)
1. Coloque o conteúdo de `site/` na raiz do repositório (apenas `index.html`).
2. `git init && git add . && git commit -m "LP2 Amar Vacinas" && git push`
3. Vercel: **Add New → Project → Import**. Framework preset: **Other**. Sem build command. Output: raiz.

Arquivo único e autocontido (imagens e scripts embutidos). Externos apenas: GTM e Google Fonts.

> Sugestão: publique como projeto/domínio separado da LP1 (ex.: `/adultos` ou subdomínio) para medir as duas em paralelo no mesmo GTM.

## O que muda em relação à LP1
- Hero em **#22317E** (azul escuro) com texto branco; Autoridade invertida para fundo claro; demais seções alternando branco e #E4E9FF.
- Corpo de texto base **18px**, botões ≥60px de altura, contraste WCAG AA (kickers sobre faixa azul-clara em #22317E).
- Mascote discreto (canto do hero e trilha da Solução) — sem elementos infantis.
- Foto da Enf. Antonia recortada, ancorada na base do hero (nasce da barra em movimento). No mobile vira faixa full-bleed de 450px com enquadramento no rosto.
- Copy do público adulto/idoso; nenhuma menção a criança, brinquedoteca, abelhinha ou caderneta infantil.

## Estrutura (10 dobras)
Hero · Faixa de confiança (marquee) · Destaques · Problema (3 dores) · Solução (3 passos, trilha animada no scroll) · Autoridade · Experiência (6 blocos, incl. **atendimento domiciliar** em destaque) · Prova social (3 depoimentos + stats) · FAQ (6 perguntas) · CTA final + rodapé.

## Conversão / rastreamento
- GTM **GTM-T88KB8FV** no `<head>` + `<noscript>` — manter.
- 3 CTAs com textos distintos + barra fixa mobile, todos para `wa.me/558699334058`, com `data-cta` (`hero`, `meio`, `final`, `sticky`).
- Sem formulário: lead = clique no WhatsApp (LGPD — não coleta dado de saúde).

## Compliance aplicado
- Sem promessa/garantia de proteção, sem alarmismo, sem superlativo.
- Sem pergunta em segunda pessoa sobre status de saúde (política de saúde da Meta).
- "Atendimento particular" visível em várias dobras; nenhuma menção negativa à rede pública.
- Responsável técnica identificada: Enf. Antonia de Maria (sem referência a COREN, conforme decisão do cliente).
- Endereço: Praça Santo Antônio, 1020 · Centro · Parnaíba (PI).

## Pendências antes de publicar
- 2 marcadores **CONFIRMAR** (tarja amarela) seguem visíveis no FAQ: valores/convênios e se o agendamento é obrigatório.
- Depoimentos são fictícios plausíveis — substituir por reais, se houver.
- Stats (+5 anos, +500 atendimentos) confirmados pelo cliente.
- Foto da seção Autoridade: hoje usa retrato da Antonia; ideal ter foto real da equipe.

## Arquivos
- `site/index.html` — LP2 final autocontida (deploy direto)
- `source/Amar Vacinas LP2 Adultos.dc.html` — fonte do protótipo
- `source/assets/` — foto recortada da Antonia, mascote, logo branca, retrato de autoridade
