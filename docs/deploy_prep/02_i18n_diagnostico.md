# Diagnóstico de i18n e overflow de texto — Samurai Edge (preparação de deploy)

Data: 2026-11-12. Escopo: somente leitura no código-fonte (nada em `src/`, `main.py`, `tests/`, `tools/` foi alterado).
Scripts/artefatos fora do repo: `/tmp/i18n_overflow_check.py` (entregável), `/tmp/i18n_overflow_report.json` (saída), `/tmp/i18n_work/` (harness de apoio).
Reproduzir: `/Users/thiagocarvalho/Public/SamuraiEdge/venv/bin/python /tmp/i18n_overflow_check.py` (~50 s, um processo, SDL dummy).

## 0. Resumo executivo

- A infraestrutura de i18n (tabelas PT/EN com 628 chaves cada, simétricas, sem placeholders divergentes) está **sólida**. O problema não é a tabela, é tudo que **não passa por ela**.
- **Nenhum bloqueador confirmado** de i18n. Há **7 itens Altos**, o mais barato e mais visível sendo a chave inexistente `invert_y_label` (a tela de Jogabilidade mostra a chave crua) e os glifos que viram quadrado/invisível nas telas mais usadas.
- Jogador em inglês ainda vê português em: tela final de partida (`VENCE A PARTIDA!`), contador de round (`RODADA n`), mensagens de loading, rótulos do HUD de habilidades (~100 literais mistos PT/EN), vários rótulos do menu de Opções e da Galeria. Jogador em português vê ~107 banners de combate só em inglês.
- Resoluções: lógica fixa 1280x720; 1280x800 (Steam Deck) funciona com letterbox de 40 px e escala 1.0 (pixel-perfect). Sem problema de layout por resolução.
- Testes existentes de i18n: 13/13 passam. **Atenção**: um deles regrava o `settings.json` real (ver Médio M6; eu restaurei o arquivo e conferi o md5).

---

## 1. Mapa do sistema (`src/i18n.py`, 1709 linhas)

| Aspecto | Como é |
|---|---|
| Idiomas | `pt` e `en` apenas (`LANG_PT`, `LANG_EN`; preferência também aceita `auto`). Nenhum outro idioma. |
| Estrutura | `I18N = {"pt": {...628 chaves...}, "en": {...628 chaves...}}` (linhas 182-944 e 946-1708). Valores `str`; 5 chaves são listas de tuplas `(texto, estilo)`: `rules_box1/2/3_lines`, `ctrl_p1_lines`, `ctrl_p2_lines`. |
| Lookup | `t(key, **kwargs)` (i18n.py:169): `I18N[lang][key]` → fallback `I18N["pt"][key]` → **a própria chave** (silencioso). Com kwargs faz `str.format`; qualquer exceção é engolida e devolve o texto cru. Idioma ativo desconhecido cai em PT. |
| Ícones | Tokens `{icon:confirm}` etc. dentro dos textos; expandidos por `svg_icon_renderer`. `t()` sem kwargs preserva o token. Nenhuma chave mistura `{icon:}` com outros placeholders (verificado), então o `format` não os quebra. |
| Seleção | `SAMURAI_EDGE_LANG` (env, prioridade absoluta) → `settings.json: gameplay.language` (`auto`/`pt`/`en`) → detecção do SO (`detect_system_lang`: Windows `GetUserDefaultUILanguage`, macOS `defaults read AppleLanguages`, senão `LC_ALL/LC_MESSAGES/LANG`; prefixo `pt` = PT, **tudo mais = EN**). O idioma do cliente Steam **não** é lido. |
| Persistência | `save_language_setting` grava em `settings.json` preservando o resto. Caminho: `BASE_DIR/settings.json` (`src/config.py:8`, `src/effects/quality.py:216`). |
| Troca em runtime | `SettingsMenu.cycle_language` (auto→pt→en), `toggle_lang` (botão PT/EN em `character_select` e `game_help`, persiste). Telas com cache (`arena_select`, `character_select`) invalidam por `get_lang()`; não achei `t()` em constante de módulo. |
| Fontes | `src/ui/fonts.py`: Shojumaru (títulos), Zen Antique (texto; wrapper `_NoMacronFont` troca ā/ē/ī/ō/ū por letra simples). Cinzel só aparece em `font_manager.py` (não vi uso direto por tela). `main.py:1000-1002` cria `font_large/mid/small = pygame.font.Font(None, 48/26/20)` (fonte **default do pygame**) e passa para título, settings, seleção de lutador/arena, galeria e Ajuda. |

---

## 2. Cobertura de chaves

Método: AST + regex sobre todo o código fora de `tests/` e `i18n.py`; resolução runtime das famílias dinâmicas (roster, arenas, `DIFF_KEYS`, `KIND_KEYS`, `PHASE_KEYS`, `settings_action_*`).

| Verificação | Resultado |
|---|---|
| Chaves faltando entre idiomas | **0** (628 = 628). Sem chaves duplicadas no literal. |
| Valores vazios | **0** |
| Placeholders divergentes PT x EN | **0**. Chamadas com `kwargs` conferidas por AST: todas passam os placeholders certos; 9 chamadas usam `.format()` direto em `settings_menu.py:1065,1121,1132,1137,1166,1426,1436,1453,1463` (funciona, mas contorna `t(**kw)`). |
| Chaves usadas e não definidas | **1**: `invert_y_label` (`src/ui/settings_menu.py:1148`) |
| Famílias dinâmicas completas | roster (24 `char_*_name`), arenas (24 + `random` x 5 campos), dificuldade, tipo de luta, fases do boss: todas resolvem. |
| Idênticos PT==EN | 70. A maioria é legítima (nomes próprios, `[5/5] MAX`, `ARCADE`). **Candidatos reais a tradução**: `char_joe_title` ("American Ninja"), `char_joe_damage` ("Shuriken (Stun)"), `char_joe_special` ("Doberman (1-Hit Kill)"), `char_teppo_title` ("Marksman"), `arcade_kind_endurance` ("ENDURANCE 1x2"). |
| Texto em idioma errado | Heurística não achou PT dentro de EN nem EN dentro de PT nas tabelas (o problema está fora das tabelas). |
| Chaves órfãs | **54** chaves definidas e nunca usadas (lista no Apêndice A), mais `arena_*_name/...` e `settings_action_*` que são dinâmicas e **estão em uso**. |

---

## 3. Strings hardcoded (fora do i18n)

Contagens por AST/grep; exemplos com arquivo:linha. "PT" = português, "EN" = inglês, "misto" = os dois no mesmo conjunto.

| Arquivo | Qtd. | Idioma | Exemplos |
|---|---|---|---|
| `src/combat/collision.py` + ~22 arquivos de entidades/mundo | **107 literais** em `FloatingBanner("...")` (28 usam `t()`) | EN | `collision.py:299 "SLASH DEFLECTION!"`, `:780 "POISONED! 6s TO SURVIVE!"`, `:1127 "HAGANE PIERCE (UNBLOCKABLE)!"`; `src/world/kyoto_map.py:587 "PERIGO DUPLO: CARRUAGENS CRUZADAS!"` (PT). `projectile.py` 8, `hazards.py` 6, `valerius.py` 6 |
| `main.py` HUD | `get_fighter_action_labels` **65** literais (main.py:290-353), `get_fighter_cooldown_data` **35** rótulos (355-538) | misto | `"Pólvora nos Olhos"`, `"Recarregando Kunai"`, `"Flurry Shaolin"`, `"Tachiai Tackle"` |
| `main.py` HUD/rodada | ~12 | misto | `:1160 round_label=f"RODADA {n}"`, `:2879/2887 "☠ FRENZY"`, `:2717/2881 "POISON"`, `:3005 "READY..."`, `:3017 "START!"`, `:2916/2951 "READY"` |
| `main.py` loading | 6 (+2 em `src/ui/loading_screen.py:22,184`) | PT | `:998 "Iniciando motor e renderizador..."`, `:1041 "Pronto! Entrando no Bakumatsu..."`, `"[ CARREGANDO ]"` |
| `src/ui/round_result.py` | 2 | PT | `:248-249 f"{nome} VENCE A PARTIDA!"` (tela final da partida em EN mostra "KENSHI VENCE A PARTIDA!") |
| `src/ui/settings_menu.py` | ~14 | PT/misto | `:933 "BGM: ..%  SFX: ..%  Qualidade: .."`, `:1066 "Alta: SSAA 2x Voxel..."`, `:1082/1446 "LAYOUT DA INTERFACE: ["`, `:1307/1474 "⚙ PERSONALIZAR BOTÕES TOUCH (HUD)"`, `:1353-1355 "] CONECTADO"`, `"[MODO TOUCH SCREEN] ..."`; card Jogabilidade (`:938`) usa "IA:/Idioma:/Boost:" fixos |
| `src/ui/gallery_screen.py` | ~25 UI + ~110 letras/títulos | PT (UI) / EN (conteúdo) | `:854 "Nenhuma ilustração encontrada..."`, `:1025 "TRILHA SONORA ["`, `:1119 ": [ Faixa "`, `:1171 "📜 LETRA DA MÚSICA & TRADUÇÃO"`, `:1206-1215`; `:136-167` nomes de temas EN; `:33-114` letras |
| `src/ui/opening_video.py` | 1 | PT | `:284 "Segure para pular"` (a chave `credits_skip_prompt` já existe e é usada em `arcade_credits.py:1015`) |
| `src/ui/character_select.py` | **30 ternários** `if lang == LANG_PT else` + `'PT'/'EN'`, `'< TROCAR P1'`, `'< MENU'` | bilíngue inline | `:1488-1510 "ESCOLHA SEU GUERREIRO"/"CHOOSE YOUR WARRIOR"`, `:1800-1822`, `:2008-2036 "CONFIRMAR P1"/"CONFIRM P1"` |
| `src/ui/game_help.py` | `FIGHTERS_GUIDE_DATA` (38-~1550): 25 fichas x `pt`/`en` inline; 5 ternários (`:2148` sub-abas) | bilíngue inline | funciona nos 2 idiomas, mas fora do `I18N` |
| `src/effects/cinematic_director.py` | 154 legendas de fatality (`:220-397`, dicts `*_pt/*_en`) | bilíngue inline | idem |
| `src/entities/hendrika.py` | `REAGENT_NAMES` / `REAGENT_NAMES_EN` (`:33,43,191`) | bilíngue inline | idem |
| `src/ui/hud_rondel.py` | 12 | PT/JP | `:19-79 'MADEIRA','FOGO','TERRA','METAL','ÁGUA','ORÁCULO'` (rótulos do rondel) |
| `src/combat/clash_system.py`, `src/entities/kabuki.py` | 3 | EN | `clash_system.py:266-267 "STRIKE!"`, `kabuki.py:266 "KAWARIMI"` |
| `src/input/controller_manager.py` | ~8 | PT | `:211 "Controle ("`, `:198 "Controle MFi ("`, `:938 "[Controle: ...]"`, `:959 "Ação Principal / Ação Secundária"` (no Steam Deck aparece "Controle (Steam ...)" também em EN) |
| `src/input/touch_controls.py`, `touch_editor.py` | 9 + 5 | PT | `touch_controls.py:445-517 "ESPECIAL","ESQUIVA","GOLPE"`, `:681 "⚙ OPÇÕES"`; `touch_editor.py:180-221` (só mobile) |
| `src/world/arenas.py` | 25 `name=` em PT | PT | `:182 "Floresta de Bambu"` etc. — **dado morto** (`theme_name` em `arena_generator.py:503` nunca é exibido); Baixo |

Bem-comportados (100% via `t()`): `title_screen`, `pause_menu`, `versus_config` (exceto setas), `arcade_screens`, `arena_select`, `round_intro` (exceto o `RODADA`), nomes/títulos/estilos de lutador e arenas (tabela), créditos (`credits_*`).

---

## 4. Overflow de texto

### 4.1 Como o texto é desenhado
- Tela lógica fixa **1280x720** (`src/config.py:11-12`), renderizada num canvas e escalada por `DisplayScaler` (`src/input/display_scaler.py`) com letterbox/pillarbox. Layout independe da resolução real.
- Fontes: Shojumaru (botões/títulos), Zen Antique (subtítulos), **default do pygame 48/26/20** nas telas que recebem `font_*` do `main.py` (settings, Ajuda, hub, cards).
- Estratégias de encaixe encontradas: elipse "..." (`parchment.fit_text`, `settings_menu._fit_text`, `game_help._fit_text`), redução de fonte (`arena_select._fit_text` até 9 px, `round_intro._render_fitted_text` 24→14 px, título de `round_result` 40→18 px), esmagamento horizontal por `smoothscale` (`pause_menu.py:163-173`), quebra de linha com rolagem (`game_help._wrap_text`), e **nenhum** encaixe em vários textos centrados (barras de dica, cartões do hub).

### 4.2 Resoluções (script, seção A)

| Janela | Escala | Viewport | Barras | Escala inteira |
|---|---|---|---|---|
| 1280x720 (padrão, `RESIZABLE`) | 1.0 | 1280x720 | nenhuma | sim |
| **1280x800 (Steam Deck)** | 1.0 | 1280x720 em y=40 | letterbox 40 px | **sim** (pixel-perfect) |
| 1366x768 | 1.067 | 1365x768 | — | não |
| 1920x1080 | 1.5 | 1920x1080 | — | não |
| 2560x1440 / 3840x2160 | 2.0 / 3.0 | cheio | — | sim |
| 1024x768 / 800x480 | 0.8 / 0.625 | com letterbox | — | não |

Modo de escala padrão é `"sharp"` (`pygame.transform.scale`, vizinho mais próximo). Em escalas não inteiras (1.067, 1.5, 0.8) o texto de 9-14 px fica irregular. `settings.json` tem `video.resolution/fullscreen/vsync` que o código **não lê** (só `quality.py` lê `video.effects_quality/game_boost`); F11 alterna tela cheia.

### 4.3 Achados medidos (PT e EN; 152 telas x 2 idiomas, 30 551 renders, 0 erros)

Truncamentos com "..." (largura cheia vs. disponível aproximada):

| Site | Idioma | Pior caso | Qtd. de textos únicos |
|---|---|---|---|
| `character_select.py:1955` linha "Vel: .. \| dano" (Zen 12) | PT | "Vel: [3/5] Equilibrado \| Ofuda Espiritual" 232 px > ~178 | 22 de 24 lutadores |
| idem | EN | "Speed: [5/5] Evasive Zoner \| Kamaitachi Blades" 272 px > ~175 | 24 de 24 |
| `character_select.py:1937` título do lutador (Zen 14) | PT | "Kunoichi das Duas Kodachi" 183 > ~112 | 8 |
| idem | EN | "Prussian Necromancer" 159 > ~112 | 4 |
| `character_select.py:1942` estilo (Zen 12) | PT | "Lança Op & Armadilha de Urso" 179 > ~117 | 3 |
| idem | EN | "Naginata & Heavy Plate" 137 > ~112 | 3 |
| `game_help.py:1602` coluna esquerda da ficha (default 20) | PT | "Sumô Imperial Rikishi, Combo Tsuppari & Tachiai 3-Fase.." 398 > ~201 | 27 |
| idem | EN | "Imperial Rikishi Sumo, 2-Hit Tsuppari Combo & 3-Phase.." 437 > ~204 | 25 |
| `arcade_screens.py:170` cartão "continuar jornada" (Shojumaru 22, `fit_text`) | PT | "CONTINUAR JORNADA" 298 > ~241 | 1 |
| idem | EN | "RESUME JOURNEY" 253 > ~235 | 1 |
| `settings_menu.py:1195` (`_fit_text` em :315) cabeçalho P1 na aba Controles, chave `player_1_label` (default 26) | PT | "PLAYER 1 (VERMELHO)" 361 > ~196 | 1 |
| idem | EN | "PLAYER 1 (RED)" 249 > ~196 | 1 |

Fonte reduzida abaixo de 11 px (`arena_select.py:343-350`, grade 8x3, cartão de ~141 px):
- PT: **11** nomes de arena caem para 9-10 px; EN: **9**. Exemplos PT: "ACAMPAMENTO NA FLORESTA", "PÁTIO DOS SINOS SHAOLIN", "JARDIM DOS LÍRIOS CARMIM"; EN: "SHAOLIN BELL COURTYARD", "DEJIMA PORT WAREHOUSE".
- **Transbordo real**: PT "ACAMPAMENTO NA FLORESTA" mede 143 px a 9 px (mínimo) contra 131 px úteis (+12 px, `arena_select.py:474-476`). É o único transbordo duro que o harness detectou.

Sem problema (medido): título de tela mais largo (~589 px "CONFIGURAÇÃO DE JOGABILIDADE" em painel de 980), pergaminho de round (nomes de lutador cabem a 24 px exceto os que o `_render_fitted_text` já reduz), pausa (nenhum item esmagado hoje), HUD de cooldown (soma dos 2 maiores rótulos 388 px < 500 px de folga), legendas de fatality (maior 765 px < 1280), banners (maior 513 px).

Casos de margem apertada, sem corte hoje: card "Jogabilidade" do hub (`settings_menu.py:938`: PT 371 px em ~389 úteis, e a linha é PT fixa).

### 4.4 O que o script NÃO cobre (honestidade)
Detecção automática só pega: truncamento por elipse, redução de fonte e cruzamento da borda do canvas; texto desenhado direto em caixas sem encaixe só foi verificado por leitura de código nos sites de maior largura. **Não renderizados**: HUD de combate real (só medição estática do `main.py`), `match_intro`, `outcome_sequence`, cinemática de fatality, créditos/karaokê (usa **Trebuchet MS do sistema** via `match_font` em `arcade_credits.py:366`, ausente no Steam Deck/Linux → cai em Shojumaru/Zen 38/24 px), touch UI, loading screen, versões demo/mobile. **Não testado em Steam Deck físico.**

---

## 5. Fontes e glifos

Latim estendido do PT (á é í ó ú â ê ô ã õ ç à + maiúsculas): **todos presentes** em Shojumaru e Zen Antique. Vogais com macron (ā ē ī ō ū): Shojumaru tem; Zen Antique não tem (Ū sai em branco) — tratado por `_NoMacronFont` **somente** quando a fonte vem de `get_text_font()`. Todos os 195 kanji distintos do código existem na Zen Antique. Não há outros alfabetos (CJK de interface, cirílico etc.) nas tabelas.

**Comportamento medido**: glifo ausente em Shojumaru/Zen renderiza **invisível** (0 pixels); na fonte default do pygame renderiza **quadrado (tofu)**.

Glifos ausentes na fonte realmente usada (43 pares; script seção C3 e `/tmp/i18n_overflow_report.json`):

| Glifo | Fonte do site | Onde | Efeito |
|---|---|---|---|
| 🏛 / 🔒 (`gallery_btn_label`, `gallery_locked_label`) | default pygame | hub de Opções, `settings_menu.py:954,989` | tofu no card da Galeria (🔒 para quem ainda não zerou o Arcade) |
| ☠ e ⚠ | default pygame | HUD de combate `main.py:2715,2879,2887,2902,2937`; o `try/except` ao redor nunca dispara porque `render` não levanta | tofu em veneno/alerta |
| ← ↑ → ↓ em `ctrl_p1_lines/ctrl_p2_lines` | default pygame | Ajuda, aba Controles, `game_help.py:1982` | tofu |
| kanji das fatalities (荒波両断, 百花乱突…, 24 caracteres) | default pygame | Ajuda, ficha do lutador, `game_help.py:2223` | tofu (PT e EN) |
| ◄ ► | Shojumaru | setas de opção do Versus, `versus_config.py:480-481` | setas **invisíveis** |
| 勝 | Shojumaru | selo da tela final, `round_result.py:233` | selo vazio |
| ▶ | Shojumaru | botão "continuar", `arcade_screens.py:178` | invisível |
| ☯ | Zen | gema do Oráculo, `hud_rondel.py:73,219` | invisível |
| 📜 🎵 ⏱ ― | Zen | Galeria `gallery_screen.py:934,1138,1171,1206` | invisível |
| ⚙ | default / Zen | `settings_menu.py:1307,1474`, `touch_controls.py:681` | tofu (mobile/touch) |
| ◄ ► e setas de `arena_selected_badge`, `settings_footer_instructions` | — | chaves órfãs | sem efeito hoje |

Se vierem outros idiomas: Shojumaru é só latim; Zen Antique cobre japonês, mas não cirílico/grego/árabe/coreano/chinês.

---

## 6. Testes existentes

Comando (um processo): `venv/bin/python -m unittest tests.test_language_setting tests.test_translation_and_ui tests.test_font_transparency` — **13 testes, OK (0,37 s)**. `pytest` **não está instalado** no venv nem no python3 do sistema; usei `unittest` (os testes são `unittest.TestCase`).
Aviso emitido: `The system font 'sans-serif' couldn't be found` (pygame.sysfont).
Efeito colateral observado: o `settings.json` real passou de `"language": "pt"` para `"en"` (ver M6). Restaurei a partir de cópia e conferi o md5 (idêntico ao original).
Cobertura dos testes: simetria de chaves, placeholders, resiliência de `t()` e render de 3 telas nos 2 idiomas. **Não cobrem**: chave usada e não definida, strings hardcoded, truncamento/overflow, glifos.

---

# Achados por severidade

## BLOQUEADOR
Nenhum confirmado em i18n. Condicional: ver A7 (persistência de idioma no build empacotado) caso o diagnóstico de dados do usuário confirme que a pasta de instalação não é gravável.

## ALTO

**A1. Chave `invert_y_label` não existe nas tabelas.** `settings_menu.py:1148`: `t("invert_y_label")` devolve a própria chave (truthy), então o fallback `else` nunca roda e o botão mostra `invert_y_label: [ ON ]` em PT e EN. Correção: adicionar a chave em PT/EN (ex.: "Inverter Eixo Y do Analógico: [ {status} ]" / "Invert Analog Y Axis") e remover o ternário; no `t()`, logar chaves ausentes em modo dev.

**A2. Tela final da partida e HUD de round em PT para quem joga em EN.** `round_result.py:248-249` (`" VENCE A PARTIDA!"`) e `main.py:1160` (`"RODADA {n}"`). Já existe `victory_text` em ambos os idiomas. Criar `match_win_text`/`round_label` nas tabelas.

**A3. Rótulos de habilidades do HUD hardcoded, misto PT/EN, sem tabela.** `main.py:290-353` (65 literais) e `:355-538` (35 rótulos), exibidos em `main.py:2893-2958`. Mover para chaves `skill_<fighter>_<slot>` em `I18N`. Nota: os cooldowns são dicts criados a cada frame; usar `t()` aí é barato (dict lookup).

**A4. 107 banners flutuantes de combate só em inglês** (28 já usam `t()`). `collision.py` (55), `projectile.py` (8), `hazards.py` (6), `valerius.py` (6) e mais ~18 arquivos; alguns em PT (`kyoto_map.py:587`). Jogador PT vê "BLIND PARRY!". Correção: chaves `banner_*` + `t()`; é mecânico e testável por AST.

**A5. Glifos que viram quadrado em telas de uso comum** (§5): 🏛/🔒 no hub de Opções (toda abertura de Opções), ☠/⚠ no HUD de veneno, setas e kanji na Ajuda. Correção: trocar o texto por ícone SVG (`svg_icon_renderer` já existe), usar Zen Antique (`get_text_font`) em vez da fonte default para o texto da Ajuda/hub (Zen cobre kanji e setas), remover emoji das chaves `gallery_*_label`, `☠` → ícone desenhado.

**A6. Setas ◄ ► do Versus e selo 勝 invisíveis** (Shojumaru sem glifo). `versus_config.py:480-481`, `round_result.py:233`, também ▶ em `arcade_screens.py:178` e ☯ no `hud_rondel.py:73`. Correção: usar Zen Antique (tem ▲▼○ mas **não** ◄►▶☯) ou desenhar polígonos/ícones; para 勝 usar `get_text_font`.

**A7. Persistência do idioma depende de `settings.json` ao lado do código.** `i18n.get_settings_path()` → `BASE_DIR/settings.json` (`config.py:8`); em build PyInstaller isso aponta para dentro do bundle/`_internal` (onefile: temp apagado; macOS .app/Steam: pode ser somente leitura; "Verificar integridade" do Steam pode apagar). `save_language_setting` falha em silêncio (`except: return False`). Correção: usar diretório de dados do usuário (`%APPDATA%`, `~/Library/Application Support`, `$XDG_CONFIG_HOME`) e cair no atual só em dev. Cruzar com o diagnóstico de dados salvos.

## MÉDIO

**M1. Textos truncados com "..." em tela principal** (§4.3): cartões de lutador (stats em 22/24 lutadores PT e 24/24 EN, título/estilo em 4-8), coluna esquerda da Ajuda (25-27 fichas), cartão "continuar jornada" do Arcade, cabeçalho "PLAYER 1 (VERMELHO)". Correção: abreviar as strings (limite ~28 caracteres a 12 px / ~22 a 14 px), quebrar em 2 linhas, ou aumentar a área; padronizar um limite de caracteres no checklist de tradução.

**M2. Grade de arenas com fonte 9-10 px e um transbordo real.** `arena_select.py:343-350`; PT "ACAMPAMENTO NA FLORESTA" excede 12 px; 11 nomes PT / 9 EN em ≤10 px (ilegível a 1280x720 e pior em Deck). Correção: nome curto para a grade (`arena_*_short`), ou duas linhas, e piso de 11 px.

**M3. Escala não inteira com `scale_mode="sharp"`.** Em 1366x768, 1920x1080 (1.5x) e janelas redimensionadas, texto de 9-14 px com vizinho mais próximo fica serrilhado/irregular. Correção: escala inteira + barras, ou `smoothscale` quando `scale` não for inteiro. 1280x800 (Deck) e 1440p/4K estão ok.

**M4. Menus de Opções com rótulos PT fixos e ternários inline.** `settings_menu.py:933,1066,1082,1110-1115,1307,1353-1355,1446,1474`; "Qualidade/Idioma/Boost" PT em EN, descrições de dificuldade e `Alta: SSAA...` só PT. Mover para `I18N`.

**M5. Bilíngue "inline" fora do `I18N`** (30 ternários em `character_select.py`, `game_help` 25 fichas + 5 ternários, `cinematic_director` 154 legendas, `hendrika` reagentes). Funciona hoje, mas um 3º idioma exige tocar ~60 pontos e a tabela não reflete a realidade; os testes de simetria não os veem. Correção: migrar para `I18N` (ou arquivo de dados por idioma) e incluir um teste que falhe em `if lang == LANG_PT` fora de `i18n.py`.

**M6. Teste regrava o `settings.json` real.** um dos testes de `SettingsMenu` em `tests/test_language_setting.py` (linhas 145 e 170; não isolei qual) chama `SettingsMenu.cycle_language()`, que usa o caminho padrão (`settings_menu.py:221-236`). Rodar a suíte altera a preferência do desenvolvedor (aconteceu aqui: pt→en). Correção: `monkeypatch`/`unittest.mock.patch` de `get_settings_path`, ou `SAMURAI_EDGE_SETTINGS` temporário no `setUp`.

**M7. Fallback e erros silenciosos em `t()`.** Chave ausente devolve o nome da chave; erro de `format` devolve texto cru; idioma desconhecido cai em PT (para um jogo com fallback de SO em EN, o natural seria EN). Correção: log único por chave ausente, modo estrito nos testes/CI, e fallback EN.

**M8. Galeria: UI em PT, conteúdo em EN.** `gallery_screen.py:854,1025,1119,1171,1206-1215` (PT fixo) e letras/temas (`:33-167`) em EN; jogador PT lê "Blades in the burning night". Decisão de produto + mover UI para `I18N`.

**M9. Mensagens de loading, vídeo de abertura e controles em PT fixo.** `main.py:998-1041`, `loading_screen.py:22,184`, `opening_video.py:284` (a chave `credits_skip_prompt` já existe), `controller_manager.py:198-211,938,959` (no Steam Deck: "Controle (Steam Virtual Gamepad)").

**M10. Traduções ausentes em chaves de lutador/modo.** `char_joe_title/damage/special`, `char_teppo_title`, `arcade_kind_endurance` idênticos em PT e EN (§2).

## BAIXO

- **B1. 54 chaves órfãs** (Apêndice A), inclusive `arcade_konami_activated` duplicado de `arcade_secret_code_activated` (ambos adicionados no diff atual de `i18n.py`). Remover ou usar (várias já têm equivalente hardcoded que deveria usá-las: `skip_video`, `boss_warning`, `banner_fell`, `banner_out_of_breath`, `boss_clank`, `boss_heal`).
- **B2. `world/arenas.py`: 25 nomes `name="..."` em PT** sem uso na UI (dado morto/confuso).
- **B3. Hub de Opções: margem apertada** no status do card Jogabilidade (371/389 px) e texto com PT fixo.
- **B4. Fonte do karaokê depende do SO** (`arcade_credits.py:366`, Trebuchet MS); em Linux/Deck cai para Shojumaru/Zen com tamanhos pensados para outra fonte. Conferir visualmente.
- **B5. Detecção de idioma ignora o idioma do cliente Steam**; só prefixo `pt` do SO vira PT. Se o Steam do jogador estiver em PT e o SO em EN (comum no Deck), abre em EN. Opcional: ler `SteamAPI_ISteamApps_GetCurrentGameLanguage` ou o `LANGUAGE` de `steam_appid`.
- **B6. `settings.json` com chaves `video.resolution/fullscreen/vsync` sem leitor** no código (confunde quem edita à mão).
- **B7. `{icon:...}` em chaves com `format`:** hoje seguro, mas qualquer chave futura que combine `{icon:x}` com `kwargs` perderá a formatação silenciosamente (`t()` engole o `KeyError`). Documentar ou tratar `icon` explicitamente.

---

## Apêndice A — chaves órfãs (54)
`arcade_development_notice, arcade_konami_activated, arcade_next_opponent, arena_navigation_hint, arena_selected_badge, arena_subtitle, arena_tag_new, arena_tag_random, arena_tag_stage1, arena_title, arrows_label, badge_ia, badge_p1, badge_p2, banner_fell, banner_out_of_breath, boss_clank, boss_heal, boss_life_label, boss_warning, btn_help, btn_start, change_warriors, char_locked_hint, char_stat_damage, char_stat_special, credits_skip_hint, fullscreen_toggle_label, gallery_karaoke_badge, gallery_music_pause, gallery_music_play, gallery_next, gallery_prev, gamepad_not_detected_p1, gamepad_not_detected_p2, guide_gamepad, guide_nav, menu_about, menu_manual, menu_play, menu_quit, menu_settings, mode_1p, mode_2p, mode_coming_soon, mode_selection_title, p1_controls_prefix, p2_controls_prefix, powder_tracker, settings_btn, settings_footer_instructions, skip_video, stat_keys, title_navigation_hint`
(`btn_start`, `gallery_music_play`, `powder_tracker` aparecem só em testes.)

## Apêndice B — o que foi verificado e como
- Tabelas/placeholders/órfãs: `/tmp/i18n_cov.py` (lógica no §2; AST por chamada para placeholders).
- Hardcoded: `/tmp/hc_scan.py` e `/tmp/hc_scan2.py` (AST; ~1 958 candidatos brutos, filtrados manualmente; contagens acima são pós-triagem; podem existir literais em variáveis intermediárias não capturados).
- Overflow/glifos: `/tmp/i18n_overflow_check.py` (harness que instrumenta `pygame.font.Font.render`, reproduz as fontes default do `main.py`; glifos via cmap `fontTools` do python3 do sistema).
- Não verificado: jogo em execução real, Steam Deck físico, fontes do sistema (Trebuchet), telas citadas em §4.4, textos dentro de vídeos/imagens.
