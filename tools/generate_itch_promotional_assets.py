#!/usr/bin/env python3
"""
generate_itch_promotional_assets.py
Generates the complete set of promotional assets for Samurai Edge: Bakumatsu on itch.io and social media:
1. Social Media Image (1200x630, 1.91:1)
2. Favicon (512x512 square + standard downscaled sizes and .ico)
3. Wide Cover (2520x1080, 21:9)
4. Logo (Transparent PNG, horizontal aspect ratio, legible on both white & black backgrounds)

Uses 100% original, copyright-free game artwork featuring original characters:
- Kenshi (female samurai protagonist) vs Musashi (dual-blade master)
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
from scipy import ndimage

DEPLOY_DIR = "deploy/itch_assets"
PROMO_DIR = "assets/promotional"
os.makedirs(DEPLOY_DIR, exist_ok=True)
os.makedirs(PROMO_DIR, exist_ok=True)

def clean_alpha_mask(alpha_arr, min_area=25):
    binary = alpha_arr > 35
    labeled, num_features = ndimage.label(binary)
    sizes = ndimage.sum(binary, labeled, range(num_features + 1))
    mask_to_keep = sizes >= min_area
    clean_binary = mask_to_keep[labeled]
    out_alpha = np.where(clean_binary, alpha_arr, 0)
    return out_alpha

# ---------------------------------------------------------------------------
# 1. EXTRACT CALLIGRAPHY & SEALS WITH ABSOLUTE PRECISION
# ---------------------------------------------------------------------------
print("--> Extracting calligraphy and seals from master artwork...")

title_concept_path = "assets/concepts/sumie_title_logo_concept.jpg"
im_master = Image.open(title_concept_path).convert("RGB")

# A. Extract Kanji 侍
kanji_crop = im_master.crop((500, 50, 950, 420))
arr_k = np.array(kanji_crop, dtype=np.float32)
lum_k = 0.299 * arr_k[:,:,0] + 0.587 * arr_k[:,:,1] + 0.114 * arr_k[:,:,2]

bg_thresh = 208.0
ink_thresh = 70.0
alpha_k = np.clip((bg_thresh - lum_k) / (bg_thresh - ink_thresh), 0.0, 1.0)
alpha_k[:170, 260:] = 0.0
alpha_k[:28, :] = 0.0
alpha_k[170:230, 360:] = 0.0
alpha_k[150:, :35] = 0.0
alpha_k[315:, :] = 0.0
alpha_k = clean_alpha_mask((alpha_k * 255).astype(np.uint8), min_area=30) / 255.0

kanji_rgba = np.zeros((arr_k.shape[0], arr_k.shape[1], 4), dtype=np.uint8)
kanji_rgba[:,:,0] = 18
kanji_rgba[:,:,1] = 18
kanji_rgba[:,:,2] = 22
kanji_rgba[:,:,3] = (alpha_k * 255).astype(np.uint8)
kanji_img = Image.fromarray(kanji_rgba).crop(Image.fromarray(kanji_rgba).getbbox())

# B. Extract Vermilion Red Seal 幕末
seal_crop = im_master.crop((340, 480, 500, 640))
arr_s = np.array(seal_crop, dtype=np.float32)
r_s, g_s, b_s = arr_s[:,:,0], arr_s[:,:,1], arr_s[:,:,2]

mask_box = np.zeros(arr_s.shape[:2], dtype=bool)
mask_box[20:142, 20:142] = True
diff_s = r_s - 0.5 * (g_s + b_s)
alpha_s = np.clip((diff_s - 32.0) / 40.0, 0.0, 1.0) * mask_box

seal_rgba = np.zeros((arr_s.shape[0], arr_s.shape[1], 4), dtype=np.uint8)
seal_rgba[:,:,0] = 196
seal_rgba[:,:,1] = 32
seal_rgba[:,:,2] = 32
seal_rgba[:,:,3] = (alpha_s * 255).astype(np.uint8)
seal_img = Image.fromarray(seal_rgba).crop(Image.fromarray(seal_rgba).getbbox())

# C. Extract Complete English Title "SAMURAI EDGE: BAKUMATSU"
title_crop = im_master.crop((320, 340, 1050, 600))
arr_t = np.array(title_crop, dtype=np.float32)
lum_t = 0.299 * arr_t[:,:,0] + 0.587 * arr_t[:,:,1] + 0.114 * arr_t[:,:,2]

alpha_t = np.clip((bg_thresh - lum_t) / (bg_thresh - ink_thresh), 0.0, 1.0)
alpha_t[148:, :172] = 0.0        # red seal region below S and left of B
alpha_t[135:150, 138:172] = 0.0   # seal corner artifact
alpha_t[:, :38] = 0.0            # left edge bamboo smudges
alpha_t[:22, :] = 0.0            # top crop line
alpha_t[:34, 420:560] = 0.0      # top edge line above EDGE
alpha_t[225:, :] = 0.0           # bottom leaves
alpha_t[195:, 680:] = 0.0        # bottom-right rock
alpha_t[90:, 646:] = 0.0         # right cloud wash
alpha_t[:45, :40] = 0.0          # top-left dust

alpha_t = clean_alpha_mask((alpha_t * 255).astype(np.uint8), min_area=35) / 255.0

title_rgba = np.zeros((arr_t.shape[0], arr_t.shape[1], 4), dtype=np.uint8)
title_rgba[:,:,0] = 18
title_rgba[:,:,1] = 18
title_rgba[:,:,2] = 22
title_rgba[:,:,3] = (alpha_t * 255).astype(np.uint8)
title_img = Image.fromarray(title_rgba).crop(Image.fromarray(title_rgba).getbbox())

print(f"Extracted: Kanji {kanji_img.size}, Seal {seal_img.size}, Title {title_img.size}")

# ---------------------------------------------------------------------------
# 2. ASSEMBLE HORIZONTAL LOGO VARIANTS (Legible on White & Black)
# ---------------------------------------------------------------------------
print("--> Assembling horizontal transparent logo...")

target_kanji_h = 240
target_kanji_w = int(kanji_img.width * (target_kanji_h / kanji_img.height))
k_scaled = kanji_img.resize((target_kanji_w, target_kanji_h), Image.Resampling.LANCZOS)

target_title_h = 220
target_title_w = int(title_img.width * (target_title_h / title_img.height))
t_scaled = title_img.resize((target_title_w, target_title_h), Image.Resampling.LANCZOS)

target_seal_h = 92
target_seal_w = int(seal_img.width * (target_seal_h / seal_img.height))
s_scaled = seal_img.resize((target_seal_w, target_seal_h), Image.Resampling.LANCZOS)

pad = 40
spacing_ks = 14
spacing_st = 28

canvas_w = pad + target_kanji_w + spacing_ks + target_seal_w + spacing_st + target_title_w + pad
canvas_h = max(target_kanji_h, target_title_h) + pad * 2

base_canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

# Paste Kanji
k_y = (canvas_h - target_kanji_h) // 2
base_canvas.paste(k_scaled, (pad, k_y), k_scaled)

# Paste Seal
s_y = (canvas_h - target_seal_h) // 2 + 8
s_x = pad + target_kanji_w + spacing_ks
base_canvas.paste(s_scaled, (s_x, s_y), s_scaled)

# Paste Title
t_y = (canvas_h - target_title_h) // 2
t_x = s_x + target_seal_w + spacing_st
base_canvas.paste(t_scaled, (t_x, t_y), t_scaled)

crop_box = base_canvas.getbbox()
base_logo = base_canvas.crop(crop_box)

final_pad_x = 24
final_pad_y = 16
logo_w = base_logo.width + final_pad_x * 2
logo_h = base_logo.height + final_pad_y * 2

logo_ink = Image.new("RGBA", (logo_w, logo_h), (0, 0, 0, 0))
logo_ink.paste(base_logo, (final_pad_x, final_pad_y), base_logo)

# --- A. UNIVERSAL MASTER LOGO (Legible on BOTH White & Black) ---
alpha_master = logo_ink.split()[3]
rim_filter = alpha_master.filter(ImageFilter.MaxFilter(7))
shadow_filter = rim_filter.filter(ImageFilter.GaussianBlur(radius=5))

universal_logo = Image.new("RGBA", (logo_w, logo_h), (0, 0, 0, 0))

# Soft dark drop shadow
shadow_arr = np.zeros((logo_h, logo_w, 4), dtype=np.uint8)
shadow_arr[:,:,3] = (np.array(shadow_filter, dtype=np.float32) * 0.70).astype(np.uint8)
universal_logo.paste(Image.fromarray(shadow_arr), (2, 3), Image.fromarray(shadow_arr))

# Luminous antique ivory rim contour (#FAF6EC)
rim_arr = np.zeros((logo_h, logo_w, 4), dtype=np.uint8)
rim_arr[:,:,0] = 250
rim_arr[:,:,1] = 246
rim_arr[:,:,2] = 236
rim_arr[:,:,3] = np.array(rim_filter, dtype=np.uint8)
universal_logo.paste(Image.fromarray(rim_arr), (0, 0), Image.fromarray(rim_arr))

# Base sumi ink and vermilion seal on top
universal_logo.paste(logo_ink, (0, 0), logo_ink)

# --- B. DARK BACKGROUND OPTIMIZED LOGO ---
arr_dark = np.array(logo_ink)
is_ink = (arr_dark[:,:,0] < 50) & (arr_dark[:,:,3] > 20)
arr_dark[is_ink, 0] = 246
arr_dark[is_ink, 1] = 240
arr_dark[is_ink, 2] = 226
fg_dark = Image.fromarray(arr_dark)

dark_contour = alpha_master.filter(ImageFilter.MaxFilter(9))
dark_logo = Image.new("RGBA", (logo_w, logo_h), (0, 0, 0, 0))
arr_dark_cont = np.zeros((logo_h, logo_w, 4), dtype=np.uint8)
arr_dark_cont[:,:,0] = 10
arr_dark_cont[:,:,1] = 10
arr_dark_cont[:,:,2] = 14
arr_dark_cont[:,:,3] = (np.array(dark_contour, dtype=np.float32) * 0.9).astype(np.uint8)
dark_logo.paste(Image.fromarray(arr_dark_cont), (0, 0), Image.fromarray(arr_dark_cont))
dark_logo.paste(fg_dark, (0, 0), fg_dark)

# --- C. LIGHT BACKGROUND OPTIMIZED LOGO ---
light_logo = logo_ink.copy()

paths_to_save = [
    (DEPLOY_DIR, "logo.png", universal_logo),
    (DEPLOY_DIR, "logo_dark_bg.png", dark_logo),
    (DEPLOY_DIR, "logo_light_bg.png", light_logo),
    (PROMO_DIR, "logo.png", universal_logo),
    (PROMO_DIR, "logo_dark_bg.png", dark_logo),
    (PROMO_DIR, "logo_light_bg.png", light_logo),
]
for d, fn, img in paths_to_save:
    p = os.path.join(d, fn)
    img.save(p, "PNG")
    print(f"  Saved: {p} ({img.size[0]}x{img.size[1]}, aspect ratio: {img.size[0]/img.size[1]:.2f}:1)")

contrast_sheet = Image.new("RGB", (logo_w + 60, logo_h * 2 + 80), (255, 255, 255))
for y in range(logo_h + 40, contrast_sheet.height):
    for x in range(contrast_sheet.width):
        contrast_sheet.putpixel((x, y), (18, 18, 22))

contrast_sheet.paste(universal_logo, (30, 20), universal_logo)
contrast_sheet.paste(universal_logo, (30, logo_h + 55), universal_logo)
contrast_sheet.save(os.path.join(DEPLOY_DIR, "logo_contrast_test.png"))
contrast_sheet.save(os.path.join(PROMO_DIR, "logo_contrast_test.png"))

# ---------------------------------------------------------------------------
# 3. GENERATE FAVICON (Square 1:1, 512x512 Master + Downscales + .ico)
# ---------------------------------------------------------------------------
print("--> Generating master square Favicon (512x512)...")

fav_size = 512
fav = Image.new("RGBA", (fav_size, fav_size), (0, 0, 0, 0))
draw_fav = ImageDraw.Draw(fav)

center = fav_size // 2
radius = 240

shadow_circle = Image.new("RGBA", (fav_size, fav_size), (0, 0, 0, 0))
draw_sc = ImageDraw.Draw(shadow_circle)
draw_sc.ellipse((center - radius - 4, center - radius - 2, center + radius + 4, center + radius + 6), fill=(0, 0, 0, 150))
fav.paste(shadow_circle.filter(ImageFilter.GaussianBlur(radius=8)), (0, 0))

draw_fav.ellipse((center - radius, center - radius, center + radius, center + radius), fill=(34, 34, 40, 255), outline=(212, 175, 55, 255), width=7)

inner_r = radius - 8
draw_fav.ellipse((center - inner_r, center - inner_r, center + inner_r, center + inner_r), fill=(18, 18, 24, 255))

ring_r = radius - 22
draw_fav.ellipse((center - ring_r, center - ring_r, center + ring_r, center + ring_r), outline=(196, 38, 38, 230), width=6)

kanji_fav_h = 320
kanji_fav_w = int(kanji_img.width * (kanji_fav_h / kanji_img.height))
k_fav_scaled = kanji_img.resize((kanji_fav_w, kanji_fav_h), Image.Resampling.LANCZOS)

arr_kf = np.array(k_fav_scaled)
arr_kf[:,:,0] = 248
arr_kf[:,:,1] = 242
arr_kf[:,:,2] = 226
k_fav_gold = Image.fromarray(arr_kf)

kf_alpha = k_fav_gold.split()[3]
kf_shadow = kf_alpha.filter(ImageFilter.GaussianBlur(radius=4))
kf_sh_layer = Image.new("RGBA", k_fav_gold.size, (0, 0, 0, 0))
arr_shk = np.zeros((kanji_fav_h, kanji_fav_w, 4), dtype=np.uint8)
arr_shk[:,:,3] = (np.array(kf_shadow, dtype=np.float32) * 0.90).astype(np.uint8)
kf_sh_img = Image.fromarray(arr_shk)

kf_x = (fav_size - kanji_fav_w) // 2
kf_y = (fav_size - kanji_fav_h) // 2 - 6

fav.paste(kf_sh_img, (kf_x + 3, kf_y + 4), kf_sh_img)
fav.paste(k_fav_gold, (kf_x, kf_y), k_fav_gold)

# Diagonal Katana Blade Glint
glint_layer = Image.new("RGBA", (fav_size, fav_size), (0, 0, 0, 0))
draw_glint = ImageDraw.Draw(glint_layer)
draw_glint.line([(70, 110), (442, 402)], fill=(255, 255, 255, 180), width=3)
draw_glint.line([(70, 110), (442, 402)], fill=(212, 175, 55, 80), width=7)
draw_glint.ellipse((center - 6, center - 6, center + 6, center + 6), fill=(255, 255, 255, 240))

glint_mask = Image.new("L", (fav_size, fav_size), 0)
draw_gm = ImageDraw.Draw(glint_mask)
draw_gm.ellipse((center - inner_r, center - inner_r, center + inner_r, center + inner_r), fill=255)

glint_alpha = ImageChops.multiply(glint_layer.split()[3], glint_mask)
glint_layer.putalpha(glint_alpha)
fav.paste(glint_layer, (0, 0), glint_layer)

# Miniature red seal in corner
seal_fav_size = 76
s_fav = seal_img.resize((seal_fav_size, seal_fav_size), Image.Resampling.LANCZOS)
s_fav_x = center + radius - 126
s_fav_y = center + radius - 126
fav.paste(s_fav, (s_fav_x, s_fav_y), s_fav)

fav.save(os.path.join(DEPLOY_DIR, "favicon.png"), "PNG")
fav.save(os.path.join(PROMO_DIR, "favicon.png"), "PNG")
print(f"  Saved master favicon: {fav.size[0]}x{fav.size[1]}")

icon_sizes = [256, 128, 64, 32, 16]
for s in icon_sizes:
    down = fav.resize((s, s), Image.Resampling.LANCZOS)
    down.save(os.path.join(DEPLOY_DIR, f"favicon-{s}.png"), "PNG")
    down.save(os.path.join(PROMO_DIR, f"favicon-{s}.png"), "PNG")

fav.save(os.path.join(DEPLOY_DIR, "favicon.ico"), format="ICO", sizes=[(16,16), (32,32), (64,64), (128,128), (256,256)])
fav.save(os.path.join(PROMO_DIR, "favicon.ico"), format="ICO", sizes=[(16,16), (32,32), (64,64), (128,128), (256,256)])

# Alternate: Traditional square Hanko seal favicon
fav_hanko = Image.new("RGBA", (fav_size, fav_size), (0, 0, 0, 0))
draw_fh = ImageDraw.Draw(fav_hanko)
draw_fh.rounded_rectangle((24, 24, fav_size - 24, fav_size - 24), radius=64, fill=(18, 18, 24, 255), outline=(212, 175, 55, 255), width=6)
s_big = seal_img.resize((380, 380), Image.Resampling.LANCZOS)
fav_hanko.paste(s_big, ((fav_size - 380) // 2, (fav_size - 380) // 2), s_big)
fav_hanko.save(os.path.join(DEPLOY_DIR, "favicon_hanko.png"), "PNG")
fav_hanko.save(os.path.join(PROMO_DIR, "favicon_hanko.png"), "PNG")

# ---------------------------------------------------------------------------
# 4. GENERATE WIDE COVER (21:9 Aspect Ratio -> 2520 x 1080)
# Uses 100% Original Game Art: Kenshi (Protagonist) vs Musashi (Master)
# ---------------------------------------------------------------------------
print("--> Generating 21:9 Wide Cover (2520x1080)...")

WIDE_W = 2520
WIDE_H = 1080  # 2520 / 1080 = 2.33333... = 21 / 9 exactly!

duel_art = Image.open("assets/concepts/kenshi_musashi_duel.jpg").convert("RGB")
w_orig, h_orig = duel_art.size

crop_h = int(w_orig / (WIDE_W / WIDE_H)) # ~590 px
y_start = 55 # Captures the moon, bamboo canopy, Kenshi and Musashi, sparks and stone path
duel_cropped = duel_art.crop((0, y_start, w_orig, y_start + crop_h))
wide_cover = duel_cropped.resize((WIDE_W, WIDE_H), Image.Resampling.LANCZOS)

vignette = Image.new("RGBA", (WIDE_W, WIDE_H), (0, 0, 0, 0))
draw_vig = ImageDraw.Draw(vignette)

for y in range(250):
    alpha = int(200 * (1.0 - y / 250.0)**1.4)
    draw_vig.line([(0, y), (WIDE_W, y)], fill=(8, 10, 14, alpha))
    draw_vig.line([(0, WIDE_H - 1 - y), (WIDE_W, WIDE_H - 1 - y)], fill=(8, 10, 14, alpha))

for y in range(360):
    for x in range(1200):
        factor_x = max(0.0, 1.0 - x / 1200.0)
        factor_y = max(0.0, 1.0 - y / 360.0)
        alpha = int(140 * (factor_x * factor_y)**1.2)
        if alpha > 0:
            vignette.putpixel((x, y), (6, 8, 12, alpha))

wide_cover.paste(vignette, (0, 0), vignette)

logo_target_w = 860
logo_target_h = int(universal_logo.height * (logo_target_w / universal_logo.width))
logo_wide_scaled = universal_logo.resize((logo_target_w, logo_target_h), Image.Resampling.LANCZOS)

# Position logo centered at the top sky area
logo_x = (WIDE_W - logo_target_w) // 2
logo_y = 28
wide_cover.paste(logo_wide_scaled, (logo_x, logo_y), logo_wide_scaled)

draw_wc = ImageDraw.Draw(wide_cover)
try:
    font_cinzel_large = ImageFont.truetype("assets/fonts/Cinzel-Regular.ttf", 26)
    font_cinzel_sub = ImageFont.truetype("assets/fonts/Cinzel-Regular.ttf", 18)
except:
    font_cinzel_large = ImageFont.load_default()
    font_cinzel_sub = ImageFont.load_default()

tagline_text = "ONE STRIKE.  ONE KILL.  NO SECOND CHANCES."
tag_bbox = draw_wc.textbbox((0, 0), tagline_text, font=font_cinzel_large)
tag_tw = tag_bbox[2] - tag_bbox[0]
tag_x = (WIDE_W - tag_tw) // 2
tagline_y = logo_y + logo_target_h + 12

# Subtle backing pill for tagline
t_pad_x, t_pad_y = 24, 6
tag_pill = Image.new("RGBA", (tag_tw + t_pad_x * 2, (tag_bbox[3] - tag_bbox[1]) + t_pad_y * 2), (0, 0, 0, 0))
draw_tp = ImageDraw.Draw(tag_pill)
draw_tp.rounded_rectangle((0, 0, tag_pill.width, tag_pill.height), radius=6, fill=(10, 12, 16, 180), outline=(212, 175, 55, 140), width=1)
wide_cover.paste(tag_pill, (tag_x - t_pad_x, tagline_y - t_pad_y), tag_pill)

draw_wc.text((tag_x + 1, tagline_y + 1), tagline_text, font=font_cinzel_large, fill=(0, 0, 0, 240))
draw_wc.text((tag_x, tagline_y), tagline_text, font=font_cinzel_large, fill=(245, 225, 175, 255))

features_text = "TACTICAL 1-HIT LETHAL DUELS  •  3D VOXEL & HD-2D  •  12 WARRIORS  •  12 ARENAS"
feat_bbox = draw_wc.textbbox((0, 0), features_text, font=font_cinzel_sub)
feat_tw = feat_bbox[2] - feat_bbox[0]
feat_x = (WIDE_W - feat_tw) // 2
features_y = WIDE_H - 52

f_pad_x, f_pad_y = 24, 8
feat_pill = Image.new("RGBA", (feat_tw + f_pad_x * 2, (feat_bbox[3] - feat_bbox[1]) + f_pad_y * 2), (0, 0, 0, 0))
draw_fp = ImageDraw.Draw(feat_pill)
draw_fp.rounded_rectangle((0, 0, feat_pill.width, feat_pill.height), radius=8, fill=(12, 14, 18, 210), outline=(212, 175, 55, 160), width=1)
wide_cover.paste(feat_pill, (feat_x - f_pad_x, features_y - f_pad_y), feat_pill)

draw_wc.text((feat_x, features_y), features_text, font=font_cinzel_sub, fill=(215, 222, 235, 240))

wide_cover.save(os.path.join(DEPLOY_DIR, "wide_cover.png"), "PNG")
wide_cover.save(os.path.join(PROMO_DIR, "wide_cover.png"), "PNG")
print(f"  Saved Wide Cover: {wide_cover.size[0]}x{wide_cover.size[1]} (21:9 ratio: {wide_cover.size[0]/wide_cover.size[1]:.2f}:1)")

# ---------------------------------------------------------------------------
# 5. GENERATE SOCIAL MEDIA IMAGE (1200 x 630 px, 1.91:1)
# Uses 100% Original Game Art: Kenshi vs Musashi
# ---------------------------------------------------------------------------
print("--> Generating 1200x630 Social Media Image...")

SOC_W = 1200
SOC_H = 630

social_img = Image.new("RGB", (SOC_W, SOC_H), (10, 12, 16))

s_scale = max(SOC_W / duel_art.width, SOC_H / duel_art.height)
soc_bg = duel_art.resize((int(duel_art.width * s_scale), int(duel_art.height * s_scale)), Image.Resampling.LANCZOS)
crop_x = (soc_bg.width - SOC_W) // 2
crop_y = (soc_bg.height - SOC_H) // 2
soc_bg = soc_bg.crop((crop_x, crop_y, crop_x + SOC_W, crop_y + SOC_H))
social_img.paste(soc_bg, (0, 0))

soc_vig = Image.new("RGBA", (SOC_W, SOC_H), (0, 0, 0, 0))
draw_sv = ImageDraw.Draw(soc_vig)

for y in range(230):
    alpha = int(210 * (1.0 - y / 230.0)**1.3)
    draw_sv.line([(0, y), (SOC_W, y)], fill=(6, 8, 12, alpha))

for y in range(160):
    alpha = int(220 * (1.0 - y / 160.0)**1.4)
    draw_sv.line([(0, SOC_H - 1 - y), (SOC_W, SOC_H - 1 - y)], fill=(6, 8, 12, alpha))

social_img.paste(soc_vig, (0, 0), soc_vig)

logo_soc_w = 680
logo_soc_h = int(universal_logo.height * (logo_soc_w / universal_logo.width))
logo_soc_scaled = universal_logo.resize((logo_soc_w, logo_soc_h), Image.Resampling.LANCZOS)

soc_logo_x = (SOC_W - logo_soc_w) // 2
soc_logo_y = 18
social_img.paste(logo_soc_scaled, (soc_logo_x, soc_logo_y), logo_soc_scaled)

draw_soc = ImageDraw.Draw(social_img)
try:
    font_soc_tag = ImageFont.truetype("assets/fonts/Cinzel-Regular.ttf", 20)
    font_soc_pill = ImageFont.truetype("assets/fonts/Cinzel-Regular.ttf", 16)
except:
    font_soc_tag = ImageFont.load_default()
    font_soc_pill = ImageFont.load_default()

soc_tagline = "ONE STRIKE.  ONE KILL.  NO SECOND CHANCES."
bbox_tag = draw_soc.textbbox((0, 0), soc_tagline, font=font_soc_tag)
tag_w = bbox_tag[2] - bbox_tag[0]
tag_x = (SOC_W - tag_w) // 2
tag_y = soc_logo_y + logo_soc_h + 10

tag_pad_x, tag_pad_y = 16, 5
tag_bar = Image.new("RGBA", (tag_w + tag_pad_x * 2, (bbox_tag[3] - bbox_tag[1]) + tag_pad_y * 2), (0, 0, 0, 0))
draw_tb = ImageDraw.Draw(tag_bar)
draw_tb.rounded_rectangle((0, 0, tag_bar.width, tag_bar.height), radius=6, fill=(10, 12, 16, 190), outline=(212, 175, 55, 140), width=1)
social_img.paste(tag_bar, (tag_x - tag_pad_x, tag_y - tag_pad_y), tag_bar)

draw_soc.text((tag_x + 1, tag_y + 1), soc_tagline, font=font_soc_tag, fill=(0, 0, 0, 240))
draw_soc.text((tag_x, tag_y), soc_tagline, font=font_soc_tag, fill=(245, 225, 175, 255))

pill_text = "TACTICAL 1-HIT LETHAL DUELS  •  3D VOXEL & HD-2D  •  12 WARRIORS"
bbox_pill = draw_soc.textbbox((0, 0), pill_text, font=font_soc_pill)
pill_w = bbox_pill[2] - bbox_pill[0]
pill_x = (SOC_W - pill_w) // 2
pill_y = SOC_H - 52

pill_pad_x = 20
pill_pad_y = 8
pill_bar = Image.new("RGBA", (pill_w + pill_pad_x * 2, (bbox_pill[3] - bbox_pill[1]) + pill_pad_y * 2), (0, 0, 0, 0))
draw_pb = ImageDraw.Draw(pill_bar)
draw_pb.rounded_rectangle((0, 0, pill_bar.width, pill_bar.height), radius=8, fill=(12, 14, 18, 210), outline=(212, 175, 55, 160), width=1)
social_img.paste(pill_bar, (pill_x - pill_pad_x, pill_y - pill_pad_y), pill_bar)

draw_soc.text((pill_x, pill_y), pill_text, font=font_soc_pill, fill=(225, 230, 240, 240))

social_img.save(os.path.join(DEPLOY_DIR, "social_media_image.png"), "PNG")
social_img.save(os.path.join(PROMO_DIR, "social_media_image.png"), "PNG")
print(f"  Saved Social Media Image: {social_img.size[0]}x{social_img.size[1]} (aspect ratio: {social_img.size[0]/social_img.size[1]:.2f}:1)")

print("\nAll 4 promotional asset sets generated successfully!")
