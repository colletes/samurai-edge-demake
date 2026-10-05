"""
Gera os assets de pergaminho (Fase 5.5.4) a partir das artes de referência em assets/concepts.

- backdrop.png: concept3 sem o pergaminho central e sem os duelistas (paisagem sumi-e, papel rasgado e moldura de madeira reais)
- rod_top.png / rod_bottom.png: varas de pergaminho recortadas de concept2 (camada de multiplicação: branco = transparente)
- crane_crest.png: brasão da garça de concept2 (camada de multiplicação)

Uso: python tools/build_parchment_assets.py
"""
import os
import cv2
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "assets", "concepts")
OUT = os.path.join(ROOT, "assets", "ui", "parchment")
W, H = 1280, 720


def feather(mask, px):
    m = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (0, 0), px)
    return np.clip(m, 0, 1)[..., None]


def build_backdrop():
    c3 = cv2.imread(os.path.join(SRC, "concept3.jpeg"))
    h, w = c3.shape[:2]
    work = c3.astype(np.float32).copy()

    ref = c3[170:300, 300:440].astype(np.float32)
    grain_std = float((ref - cv2.GaussianBlur(ref, (0, 0), 3)).std())
    rng = np.random.default_rng(7)

    # 1) Centro (onde ficava o pergaminho): paisagem esquerda refletida em "vai-e-vem", contínua e sem emendas
    src = work[:, 84:476][:, ::-1]
    period = 2 * src.shape[1]
    idx = np.arange(1046 - 476) % period
    idx = np.where(idx < src.shape[1], idx, period - 1 - idx)
    pingpong = src[:, idx]
    work[:, 476:926] = pingpong[:, : 926 - 476]
    seam = np.linspace(0, 1, 120, dtype=np.float32)[None, :, None]
    work[:, 926:1046] = pingpong[:, 926 - 476:] * (1 - seam) + c3[:, 926:1046].astype(np.float32) * seam

    # 2) Duelistas: papel limpo (tom amostrado da própria arte) com variação suave e a mesma granulação
    x1, y1, x2, y2 = 862, 318, 1296, 664
    paper = np.median(work[640:720, 420:570].reshape(-1, 3), axis=0)
    low = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 45)
    low = low / (low.std() + 1e-6) * 5
    grain = cv2.GaussianBlur(rng.normal(0, grain_std * 0.8, (h, w)).astype(np.float32), (0, 0), 0.8)
    filled = np.empty_like(work)
    filled[:] = paper
    filled = filled + low[..., None] + grain[..., None]
    soft = np.zeros((h, w), np.uint8)
    cv2.rectangle(soft, (x1 + 10, y1 + 24), (x2 - 24, y2 - 2), 255, -1)
    soft = feather(soft, 18)
    work = work * (1 - soft) + filled * soft

    out = np.clip(work, 0, 255).astype(np.uint8)
    out = cv2.resize(out, (W, H), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(OUT, "backdrop.png"), out)


def multiply_layer(img, box, paper_bgr, edge=10):
    """Recorta box e normaliza pelo tom do papel: o resultado multiplicado sobre papel devolve o original."""
    x1, y1, x2, y2 = box
    crop = img[y1:y2, x1:x2].astype(np.float32)
    norm = np.clip(crop / np.array(paper_bgr, np.float32) * 1.0, 0, 1)
    hh, ww = norm.shape[:2]
    ramp = np.ones((hh, ww), np.float32)
    e = min(edge, hh // 2, ww // 2)
    for i in range(e):
        a = (i + 1) / (e + 1)
        ramp[i, :] = np.minimum(ramp[i, :], a)
        ramp[hh - 1 - i, :] = np.minimum(ramp[hh - 1 - i, :], a)
        ramp[:, i] = np.minimum(ramp[:, i], a)
        ramp[:, ww - 1 - i] = np.minimum(ramp[:, ww - 1 - i], a)
    norm = 1.0 - (1.0 - norm) * ramp[..., None]
    return np.clip(norm * 255, 0, 255).astype(np.uint8)


def build_ornaments():
    c2 = cv2.imread(os.path.join(SRC, "concept2.jpeg"))
    # tom médio do papel claro ao redor das varas
    paper = np.median(c2[100:130, 300:480].reshape(-1, 3), axis=0)
    paper = np.maximum(paper, 1)

    top = multiply_layer(c2, (484, 36, 928, 102), paper, edge=8)
    bottom = multiply_layer(c2, (488, 676, 922, 736), paper, edge=8)
    crest = multiply_layer(c2, (1282, 660, 1396, 752), paper, edge=8)

    cv2.imwrite(os.path.join(OUT, "rod_top.png"), top)
    cv2.imwrite(os.path.join(OUT, "rod_bottom.png"), bottom)
    cv2.imwrite(os.path.join(OUT, "crane_crest.png"), crest)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build_backdrop()
    build_ornaments()
    print("assets gerados em", OUT)
