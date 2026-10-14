# Feedback de Melhorias — Priorização & Roadmap

**Date:** 2026-10-01  
**User Feedback:** Detalhado com 10 pontos críticos

---

## 🎯 CRÍTICOS (FASE 1) — Afetam experiência principal

### 1. Loading Screen
**Problema:** Artefatos visuais, texto amarelo com highlight amarelo (ilegível)  
**Solução:** Revisar renderização de texto, aplicar cores contrastantes (preto/nanquim)  
**Arquivo:** `src/ui/loading.py`  
**Tempo Est.:** 20 min

### 2. Title Screen & Main Menu Visuais
**Problema:** Menu minúsculo, sem ornamentação, sem transparência. Cores verde escuro + amarelo gritante  
**Esperado:** Placa dourada oriental, fonte caligrafia, cores pergaminho + nanquim  
**Solução:**
- Aumentar tamanho menu
- Aplicar ornate frame (PanelRenderer ORNATE_FRAME ou LACQUER_PANEL)
- Trocar cores para paleta suave
- Adicionar transparência (ink-wash background)
- Fonte mais elegante (serif/brush style)
**Arquivo:** `src/ui/main_menu_enhanced.py`  
**Tempo Est.:** 45 min

### 3. Settings Menu Visual
**Problema:** Cores ruins, overlap de textos, fonte quadrada  
**Solução:** Aplicar mesma paleta suave + melhor espaçamento  
**Arquivo:** `src/ui/settings_menu_enhanced.py`  
**Tempo Est.:** 30 min

### 4. Opening Video Skip Button
**Problema:** Mostra "Start/" + espaço branco (SVG não aparece)  
**Esperado:** Usar SVG dos botões PlayStation (como no menu de opções)  
**Arquivo:** Procurar onde é renderizado o texto "Start/" + aplicar SVG  
**Tempo Est.:** 15 min

### 5. Localização Incompleta
**Problema:** Não aplicada em:
  - Descrições de ações dos personagens (skills)
  - Seleção de cenários (arena select)
**Solução:** Adicionar chaves i18n às descrições + aplicar t()  
**Arquivos:** `src/entities/fighters.py`, `src/ui/arena_select.py` (se existir)  
**Tempo Est.:** 25 min

---

## ⚠️ IMPORTANTES (FASE 2) — Afetam gameplay

### 6. Balanceamento: Kenshin vs Musashi
**Problema:** Musashi invencível contra Kenshin  
- Kenshin ataca, congela após iai
- Musashi tem tempo infinito para cadeado + vencer
**Solução:** Uma das duas:
  - Opção A: Adicionar stun breve a Kenshin após iai (0.3-0.5s)
  - Opção B: Knockback automático para fora do alcance combo
**Avaliação necessária:** Testar ambas as opções  
**Arquivo:** `src/combat/moves.py` ou `src/entities/fighters.py`  
**Tempo Est.:** 40 min (implementação + testes)

### 7. UI/UX: Modo de Jogo Submenu
**Problema:** Botões 1P vs IA/2P (treino/dificuldade) na mesma tela de seleção  
**Esperado:** Submenu ANTES de character select (deixa tela mais limpa)  
**Solução:** Adicionar nova tela: MAIN_MENU → MODE_SELECT → CHARACTER_SELECT  
**Arquivo:** `main.py`, criar `src/ui/mode_select.py`  
**Tempo Est.:** 30 min

### 8. Game Guide Button
**Problema:** Texto completo (toma espaço)  
**Esperado:** Apenas "?" arredondado, clicável  
**Arquivo:** `src/ui/character_select.py`  
**Tempo Est.:** 10 min

---

## 📍 MÉDIA PRIORIDADE (FASE 3) — Melhorias de UX

### 9. Kyoto Arena: Delay de Efeitos
**Problema:** Carruagens e escombros começam imediatamente  
**Esperado:** Aguardar 3-5 segundos antes de iniciar  
**Arquivo:** `src/world/arenas.py` ou arena logic  
**Tempo Est.:** 15 min

### 10. Arena Select Localização
**Problema:** Não tem i18n  
**Solução:** Adicionar chaves para nomes e descrições de cenários  
**Arquivo:** `src/ui/arena_select.py`  
**Tempo Est.:** 15 min

---

## 📊 RESUMO PRIORIZAÇÃO

| Fase | Categoria | Problemas | Est. Tempo | Impacto |
|------|-----------|-----------|-----------|---------|
| **1** | CRÍTICOS | 1,2,3,4,5 | ~2h 15m | ⭐⭐⭐⭐⭐ |
| **2** | GAMEPLAY/UX | 6,7,8 | ~1h 20m | ⭐⭐⭐⭐ |
| **3** | POLIMENTO | 9,10 | ~30m | ⭐⭐⭐ |

**Total Estimado:** ~4 horas

---

## 🎨 Mudanças de Cor Propostas

**ATUAL (Ruim):**
- Verde escuro (#2d5016) + Amarelo gritante (#ffff00)

**NOVO (Suave):**
- Pergaminho: #d4c5a0 ou #c9baa0 (bege quente)
- Nanquim: #1a1a1a ou #2a2620 (preto/marrom escuro)
- Acentos: #c9a961 ou #b8860b (ouro suave)
- Transparência: 80-90% opacity para overlays

---

## 🔄 Recomendação de Execução

**Começar por:** FASE 1 (críticos) → FASE 2 (gameplay) → FASE 3 (polimento)

**Ordem sugerida:**
1. ✅ Loading screen (20 min) — quick win
2. ✅ Title + Main menu cores + ornamentação (45 min)
3. ✅ Settings menu (30 min)
4. ✅ Opening video SVG (15 min)
5. ✅ Localização (25 min)
6. ✅ Kenshin vs Musashi balance (40 min) — precisa testes
7. ✅ Mode select submenu (30 min)
8. ✅ Game guide "?" button (10 min)
9. ✅ Kyoto delay (15 min)
10. ✅ Arena select i18n (15 min)

---

## ❓ DÚVIDAS PARA VOCÊ

Antes de começar:

1. **Fase 1 (Críticos):** Fazer tudo de uma vez? (recomendado)
2. **Kenshin Balance:** Prefere STUN ou KNOCKBACK?
3. **Colors:** Aceita a paleta pergaminho/nanquim proposta?
4. **Mode Select:** Quer apenas EASY/NORMAL/HARD ou também inclui 1P vs 2P ali?

---

**Status:** PRONTO PARA INICIAR FASE 1

Pode confirmar e começamos com loading screen + title/menu?
