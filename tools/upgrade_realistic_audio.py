"""
Script para remasterização e instalação dos efeitos sonoros acústicos autênticos (Foley real).
Substitui as fórmulas matemáticas procedurais por gravações reais de lâminas de aço,
impactos metálicos, passos em superfícies reais, detonações de pólvora e gongos orientais.
"""
import os
import sys
import subprocess
import wave
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SFX_DIR = os.path.join(ROOT, "assets", "sounds", "sfx")
RAW_DIR = "/tmp/sfx_raw"
FFMPEG = "/opt/homebrew/bin/ffmpeg"

def run_ffmpeg(cmd: list[str]):
    res = subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        raise RuntimeError(f"FFmpeg failed: {res.stderr}")

def normalize_wav(file_path: str, target_peak_db: float = -1.5):
    """Normaliza o arquivo WAV para o volume ideal sem clipar."""
    with wave.open(file_path, "rb") as wf:
        n_ch = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    if sampwidth == 2:
        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        peak = np.max(np.abs(data))
        if peak > 0:
            target_amplitude = 32767.0 * (10.0 ** (target_peak_db / 20.0))
            gain = target_amplitude / peak
            data = np.clip(data * gain, -32767.0, 32767.0).astype(np.int16)
            with wave.open(file_path, "wb") as wf:
                wf.setnchannels(n_ch)
                wf.setsampwidth(sampwidth)
                wf.setframerate(framerate)
                wf.writeframes(data.tobytes())

def build_all_audio():
    os.makedirs(SFX_DIR, exist_ok=True)
    print("🔊 Iniciando masterização de áudio Foley de alta fidelidade...")

    # 1. SWORD SLASH / SLASH KATANA (Corte afiado de lâmina de katana cortando o ar)
    slash_src = os.path.join(RAW_DIR, "attacks/sword - StarNinjas/sword.1.ogg")
    swing_src = os.path.join(RAW_DIR, "rpg/RPG Sound Pack/battle/swing.wav")
    slash_out = os.path.join(SFX_DIR, "sword_slash.wav")
    katana_out = os.path.join(SFX_DIR, "slash_katana.wav")
    run_ffmpeg([
        "-i", slash_src, "-i", swing_src,
        "-filter_complex", "[0:a]volume=1.4,highpass=f=400[a0];[1:a]volume=0.9[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.32:d=0.08",
        "-t", "0.40", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", slash_out
    ])
    normalize_wav(slash_out, -1.0)
    # Katana rápida usa variação com ligeiro pitch up
    run_ffmpeg([
        "-i", slash_out,
        "-filter_complex", "asetrate=44100*1.08,aresample=44100",
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", katana_out
    ])
    normalize_wav(katana_out, -1.0)
    print("  ✓ sword_slash.wav & slash_katana.wav (Corte de aço real)")

    # 2. SLASH HEAVY (Corte pesado / Naginata / Clava / Forjado)
    heavy_swish = os.path.join(RAW_DIR, "attacks/sword - StarNinjas/sword.5.ogg")
    deep_whoosh = os.path.join(RAW_DIR, "battle/battle_sound_effects/swish_3.wav")
    heavy_out = os.path.join(SFX_DIR, "slash_heavy.wav")
    run_ffmpeg([
        "-i", heavy_swish, "-i", deep_whoosh,
        "-filter_complex", "[0:a]volume=1.2,lowpass=f=2800[a0];[1:a]volume=1.5,lowpass=f=1200[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.38:d=0.10",
        "-t", "0.48", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", heavy_out
    ])
    normalize_wav(heavy_out, -1.0)
    print("  ✓ slash_heavy.wav (Corte pesado encorpado)")

    # 3. SLASH RAPIER (Estocada de florete / corte perfurante rápido)
    rapier_src = os.path.join(RAW_DIR, "attacks/sword - StarNinjas/sword.6.ogg")
    rapier_out = os.path.join(SFX_DIR, "slash_rapier.wav")
    run_ffmpeg([
        "-i", rapier_src,
        "-filter_complex", "asetrate=44100*1.18,aresample=44100,highpass=f=800,afade=t=out:st=0.22:d=0.06",
        "-t", "0.28", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", rapier_out
    ])
    normalize_wav(rapier_out, -1.5)
    print("  ✓ slash_rapier.wav (Estocada rápida de florete)")

    # 4. SWORD CLASH (Choque mútuo de katanas com contato metálico e fricção real)
    clash_src = os.path.join(RAW_DIR, "clashes/sword_clash.1.ogg")
    metal_src = os.path.join(RAW_DIR, "impacts/Audio/impactMetal_heavy_000.ogg")
    clash_out = os.path.join(SFX_DIR, "sword_clash.wav")
    run_ffmpeg([
        "-i", clash_src, "-i", metal_src,
        "-filter_complex", "[0:a]volume=1.6[a0];[1:a]volume=1.3,highpass=f=350[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.45:d=0.15",
        "-t", "0.60", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", clash_out
    ])
    normalize_wav(clash_out, -1.0)
    print("  ✓ sword_clash.wav (Choque de katanas aço contra aço)")

    # 5. PARRY (Aparada perfeita com ressonância harmônica de têmpera cristalina)
    parry_src = os.path.join(RAW_DIR, "clashes/sword_clash.2.ogg")
    ring_src = os.path.join(RAW_DIR, "rpg/RPG Sound Pack/inventory/metal-ringing.wav")
    plate_src = os.path.join(RAW_DIR, "impacts/Audio/impactPlate_heavy_000.ogg")
    parry_out = os.path.join(SFX_DIR, "parry.wav")
    run_ffmpeg([
        "-i", parry_src, "-i", ring_src, "-i", plate_src,
        "-filter_complex", "[0:a]volume=1.3[a0];[1:a]volume=1.8,highpass=f=700[a1];[2:a]volume=1.0[a2];[a0][a1][a2]amix=inputs=3:duration=first,afade=t=out:st=0.55:d=0.20",
        "-t", "0.75", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", parry_out
    ])
    normalize_wav(parry_out, -1.0)
    print("  ✓ parry.wav (Aparada brilhante e ressonante)")

    # 6. FATAL STRIKE (Golpe de morte instantânea: impacto corporal + corte letal profundo)
    punch_src = os.path.join(RAW_DIR, "impacts/Audio/impactPunch_heavy_000.ogg")
    cut_src = os.path.join(RAW_DIR, "attacks/sword - StarNinjas/sword.2.ogg")
    fatal_out = os.path.join(SFX_DIR, "fatal_strike.wav")
    run_ffmpeg([
        "-i", punch_src, "-i", cut_src,
        "-filter_complex", "[0:a]volume=2.2,lowpass=f=800[a0];[1:a]volume=1.8,highpass=f=250[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.48:d=0.15",
        "-t", "0.65", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", fatal_out
    ])
    normalize_wav(fatal_out, -0.8)
    print("  ✓ fatal_strike.wav (Golpe mortal visceral cinematográfico)")

    # 7. FLESH CLEAVE & BONE CRUSH
    flesh_out = os.path.join(SFX_DIR, "flesh_cleave.wav")
    bone_out = os.path.join(SFX_DIR, "bone_crush.wav")
    punch_med = os.path.join(RAW_DIR, "impacts/Audio/impactPunch_medium_000.ogg")
    wood_heavy = os.path.join(RAW_DIR, "impacts/Audio/impactWood_heavy_000.ogg")
    run_ffmpeg([
        "-i", punch_med, "-i", cut_src,
        "-filter_complex", "[0:a]volume=1.6[a0];[1:a]volume=1.4[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.30:d=0.08",
        "-t", "0.38", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", flesh_out
    ])
    normalize_wav(flesh_out, -1.2)
    run_ffmpeg([
        "-i", punch_src, "-i", wood_heavy,
        "-filter_complex", "[0:a]volume=1.8[a0];[1:a]volume=1.4[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.35:d=0.10",
        "-t", "0.45", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", bone_out
    ])
    normalize_wav(bone_out, -1.0)
    print("  ✓ flesh_cleave.wav & bone_crush.wav (Impactos anatômicos)")

    # 8. ARMOR CLANG (Deflexão em armadura metálica / kabuto / ō-sode)
    plate_heavy = os.path.join(RAW_DIR, "impacts/Audio/impactPlate_heavy_002.ogg")
    armor_out = os.path.join(SFX_DIR, "armor_clang.wav")
    run_ffmpeg([
        "-i", plate_heavy,
        "-filter_complex", "volume=1.6,afade=t=out:st=0.35:d=0.12",
        "-t", "0.48", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", armor_out
    ])
    normalize_wav(armor_out, -1.0)
    print("  ✓ armor_clang.wav (Deflexão de armadura pesada)")

    # 9. OBSTACLE HIT & WOOD SHATTER (Choque contra madeira / lanternas / cercas)
    wood_hit = os.path.join(RAW_DIR, "impacts/Audio/impactWood_heavy_001.ogg")
    metal_light = os.path.join(RAW_DIR, "impacts/Audio/impactMetal_light_000.ogg")
    obs_out = os.path.join(SFX_DIR, "obstacle_hit.wav")
    run_ffmpeg([
        "-i", wood_hit, "-i", metal_light,
        "-filter_complex", "[0:a]volume=1.5[a0];[1:a]volume=0.9[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.25:d=0.08",
        "-t", "0.34", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", obs_out
    ])
    normalize_wav(obs_out, -1.2)
    wood_shatter_src = os.path.join(RAW_DIR, "impacts/Audio/impactWood_heavy_003.ogg")
    shatter_out = os.path.join(SFX_DIR, "wood_shatter.wav")
    run_ffmpeg([
        "-i", wood_shatter_src,
        "-filter_complex", "volume=1.6,afade=t=out:st=0.30:d=0.10",
        "-t", "0.40", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", shatter_out
    ])
    normalize_wav(shatter_out, -1.2)
    print("  ✓ obstacle_hit.wav & wood_shatter.wav (Impactos de ambiente)")

    # 10. TANEGASHIMA & FLINTLOCK & CANNON & BOMB (Pólvora preta e artilharia feudal)
    shot_src = os.path.join(RAW_DIR, "bangs/shot_01.ogg")
    cannon_sub = os.path.join(RAW_DIR, "bangs/cannon_03.ogg")
    tane_out = os.path.join(SFX_DIR, "tanegashima_shot.wav")
    run_ffmpeg([
        "-i", shot_src, "-i", cannon_sub,
        "-filter_complex", "[0:a]volume=1.6[a0];[1:a]volume=1.4,lowpass=f=1600[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.55:d=0.20",
        "-t", "0.75", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", tane_out
    ])
    normalize_wav(tane_out, -0.8)

    flint_src = os.path.join(RAW_DIR, "bangs/shot_02.ogg")
    flint_out = os.path.join(SFX_DIR, "flintlock_shot.wav")
    run_ffmpeg([
        "-i", flint_src,
        "-filter_complex", "volume=1.5,afade=t=out:st=0.35:d=0.10",
        "-t", "0.45", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", flint_out
    ])
    normalize_wav(flint_out, -1.0)

    cannon_main = os.path.join(RAW_DIR, "bangs/cannon_01.ogg")
    cannon_out = os.path.join(SFX_DIR, "cannon_fire.wav")
    run_ffmpeg([
        "-i", cannon_main,
        "-filter_complex", "volume=1.8,afade=t=out:st=0.90:d=0.30",
        "-t", "1.20", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", cannon_out
    ])
    normalize_wav(cannon_out, -0.8)

    bomb_src = os.path.join(RAW_DIR, "bangs/bang_01.ogg")
    bomb_out = os.path.join(SFX_DIR, "bomb_explode.wav")
    run_ffmpeg([
        "-i", bomb_src,
        "-filter_complex", "volume=1.6,afade=t=out:st=0.60:d=0.20",
        "-t", "0.80", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", bomb_out
    ])
    normalize_wav(bomb_out, -0.8)
    print("  ✓ tanegashima_shot.wav, flintlock_shot.wav, cannon_fire.wav, bomb_explode.wav (Pólvora realista)")

    # 11. BOW & ARROW (Disparo de arco longo Yumi e flecha fincando)
    bow_src = os.path.join(RAW_DIR, "battle/battle_sound_effects/Bow.wav")
    arrow_rel_out = os.path.join(SFX_DIR, "arrow_release.wav")
    run_ffmpeg([
        "-i", bow_src,
        "-filter_complex", "volume=1.8,afade=t=out:st=0.30:d=0.10",
        "-t", "0.40", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", arrow_rel_out
    ])
    normalize_wav(arrow_rel_out, -1.2)

    arrow_hit_src = os.path.join(RAW_DIR, "impacts/Audio/impactPunch_medium_002.ogg")
    arrow_hit_out = os.path.join(SFX_DIR, "arrow_hit.wav")
    run_ffmpeg([
        "-i", arrow_hit_src, "-i", wood_hit,
        "-filter_complex", "[0:a]volume=1.4[a0];[1:a]volume=1.2[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.20:d=0.08",
        "-t", "0.28", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", arrow_hit_out
    ])
    normalize_wav(arrow_hit_out, -1.2)
    print("  ✓ arrow_release.wav & arrow_hit.wav (Arco e flecha)")

    # 12. SHUKUCHI & RYUU TSUI SEN (Golpes de Kenshi: avanço relâmpago e salto aéreo)
    draw_src = os.path.join(RAW_DIR, "rpg/RPG Sound Pack/battle/sword-unsheathe.wav")
    whoosh_fast = os.path.join(RAW_DIR, "battle/battle_sound_effects/swish_2.wav")
    shukuchi_out = os.path.join(SFX_DIR, "shukuchi.wav")
    run_ffmpeg([
        "-i", draw_src, "-i", whoosh_fast,
        "-filter_complex", "[0:a]volume=1.5,asetrate=44100*1.12,aresample=44100[a0];[1:a]volume=1.4[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.32:d=0.08",
        "-t", "0.40", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", shukuchi_out
    ])
    normalize_wav(shukuchi_out, -1.0)

    ryuu_out = os.path.join(SFX_DIR, "ryuu_tsui_sen.wav")
    run_ffmpeg([
        "-i", whoosh_fast, "-i", heavy_swish,
        "-filter_complex", "[0:a]volume=1.5[a0];[1:a]volume=1.6[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.38:d=0.10",
        "-t", "0.48", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", ryuu_out
    ])
    normalize_wav(ryuu_out, -1.0)
    print("  ✓ shukuchi.wav & ryuu_tsui_sen.wav (Técnicas de espada)")

    # 13. ROUND START & ROUND WIN (Gongos rituais feudais)
    gong_start = os.path.join(RAW_DIR, "100_sfx/gong_01.ogg")
    gong_win = os.path.join(RAW_DIR, "100_sfx/gong_02.ogg")
    round_start_out = os.path.join(SFX_DIR, "round_start.wav")
    round_win_out = os.path.join(SFX_DIR, "round_win.wav")
    run_ffmpeg([
        "-i", gong_start,
        "-filter_complex", "volume=1.6,afade=t=out:st=1.10:d=0.30",
        "-t", "1.40", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", round_start_out
    ])
    normalize_wav(round_start_out, -1.0)

    run_ffmpeg([
        "-i", gong_win,
        "-filter_complex", "volume=1.7,afade=t=out:st=1.30:d=0.40",
        "-t", "1.70", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", round_win_out
    ])
    normalize_wav(round_win_out, -1.0)
    print("  ✓ round_start.wav & round_win.wav (Gongos rituais)")

    # 14. UI SOUNDS (Seleção e confirmação tátil limpa)
    ui_sel_src = os.path.join(RAW_DIR, "rpg/RPG Sound Pack/interface/interface1.wav")
    ui_conf_src = os.path.join(RAW_DIR, "rpg/RPG Sound Pack/interface/interface2.wav")
    ui_canc_src = os.path.join(RAW_DIR, "rpg/RPG Sound Pack/interface/interface4.wav")
    run_ffmpeg(["-i", ui_sel_src, "-t", "0.15", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "ui_select.wav")])
    normalize_wav(os.path.join(SFX_DIR, "ui_select.wav"), -3.0)
    run_ffmpeg(["-i", ui_conf_src, "-t", "0.30", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "ui_confirm.wav")])
    normalize_wav(os.path.join(SFX_DIR, "ui_confirm.wav"), -2.0)
    run_ffmpeg(["-i", ui_canc_src, "-t", "0.22", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "ui_cancel.wav")])
    normalize_wav(os.path.join(SFX_DIR, "ui_cancel.wav"), -3.0)
    print("  ✓ ui_select.wav, ui_confirm.wav, ui_cancel.wav (Interface tátil)")

    # 15. PASSOS POR TERRENO (Grama, Madeira, Pedra, Cascalho, Água, Geral)
    step_grass = os.path.join(RAW_DIR, "impacts/Audio/footstep_grass_000.ogg")
    step_wood = os.path.join(RAW_DIR, "impacts/Audio/footstep_wood_000.ogg")
    step_stone = os.path.join(RAW_DIR, "impacts/Audio/footstep_concrete_000.ogg")
    step_gravel = os.path.join(RAW_DIR, "impacts/Audio/footstep_concrete_002.ogg")
    step_carpet = os.path.join(RAW_DIR, "impacts/Audio/footstep_carpet_000.ogg")

    run_ffmpeg(["-i", step_wood, "-t", "0.18", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "footstep.wav")])
    normalize_wav(os.path.join(SFX_DIR, "footstep.wav"), -4.0)
    run_ffmpeg(["-i", step_grass, "-t", "0.18", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "footstep_grass.wav")])
    normalize_wav(os.path.join(SFX_DIR, "footstep_grass.wav"), -4.0)
    run_ffmpeg(["-i", step_wood, "-t", "0.18", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "footstep_wood.wav")])
    normalize_wav(os.path.join(SFX_DIR, "footstep_wood.wav"), -4.0)
    run_ffmpeg(["-i", step_stone, "-t", "0.18", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "footstep_stone.wav")])
    normalize_wav(os.path.join(SFX_DIR, "footstep_stone.wav"), -4.0)
    run_ffmpeg(["-i", step_gravel, "-t", "0.18", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "footstep_gravel.wav")])
    normalize_wav(os.path.join(SFX_DIR, "footstep_gravel.wav"), -4.0)
    # Água e lama processados a partir de passo úmido
    run_ffmpeg([
        "-i", step_carpet,
        "-filter_complex", "volume=1.8,lowpass=f=1800,afade=t=out:st=0.14:d=0.06",
        "-t", "0.20", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "footstep_mud.wav")
    ])
    normalize_wav(os.path.join(SFX_DIR, "footstep_mud.wav"), -4.0)
    run_ffmpeg([
        "-i", step_carpet,
        "-filter_complex", "volume=1.8,highpass=f=600,afade=t=out:st=0.14:d=0.06",
        "-t", "0.20", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(SFX_DIR, "footstep_water.wav")
    ])
    normalize_wav(os.path.join(SFX_DIR, "footstep_water.wav"), -4.0)
    print("  ✓ Passos autênticos por superfície (footstep_*.wav)")

    # 16. CHAIN & DODGE
    chain_src = os.path.join(RAW_DIR, "rpg/RPG Sound Pack/inventory/chainmail1.wav")
    chain_rattle_out = os.path.join(SFX_DIR, "chain_rattle.wav")
    run_ffmpeg([
        "-i", chain_src,
        "-filter_complex", "volume=1.5,afade=t=out:st=0.45:d=0.15",
        "-t", "0.60", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", chain_rattle_out
    ])
    normalize_wav(chain_rattle_out, -2.0)

    chain_whip_out = os.path.join(SFX_DIR, "chain_whip.wav")
    run_ffmpeg([
        "-i", chain_src, "-i", whoosh_fast,
        "-filter_complex", "[0:a]volume=1.4[a0];[1:a]volume=1.5[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.30:d=0.10",
        "-t", "0.40", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", chain_whip_out
    ])
    normalize_wav(chain_whip_out, -1.5)

    dodge_out = os.path.join(SFX_DIR, "dodge_whoosh.wav")
    run_ffmpeg([
        "-i", whoosh_fast,
        "-filter_complex", "volume=1.5,afade=t=out:st=0.22:d=0.08",
        "-t", "0.30", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", dodge_out
    ])
    normalize_wav(dodge_out, -2.0)
    print("  ✓ chain_rattle.wav, chain_whip.wav, dodge_whoosh.wav (Kusarigama e esquiva)")

    # 17. KUNAI & TACTICAL KNIFE & SHURIKEN (Faca de combate, kunai e estrela ninja em foley real)
    kunai_out = os.path.join(SFX_DIR, "kunai_throw.wav")
    shuriken_out = os.path.join(SFX_DIR, "shuriken_throw.wav")
    sword_knife = os.path.join(RAW_DIR, "attacks/sword - StarNinjas/sword.4.ogg")
    sword_shuriken = os.path.join(RAW_DIR, "attacks/sword - StarNinjas/sword.6.ogg")
    swish_tight = os.path.join(RAW_DIR, "battle/battle_sound_effects/swish_4.wav")

    run_ffmpeg([
        "-i", sword_knife, "-i", swish_tight,
        "-filter_complex", "[0:a]asetrate=44100*1.30,aresample=44100,highpass=f=750,volume=1.7[a0];[1:a]asetrate=44100*1.25,aresample=44100,volume=1.3[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.20:d=0.06",
        "-t", "0.26", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", kunai_out
    ])
    normalize_wav(kunai_out, -1.0)

    run_ffmpeg([
        "-i", sword_shuriken, "-i", whoosh_fast,
        "-filter_complex", "[0:a]asetrate=44100*1.45,aresample=44100,highpass=f=900,volume=1.5[a0];[1:a]asetrate=44100*1.35,aresample=44100,volume=1.4[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=out:st=0.18:d=0.06",
        "-t", "0.24", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", shuriken_out
    ])
    normalize_wav(shuriken_out, -1.0)
    print("  ✓ kunai_throw.wav & shuriken_throw.wav (Faca tática e lâminas afiadas)")

    print("\n✨ Masterização acústica concluída com sucesso! Todos os efeitos agora usam gravações reais!")

if __name__ == "__main__":
    build_all_audio()
