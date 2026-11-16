# Diagnóstico de crashes e soft-locks ponta a ponta — Samurai Edge (preparação de deploy)

Data: 2026-11-12. Escopo: **somente leitura** em `src/`, `main.py`, `tests/`, `tools/` (nada foi alterado). Estado avaliado: **working tree sujo** (64 entradas no `git status`), não só o HEAD (`01c76fe`).
Ambiente: macOS (Darwin, arm64), Python 3.11.6 do `venv/`, pygame-ce 2.5.8 (SDL 2.32.10), numpy 2.4.6, SDL em modo `dummy` (vídeo e áudio). A máquina estava sob carga forte de benchmark (load average 8 a 50), então **tempos/FPS medidos não são representativos**; os resultados funcionais (crash / não crash) são.
Todos os scripts estão copiados em `docs/deploy_prep/03_scripts/` (os originais ficam em `/tmp/se/`; eles referenciam caminhos `/tmp/se`).

---

## 0. Resumo executivo

**Veredito: não está pronto para deploy como está.** Há 1 bloqueador determinístico no caminho normal e 1 crash certo por clique num botão visível do menu de Opções. Ambos têm correção de poucas linhas.

| # | Sev. | Prob. de o jogador atingir | Item |
|---|---|---|---|
| B1 | **Bloqueador** | Alta (100% em `mist_temple`; ~4,2% de qualquer run de Arcade; 100% dos runs de Arcade com a Kasumi) | `UnboundLocalError` em `FireworkMortars.on_phase` (`src/world/hazards.py:443`/`:462`), código **não commitado**. Derruba o jogo ~6 s depois do início da luta |
| A1 | **Alto** | Média (botão visível em Opções > Controles, só com mouse) | Clicar em "PERSONALIZAR BOTÕES TOUCH (HUD)" derruba o jogo: `settings_menu.py:822` chama `touch_editor.render(surface)` sem as fontes (`touch_editor.py:162`). Código **commitado** (HEAD) |
| A2 | **Alto** (a validar em hardware) | Alta no Steam Deck | Layout de gamepad assume a ordem de botões do SDL GameController/HIDAPI (macOS). No Linux/Steam Input o layout evdev é outro: LB/RB na tela de título **fecham o jogo**; Start não pausa |
| A3 | **Alto** | Alta em instalações read-only / `.app` translocado | Saves e settings gravados **dentro da pasta do jogo** (`BASE_DIR`); falha de escrita é silenciosa |
| A4 | **Alto** (pipeline) | Certa para quem usar o `pytest` | `tests/test_game.py:760` chama `os._exit(0)`: `pytest tests/` **sai com código 0 no meio** (depois de ~38% da suíte) e nunca roda o resto. Mais 11 testes falhando (6 já no HEAD) |
| A5 | **Alto** (a validar) | Só no build `.app` do macOS | Detecção de iOS por `".app" in bundle_path` classifica o `.app` do Mac como iOS (`main.py:41-50`, `controller_manager.py:16-24`) |
| M1 | Médio | Baixa (arquivo editado/corrompido) | `controls_config.json` com valores não numéricos derruba o jogo **a cada inicialização** (`main.py:1015`, `sound_manager.py:385`) |
| M2 | Médio | Baixa/Média (troca de dispositivo de áudio, suspend/resume) | `SoundManager.play()` não protege a geração/uso do som: qualquer `pygame.error` vira crash |
| M3 | Médio | Certa p/ Android | `buildozer.spec` não lista `numpy`, que é import duro em 6 módulos |
| L1 | Baixo (latente) | ~Nula hoje | `cinematic_director.py:2178` usa `camera` indefinido (finisher `EARTH_STOMP_CRUSH` da Goro), código **não commitado** |
| L2-L6 | Baixo | ver §6 | Detalhes menores |

**O que está bom (evidência):** nenhum crash, NaN/inf, soft-lock ou vazamento de memória em: ~65 mil frames de monkey test (eventos aleatórios em todas as telas, `dt` de 0 a 1000 ms, gamepad/toque/resize sintéticos), arcade completo de 12 lutas com o chefe até os créditos, 1128 sequências de finisher (56 estilos x 24 lutadores) com render completo, 25 arenas x 150 s de simulação com perigos e quedas em buraco, 24 duelos com lutadores sobrepostos (distância 0), soak de 5000 frames, 74 variações de arquivos corrompidos, ausência total de `assets/`, falha total de `mixer.init`, ausência de cv2/pyvidplayer2/imageio-ffmpeg.

---

## 1. Suíte de testes (item 1)

Comando base: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/ ...` com um único processo. **O `venv/` não tem `pytest`**: instalei em `/tmp/se/pylib` (`pip install --target`) e usei `PYTHONPATH`, sem tocar no venv.

### 1.1 `pytest tests/` aborta no meio com código 0 (A4)

`tests/test_game.py:760` termina `test_complete_roster()` com `os._exit(0)` (a função está em `tests/test_game.py:44`). Quando o pytest roda a função, o processo inteiro morre **sem relatório e com exit code 0**. Evidência: `pytest tests/ -v` parou em `tests/test_game.py::test_complete_roster` (38% de 420) e retornou `exit 0`; repeti duas vezes. Tudo que vem depois na ordem alfabética (`test_gameplay_adjustments_cycle6` ... `test_versus_config_and_arcade_frame`, ~210 testes) **não é executado** num `pytest tests/` normal. Um CI que olhe só o código de saída fica verde.
Correção: remover o `os._exit(0)` da função de teste (e o de `tests/test_parchment_screens.py:203`, que só roda no `__main__`) ou isolá-lo em `if __name__ == "__main__"`.

### 1.2 Resultado real (rodando com `--deselect tests/test_game.py::test_complete_roster`; esse teste roda à parte e passa)

| Árvore | Resultado |
|---|---|
| Working tree atual | **11 falhas**, 409 passaram, 1 desselecionado, 5 warnings (20 s) |
| HEAD limpo (`git archive HEAD` em `/tmp/se/head`) | 6 falhas, 378 passaram (a suíte do HEAD não tem os testes novos não rastreados) |

Falhas **novas no working tree** (passam no HEAD, falham agora): todas por tuning de balanceamento não refletido nos testes (diffs em `yellow_ninja.py`, `blue_samurai.py`, `ichi.py`, `voxel_corpse.py`):

| Teste | Causa raiz |
|---|---|
| `test_hanzo_overhaul::test_hanzo_two_step_combo` | `yellow_ninja.py:145` `hitbox_damage` 1 -> 2; o teste espera 1 |
| `test_ichi_overhaul::test_02_primary_gyaku_iai`, `::test_05_cane_tap_slip_dodge` | `attack_duration` 0.11 -> 0.22, `invincible_timer` 0.22 -> 0.25 |
| `test_musashi_overhaul::test_musashi_three_step_combo` | `state_timer` do combo 0.18 -> 0.26/0.28/0.32; o teste avança 0.19 s |
| `test_musashi_overhaul::test_musashi_3hp_survives_single_kunai` | dano/HP de Musashi mudou (ficou com 2 HP, esperava 1) |
| `test_valerius_overhaul::test_08_soul_reap_...` | `voxel_corpse.py` (SOUL_REAP) agora não cria `severed_head`; teste espera a cabeça |

Falhas que **já existem no HEAD** (não são regressões do working tree): `test_gameplay_adjustments_cycle6::test_item4_seimei_finisher_no_residual_body`, `test_musashi_overhaul::test_musashi_cross_guard_and_shockwave` (`parry_reflect_active_timer` 0.0 em vez de 0.28), `test_projectile_dodge_immunity` (2), `test_seimei_overhaul::test_02_seimei_ofuda_toss_and_obstacle_block` (nenhum projétil gerado). No HEAD também falhou `test_fase3_extreme_arenas::test_7_rendering_performance_all_extreme_arenas` (teste de desempenho, sensível à carga da máquina).
Triagem necessária: para cada item, decidir se o teste está obsoleto ou se é regressão real (Valerius SOUL_REAP e Seimei ofuda merecem olhar humano; no e2e não vi crash em nenhum deles).

### 1.3 Flaky e efeitos colaterais

- `test_arena_balance_friction::test_5_dohyo_sumo_ring_out_resolution` falhou numa execução e passou nas outras 4: usa `simulate_single_battle` com `random` sem semente (assert `duration < 10.0`). Flaky por RNG.
- Testes isolados falham por dependência de ordem: `test_finisher_and_stance_fixes` (2 testes: `pygame.error: font not initialized`) passa na suíte completa e falha quando o arquivo roda sozinho.
- **A suíte regrava os arquivos reais do repo** (`settings.json`, `controls_config.json`, `arcade_save.json`, todos no .gitignore): mtime 15:16 = minhas execuções. `arcade_save.json` atual é idêntico a `/tmp/arcade_save.bak` (sem perda). O relatório 02 já havia notado o mesmo para `settings.json`. **Não rode os testes na pasta que vai virar release** e confira esses 3 arquivos antes do empacotamento (o `.spec` só copia `assets/`, então não vão para o bundle).
- Warnings: 3x `ResourceWarning: unclosed file main.py` (`open(...).read()` sem `with` em 3 testes) e 2x `UserWarning: system font 'sans-serif' couldn't be found` (cai na fonte default; no Steam Deck/SteamOS a fonte também pode faltar).

---

## 2. Bloqueador

### B1. `UnboundLocalError` ao disparar os morteiros de `mist_temple`

- **Onde:** `src/world/hazards.py:443` (`particles.append(SmokeParticle(...))` em `FireworkMortars.on_phase`, fase ACTIVE) e `:462` (`from src.effects.particles import BloodParticle, SmokeParticle, SparkParticle` dentro do mesmo método). Como o `import` está dentro da função, `SmokeParticle` vira variável local de **todo** o método e a linha 443 levanta `UnboundLocalError` antes de o import executar. Código do import em `:462` é **não commitado** (`git diff HEAD -- src/world/hazards.py`).
- **Traceback** (`python /tmp/se/repro_mortar.py`, 30 s simulados sem nenhum lutador atacando):
  ```
  File ".../src/world/hazards.py", line 395, in update
  File ".../src/world/hazards.py", line 48, in update
  File ".../src/world/hazards.py", line 39, in _set_phase
  File ".../src/world/hazards.py", line 443, in on_phase
      particles.append(SmokeParticle(cx, cy, wz=0.5, color=(190, 184, 200), radius=0.4, lifetime=0.9))
  UnboundLocalError: cannot access local variable 'SmokeParticle' where it is not associated with a value
  ```
- **Quando:** na primeira salva de morteiros: `initial_delay 4.0 s + warn_time 1.9 s` = **~5,9 s depois da criação da arena** (já inclui a introdução do round), com ou sem lutadores atingidos. É 100% determinístico; o `main.run_game` não tem `try/except` em volta de `game_map.update` (confirmado também pelo coordenador no loop real).
- **Alcance:** Versus em `mist_temple` (arena da Kasumi); "Arena Aleatória" (1/24 = 4,2% dos sorteios); Arcade: calculei 4800 runs simulados (24 lutadores x 200 sementes) com `build_ladder`: 200 contêm `mist_temple` (4,2%), **todos e somente quando o jogador é a Kasumi** (luta-espelho nº 9). Ou seja, **todo run de Arcade com a Kasumi crasha na luta 9**. O relatório 01 já contou 20/552 duelos simulados com erro, todos nesta arena.
- **Varredura de irmãos:** `scan_shadow.py`/`scan_shadow2.py` (AST: nomes importados localmente e usados antes/fora do import) e `pyflakes` sobre `main.py` + `src/**`: nenhum outro caso real. (`projectile.py:509` e os `SoundEvent` de `cinematic_director.update` parecem suspeitos mas são protegidos por `if banners is not None` / `if sm:`. Os 4 avisos de `t` sombreado em `hazards.py:987/1015/1380/1389` são falso alarme: nenhum `t(...)` é chamado nesses escopos.)
- **Correção:** remover `SmokeParticle` da linha 462 (já é importado no topo, `hazards.py:7`) ou mover o import para o topo do método. Adicionar teste que avança `FireworkMortars` até ACTIVE com `particles=[]`.

---

## 3. Altos

### A1. Botão "PERSONALIZAR BOTÕES TOUCH (HUD)" derruba o jogo

- `src/ui/settings_menu.py:822`: `self.touch_editor.render(surface)`; mas `TouchControlsEditorScreen.render(self, surface, font_large, font_small)` (`src/input/touch_editor.py:162`) exige as duas fontes. O botão aparece em Opções > Controles quando há `touch_controls` (sempre, `main.py` passa `TouchControls()`), `settings_menu.py:150, 1304-1308` (e `:1471` no layout mobile); o clique abre o editor em `:761-762` e o **próximo render** levanta `TypeError`. Linha do HEAD (`f1a1a3af`), não é do working tree.
- **Repro determinístico:** `python /tmp/se/repro_touch_editor.py` ->
  `TypeError: TouchControlsEditorScreen.render() missing 2 required positional arguments: 'font_large' and 'font_small'`
  Também reproduzido pelo monkey test ponta a ponta (seed 1, frame ~225), dentro de `main.run_game` (`main.py:1490`).
- Alcance: só com mouse/trackpad (Steam Deck: trackpad e tela touch), não via teclado/gamepad. O rótulo do botão é texto fixo em PT (também fora do i18n).
- **Correção:** `self.touch_editor.render(surface, font_large, font_small)`.

### A2. Mapeamento de gamepad assume o layout do macOS/HIDAPI (Steam Deck / Linux)

Análise estática (não há hardware aqui). O jogo usa a API de joystick crua (`pygame.joystick`), com índices de botão do SDL GameController (`controller_manager.py:49-65`: 4=Back, 5=Guide, 6=Start, 9=LB, 10=RB, 11-14=D-pad). No Linux, o Steam Input expõe um gamepad virtual Xbox 360 (evdev), cujo layout cru é 0=A 1=B 2=X 3=Y **4=LB 5=RB** 6=Back **7=Start** 8=Guide 9=L3 10=R3, com D-pad em hat.
Consequências prováveis no Deck (a confirmar em hardware, e dependente de o jogo rodar com ou sem Steam Input):
- **Tela de título:** `title_screen.py:109-111`: botões 4 e 5 = `"QUIT"`. No layout evdev são LB/RB: apertar um bumper no título **fecha o jogo** (o monkey test fechou o jogo assim, via evento sintético `JOYBUTTONDOWN` 4/5).
- **Pausa:** `get_default_action_buttons` (Xbox, `controller_manager.py:484-`) mapeia MENU = [10, 8, 6]; em evdev 10 é R3 (excluído por colidir com ATTACK), 8 é o botão Steam (capturado pelo Steam), 6 é View/Back. O botão **Start/Menu (7) não pausa**.
- Os botões de ação (A/B/X/Y) coincidem nos dois layouts; LB/RB (dash/ataque) acabam coerentes por acaso.
- **Recomendação:** usar `pygame._sdl2.controller` (SDL GameController, que normaliza o layout) ou detectar o layout pelo GUID; tirar o QUIT dos botões 4/5 (ou exigir confirmação). Testar com e sem Steam Input.

### A3. Escrita de saves/config na pasta do jogo (Linux/Steam, AppImage, macOS)

- Caminhos derivados de `__file__`/`BASE_DIR`: `arcade_save.py:12`, `quality.py:216`, `controls_storage.py:11-12`, `versus_config.py:22`, `i18n.py:15-21`. Em PyInstaller onedir isso vira `<instalação>/_internal/`.
- Steam/SteamOS: normalmente gravável, mas o diretório pertence ao depot (atualização/verificação pode apagar `_internal` e levar os saves junto). AppImage/Flatpak: read-only -> `arcade_save.save()` devolve `False` (testei a tolerância: não crasha) mas **`main.py:1201-1204` ignora o retorno**: o jogador perde o progresso sem aviso. macOS: gravar dentro do `.app` quebra assinatura/notarização e, com App Translocation, a pasta é read-only.
- **Recomendação:** `SDL_GetPrefPath`-equivalente (`pygame.system.get_pref_path("SamuraiEdge","SamuraiEdge")` no pygame-ce 2.5, ou `$XDG_DATA_HOME/SamuraiEdge`, `~/Library/Application Support`, `%APPDATA%`), com migração do arquivo antigo se existir. Testei também `RUN_CWD=/`: executar de outro diretório funciona (todos os caminhos vêm de `__file__`).

### A4. (ver §1.1) `os._exit(0)` em teste mascara a suíte. A5 abaixo.

### A5. `.app` do Mac é detectado como iOS

`main.py:41-50` e `controller_manager.py:16-24`: `".app" in bundle_path` é verdadeiro para `.../SamuraiEdge.app/Contents/...` (verifiquei a função com caminhos de exemplo: `True` para `/Applications/SamuraiEdge.app/Contents/Resources`, `False` para a pasta de dev e para `.../steamapps/common/...`). Num `.app` empacotado isso pula o bloco macOS que seta `SDL_JOYSTICK_IOKIT=0` (justamente a proteção contra o crash do `__IOHIDManagerInitialEnumCallback` no macOS 26+) e faz `ControllerDevice.invert_y` nascer `True` (`controller_manager.py:154`) além de trocar os botões padrão do PlayStation (`[2,5,10]`). **Não testei o `.app` empacotado**; é conclusão de leitura de código. No Linux o risco é só um caminho de instalação contendo ".app" (raro).
Correção: usar `sys.platform == "ios"` ou `sys.platform == "darwin" and "/private/var/containers/Bundle/Application" in path`.

---

## 4. Médios

### M1. `controls_config.json` válido em JSON mas com tipos errados = crash em toda inicialização
Teste `corrupt.py` (74 variações; cada uma sobe `main.run_game` até o título e entra em Arcade/Opções; 69 passaram):
```
main.py:1015  controls[k] = int(v)
ValueError: invalid literal for int() with base 10: 'abc'      # keyboard.P1_UP = "abc"
TypeError : int() argument must be ... not 'NoneType' / 'list'  # null / [1]
sound_manager.py:385  self.master_volume = max(0.0, min(1.0, vol))
TypeError: '<' not supported between instances of 'str' and 'float'  # audio.master = "loud" / null (chamado em main.py:1386-1388)
```
Persiste até apagar o arquivo (o jogo nunca chega a regravá-lo). Casos aceitos sem crash: arquivo ausente/vazio/truncado/binário, raiz `[]`/`null`/string, `keyboard` lista, valores numéricos absurdos (-5, 1.5, 1e999, NaN, 10^20), `controllers` com tipos errados, `touch_mode`/`ai_difficulty` inválidos, versão antiga. Em `settings.json` (18 variações) e `arcade_save.json` (26 variações, incluindo `current_run` com campos inválidos, versão 0/futura, diretório no lugar do arquivo): **nenhum crash**.
Probabilidade baixa (precisa de edição manual ou corrupção parcial que mantenha o JSON válido). Correção: `try/except (TypeError, ValueError)` por chave em `main.py:1013-1015` e coerção `float()` com fallback nos setters de volume.
Detalhes menores no mesmo tema: `quality.save_video_setting` (`quality.py:198`) levanta `TypeError` se `video` não for dict (só captura `OSError`); `ArcadeRun.from_dict` com `"index": Infinity` (JSON aceita) levanta `OverflowError`, fora do `except (ValueError, KeyError, TypeError)` de `main.py` (fuzz de 20 mil dicts: 523 `OverflowError`, nenhuma outra exceção não tratada).

### M2. `SoundManager.play()` não protege a geração/uso do som
`sound_manager.py:137` (`generate_procedural_sound`) e `:163-172` (`set_volume`) estão fora de qualquer `try`; só `sound.play()` é protegido. Com `FAIL_MIXER=2` (mixer inicia, mas `pygame.mixer.Sound(...)` falha) o jogo morre no primeiro finisher:
```
cinematic_director.py:496 get_sound_manager().play(SoundEvent.HEARTBEAT)
sound_manager.py:137  generate_procedural_sound(event) -> procedural_sfx.py:72 pygame.mixer.Sound(buf)
pygame.error: simulated sound load failure
```
Cenário real: queda/troca do dispositivo de áudio (fone Bluetooth, suspend/resume do Deck) com `ensure_mixer_ready()` reinicializando o mixer e deixando `Sound` antigos no cache. `mixer.init` falhando de vez (`FAIL_MIXER=1`) e `SDL_AUDIODRIVER=dummy` funcionam sem problema (4 duelos completos). Correção: `try/except pygame.error` em volta do corpo de `play()`/`get_sound()` e invalidar `_sfx_cache`/`_pitch_pool` quando o mixer for reinicializado.

### M3. Android: `numpy` ausente em `buildozer.spec`
`buildozer.spec:32` `requirements = python3,pygame-ce`, mas `numpy` é import de módulo (sem proteção) em `src/ui/match_intro.py:15`, `effects/parchment.py:16`, `effects/fog.py:15`, `effects/lighting.py:18`, `entities/voxel_corpse.py:12` e `audio/sound_manager.py:93` (este protegido). O APK falharia com `ImportError` na inicialização. Também faltam `svg` em `source.include_exts` (há 8 SVG em `assets/`). Não tentei o build Android.

### M4. Memória e travadas (informativo)
Soak de 5000 frames (IA x IA, 14 e 17 rounds, 2 arenas): RSS oscila em dente de serra 330 a 980 MB (o cache de arena é recriado a cada round; sem tendência de alta), objetos Python 35k -> 47k em 5000 frames no primeiro soak (listas de partículas/projéteis/banners/corpos sempre voltam a 0) e **+565 objetos** no segundo (Raiden x Hendrika, dohyo). Não há vazamento linear relevante; pico ~1 GB por partida é alto para PCs fracos. Travadas de 1 a 4,6 s apareceram em transições (criação de arena/primeiro uso de cache) mas sob carga extrema da máquina; **inconclusivo** sem a máquina ociosa.

---

## 5. Baixos / latentes

- **L1. `camera` indefinido no finisher `EARTH_STOMP_CRUSH`** (`src/effects/cinematic_director.py:2178-2179`, `update(self, dt, game_map, particles)` não tem `camera`; código **não commitado**). Repro: `python /tmp/se/repro_stomp.py` -> `NameError: name 'camera' is not defined` no frame 64. Varredura de finishers (`t_finisher.py`, 56 estilos, 141 pares atacante/estilo, 1128 sequências com update+render): **é a única falha** (8/8 vítimas da Goro). Alcance hoje: `_get_death_style_for_attacker` só devolve esse estilo se a Goro tiver `state == "EARTH_STOMP"` no momento do golpe fatal com hitbox ativa, e o pisotão não ativa hitbox; em ~50 mortes provocadas pela Goro (IA x IA e kills forçados pelo pisotão) o estilo nunca disparou (o kill por onda de choque não chama `trigger_fatal_strike`). Latente; corrigir antes que alguma mudança de balanceamento o ative (ex.: guardar `camera` em `self` no início do finisher).
- **L2. Erros engolidos:** não há `except:` sem tipo; há **154 `except Exception: ... pass` de 225** `except Exception` em `main.py` + `src/` (`grep -A1`). Defensivo, mas esconde falhas reais (o bug do botão touch, por exemplo, não estava coberto por nenhum).
- **L3. Saída:** `ESC` no título fecha o jogo sem confirmação (`main.py:1498`); o loop termina em `os._exit(0)` (`main.py:3074`). No Arcade, `Enter` no cartão de dificuldade padrão **inicia um run novo e sobrescreve o run salvo** sem confirmação (o cartão "continuar" é o primeiro, mas a seleção inicial é a dificuldade; `main.py:1573`, `arcade_screens.py:121-123`).
- **L4. Fontes:** se `assets/fonts` faltar, cai em `pygame.font.Font(None)` sem glifos CJK (kanji viram quadrados), sem crash (`ui/fonts.py`).
- **L5. Vídeo de abertura/créditos:** `OpeningVideoScreen` e `ArcadeCreditsScreen` só abrem vídeo quando `SDL_VIDEODRIVER != "dummy"`; em headless sempre pulam. Testei em processo à parte trocando a variável de ambiente depois do init: com pyvidplayer2/cv2/imageio-ffmpeg/sounddevice presentes, bloqueados um a um e todos juntos, arquivo inexistente e MP4 corrompido (`/dev/urandom`): **sem exceção** (cai para pular a abertura / slides nos créditos). Só validei inicialização, skip e fallback; **não validei a reprodução visual/sonora**.

---

## 6. O que foi executado (item 2) e resultado

Harness próprio (`03_scripts/drv.py`): importa `main.py` (cópia numa sandbox em `/tmp/se/play_*` com symlinks para `src/` e `assets/`, para que **nenhum save real fosse tocado**), troca `pygame.time.Clock` por relógio falso (dt fixo ou aleatório, sem dormir), injeta `pygame.event.get`/`key.get_pressed` sintéticos e lê o estado de `run_game` pelo frame (`game_state`, `p1`, `p2`, `round_winner`, ...). Roda o **loop real** (update + draw reais em 1280x720).

| Teste | Cobertura | Resultado |
|---|---|---|
| Monkey (`e2e_monkey.py`) | 5 seeds (~6k a 12k frames cada; o jogo é fechado quando o monkey aperta Sair) + 1 seed com Galeria desbloqueada: teclado (+mods), mouse/roda, gamepad (botão/hat/eixo incl. NaN, device add/remove), toque, `VIDEORESIZE` (1x1, 0x0, 4K...), foco, `dt` em {0,1,8,16,33,50,100,250,1000} ms; telas: título, Versus, seleção de lutador/arena, Arcade (dificuldade, seleção, chaves), duelo, pausa, Opções, Galeria | **1 crash (A1)**; depois do contorno, 0 crashes e 0 soft-locks em ~65 mil frames. Visitados: todas as telas acima exceto vídeo de abertura e créditos (cobertos à parte) |
| Arcade completo (`e2e_arcade.py`) | Kenshin, 12 lutas (duelos BO3, espelho, endurance, Desafio Ninja com 4 oponentes, **chefe Oni**), derrotas/Continue, salvamento a cada luta, créditos (segurar Enter 1 s), resultado, recordes e desbloqueio da Galeria; retomada de run salvo (`ARC_RESUME=1`: voltou na luta 3 com a dificuldade salva) | Sem crash nem soft-lock (12945 frames; o "soft-lock suspeito" nos créditos foi falha do meu script, que não segurava a tecla) |
| Chefe Oni (`ARC_START=boss`) | Konami code, luta real com 5 fases até a morte do chefe, créditos, resultado | OK com Kenshin. **Só 1 lutador testado contra o chefe** (o lote de 24 não foi executado, ver §8) |
| Matriz de partidas (`e2e_matches.py`/`matrix.py`) | Quadrado latino: para cada arena, 24 pares (cada lutador 1x como P1 e 1x como P2), alternando IA x IA ("watch") e P1 humano com teclado aleatório; KO forçado (`hp=1`) na metade; finishers, vitória, rounds seguintes | **59 duelos executados** (`bamboo` 24/24, `kyoto` 24/24, `ganryu_island` 11/24; os 24 lutadores apareceram como P1 e como P2; 30 IA x IA + 29 P1 humano): 59 KOs, **0 crashes, 0 NaN/inf, 0 soft-locks** (nenhum round travou: todos terminaram com `round_winner` e avançaram). Interrompi a matriz por pedido do coordenador |
| Sobreposição (distância 0) | 24 duelos em `bamboo` com P2 teleportado para a mesma posição do P1 a cada 2 frames (`OVERLAP=1`), cobrindo IA, combate e finishers | 0 crashes, 0 NaN |
| Perigos/arenas (`t_hazards.py`) | **25 arenas** (24 + a do chefe) x 150 s simulados, 2 lutadores errantes, quedas em buracos (até 36 por arena), render de terreno/props/perigos/overhead/iluminação/névoa | só `mist_temple` falha (**B1**); 0 NaN |
| Finishers (`t_finisher.py`) | 56 estilos x 141 pares atacante/estilo x 8 vítimas = 1128 sequências completas com render | só **L1** |
| Soak (`e2e_soak.py`) | 2 x 5000 frames IA x IA com reinício automático (31 rounds), amostragem de RSS/listas/objetos | sem vazamento (ver M4) |
| Arquivos corrompidos (`corrupt.py`) | 28 de `controls_config.json`, 18 de `settings.json`, 26 de `arcade_save.json` (vazio, truncado, binário, tipos errados, versões, diretório no lugar do arquivo) | 5 falhas = **M1** |
| Áudio | `SDL_AUDIODRIVER=dummy` (todo o resto); `mixer.init` levantando erro (4 duelos); `Sound`/`music.load` falhando | OK / OK / **M2** |
| Assets ausentes | removidos (um por vez) `fonts`, `portraits`, `sprites`, `ui`, `icons`, `concepts`, `sounds`, `design`, e **todo `assets/`**; Arcade/créditos sem `design`, `concepts`, `ui`, `Opening Videos`, `icons` | 0 crashes (jogo usa fontes default e áudio procedural) |
| Dependências opcionais | cv2, pyvidplayer2, imageio_ffmpeg, sounddevice bloqueados via `sys.modules[...] = None`; vídeo ausente/corrompido | OK (ver L5). `numpy` é obrigatório (declarado em `requirements.txt`) |
| Idioma em runtime / resize | troca PT/EN coberta pelo monkey (menus) e `tests`; `DisplayScaler` testado com 14 tamanhos (1x1, 0x0, 1280x800, 4K) | OK. Fullscreen real não é exercitável em dummy |
| Execução fora do diretório | `RUN_CWD=/` | OK |

Análise estática dirigida (item 3): sem recursão direta em `main.py`/`src/`; único `while True` (`arena_select.py:345`) termina; `pick_spawns` tem `fallback`; divisões por distância estão quase todas protegidas (`dist < 0.001`, `max(...)`, `or 1.0`), e o teste de sobreposição não achou exceção; `i18n.t()` nunca levanta (fallback para PT/chave); import de `cv2`/`sounddevice`/`pyvidplayer2`/`imageio_ffmpeg` está protegido (`video_utils.py`, `opening_video.py`, `arcade_credits.py:548-551`).

---

## 7. Linux / Steam Deck (item 4)

- **Resolução:** lógica 1280x720 com letterbox; em 1280x800 o `DisplayScaler` usa escala 1.0 com barras de 40 px (testado). Sem crash em nenhum tamanho de janela. O jogo abre `RESIZABLE` e alterna fullscreen por F11/Ctrl+F (`main.py:975-988`, protegido por `try`), sem opção de iniciar em tela cheia.
- **Código específico de macOS:** protegido por `sys.platform` (`i18n.py:107`, `quality.py:33`, `settings_menu.py:259`, env do joystick). `Launch_Menu.command`/`Play_Game.command` são só do Mac. `pygame.font.match_font("Trebuchet MS")` (`arcade_credits.py:366`) cai na fonte do jogo se não existir (não testado em Linux). Detecção de idioma usa `LANG`/`LC_*` em Linux (não lê o idioma do Steam).
- **Gamepad:** ver **A2**. **Escrita:** ver **A3**.
- **Empacotamento:** `samurai_edge.spec` é onedir, `console=False`, `excludes=['unittest','tkinter']` (nenhum import de `unittest` em `src/`); precisa ser gerado **em Linux** (PyInstaller não cruza SO) e o `imageio_ffmpeg` entra como binário em `imageio_ffmpeg/binaries`. `assets/` pesa 1,2 GB (o `.spec` já exclui `promotional`, 710 MB); `concepts` (270 MB) e `Opening Videos` (128 MB) entram. Não gerei o bundle.
- **Desempenho:** render 100% em CPU (software); o `quality.update_fps_governor` baixa a qualidade abaixo de 48 FPS. Não medi FPS em x86_64/Deck (máquina carregada); recomendo medir no hardware-alvo.

---

## 8. O que NÃO foi coberto (honestidade)

- **Matriz completa 24 lutadores x 24 arenas (576 duelos):** só **59 dos 576** duelos rodaram (`bamboo` 24/24, `kyoto` 24/24, `ganryu_island` 11/24; as outras 21 arenas e a arena do chefe ficaram sem duelo completo no harness). O fluxo é o mesmo para qualquer arena, e as arenas foram cobertas à parte por `t_hazards.py` (todas, 150 s) e os lutadores por `t_finisher.py` (todos), mas **combinações específicas lutador x arena x lutador não rodadas podem esconder crashes**.
- **Chefe Oni com os outros 23 lutadores:** não executado (`boss_batch.sh` estava na fila e foi cancelado). Só Kenshin.
- **Hardware real:** janela/GPU/Wayland/X11, fullscreen, gamepads reais (Steam Input, DualSense, Xbox), dispositivo de áudio real, toque real, reprodução visual de vídeo. Tudo com SDL `dummy`.
- **Plataformas:** nada foi executado em Linux, SteamOS, Windows, Android ou iOS; PyInstaller/buildozer não foram rodados; o `.app` não foi aberto.
- **Desempenho/FPS e travadas:** medições inválidas (máquina com load average até 50).
- **Qualidade visual** dos frames renderizados não foi inspecionada (só ausência de exceção).
- Partidas P1 x P2 humanos em dois teclados e 2 gamepads simultâneos só via eventos sintéticos do monkey.
- O contorno aplicado no harness (monkeypatch de `FireworkMortars.on_phase` e `TouchControlsEditorScreen.render`, via `WORKAROUNDS=1`) foi usado **apenas** depois de reproduzir B1/A1 e para permitir que o monkey/matriz encontrassem outros problemas; os achados B1/A1 estão reproduzidos sem contorno.

---

## 9. Ordem de correção sugerida

1. **B1** (remover o import local de `SmokeParticle`, `hazards.py:462`) e **A1** (`settings_menu.py:822`): 2 linhas, bloqueiam o release.
2. **A4** (`os._exit` nos testes) e triagem das 11 falhas; só então rodar o CI de verdade.
3. **A3** (diretório de usuário para saves/config) e checagem de `arcade_save.save()` (avisar o jogador quando falhar).
4. **A2** (layout de gamepad / QUIT em LB-RB) com um teste num Steam Deck real; **A5** se houver build `.app`.
5. **M1, M2, M3, L1**.
