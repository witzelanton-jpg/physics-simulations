import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _(BLAU, GRUEN, ORANGE, farbig, mo):
    mo.md(f"""
    # Rotation und Divergenz eines Vektorfelds

    Stell dir das Vektorfeld $\\vec F(x, y)$ als Strömung vor. Mit **Strömung starten**
    schwimmen {farbig("Teilchen", BLAU)} mit dem Feld. Am Messpunkt $P$ gibt es zwei
    „Messgeräte“:

    - Ein {farbig("Farbfleck", ORANGE)} bei $P$ wird von der Strömung verformt. Seine Fläche wächst, wenn
      $\\operatorname{{div}} \\vec F > 0$ (Quelle), und schrumpft, wenn
      $\\operatorname{{div}} \\vec F < 0$ (Senke).
    - Ein verankertes {farbig("Schaufelrad", GRUEN)} dreht sich mit der Winkelgeschwindigkeit
      $\\omega = \\tfrac12 \\operatorname{{rot}} \\vec F$: gegen den Uhrzeigersinn bei
      $\\operatorname{{rot}} \\vec F > 0$, im Uhrzeigersinn bei $\\operatorname{{rot}} \\vec F < 0$.

    $$ \\operatorname{{div}} \\vec F = \\frac{{\\partial F_x}}{{\\partial x}} +
    \\frac{{\\partial F_y}}{{\\partial y}}, \\qquad
    \\operatorname{{rot}} \\vec F = \\frac{{\\partial F_y}}{{\\partial x}} -
    \\frac{{\\partial F_x}}{{\\partial y}} $$

    **Gradientenfelder** $\\vec F = \\nabla \\varphi$ sind immer wirbelfrei
    ($\\operatorname{{rot}} \\vec F = 0$): Dort dreht sich das Schaufelrad nie.
    In der Auswahl sind sie mit „Gradientenfeld“ markiert.
    """)
    return


@app.cell
def _():
    import time
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.patches import Polygon
    return LineCollection, Polygon, mo, np, plt, time


@app.cell
def _():
    # ===== Farben =====
    BLAU = "#1f77b4"    # Teilchen
    ORANGE = "#ff8c00"  # Farbfleck (Divergenz)
    GRUEN = "#2ca02c"   # Schaufelrad (Rotation)

    def farbig(text, color):
        """Färbt normalen Text (Markdown/HTML)."""
        return f'<span style="color:{color}">{text}</span>'

    def tex(formel, color):
        """Färbt einen Teil einer LaTeX-Formel."""
        return r"\textcolor{" + color + "}{" + formel + "}"
    return BLAU, GRUEN, ORANGE, farbig, tex


@app.cell
def _(mo, np):
    # ===== 1. Eingabe =====
    # Jedes Feld: (Funktion, LaTeX für F, LaTeX für div, LaTeX für rot)
    FELDER = {
        "Quelle: F = (x, y) · Gradientenfeld": (
            lambda x, y: (x, y), r"(x,\ y)", "2", "0"),
        "Senke: F = (−x, −y) · Gradientenfeld": (
            lambda x, y: (-x, -y), r"(-x,\ -y)", "-2", "0"),
        "Sattel: F = (x, −y) · Gradientenfeld": (
            lambda x, y: (x, -y), r"(x,\ -y)", "0", "0"),
        "Hügel und Täler: F = (sin x, cos y) · Gradientenfeld": (
            lambda x, y: (np.sin(x), np.cos(y)), r"(\sin x,\ \cos y)",
            r"\cos x - \sin y", "0"),
        "Wirbel: F = (−y, x)": (
            lambda x, y: (-y, x), r"(-y,\ x)", "0", "2"),
        "Scherströmung: F = (y, 0)": (
            lambda x, y: (y, 0 * x), r"(y,\ 0)", "0", "-1"),
        "Spiralquelle: F = (x − y, x + y)": (
            lambda x, y: (x - y, x + y), r"(x - y,\ x + y)", "2", "2"),
        "Lokaler Wirbel: F = (−y, x)·exp(−r²/2)": (
            lambda x, y: (-y * np.exp(-(x**2 + y**2) / 2), x * np.exp(-(x**2 + y**2) / 2)),
            r"(-y,\ x)\,e^{-r^2/2}", "0", r"(2 - r^2)\,e^{-r^2/2}"),
    }
    feld_wahl = mo.ui.dropdown(list(FELDER), value="Hügel und Täler: F = (sin x, cos y) · Gradientenfeld",
                               label="Vektorfeld")
    heatmap_wahl = mo.ui.radio(["Divergenz", "Rotation"], value="Divergenz",
                               label="Hintergrundfarbe zeigt", inline=True)
    px_slider = mo.ui.slider(-2.5, 2.5, step=0.1, value=1.0, show_value=True,
                             label="Messpunkt P: x")
    py_slider = mo.ui.slider(-2.5, 2.5, step=0.1, value=-0.5, show_value=True,
                             label="Messpunkt P: y")
    run_button = mo.ui.run_button(label="▶ Strömung starten")
    mo.vstack([
        feld_wahl,
        heatmap_wahl,
        mo.hstack([px_slider, py_slider], justify="start"),
        run_button,
    ])
    return FELDER, feld_wahl, heatmap_wahl, px_slider, py_slider, run_button


@app.cell
def _(FELDER, feld_wahl, np, px_slider, py_slider):
    # ===== 2. Feld, Divergenz und Rotation =====
    F, F_tex, div_tex, rot_tex = FELDER[feld_wahl.value]
    P = np.array([px_slider.value, py_slider.value])
    _H = 1e-4

    def feld(x, y):
        fx, fy = F(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
        return np.asarray(fx, dtype=float), np.asarray(fy, dtype=float)

    def divergenz(x, y):
        """div F = ∂Fx/∂x + ∂Fy/∂y (numerisch, zentrale Differenzen)."""
        return ((feld(x + _H, y)[0] - feld(x - _H, y)[0])
                + (feld(x, y + _H)[1] - feld(x, y - _H)[1])) / (2 * _H)

    def rotation(x, y):
        """rot F = ∂Fy/∂x − ∂Fx/∂y (numerisch, zentrale Differenzen)."""
        return ((feld(x + _H, y)[1] - feld(x - _H, y)[1])
                - (feld(x, y + _H)[0] - feld(x, y - _H)[0])) / (2 * _H)

    div_P = float(divergenz(P[0], P[1]))
    rot_P = float(rotation(P[0], P[1]))
    return F_tex, P, div_P, div_tex, divergenz, feld, rot_P, rot_tex, rotation


@app.cell
def _(F_tex, GRUEN, ORANGE, P, div_P, div_tex, mo, rot_P, rot_tex, tex):
    # ===== 3. Formeln =====
    _div = tex(rf"\operatorname{{div}} \vec F = {div_tex}", ORANGE)
    _rot = tex(rf"\operatorname{{rot}} \vec F = {rot_tex}", GRUEN)
    _divP = tex(rf"\operatorname{{div}} \vec F(P) = {div_P:.2f}", ORANGE)
    _rotP = tex(rf"\operatorname{{rot}} \vec F(P) = {rot_P:.2f}", GRUEN)
    mo.md(
        rf"""
        $$ \vec F(x, y) = {F_tex}, \qquad {_div}, \qquad {_rot} $$

        $$ P = ({P[0]:g},\ {P[1]:g}): \qquad {_divP}, \qquad {_rotP} $$
        """
    )
    return


@app.cell
def _(
    BLAU,
    GRUEN,
    LineCollection,
    ORANGE,
    P,
    Polygon,
    div_P,
    divergenz,
    feld,
    heatmap_wahl,
    np,
    plt,
    rot_P,
    rotation,
):
    # ===== 4. Szene mit Strömungssimulation =====
    L = 3.0
    N_TEILCHEN = 350
    FLECK_RADIUS = 0.2
    RAD_RADIUS = 0.45

    _g = np.linspace(-L, L, 150)
    hx, hy = np.meshgrid(_g, _g)
    if heatmap_wahl.value == "Divergenz":
        heat = divergenz(hx, hy)
        heat_titel = "div F"
    else:
        heat = rotation(hx, hy)
        heat_titel = "rot F"
    heat_max = max(np.abs(heat).max(), 0.5)

    qx, qy = np.meshgrid(np.linspace(-L, L, 19), np.linspace(-L, L, 19))
    qfx, qfy = feld(qx, qy)
    qbetrag = np.sqrt(qfx**2 + qfy**2) + 1e-12

    # Simulierte Zeit so wählen, dass sich die Teilchen gut sichtbar bewegen
    _speed = np.mean(np.sqrt(feld(hx, hy)[0]**2 + feld(hx, hy)[1]**2))
    T_SIM = float(np.clip(2.2 / max(_speed, 1e-3), 0.8, 8))

    def rk4(pos, dt):
        """Ein Runge-Kutta-Schritt für dr/dt = F(r). pos: Form (2, n)."""
        k1 = np.array(feld(*pos))
        k2 = np.array(feld(*(pos + 0.5 * dt * k1)))
        k3 = np.array(feld(*(pos + 0.5 * dt * k2)))
        k4 = np.array(feld(*(pos + dt * k3)))
        return pos + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

    def flaeche(pts):
        """Fläche eines Polygons (Gaußsche Trapezformel)."""
        x, y = pts
        return abs(0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))

    def make_scene():
        rng = np.random.default_rng(1)
        fig, ax = plt.subplots(figsize=(8, 7.5), dpi=80)
        im = ax.imshow(heat, extent=(-L, L, -L, L), origin="lower", cmap="RdBu_r",
                       vmin=-heat_max, vmax=heat_max, alpha=0.55)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03, label=heat_titel)
        ax.quiver(qx, qy, qfx / qbetrag, qfy / qbetrag, color="black", alpha=0.45,
                  scale=26, width=0.0035)
        ax.set_xlim(-L, L)
        ax.set_ylim(-L, L)
        ax.set_aspect("equal")
        ax.plot(*P, "+", color="black", ms=12, mew=2, zorder=8)
        ax.text(P[0] + 0.1, P[1] + 0.1, "P", fontsize=12, zorder=8)

        state = {}

        # Teilchen mit begrenzter Lebensdauer: danach tauchen sie woanders neu auf
        def neu_verteilen(maske):
            state["pos"][:, maske] = rng.uniform(-L, L, size=(2, maske.sum()))
            state["alter"][maske] = 0
            state["lebensdauer"][maske] = rng.uniform(0.3, 1.0, maske.sum()) * T_SIM

        state["pos"] = np.zeros((2, N_TEILCHEN))
        state["alter"] = np.zeros(N_TEILCHEN)
        state["lebensdauer"] = np.zeros(N_TEILCHEN)
        neu_verteilen(np.ones(N_TEILCHEN, dtype=bool))
        state["alter"] = rng.uniform(0, 1, N_TEILCHEN) * state["lebensdauer"]
        teilchen, = ax.plot([], [], "o", color=BLAU, ms=3, zorder=5)

        # Farbfleck (Divergenz): Kreis aus Punkten, der mitschwimmt
        _phi = np.linspace(0, 2 * np.pi, 240, endpoint=False)
        state["fleck"] = P[:, None] + FLECK_RADIUS * np.array([np.cos(_phi), np.sin(_phi)])
        fleck_start = flaeche(state["fleck"])
        fleck = Polygon(state["fleck"].T, closed=True, facecolor=ORANGE, alpha=0.6,
                        edgecolor=ORANGE, lw=2, zorder=6)
        ax.add_patch(fleck)

        # Schaufelrad (Rotation): am Punkt P verankert, dreht sich mit ω = rot/2
        state["winkel"] = 0.0
        rad = LineCollection([], color=GRUEN, lw=3, zorder=7)
        ax.add_collection(rad)
        rad_ring = plt.Circle(P, RAD_RADIUS, fill=False, color=GRUEN, lw=1.5, zorder=7)
        ax.add_patch(rad_ring)

        def zeichne_rad():
            a = state["winkel"] + np.arange(4) * np.pi / 2
            spitzen = P[:, None] + RAD_RADIUS * np.array([np.cos(a), np.sin(a)])
            rad.set_segments([[P, spitzen[:, i]] for i in range(4)])

        zeichne_rad()
        state["t"] = 0.0

        def info_line(row, color):
            return ax.text(0.02, 0.97 - 0.05 * row, "", color=color, transform=ax.transAxes,
                           va="top", zorder=9,
                           bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
        info_div = info_line(0, ORANGE)
        info_rot = info_line(1, GRUEN)

        def schreibe_info():
            faktor = flaeche(state["fleck"]) / fleck_start
            art = "Quelle" if div_P > 0.05 else "Senke" if div_P < -0.05 else "quellenfrei"
            info_div.set_text(f"div F(P) = {div_P:.2f} ({art}):  Fläche Fleck ×{faktor:.2f}")
            drehung = np.degrees(state["winkel"])
            sinn = ("gegen den Uhrzeigersinn" if rot_P > 0.05 else
                    "im Uhrzeigersinn" if rot_P < -0.05 else "keine Drehung")
            info_rot.set_text(f"rot F(P) = {rot_P:.2f} ({sinn}):  Rad gedreht {drehung:.0f}°")

        schreibe_info()

        def step(dt_sim, active=True):
            """Simulation um dt_sim weiterrechnen und die Grafik aktualisieren."""
            teilchen.set_visible(active)
            if not active or dt_sim <= 0:
                return
            n_sub = int(np.ceil(dt_sim / 0.02))
            dt = dt_sim / n_sub
            for _ in range(n_sub):
                state["pos"] = rk4(state["pos"], dt)
                # Fleck verformt sich mit der Strömung, bleibt aber bei P verankert
                # (Divergenz ist eine lokale Größe, sie gilt nur am Punkt P)
                fl = rk4(state["fleck"], dt)
                state["fleck"] = fl - (fl.mean(axis=1) - P)[:, None]
                state["winkel"] += 0.5 * rot_P * dt
            state["t"] += dt_sim
            state["alter"] += dt_sim
            p = state["pos"]
            weg = (state["alter"] > state["lebensdauer"]) | (np.abs(p) > L).any(axis=0)
            neu_verteilen(weg)
            teilchen.set_data(*state["pos"])
            fleck.set_xy(state["fleck"].T)
            zeichne_rad()
            schreibe_info()

        return fig, step
    return T_SIM, make_scene


@app.cell
def _(T_SIM, make_scene, mo, run_button, time):
    # ===== 5. Anzeige und Animation =====
    DURATION = 6.0  # Sekunden Echtzeit für T_SIM Sekunden simulierte Zeit

    _fig, _step = make_scene()
    if run_button.value:
        _t0 = _last = time.perf_counter()
        while (_now := time.perf_counter()) - _t0 < DURATION:
            _step((_now - _last) * T_SIM / DURATION)
            _last = _now
            mo.output.replace(_fig)
        _step((_t0 + DURATION - _last) * T_SIM / DURATION)  # genau bis zum Ende
    else:
        _step(0, active=False)
    _fig
    return


if __name__ == "__main__":
    app.run()
