import streamlit as st
import math
import random
import io
import time
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(layout="centered", page_title="Birthday Heart Animation")

# ---------- Default Parameters (tweak for performance) ----------
W, H = 900, 700
DEFAULT_FRAMES = 140          # total frames of GIF (smaller -> faster generation)
HEART_STEPS = 400             # keeps the same paramization you used
DEFAULT_HEART_PER_FRAME = 3   # how many heart steps to draw per frame
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
HEART_COLOR = (255, 40, 40)
GIF_DURATION = 40             # ms per frame

# ---------- Heart parametric functions (exact math you used) ----------
def hearta(k):
    return 15 * math.sin(k) ** 3

def heartb(k):
    return 12 * math.cos(k) - 5 * math.cos(2 * k) - 2 * math.cos(3 * k) - math.cos(4 * k)

# ---------- Sidebar UI ----------
st.sidebar.header("Animation settings")
frames_input = st.sidebar.slider("Frames (smaller = faster)", 40, 300, DEFAULT_FRAMES)
heart_per_frame = st.sidebar.slider("Heart points per frame", 1, 8, DEFAULT_HEART_PER_FRAME)
show_preview = st.sidebar.checkbox("Show single-frame preview (faster)", value=False)
use_uploaded_video = st.sidebar.checkbox("Show uploaded screen recording (if available)", value=False)

FRAMES = frames_input
HEART_PER_FRAME = heart_per_frame

# ---------- Prepare balloons and glitters ----------
NUM_BALLOONS = 8
NUM_GLITTERS = 60

class Balloon:
    def __init__(self):
        self.x = random.randint(50, W - 50)
        self.y = random.randint(H // 2 - 50, H - 40)
        self.size = random.randint(14, 28)
        self.color = random.choice([
            (255, 107, 107),  # #FF6B6B
            (255, 217, 61),   # #FFD93D
            (107, 203, 119),  # #6BCB77
            (77, 150, 255),   # #4D96FF
            (199, 146, 234)   # #C792EA
        ])
        self.speed = random.uniform(0.6, 2.0)

    def step(self):
        self.y -= self.speed
        if self.y < -50:
            self.y = H + 40
            self.x = random.randint(50, W - 50)

balloons = [Balloon() for _ in range(NUM_BALLOONS)]

glitters = []
for _ in range(NUM_GLITTERS):
    gx = random.randint(10, W - 10)
    gy = random.randint(10, H - 10)
    sp = random.uniform(0.04, 0.12)
    seed = random.random() * 10
    glitters.append((gx, gy, sp, seed))

# ---------- Fonts ----------
try:
    font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    font_small = ImageFont.truetype("DejaVuSans.ttf", 16)
except Exception:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# ---------- Frame builder ----------
def build_frames(frames=FRAMES, show_preview_only=False):
    heart_coords = []
    for i in range(HEART_STEPS):
        k = i
        x = hearta(k) * 20
        y = heartb(k) * 20
        px = int(W / 2 + x)
        py = int(H / 2 - y)
        heart_coords.append((px, py))

    text_frames = max(6, int(frames * 0.12))
    total_heart_points = HEART_STEPS
    points_drawn = 0

    frames_list = []
    for f in range(frames):
        im = Image.new("RGB", (W, H), BG_COLOR)
        draw = ImageDraw.Draw(im)

        # draw balloons (background)
        for b in balloons:
            bx, by = int(b.x), int(b.y)
            r = b.size
            draw.ellipse([bx - r, by - r, bx + r, by + r], fill=b.color)
            draw.line([(bx, by + r), (bx, by + r + 28)], fill=(220, 220, 220))

        # draw glitters (twinkling)
        for gx, gy, sp, seed in glitters:
            v = (math.sin(f * sp + seed) + 1) / 2
            size = 1 + 3 * v
            brightness = int(180 + 75 * v)
            draw.ellipse([gx - size, gy - size, gx + size, gy + size], fill=(brightness, brightness, brightness))

        # typing text phase
        if f < text_frames:
            full_text = "Happy Birthday\nBestie ❤ 🎂"
            total_chars = len(full_text)
            visible_chars = int((f + 1) / text_frames * total_chars)
            visible = full_text[:visible_chars]
            bbox = draw.multiline_textbbox((0, 0), visible, font=font_large, spacing=6)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.multiline_text(((W - w) / 2, (H / 2 - 40) - h / 2), visible,
                                font=font_large, fill=TEXT_COLOR, align="center", spacing=6)
        else:
            draw.multiline_text(((W / 2) - 200, (H / 2 - 40) - 10), "Happy Birthday\nBestie ❤ 🎂",
                                font=font_large, fill=TEXT_COLOR, align="center", spacing=6)

        # draw heart progressively after text phase
        if f >= text_frames:
            frames_since_text = f - text_frames
            points_to_draw = min(total_heart_points, (frames_since_text + 1) * HEART_PER_FRAME)
            for p in range(points_to_draw):
                px, py = heart_coords[p]
                draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=HEART_COLOR)
            points_drawn = points_to_draw

        # advance balloons
        for b in balloons:
            b.step()

        # occasional sparkle near heart
        if points_drawn > 0 and random.random() > 0.96:
            px, py = heart_coords[min(points_drawn - 1, total_heart_points - 1)]
            sx = random.randint(-12, 12)
            sy = random.randint(-12, 12)
            draw.ellipse([px + sx - 6, py + sy - 6, px + sx + 6, py + sy + 6], fill=(255, 220, 80))

        frames_list.append(im.convert("P"))

        if show_preview_only:
            break

    return frames_list

# ---------- Page UI ----------
st.write("# Birthday Heart — GIF generator")

uploaded_path = "/mnt/data/Screen Recording 2025-11-19 185503.mp4"
if use_uploaded_video:
    st.info(f"Attempting to show uploaded file (if available): {uploaded_path}")

if st.button("Generate animation"):
    with st.spinner("Generating frames — this may take a few seconds..."):
        frames = build_frames(frames=FRAMES, show_preview_only=show_preview)
        buf = io.BytesIO()
        frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=GIF_DURATION, loop=0, optimize=True)
        buf.seek(0)
        st.image(buf.getvalue(), caption="Happy Birthday Animation", use_column_width=True)
        st.download_button("Download GIF", data=buf.getvalue(), file_name="birthday_heart.gif", mime="image/gif")

# small preview auto
if show_preview:
    preview_frames = build_frames(frames=6, show_preview_only=True)
    bufp = io.BytesIO()
    preview_frames[0].save(bufp, format="GIF", save_all=True, append_images=preview_frames[1:], duration=120, loop=0, optimize=True)
    bufp.seek(0)
    st.image(bufp.getvalue(), caption="Preview", use_column_width=True)

# show uploaded video if requested and available on the instance
if use_uploaded_video:
    try:
        with open(uploaded_path, "rb") as fh:
            st.video(fh.read())
    except Exception:
        st.info("Uploaded file not found at the path; if you want it displayed in production, place it in your repo's assets and update the path in the code.")

st.write("----")
st.markdown("Tip: reduce **Frames** or **Image size** in the code for faster generation on Streamlit Cloud.")


