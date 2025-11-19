# streamlit_app.py
for gx, gy, sp, seed in glitters:
v = (math.sin(f * sp + seed) + 1) / 2
size = 1 + 3 * v
brightness = int(180 + 75 * v)
draw.ellipse([gx-size, gy-size, gx+size, gy+size], fill=(brightness, brightness, brightness))


# typing text
if f < text_frames:
full_text = "Happy Birthday\nBestie ❤ 🎂"
total_chars = len(full_text)
visible_chars = int((f+1) / text_frames * total_chars)
visible = full_text[:visible_chars]
w, h = draw.multiline_textsize(visible, font=font_large, spacing=6)
draw.multiline_text(((W-w)/2, (H/2 - 40) - h/2), visible, font=font_large, fill=TEXT_COLOR, align="center", spacing=6)
else:
draw.multiline_text(((W/2)-200, (H/2 - 40) - 10), "Happy Birthday\nBestie ❤ 🎂", font=font_large, fill=TEXT_COLOR, align="center", spacing=6)


# heart drawing
if f >= text_frames:
frames_since_text = f - text_frames
points_to_draw = min(total_heart_points, (frames_since_text + 1) * HEART_PER_FRAME)
for p in range(points_to_draw):
px, py = heart_coords[p]
draw.ellipse([px-3, py-3, px+3, py+3], fill=HEART_COLOR)
points_drawn = points_to_draw


# step balloons
for b in balloons:
b.step()


# occasional sparkle near heart
if points_drawn > 0 and random.random() > 0.96:
px, py = heart_coords[min(points_drawn-1, total_heart_points-1)]
sx = random.randint(-12,12)
sy = random.randint(-12,12)
draw.ellipse([px+sx-6, py+sy-6, px+sx+6, py+sy+6], fill=(255,220,80))


frames_list.append(im.convert("P"))


if show_preview_only:
break


return frames_list


# ---------- UI and generation ----------
st.write("# Birthday Heart — GIF generator")
if use_uploaded_video:
st.info("Using uploaded local file if present: /mnt/data/Screen Recording 2025-11-19 185503.mp4")


if st.button("Generate animation"):
with st.spinner("Generating frames — this may take a few seconds..."):
frames = build_frames(frames=FRAMES, show_preview_only=show_preview)
buf = io.BytesIO()
frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=GIF_DURATION, loop=0, optimize=True)
buf.seek(0)
st.image(buf.getvalue(), caption="Happy Birthday Animation", use_column_width=True)
st.download_button("Download GIF", data=buf.getvalue(), file_name="birthday_heart.gif", mime="image/gif")


# Small preview automatically
if show_preview:
preview_frames = build_frames(frames=6, show_preview_only=True)
bufp = io.BytesIO()
preview_frames[0].save(bufp, format="GIF", save_all=True, append_images=preview_frames[1:], duration=120, loop=0, optimize=True)
bufp.seek(0)
st.image(bufp.getvalue(), caption="Preview", use_column_width=True)


# If the user uploaded a file during the session and it's available at the path below, show it.
uploaded_path = "/mnt/data/Screen Recording 2025-11-19 185503.mp4"
try:
with open(uploaded_path, "rb") as fh:
st.video(fh.read())
except Exception:
# ignore if not available
pass

