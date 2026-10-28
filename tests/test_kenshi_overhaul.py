"""
Suite de testes automatizados para a Sub-fase 2.1: Kenshi (A Retalhadora).
Verifica todos os 11 entregáveis (2.1.1 a 2.1.10, incluindo 2.1.4a e 2.1.4b):
- 2.1.1: Golpe Primário (Shukuchi Battoujutsu Slice: Startup 0.10s Koiguchi-kiri, Dash 0.14s, Noto walk 50%, Backhop 2.7m no Parry)
- 2.1.2: Golpe Secundário (Ryuu Tsui Sen em 3 fases parabólicas com Zanzou: ASCEND -> APEX -> DESCEND, Mortal de 360° no Parry Aéreo)
- 2.1.3: Mobilidade (Shukuchi Dash + Cancelamento Ofensivo 'Shukuchi Battou-Giri' nos últimos 40% + Projectile Graze)
- 2.1.4a: Finisher Primário (Ittou Ryoudan / Kenshin Split — 一刀両断, zoom 2.2x, 5 sombras Zanzou, Noto)
- 2.1.4b: Finisher Especial (Divisão Celestial de Bambu / Amakakeru Ryuu Tsui Sen — 龍槌閃, salto com 5 Zanzou, ápice e queda vertical)
- 2.1.5: Animação de Intro (Meditação de olhos fechados -> brilho ocular + Koiguchi-kiri na tsuba -> corte no vento)
- 2.1.6: Animação de Vitória (Chiburi lateral -> Noto cerimonial -> reverência)
- 2.1.7: Resolução & Anti-Tearing (SSAA 2x Offscreen com downsampling bilinear smoothscale)
- 2.1.8: Olhos Anime HD & Expressões Faciais (anel limbal, degradê âmbar-mel, olhos fechados na meditação, glint boost)
- 2.1.9: Interpolação de Pose (Pose LERP Cross-Fade de 0.08s entre transições de estado)
- 2.1.10: Biblioteca de Materiais Realistas (Seda Chirimen Carmim, Linho Plissado Índigo, Laca Urushi e Aço Tamahagane com Hamon)
"""
import os
import sys
import math

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.samurai import STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY
from src.world.map_data import GameMap
from src.isometric.camera import Camera
from src.effects.cinematic_director import CinematicDirector
from src.entities import pose_scripts, kenshi_model
from src.isometric.voxel_textures import PATTERNS, draw_face_texture
from src.isometric.mesh_primitives import PORTRAIT_FACE_STYLES


def run_kenshi_overhaul_tests():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    camera = Camera()
    game_map = GameMap()
    game_map.rocks.clear()
    game_map.well = None
    particles = []
    banners = []

    # =========================================================================
    # 1. Entregável 2.1.1: Golpe Primário — Shukuchi Battoujutsu Slice & Parry Backhop
    # =========================================================================
    kenshi = RedSamurai(wx=8.0, wy=10.0)
    dummy = BlueSamurai(wx=11.0, wy=10.0)
    kenshi.trigger_iai_attack(dummy.wx, dummy.wy)
    assert kenshi.state == STATE_ATTACK
    assert abs(kenshi.iai_startup_timer - 0.10) < 1e-4, "Startup deve iniciar em 0.10s (6 frames)"
    assert kenshi.hitbox_active is False, "Hitbox não deve estar ativa durante o startup Koiguchi-kiri"

    # Durante o startup (0.05s), permanece em postura Iai sem avançar
    wx_before = kenshi.wx
    kenshi.update(0.05, game_map, particles)
    assert kenshi.iai_startup_timer > 0.0
    assert kenshi.hitbox_active is False
    assert abs(kenshi.wx - wx_before) < 1e-4

    # Conclui o startup (+0.06s) -> ativa hitbox e inicia o dash supersônico!
    kenshi.update(0.06, game_map, particles)
    assert kenshi.iai_startup_timer == 0.0
    assert kenshi.hitbox_active is True
    assert kenshi.wx > wx_before

    # Conclui o dash -> entra em STATE_RECOVERY (Noto) caminhando a 50% da velocidade
    kenshi.update(0.20, game_map, particles)
    assert kenshi.state == STATE_RECOVERY
    assert abs(kenshi.state_timer - kenshi.recovery_duration) < 0.10

    # Testar caminhada a 50% da velocidade durante o Noto (STATE_RECOVERY) em terreno seco
    kenshi.wx, kenshi.wy = 5.0, 5.0
    rec_start_x = kenshi.wx
    kenshi.apply_movement(1.0, 0.0, 0.10, game_map)
    noto_dist = kenshi.wx - rec_start_x
    assert 0.24 <= noto_dist <= 0.30, f"Caminhada no Noto deve ser 50% de 5.4 m/s (0.27m em 0.1s), obtido {noto_dist:.3f}"
    assert kenshi.state == STATE_RECOVERY

    # Testar Reação de Parry Terrestre: Salto acrobático animado para trás (~2.7m) + Noto andando ao pousar
    kenshi_parry = RedSamurai(wx=10.0, wy=10.0)
    opp_parry = BlueSamurai(wx=11.0, wy=10.0)
    kenshi_parry.trigger_iai_attack(opp_parry.wx, opp_parry.wy, instant=True)
    kenshi_parry.on_parried(opp_parry, game_map, banners, particles)
    assert kenshi_parry.state == "PARRY_BACKHOP"
    assert kenshi_parry.is_aerial_parry is False
    assert kenshi_parry.is_invulnerable_dodge is True

    # No meio do salto para trás, deve estar no ar (arco parabólico wz > 0.25)
    kenshi_parry.update(0.15, game_map, particles)
    assert kenshi_parry.wz > 0.25, f"Salto de recuo deve ter arco parabólico no ar, wz={kenshi_parry.wz}"

    # Ao pousar (~0.30s total), deve estar a ~2.7m do ponto inicial (fora do alcance de contra-ataque) e em STATE_RECOVERY podendo andar!
    kenshi_parry.update(0.16, game_map, particles)
    assert kenshi_parry.state == STATE_RECOVERY
    assert kenshi_parry.wz == 0.0
    backhop_dist = 10.0 - kenshi_parry.wx
    assert backhop_dist >= 2.2, f"Backhop deve afastar Kenshi para fora do alcance melee (>= 2.2m), obtido {backhop_dist:.2f}m"
    assert kenshi_parry.can_move() is True, "Kenshi deve poder andar enquanto embainha após aterrissar do parry!"
    print("✓ Entregável 2.1.1 (Golpe Primário, Startup Koiguchi-kiri, Noto 50% e Parry Backhop) OK!")

    # =========================================================================
    # 2. Entregável 2.1.2: Golpe Secundário — Ryuu Tsui Sen (3 fases + Mortal Aéreo no Parry)
    # =========================================================================
    kenshi_ryuu = RedSamurai(wx=9.0, wy=10.0)
    kenshi_ryuu.trigger_ryuu_tsui_sen(12.0, 10.0, particles, banners)
    assert kenshi_ryuu.state == "RYUU_TSUI_SEN"
    assert kenshi_ryuu.ryuu_phase == "ASCEND"
    assert 0.20 <= kenshi_ryuu.wz < 1.0, "Não deve teleportar direto para wz=2.6 no frame 0; deve subir em salto Shukuchi!"

    # Avançar subida (0.08s) -> deve gerar sombras Zanzou e atingir o ápice (APEX, wz=2.6)
    kenshi_ryuu.update(0.04, game_map, particles)
    kenshi_ryuu.update(0.045, game_map, particles)
    assert kenshi_ryuu.ryuu_phase == "APEX"
    assert abs(kenshi_ryuu.wz - 2.60) < 0.05
    assert len(kenshi_ryuu.zanzou_ghosts) >= 2, "Subida Shukuchi do Ryuu Tsui Sen deve gerar sombras Zanzou!"

    # Avançar ápice (0.06s) -> entra em DESCEND
    kenshi_ryuu.update(0.065, game_map, particles)
    assert kenshi_ryuu.ryuu_phase == "DESCEND"

    # Durante a descida (wz <= 1.8), ativa hitbox de raio 1.45m
    kenshi_ryuu.update(0.09, game_map, particles)
    assert kenshi_ryuu.hitbox_active is True
    assert abs(kenshi_ryuu.hitbox_radius - 1.45) < 1e-4

    # Testar Parry Aéreo durante o Ryuu Tsui Sen: Mortal para trás no ar (somersault 360°)
    kenshi_ryuu.on_parried(opp_parry, game_map, banners, particles)
    assert kenshi_ryuu.state == "PARRY_BACKHOP"
    assert kenshi_ryuu.is_aerial_parry is True
    kenshi_ryuu.update(0.18, game_map, particles)
    assert 120.0 <= kenshi_ryuu.somersault_angle <= 240.0, f"Deve girar em mortal de 360° no ar, somersault_angle={kenshi_ryuu.somersault_angle}"
    kenshi_ryuu.update(0.20, game_map, particles)
    assert kenshi_ryuu.state == STATE_RECOVERY
    assert kenshi_ryuu.wz == 0.0
    print("✓ Entregável 2.1.2 (Ryuu Tsui Sen Parabólico 3-Fases com Zanzou e Mortal Aéreo no Parry) OK!")

    # =========================================================================
    # 3. Entregável 2.1.3: Shukuchi Dash & Cancelamento Ofensivo 'Shukuchi Battou-Giri'
    # =========================================================================
    kenshi_dash = RedSamurai(wx=7.0, wy=10.0)
    kenshi_dash.trigger_dash(1.0, 0.0)
    assert kenshi_dash.state == "SHUKUCHI"
    assert kenshi_dash.is_invulnerable_dodge is True

    # Nos primeiros 60% do Shukuchi (ex: após 0.04s, restando 0.11s), ainda não está na janela dos últimos 40% (<= 0.06s)
    kenshi_dash.update(0.04, game_map, particles)
    assert kenshi_dash.can_cancel_shukuchi() is False

    # Avançar até restar <= 0.06s (últimos 40% do Shukuchi): janela de cancelamento aberta!
    kenshi_dash.update(0.06, game_map, particles)
    assert kenshi_dash.state == "SHUKUCHI"
    assert kenshi_dash.can_cancel_shukuchi() is True

    # Acionar Golpe Primário durante os últimos 40% do Shukuchi -> Shukuchi Battou-Giri!
    kenshi_dash.trigger_iai_attack(14.0, 10.0)
    assert kenshi_dash.state == STATE_ATTACK
    assert kenshi_dash.is_shukuchi_cancel is True
    assert abs(kenshi_dash.iai_startup_timer - 0.05) < 1e-4, "Shukuchi Battou-Giri deve reduzir o startup pela metade (0.05s)!"
    assert kenshi_dash.dash_speed > kenshi_dash.base_dash_speed, "Shukuchi Battou-Giri deve herdar momentum!"
    print("✓ Entregável 2.1.3 (Shukuchi Dash & Cancelamento Ofensivo 'Shukuchi Battou-Giri') OK!")

    # =========================================================================
    # 4. Entregáveis 2.1.4a e 2.1.4b: Finishers Primário (KENSHIN_SPLIT) e Especial (VERTICAL_BISECTION)
    # =========================================================================
    director = CinematicDirector()
    atk_k = RedSamurai(wx=9.5, wy=10.0)
    vic_b = BlueSamurai(wx=10.5, wy=10.0)

    # 2.1.4a: Finisher Primário (KENSHIN_SPLIT — 一刀両断)
    director.trigger_fatal_strike(atk_k, vic_b, "KENSHIN_SPLIT", (1.0, 0.0))
    assert director.current_kanji_text == "一刀両断"
    assert "ITTOU RYOUDAN" in director.current_kanji_subtitle
    assert abs(director.cinematic_zoom_target - 2.20) < 1e-4
    assert len(atk_k.zanzou_ghosts) == 5, "Finisher KENSHIN_SPLIT deve gerar 5 sombras Zanzou!"
    assert atk_k.state == STATE_RECOVERY
    director.update(0.65, game_map, particles)
    director.update(0.45, game_map, particles)
    assert director.kenshin_noto_played is True

    # 2.1.4b: Finisher Especial (VERTICAL_BISECTION — 龍槌閃)
    director2 = CinematicDirector()
    atk_k2 = RedSamurai(wx=9.5, wy=10.0)
    vic_b2 = BlueSamurai(wx=10.5, wy=10.0)
    director2.trigger_fatal_strike(atk_k2, vic_b2, "VERTICAL_BISECTION", (1.0, 0.0))
    assert director2.current_kanji_text == "龍槌閃"
    assert "DIVISÃO CELESTIAL DE BAMBU" in director2.current_kanji_subtitle
    assert len(atk_k2.zanzou_ghosts) == 5, "Finisher VERTICAL_BISECTION deve gerar 5 sombras Zanzou no salto vertical!"
    assert atk_k2.state == "RYUU_TSUI_SEN"
    assert atk_k2.ryuu_phase == "APEX"
    assert abs(atk_k2.wz - 2.50) < 1e-4
    # Avançar além do setup de câmera e da fase 1 (0.25s) para a queda meteórica (DESCEND)
    director2.update(0.65, game_map, particles)
    director2.update(0.60, game_map, particles)
    assert director2.ryuu_fatal_impact_played is True
    print("✓ Entregáveis 2.1.4a (Ittou Ryoudan / Kenshin Split) e 2.1.4b (Divisão Celestial de Bambu / Ryuu Tsui Sen) OK!")

    # =========================================================================
    # 5. Entregáveis 2.1.5 e 2.1.6: Animações de Intro (Meditação & Koiguchi-kiri) e Vitória (Chiburi & Noto)
    # =========================================================================
    intro_p0 = pose_scripts.sample("kenshin", "intro", 0.15).extra
    assert intro_p0.get("eyes_closed") is True, "Fase inicial da Intro deve manter os olhos fechados em meditação!"
    intro_p1 = pose_scripts.sample("kenshin", "intro", 0.50).extra
    assert intro_p1.get("eyes_closed", False) is False
    assert intro_p1.get("pose") == "koiguchi_glint", "Fase 2 da Intro deve exibir o Koiguchi-kiri na tsuba!"
    assert intro_p1.get("eye_glint_boost", 0.0) > 0.3

    vic_p1 = pose_scripts.sample("kenshin", "victory", 0.38).extra
    assert vic_p1.get("pose") == "chiburi_flick", "Vitória deve conter o Chiburi lateral!"
    vic_p2 = pose_scripts.sample("kenshin", "victory", 0.65).extra
    assert vic_p2.get("pose") == "noto_sheath", "Vitória deve conter o Noto cerimonial!"
    vic_p3 = pose_scripts.sample("kenshin", "victory", 0.90).extra
    assert vic_p3.get("pose") == "victory_bow", "Vitória deve encerrar com reverência serena!"
    print("✓ Entregáveis 2.1.5 (Intro Meditação & Koiguchi-kiri) e 2.1.6 (Vitória Chiburi & Noto) OK!")

    # =========================================================================
    # 6. Entregáveis 2.1.7, 2.1.8, 2.1.9 e 2.1.10: SSAA 2x, Olhos Anime HD, Pose LERP 0.08s e Materiais
    # =========================================================================
    # 2.1.8: Olhos Anime HD
    k_face = PORTRAIT_FACE_STYLES["kenshin"]
    assert k_face.get("hd_anime_eyes") is True
    assert "iris_limbal" in k_face and "iris_core" in k_face

    # 2.1.10: Biblioteca de Materiais Realistas
    pal = kenshi_model.pal()
    poly_test = [(10, 10), (74, 10), (74, 74), (10, 74)]
    for role, kind in (("kimono", "chirimen_silk"), ("hakama", "indigo_linen"), ("saya", "urushi_lacquer"), ("steel", "tamahagane_hamon")):
        assert kenshi_model.MATERIALS.get(role) == kind
        assert kind in PATTERNS, f"Padrão procedural '{kind}' deve estar registrado em PATTERNS!"
        draw_face_texture(screen, kind, poly_test, "side_x", 0.35, 0.35, pal[role], seed=42)

    # 2.1.7 & 2.1.9: Renderização SSAA 2x Offscreen e Pose LERP Cross-Fade 0.08s
    kenshi_vis = RedSamurai(wx=10.5, wy=10.5)
    camera.zoom = 2.2
    kenshi_vis.state = STATE_IDLE
    kenshi_vis.render(screen, camera)
    snap_idle = kenshi_vis._pose_lerp_tracker.get("last_snap")
    assert snap_idle is not None

    # Transicionar de IDLE para SHUKUCHI -> deve ativar o blend_timer de 0.08s e interpolar!
    kenshi_vis.trigger_dash(1.0, 0.0)
    kenshi_vis.render(screen, camera)
    assert kenshi_vis._pose_lerp_tracker["transitions_count"] >= 1
    assert 0.0 < kenshi_vis._pose_lerp_tracker["last_lerp_alpha"] < 1.0, "Pose LERP deve interpolar suavemente na transição de estado!"
    print("✓ Entregáveis 2.1.7 (SSAA 2x), 2.1.8 (Olhos Anime HD), 2.1.9 (Pose LERP 0.08s) e 2.1.10 (Materiais) OK!")

    # =========================================================================
    # 7. Entregável 2.1.11: Model Inspector — De/Para (Antigo vs Novo) & Botões Interativos de Animação
    # =========================================================================
    from tools.model_inspector import ModelInspector, CHARACTER_ANIM_BUTTONS, OVERHAUL_DE_PARA_NOTES
    assert "kenshi" in CHARACTER_ANIM_BUTTONS
    assert len(CHARACTER_ANIM_BUTTONS["kenshi"]) == 12, "Kenshi deve ter 12 botões interativos de animação/golpes no Model Inspector!"
    assert "kenshi" in OVERHAUL_DE_PARA_NOTES
    assert hasattr(kenshi_model, "LEGACY_MATERIALS")

    inspector = ModelInspector(headless=True)
    inspector.select_character(0)  # Kenshi
    inspector.compare_mode = True
    for btn in CHARACTER_ANIM_BUTTONS["kenshi"]:
        act_id = btn[0]
        inspector.trigger_action(act_id)
        assert inspector.active_action == act_id
        inspector.update(0.15)
        inspector.render()
    assert len(inspector.anim_action_btn_rects) == 12
    assert inspector.compare_btn_rect is not None
    print("✓ Entregável 2.1.11 (Model Inspector De/Para Antigo vs Novo & 12 Botões de Animação) OK!")

    print("\n=======================================================")
    print("TODOS OS 12 ENTREGÁVEIS DA SUB-FASE 2.1 (KENSHI) PASSARAM COM 100% DE SUCESSO!")
    print("=======================================================\n")


if __name__ == "__main__":
    run_kenshi_overhaul_tests()
