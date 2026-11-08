"""
Rotation mit Eingabe: Du gibst Winkel und Vektor ein,
dann wird der Vektor gezeichnet und anschließend gedreht.
Der Code läuft von oben nach unten durch.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# ===== 1. Eingabe =====
# input() liefert immer Text. float() macht daraus eine Kommazahl.
# .replace(",", ".") erlaubt auch deutsche Schreibweise wie 2,5
print("--- Rotation eines Vektors ---")
end_angle = float(input("Drehwinkel θ in Grad: ").replace(",", "."))
x = float(input("x-Komponente des Vektors: ").replace(",", "."))
y = float(input("y-Komponente des Vektors: ").replace(",", "."))

vector = np.array([x, y])


# ===== 2. Weitere Einstellungen =====
PAUSE_FRAMES = 40     # so lange wird der Vektor erst still gezeigt
ROTATE_FRAMES = 60    # in so vielen Schritten wird gedreht
GRID_SIZE = 3


# ===== 3. Mathematik =====
def rotation_matrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s],
                     [s,  c]])


# Gitter: jede Linie besteht aus Anfangs- und Endpunkt
lines = []
for p in range(-GRID_SIZE, GRID_SIZE + 1):
    lines.append(np.array([[-GRID_SIZE, GRID_SIZE], [p, p]]))  # horizontal
    lines.append(np.array([[p, p], [-GRID_SIZE, GRID_SIZE]]))  # vertikal


# ===== 4. Fenster vorbereiten =====
fig, ax = plt.subplots(figsize=(6, 6))

# Achsen groß genug wählen, damit auch lange Vektoren reinpassen
length = np.linalg.norm(vector)          # Länge des Vektors
limit = max(GRID_SIZE * 1.5, length + 1)
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_aspect("equal")

# Startzustand blass im Hintergrund
for line in lines:
    ax.plot(line[0], line[1], color="lightgray")
ax.plot([0, x], [0, y], color="gray", lw=2, ls="--")

# Objekte, die sich bewegen werden (erst mal leer)
grid_plots = []
for line in lines:
    grid_plots.append(ax.plot([], [], color="tab:blue")[0])

vector_plot = ax.plot([], [], color="tab:red", lw=3, marker="o")[0]
info = ax.text(0.02, 0.96, "", transform=ax.transAxes)   # Text oben links


# ===== 5. Animation: wird für jedes Bild einmal aufgerufen =====
def update(frame):
    # Phase 1: Pause, Winkel bleibt 0
    if frame < PAUSE_FRAMES:
        angle = 0
    # Phase 2: Drehung von 0 bis end_angle
    else:
        step = frame - PAUSE_FRAMES
        angle = end_angle * step / (ROTATE_FRAMES - 1)

    R = rotation_matrix(np.radians(angle))

    for plot, line in zip(grid_plots, lines):
        rotated = R @ line
        plot.set_data(rotated[0], rotated[1])

    v = R @ vector
    vector_plot.set_data([0, v[0]], [0, v[1]])
    info.set_text(f"θ = {angle:.0f}°   v = ({v[0]:.2f}, {v[1]:.2f})")


total_frames = PAUSE_FRAMES + ROTATE_FRAMES
anim = FuncAnimation(fig, update, frames=total_frames, interval=30, repeat=False)
plt.show()


# ===== 6. Ergebnis in der Konsole =====
result = rotation_matrix(np.radians(end_angle)) @ vector
print("Vorher: ", vector)
print("Nachher:", np.round(result, 3))