# streamlit_app.py
import streamlit as st
import math, random, io, time
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(layout="centered", page_title="Birthday Heart Animation")

# ---------- Parameters (tweak to trade quality vs speed) ----------
W, H = 900, 700
FRAMES = 140            # total frames of GIF (smaller -> faster generation)
HEART_STEPS = 400       # number of param points along the heart (kept same as your code)
HEART_PER_FRAME = 3     # how many heart steps to draw per frame (controls drawing speed)
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
HEART_COLOR = (255, 40, 40)
GIF_DURATION = 40       # ms per frame

# ---------- Heart parametric functions (exact math you used) ----------
def hearta(k):
    return 15 * math.sin(k) ** 3

def heartb(k):
    return 12 * math.cos(k) - 5 * math.cos(2 * k) - 2 * math.cos(3 * k) - math.cos(4 * k)

# ---------- Prepare balloons and glitters ----------
NUM_BALLOONS = 8
NUM_GLITTERS = 60

class Balloon:
    def __init__(self):
        self.x = random.randint(50, W-50)
        self.y = random.randint(H//2 - 50, H - 40)
        self.size = random.randint(14, 28)
        self.color = tuple(int(x*255) for x in ImageColor_safe(random.choice(["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#C792EA"])))
        self.speed = random.uniform(0.6, 2.0)
    def step(self):
        self.y -= self.speed
        if self.y < -50:
            self.y = H + 40
            self.x = random.randint(50, W-50)

def ImageColor_safe(hexcolor):
    # converts "#RRGGBB" to normalized floats (0..1)
    hexcolor = hexcolor.lstrip("#")
    r = int(hexcolor[0:2],16)/255.0
    g = int(hexcolor[2:4],16)/255.0
    b = int(hexcolor[4:6],16)/255.0
    return (r,g,b)

balloons = [Balloon() for _ in range(NUM_BALLOONS)]
glitters = []
for _ in range(NUM_GLITTERS):
    gx = random.randint(10, W-10)
    gy = random.randint(10, H-10)
    sp = random.uniform(0.04, 0.12)
    seed = random.random()*10
    glitters.append((gx, gy, sp, seed))

# ---------- Font ----------
try:
    # try a nicer truetype font if available
    font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    font_small = ImageFont.truetype("DejaVuSans.ttf", 16)
except Exception:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# ---------- Build frames ----------
st.info("Generating animation frames — this may take a few seconds.")
progress = st.progress(0)

frames = []
# Precompute heart coords for HEART_STEPS to match your paramization
heart_coords = []
for i in range(HEART_STEPS):
    k = i
    x = hearta(k) * 20
    y = heartb(k) * 20
    # map heart (0,0) center to canvas center
    px = int(W/2 + x)
    py = int(H/2 - y)
    heart_coords.append((px, py))

# We'll reveal the text first for a number of frames, then start plotting the heart points
text_frames = max(8, int(FRAMES * 0.12))  # show typing text for this many frames
# Total heart points to draw across the animation:
total_heart_points = HEART_STEPS
points_drawn = 0

for f in range(FRAMES):
    # create base image
    im = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(im)

    # draw balloons (background)
    for b in balloons:
        # simple oval as balloon
        bx, by = int(b.x), int(b.y)
        r = b.size
        draw.ellipse([bx-r, by-r, bx+r, by+r], fill=b.color)
        # string
        draw.line([(bx, by+r), (bx, by+r+28)], fill=(220,220,220))

    # draw glitters: twinkle using sin(t)
    for gx, gy, sp, seed in glitters:
        v = (math.sin(f * sp + seed) + 1) / 2
        size = 1 + 3 * v
        brightness = int(180 + 75 * v)
        draw.ellipse([gx-size, gy-size, gx+size, gy+size], fill=(brightness, brightness, brightness))

    # typing text phase
    if f < text_frames:
        # show typing effect: characters revealed proportional to frame number
        full_text = "Happy Birthday\nBestie ❤ 🎂"
        total_chars = len(full_text)
        visible_chars = int((f+1) / text_frames * total_chars)
        visible = full_text[:visible_chars]
        w, h = draw.multiline_textsize(visible, font=font_large, spacing=6)
        draw.multiline_text(((W-w)/2, (H/2 - 40) - h/2), visible, font=font_large, fill=TEXT_COLOR, align="center", spacing=6)
    else:
        # text stays visible after typing is done
        draw.multiline_text(((W/2)-200, (H/2 - 40) - 10), "Happy Birthday\nBestie ❤ 🎂", font=font_large, fill=TEXT_COLOR, align="center", spacing=6)

    # after typing finished, start drawing the heart progressively
    if f >= text_frames:
        # determine how many heart points to draw by this frame
        frames_since_text = f - text_frames
        points_to_draw = min(total_heart_points, (frames_since_text + 1) * HEART_PER_FRAME)
        # draw heart points up to points_to_draw
        for p in range(points_to_draw):
            px, py = heart_coords[p]
            # small red dot
            draw.ellipse([px-3, py-3, px+3, py+3], fill=HEART_COLOR)
        points_drawn = points_to_draw

    # step balloons upward a little for next frame
    for b in balloons:
        b.step()

    # we want some extra sparkle near the latest heart point occasionally
    if points_drawn > 0 and random.random() > 0.96:
        px, py = heart_coords[min(points_drawn-1, total_heart_points-1)]
        sx = random.randint(-12,12)
        sy = random.randint(-12,12)
        draw.ellipse([px+sx-6, py+sy-6, px+sx+6, py+sy+6], fill=(255,220,80))

    # append frame
    frames.append(im.convert("P"))  # palettized image for GIF efficiency

    # progress update
    progress.progress(int((f+1)/FRAMES * 100))

# Save to in-memory GIF
buf = io.BytesIO()
frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=GIF_DURATION, loop=0, optimize=True)
buf.seek(0)

st.success("Animation generated!")
st.image(buf.getvalue(), caption="Happy Birthday Animation", use_column_width=True)

# Optional: allow download of GIF
st.download_button("Download GIF", data=buf.getvalue(), file_name="birthday_heart.gif", mime="image/gif")

