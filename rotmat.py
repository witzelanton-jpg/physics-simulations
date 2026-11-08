import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _(BLAU, GRAU, ORANGE, farbig, mo):
    mo.md(f"""
    # Rotation eines Vektors

    Gib einen Vektor ein und wähle den Drehwinkel {farbig("θ", ORANGE)}. Mit
    **Rotation ausführen** wird der Vektor samt Koordinatensystem gedreht.
    {farbig("Grau", GRAU)} ist der Ausgangszustand, {farbig("blau", BLAU)} der
    gedrehte Zustand, {farbig("orange", ORANGE)} der Drehwinkel.
    """)
    return


@app.cell
def _():
    import time
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.patches import Arc
    from matplotlib.collections import LineCollection
    return Arc, LineCollection, mo, np, plt, time


@app.cell
def _():
    # ===== Farben: einmal festlegen, überall verwenden =====
    GRAU = "#808080"        # Vektor v (Ausgangszustand)
    DUNKELGRAU = "#696969"  # Basisvektoren e1, e2
    BLAU = "#1f77b4"        # gedrehter Zustand: e1', e2', v', Gitter'
    ORANGE = "#ff8c00"      # Drehwinkel θ

    def farbig(text, color):
        """Färbt normalen Text (Markdown/HTML)."""
        return f'<span style="color:{color}">{text}</span>'

    def tex(formel, color):
        """Färbt einen Teil einer LaTeX-Formel."""
        return r"\textcolor{" + color + "}{" + formel + "}"
    return BLAU, DUNKELGRAU, GRAU, ORANGE, farbig, tex


@app.cell
def _(GRAU, ORANGE, farbig, mo):
    # ===== 1. Eingabe =====
    # Ändert man einen Wert, werden alle abhängigen Zellen neu berechnet.
    # show_value=True zeigt den aktuellen Wert direkt neben dem Slider an
    theta_slider = mo.ui.slider(-180, 180, step=5, value=45,
                                label=f"Drehwinkel {farbig('θ', ORANGE)} (Grad)",
                                show_value=True)
    x_input = mo.ui.number(-10, 10, step=0.5, value=2,
                           label=f"{farbig('e₁', GRAU)}-Komponente")
    y_input = mo.ui.number(-10, 10, step=0.5, value=1,
                           label=f"{farbig('e₂', GRAU)}-Komponente")
    # run_button ist nur direkt nach dem Klick True. Sobald man danach
    # x, y oder θ ändert, ist er wieder False -> Ausgangszustand.
    rotate_button = mo.ui.run_button(label="▶ Rotation ausführen")

    mo.vstack([
        mo.hstack([x_input, y_input], justify="start"),
        theta_slider,
        rotate_button,
    ])
    return rotate_button, theta_slider, x_input, y_input


@app.cell
def _(
    BLAU,
    GRAU,
    ORANGE,
    mo,
    np,
    rotate_button,
    rotation_matrix,
    tex,
    theta_slider,
    vector,
):
    # ===== 2. Ergebnis als Formel (erst nach der Rotation) =====
    # Farbige Bausteine der Formel
    _v = tex(r"\vec v", GRAU)
    _v_spalte = tex(rf"\begin{{pmatrix}} {vector[0]:g} \\ {vector[1]:g} \end{{pmatrix}}", GRAU)

    if rotate_button.value:
        _angle = theta_slider.value
        _R = rotation_matrix(np.radians(_angle))
        _result = _R @ vector
        _w = tex(rf"{_angle}^\circ", ORANGE)  # Winkel
        _v_rot = tex(r"\vec v\,'", BLAU)
        _v_rot_spalte = tex(
            rf"\begin{{pmatrix}} {_result[0]:.3f} \\ {_result[1]:.3f} \end{{pmatrix}}", BLAU)
        _out = mo.md(
            rf"""
            $$
            {_v_rot} = R({_w})\,{_v} =
            \begin{{pmatrix}} \cos({_w}) & -\sin({_w}) \\ \sin({_w}) & \cos({_w}) \end{{pmatrix}}
            {_v_spalte}
            =
            \begin{{pmatrix}} {_R[0,0]:.3f} & {_R[0,1]:.3f} \\ {_R[1,0]:.3f} & {_R[1,1]:.3f} \end{{pmatrix}}
            {_v_spalte}
            =
            {_v_rot_spalte}
            $$
            """
        )
    else:
        _out = mo.md(
            rf"${_v} = {_v_spalte}$"
            "  — klicke auf **Rotation ausführen**."
        )
    _out
    return


@app.cell
def _(np):
    # ===== 3. Mathematik =====
    def rotation_matrix(theta):
        c, s = np.cos(theta), np.sin(theta)
        return np.array([[c, -s],
                         [s,  c]])

    def make_grid(size):
        """Gitterlinien mit Abstand 1 von -size bis size.
        Jede Linie besteht aus Anfangs- und Endpunkt."""
        lines = []
        for p in range(-size, size + 1):
            lines.append(np.array([[-size, size], [p, p]]))  # horizontal
            lines.append(np.array([[p, p], [-size, size]]))  # vertikal
        return lines
    return make_grid, rotation_matrix


@app.cell
def _(x_input, y_input, np):
    # ===== 4. Vektor aus der Eingabe =====
    vector = np.array([x_input.value, y_input.value])
    return (vector,)


@app.cell
def _(
    Arc,
    BLAU,
    GRAU,
    LineCollection,
    ORANGE,
    make_grid,
    np,
    plt,
    rotation_matrix,
    vector,
):
    # ===== 5. Szene: Figur einmal aufbauen, danach nur noch Positionen ändern =====
    # (Neu zeichnen bei jedem Bild wäre zu langsam für eine flüssige Animation.)

    # Sichtbereich groß genug wählen, damit auch lange Vektoren reinpassen
    limit = max(4.5, np.linalg.norm(vector) + 1)
    # "Unendliches" Gitter: so groß, dass es auch gedreht die Ecken des
    # Sichtbereichs abdeckt (Diagonale = limit * √2). Der Rest wird abgeschnitten.
    grid = make_grid(int(np.ceil(limit * np.sqrt(2))) + 1)
    e1, e2 = np.array([1, 0]), np.array([0, 1])
    norm_v = np.linalg.norm(vector)
    start_deg = np.degrees(np.arctan2(vector[1], vector[0]))
    # Winkelbogen außerhalb der e-Beschriftungen (bei ca. 1.35)
    arc_radius = max(1.7, 0.55 * norm_v)

    def make_scene():
        """Erzeugt die Figur und gibt (fig, update) zurück.
        update(phi, rotated) stellt den Zustand bei Drehwinkel phi (Grad) ein.
        rotated=False: nur Ausgangszustand, ohne gestrichene Größen."""
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_aspect("equal")

        def arrow(tip, color, label):
            """Vektorpfeil vom Ursprung zur Spitze, mit Beschriftung an der Spitze.
            Schaft und Spitze sind getrennte Objekte, damit man den Schaft
            stricheln kann, ohne dass die Spitze mitgestrichelt wird."""
            shaft = ax.annotate("", xy=tip, xytext=(0, 0), zorder=5,
                                arrowprops=dict(arrowstyle="-", color=color, lw=1.5,
                                                shrinkA=0, shrinkB=0))
            # Spitze: ein winziger Pfeil direkt an der Spitze, immer durchgezogen
            head = ax.annotate("", xy=tip, xytext=(0, 0), zorder=5,
                               arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5,
                                               mutation_scale=20, shrinkA=0, shrinkB=0))
            t = ax.text(0, 0, label, color=color, fontsize=14, zorder=6,
                        ha="center", va="center")
            move_arrow((shaft, head, t), tip)
            return shaft, head, t

        def move_arrow(arr, tip):
            shaft, head, t = arr
            n = np.linalg.norm(tip)
            direction = tip / n if n > 0 else np.array([1.0, 0.0])
            shaft.xy = tip
            head.xy = tip
            head.xyann = tip - 0.01 * direction  # kurzes Stück -> nur die Spitze
            # Beschriftung etwas hinter die Spitze schieben
            offset = 0.35 * direction if n > 0 else np.array([0.2, 0.2])
            t.set_position(tip + offset)

        # Ausgangszustand: Gitter, e1, e2, v (bleibt immer gleich)
        # Eine LineCollection statt vieler einzelner Linien ist viel schneller.
        ax.add_collection(LineCollection([line.T for line in grid],
                                         color="lightgray", lw=1, zorder=1))
        # Die Ausgangspfeile merken, damit sie nach der Rotation gestrichelt werden
        originals = [
            arrow(e1, GRAU, r"$\vec{e}_1$"),
            arrow(e2, GRAU, r"$\vec{e}_2$"),
            arrow(vector, GRAU, r"$\vec{v}$"),
        ]

        # Gedrehter Zustand: Gitter', e1', e2', v', Winkelbogen θ
        grid_rot = LineCollection([], color=BLAU, lw=1, alpha=0.35, zorder=2)
        ax.add_collection(grid_rot)
        e1_rot = arrow(e1, BLAU, r"$\vec{e'}_1$")
        e2_rot = arrow(e2, BLAU, r"$\vec{e'}_2$")
        v_rot = arrow(vector, BLAU, r"$\vec{v}\,'$")
        arc = Arc((0, 0), 2 * arc_radius, 2 * arc_radius, color=ORANGE, lw=2, zorder=4)
        ax.add_patch(arc)
        arc_label = ax.text(0, 0, "θ", color=ORANGE, fontsize=15, zorder=6,
                            ha="center", va="center")

        # Bildbeschriftung oben links: eine Zeile pro Größe, jeweils in ihrer Farbe
        def info_line(row, color):
            return ax.text(0.02, 0.97 - 0.05 * row, "", color=color, transform=ax.transAxes,
                           va="top", zorder=7,
                           bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1))
        info_v = info_line(0, GRAU)
        info_theta = info_line(1, ORANGE)
        info_v_rot = info_line(2, BLAU)
        info_v.set_text(f"v = ({vector[0]:.2f}, {vector[1]:.2f})")

        rotated_artists = [grid_rot, *e1_rot, *e2_rot, *v_rot, arc, arc_label,
                           info_theta, info_v_rot]

        def update(phi, rotated):
            for artist in rotated_artists:
                    artist.set_visible(rotated)
            # Nach dem Klick: e1, e2, v gestrichelt, davor durchgezogen
            # (nur der Schaft, die Spitze bleibt durchgezogen)
            for shaft, _head, _label in originals:
                shaft.arrow_patch.set_linestyle((0, (4, 3)) if rotated else "-")
            if not rotated:
                return

            R = rotation_matrix(np.radians(phi))
            result = R @ vector
            grid_rot.set_segments([(R @ line).T for line in grid])
            move_arrow(e1_rot, R @ e1)
            move_arrow(e2_rot, R @ e2)
            move_arrow(v_rot, result)

            # Winkelbogen θ zwischen v und v'
            show_arc = norm_v > 0 and abs(phi) > 0.5
            arc.set_visible(show_arc)
            arc_label.set_visible(show_arc)
            arc.theta1, arc.theta2 = sorted([start_deg, start_deg + phi])
            mid = np.radians(start_deg + phi / 2)
            arc_label.set_position(((arc_radius + 0.3) * np.cos(mid),
                                    (arc_radius + 0.3) * np.sin(mid)))

            info_theta.set_text(f"θ = {phi:.0f}°")
            info_v_rot.set_text(f"v' = ({result[0]:.2f}, {result[1]:.2f})")

        return fig, update
    return (make_scene,)


@app.cell
def _(make_scene, mo, np, rotate_button, theta_slider, time):
    # ===== 6. Anzeige und Animation =====
    DURATION = 2.0  # Dauer der Drehung in Sekunden

    def ease(s):
        """Sanftes Anfahren und Abbremsen: s läuft von 0 bis 1."""
        return (1 - np.cos(np.pi * s)) / 2

    _fig, _update = make_scene()

    if rotate_button.value:
        # Animation: so viele Bilder wie möglich, der Winkel richtet sich
        # nach der vergangenen Zeit -> dauert immer genau DURATION Sekunden.
        _angle = theta_slider.value
        _t0 = time.perf_counter()
        while (_s := (time.perf_counter() - _t0) / DURATION) < 1:
            _update(_angle * ease(_s), rotated=True)
            mo.output.replace(_fig)
        _update(_angle, rotated=True)
    else:
        # Vor der Rotation: nur v, e1, e2 und Gitter, live aktualisiert
        _update(0, rotated=False)
    _fig
    return


if __name__ == "__main__":
    app.run()
