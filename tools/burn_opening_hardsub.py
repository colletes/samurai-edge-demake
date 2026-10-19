#!/usr/bin/env python3
"""
Burn ASS subtitles into the opening video with native libass and VideoToolbox / x264 hardware encoding.
Generates: assets/Opening Videos/Samurai_Edge_Opening_Hardsub.mp4
"""
import os
import sys
import time
import ctypes
import subprocess
import cv2
import numpy as np

# Path configurations
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_VIDEO = os.path.join(ROOT, "assets/Opening Videos/Samurai_Edge_Opening_Final.mp4")
INPUT_ASS = os.path.join(ROOT, "assets/Opening Videos/Samurai_Edge_Opening_Final.ass")
OUTPUT_VIDEO = os.path.join(ROOT, "assets/Opening Videos/Samurai_Edge_Opening_Hardsub.mp4")

LIBASS_PATHS = [
    "/opt/homebrew/Cellar/libass/0.17.1/lib/libass.dylib",
    "/opt/homebrew/lib/libass.dylib",
    "/usr/local/lib/libass.dylib"
]

libass_path = None
for p in LIBASS_PATHS:
    if os.path.exists(p):
        libass_path = p
        break

if not libass_path:
    print("Error: libass.dylib not found")
    sys.exit(1)

libass = ctypes.CDLL(libass_path)

class ASS_Image(ctypes.Structure):
    pass

ASS_Image._fields_ = [
    ('w', ctypes.c_int),
    ('h', ctypes.c_int),
    ('stride', ctypes.c_int),
    ('bitmap', ctypes.POINTER(ctypes.c_uint8)),
    ('color', ctypes.c_uint32),
    ('dst_x', ctypes.c_int),
    ('dst_y', ctypes.c_int),
    ('next', ctypes.POINTER(ASS_Image))
]

libass.ass_library_init.restype = ctypes.c_void_p
libass.ass_renderer_init.restype = ctypes.c_void_p
libass.ass_renderer_init.argtypes = [ctypes.c_void_p]

libass.ass_set_frame_size.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
libass.ass_set_fonts.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
libass.ass_read_file.restype = ctypes.c_void_p
libass.ass_read_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]

libass.ass_render_frame.restype = ctypes.POINTER(ASS_Image)
libass.ass_render_frame.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_longlong, ctypes.POINTER(ctypes.c_int)]

def main():
    print(f"Loading libass from: {libass_path}")
    ass_lib = libass.ass_library_init()
    renderer = libass.ass_renderer_init(ass_lib)
    
    cap = cv2.VideoCapture(INPUT_VIDEO)
    if not cap.isOpened():
        print(f"Error opening video: {INPUT_VIDEO}")
        sys.exit(1)
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video info: {width}x{height} @ {fps:.2f} FPS ({total_frames} total frames)")
    
    libass.ass_set_frame_size(renderer, width, height)
    libass.ass_set_fonts(renderer, None, b"Trebuchet MS", 1, None, 1)
    
    ass_track = libass.ass_read_file(ass_lib, INPUT_ASS.encode("utf-8"), b"UTF-8")
    if not ass_track:
        print(f"Error reading ASS track: {INPUT_ASS}")
        sys.exit(1)
        
    # Start ffmpeg encoder process reading raw video from pipe and original audio from input video
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
        "-i", INPUT_VIDEO,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "h264_videotoolbox",
        "-b:v", "5000k",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        OUTPUT_VIDEO
    ]
    
    print("Launching ffmpeg writer process...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    detect_change = ctypes.c_int(0)
    frame_idx = 0
    t0 = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break
            
        ms = int((frame_idx / fps) * 1000)
        img_ptr = libass.ass_render_frame(renderer, ass_track, ms, ctypes.byref(detect_change))
        
        curr = img_ptr
        while curr:
            img = curr.contents
            w, h, stride = img.w, img.h, img.stride
            dst_x, dst_y = img.dst_x, img.dst_y
            color = img.color
            
            # Extract color channels and ASS alpha
            r = (color >> 24) & 0xFF
            g = (color >> 16) & 0xFF
            b = (color >> 8) & 0xFF
            a = 255 - (color & 0xFF)
            
            if a > 0 and w > 0 and h > 0:
                buf = np.ctypeslib.as_array(img.bitmap, shape=(h, stride))[:, :w]
                alpha = (buf.astype(np.float32) / 255.0) * (a / 255.0)
                
                x1, y1 = max(0, dst_x), max(0, dst_y)
                x2, y2 = min(width, dst_x + w), min(height, dst_y + h)
                
                bx1, by1 = x1 - dst_x, y1 - dst_y
                bx2, by2 = bx1 + (x2 - x1), by1 + (y2 - y1)
                
                sub_alpha = alpha[by1:by2, bx1:bx2, np.newaxis]
                rgb_val = np.array([b, g, r], dtype=np.float32)
                
                slice_dst = frame[y1:y2, x1:x2].astype(np.float32)
                frame[y1:y2, x1:x2] = (slice_dst * (1.0 - sub_alpha) + rgb_val * sub_alpha).astype(np.uint8)
                
            curr = img.next
            
        proc.stdin.write(frame.tobytes())
        frame_idx += 1
        
        if frame_idx % 240 == 0 or frame_idx == total_frames:
            elapsed = time.time() - t0
            cur_fps = frame_idx / elapsed if elapsed > 0 else 0
            pct = (frame_idx / total_frames) * 100
            print(f"Progress: {frame_idx}/{total_frames} ({pct:.1f}%) @ {cur_fps:.1f} FPS")
            
    cap.release()
    proc.stdin.close()
    proc.wait()
    
    elapsed = time.time() - t0
    out_size = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"\nDone! Hardsub video generated in {elapsed:.1f}s ({frame_idx/elapsed:.1f} FPS):")
    print(f"Output: {OUTPUT_VIDEO} ({out_size:.1f} MB)")

if __name__ == "__main__":
    main()
