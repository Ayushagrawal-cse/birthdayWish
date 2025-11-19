import math
import random
import time
from turtle import Screen, Turtle, speed, bgcolor, goto, color, dot, done

# ---------- Heart math (single definition) ----------
def hearta(k):
    return 15 * math.sin(k) ** 3

def heartb(k):
    return 12 * math.cos(k) - 5 * math.cos(2 * k) - 2 * math.cos(3 * k) - math.cos(4 * k)

# ---------- Screen setup ----------
screen = Screen()
screen.setup(900, 700)
screen.bgcolor("black")
screen.title("Happy Birthday Heart")
screen.tracer(0)   # manual updates for smooth animation

# ---------- Typing text (module-level turtle used for simplicity) ----------
text_t = Turtle()
text_t.hideturtle()
text_t.penup()
text_t.color("white")
text_t.goto(0, -15)

message = "Happy Birthday\nBestie ❤ 🎂"
display = ""
for ch in message:
    display += ch
    text_t.clear()
    text_t.write(display, align="center", font=("Arial", 28, "bold"))
    screen.update()
    time.sleep(0.06 if ch != "\n" else 0.22)

time.sleep(0.25)  # small pause before heart starts

# ---------- Background animation turtles ----------
glitter_t = Turtle(visible=False)
glitter_t.hideturtle()
glitter_t.penup()

balloon_t = Turtle(visible=False)
balloon_t.hideturtle()
balloon_t.penup()

# ---------- Prepare glitters (twinkling points) ----------
glitters = []
for _ in range(60):
    gx = random.randint(-420, 420)
    gy = random.randint(-320, 320)
    sp = random.uniform(0.5, 2.0)
    seed = random.random() * 10
    glitters.append({"x": gx, "y": gy, "speed": sp, "seed": seed})

def draw_glitters(tick):
    glitter_t.clear()
    for g in glitters:
        v = (math.sin(tick * g["speed"] + g["seed"]) + 1) / 2  # 0..1
        size = 1.0 + 3.0 * v
        # occasionally warm sparkle
        if v > 0.78 and random.random() > 0.85:
            glitter_t.color("#FFFACD")
        else:
            glitter_t.color("white")
        glitter_t.goto(g["x"], g["y"])
        glitter_t.dot(size)

# ---------- Prepare balloons ----------
class Balloon:
    def __init__(self):
        self.x = random.randint(-380, 380)
        self.y = random.randint(-340, 340)
        self.color = random.choice(["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#C792EA"])
        self.size = random.randint(12, 28)
        self.speed = random.uniform(0.2, 1.0)

    def step(self):
        self.y += self.speed
        if self.y > 380:
            # wrap to bottom with new x, size, color
            self.y = -380
            self.x = random.randint(-380, 380)
            self.size = random.randint(12, 28)
            self.color = random.choice(["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#C792EA"])
            self.speed = random.uniform(0.2, 1.0)

    def draw(self, t: Turtle):
        t.goto(self.x, self.y)
        t.color(self.color)
        t.begin_fill()
        t.pendown()
        t.circle(self.size)
        t.penup()
        t.end_fill()
        # string
        t.goto(self.x, self.y - self.size)
        t.color("white")
        t.pendown()
        t.setheading(-90)
        t.forward(24)
        t.penup()

balloons = [Balloon() for _ in range(8)]

def draw_balloons():
    balloon_t.clear()
    for b in balloons:
        b.draw(balloon_t)

# ---------- Heart drawing (exact style you used) ----------
speed(0)         # fastest drawing speed
bgcolor("black") # keep background black

tick = 0.0
# use the default turtle with goto()/dot() like your original
for i in range(400):
    # move along the heart parametric path (keeps exact behavior)
    x = hearta(i) * 20
    y = heartb(i) * 20
    goto(x, y)
    color("red")
    dot()   # same as your original

    # update background objects each frame
    # step balloons
    for b in balloons:
        b.step()
    draw_balloons()

    # draw twinkling glitters
    draw_glitters(tick)

    # occasional extra sparkle near heart
    if random.random() > 0.986:
        glitter_t.goto(x + random.randint(-10, 10), y + random.randint(-10, 10))
        glitter_t.dot(random.randint(5, 8))

    # show frame
    screen.update()
    tick += 0.06

# ensure final frame is visible
screen.tracer(1)
text_t.goto(0, -260)
text_t.write("Press any key or close window to exit", align="center", font=("Arial", 12, "normal"))

goto(0, 0)
done()
