import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _(BLAU, GRAU, GRUEN, ORANGE, farbig, mo):
    mo.md(f"""
    # Matrix-Multiplikation: Skalierung und Drehung

    Eine Matrix $M = R(\\theta)\\,S$ streckt zuerst mit der Skalierungsmatrix
    {farbig("S", GRUEN)} und dreht dann mit {farbig("R(θ)", ORANGE)}.
    Mit **Transformation ausführen** laufen Skalierung und Drehung **gleichzeitig** ab.
    {farbig("Grau", GRAU)} ist der Ausgangszustand, {farbig("blau", BLAU)} der
    transformierte Zustand. Der Einheitskreis wird dabei zu einer Ellipse.
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
    GRAU = "#808080"    # Ausgangszustand
    BLAU = "#1f77b4"    # transformierter Zustand
    ORANGE = "#ff8c00"  # Drehwinkel θ
    GRUEN = "#2ca02c"   # Skalierung

    def farbig(text, color):
        """Färbt normalen Text (Markdown/HTML)."""
        return f'<span style="color:{color}">{text}</span>'

    def tex(formel, color):
        """Färbt einen Teil einer LaTeX-Formel."""
        return r"\textcolor{" + color + "}{" + formel + "}"
    return BLAU, GRAU, GRUEN, ORANGE, farbig, tex


@app.cell
def _(GRAU, GRUEN, ORANGE, farbig, mo):
    # ===== 1. Eingabe =====
    theta_slider = mo.ui.slider(-180, 180, step=5, value=60,
                                label=f"Drehwinkel {farbig('θ', ORANGE)} (Grad)",
                                show_value=True)
    sx_slider = mo.ui.slider(0.25, 3, step=0.25, value=2,
                             label=f"Skalierung {farbig('s₁', GRUEN)} (e₁-Richtung)",
                             show_value=True)
    sy_slider = mo.ui.slider(0.25, 3, step=0.25, value=0.5,
                             label=f"Skalierung {farbig('s₂', GRUEN)} (e₂-Richtung)",
                             show_value=True)
    x_input = mo.ui.number(-10, 10, step=0.5, value=1.5,
                           label=f"{farbig('e₁', GRAU)}-Komponente")
    y_input = mo.ui.number(-10, 10, step=0.5, value=1,
                           label=f"{farbig('e₂', GRAU)}-Komponente")
    run_button = mo.ui.run_button(label="▶ Transformation ausführen")

    mo.vstack([
        mo.hstack([x_input, y_input], justify="start"),
        theta_slider,
        sx_slider,
        sy_slider,
        run_button,
    ])
    return run_button, sx_slider, sy_slider, theta_slider, x_input, y_input


@app.cell
def _(
    BLAU,
    GRAU,
    GRUEN,
    ORANGE,
    mo,
    np,
    rotation_matrix,
    run_button,
    sx_slider,
    sy_slider,
    tex,
    theta_slider,
    vector,
):
    # ===== 2. Ergebnis als Formel (erst nach der Transformation) =====
    _v = tex(r"\vec v", GRAU)
    _v_spalte = tex(rf"\begin{{pmatrix}} {vector[0]:g} \\ {vector[1]:g} \end{{pmatrix}}", GRAU)

    if run_button.value:
        _angle = theta_slider.value
        _sx, _sy = sx_slider.value, sy_slider.value
        _M = rotation_matrix(np.radians(_angle)) @ np.diag([_sx, _sy])
        _result = _M @ vector
        _w = tex(rf"{_angle}^\circ", ORANGE)
        _S = tex(rf"\begin{{pmatrix}} {_sx:g} & 0 \\ 0 & {_sy:g} \end{{pmatrix}}", GRUEN)
        _v_neu = tex(r"\vec v\,'", BLAU)
        _v_neu_spalte = tex(
            rf"\begin{{pmatrix}} {_result[0]:.3f} \\ {_result[1]:.3f} \end{{pmatrix}}", BLAU)
        _out = mo.md(
            rf"""
            $$
            {_v_neu} = R({_w})\,S\,{_v} =
            \begin{{pmatrix}} \cos({_w}) & -\sin({_w}) \\ \sin({_w}) & \cos({_w}) \end{{pmatrix}}
            {_S}\,{_v_spalte}
            =
            \begin{{pmatrix}} {_M[0,0]:.3f} & {_M[0,1]:.3f} \\ {_M[1,0]:.3f} & {_M[1,1]:.3f} \end{{pmatrix}}
            {_v_spalte}
            =
            {_v_neu_spalte}
            $$

            Die Reihenfolge ist wichtig: Im Allgemeinen ist $R\,S \neq S\,R$.
            """
        )
    else:
        _out = mo.md(
            rf"${_v} = {_v_spalte}$"
            "  — klicke auf **Transformation ausführen**."
        )
    _out
    return


@app.cell
def _(np):
    # ===== 3. Mathematik und Zeichenhilfen =====
    def rotation_matrix(theta):
        c, s = np.cos(theta), np.sin(theta)
        return np.array([[c, -s],
                         [s,  c]])

    def make_grid(size):
        """Gitterlinien mit Abstand 1 von -size bis size."""
        lines = []
        for p in range(-size, size + 1):
            lines.append(np.array([[-size, size], [p, p]]))  # horizontal
            lines.append(np.array([[p, p], [-size, size]]))  # vertikal
        return lines

    def make_arrow(ax, tip, color, label):
        """Vektorpfeil vom Ursprung zur Spitze. Schaft und Spitze sind getrennt,
        damit nur der Schaft gestrichelt werden kann."""
        shaft = ax.annotate("", xy=tip, xytext=(0, 0), zorder=5,
                            arrowprops=dict(arrowstyle="-", color=color, lw=1.5,
                                            shrinkA=0, shrinkB=0))
        head = ax.annotate("", xy=tip, xytext=(0, 0), zorder=5,
                           arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5,
                                           mutation_scale=20, shrinkA=0, shrinkB=0))
        t = ax.text(0, 0, label, color=color, fontsize=14, zorder=6,
                    ha="center", va="center")
        move_arrow((shaft, head, t), tip)
        return shaft, head, t

    def move_arrow(arr, tip):
        shaft, head, t = arr
        tip = np.asarray(tip, dtype=float)
        n = np.linalg.norm(tip)
        direction = tip / n if n > 0 else np.array([1.0, 0.0])
        shaft.xy = tip
        head.xy = tip
        head.xyann = tip - 0.01 * direction  # kurzes Stück -> nur die Spitze
        t.set_position(tip + 0.35 * direction)

    def ease(s):
        """Sanftes Anfahren und Abbremsen: s läuft von 0 bis 1."""
        return (1 - np.cos(np.pi * s)) / 2
    return ease, make_arrow, make_grid, move_arrow, rotation_matrix


@app.cell
def _(np, x_input, y_input):
    # ===== 4. Vektor aus der Eingabe =====
    vector = np.array([x_input.value, y_input.value])
    return (vector,)


@app.cell
def _(
    Arc,
    BLAU,
    GRAU,
    GRUEN,
    LineCollection,
    ORANGE,
    make_arrow,
    make_grid,
    move_arrow,
    np,
    plt,
    rotation_matrix,
    sx_slider,
    sy_slider,
    vector,
):
    # ===== 5. Szene: Figur einmal aufbauen, danach nur noch Positionen ändern =====
    sx, sy = sx_slider.value, sy_slider.value
    e1, e2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])

    # Sichtbereich: groß genug für v, v' und die gestreckten Basisvektoren
    limit = max(4.5, np.linalg.norm(vector) * max(sx, sy, 1) + 1, max(sx, sy) + 1)
    # Gitter so groß, dass es auch nach dem Stauchen (kleinstes s) den Sichtbereich füllt
    grid = make_grid(min(60, int(np.ceil(limit * np.sqrt(2) / min(sx, sy, 1))) + 1))
    phis = np.linspace(0, 2 * np.pi, 120)
    circle = np.array([np.cos(phis), np.sin(phis)])  # Einheitskreis

    def matrix_at(s, angle):
        """Zwischenstand der Animation: s=0 -> Einheitsmatrix, s=1 -> volle Matrix.
        Skalierung und Drehung laufen gleichzeitig."""
        S = np.diag([1 + s * (sx - 1), 1 + s * (sy - 1)])
        return rotation_matrix(np.radians(s * angle)) @ S

    def make_scene():
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_aspect("equal")

        # Ausgangszustand
        ax.add_collection(LineCollection([line.T for line in grid],
                                         color="lightgray", lw=1, zorder=1))
        circle_orig, = ax.plot(*circle, color=GRAU, lw=1.2, zorder=3)
        originals = [
            make_arrow(ax, e1, GRAU, r"$\vec{e}_1$"),
            make_arrow(ax, e2, GRAU, r"$\vec{e}_2$"),
            make_arrow(ax, vector, GRAU, r"$\vec{v}$"),
        ]

        # Transformierter Zustand
        grid_new = LineCollection([], color=BLAU, lw=1, alpha=0.35, zorder=2)
        ax.add_collection(grid_new)
        ellipse, = ax.plot([], [], color=GRUEN, lw=2, zorder=3)
        e1_new = make_arrow(ax, e1, BLAU, r"$\vec{e'}_1$")
        e2_new = make_arrow(ax, e2, BLAU, r"$\vec{e'}_2$")
        v_new = make_arrow(ax, vector, BLAU, r"$\vec{v}\,'$")
        # Drehwinkel zwischen e1 und e1' (Skalierung ändert die Richtung von e1 nicht)
        arc = Arc((0, 0), 1.2, 1.2, color=ORANGE, lw=2, zorder=4)
        ax.add_patch(arc)
        arc_label = ax.text(0, 0, "θ", color=ORANGE, fontsize=12, zorder=6,
                            ha="center", va="center")

        def info_line(row, color):
            return ax.text(0.02, 0.97 - 0.05 * row, "", color=color, transform=ax.transAxes,
                           va="top", zorder=7,
                           bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1))
        info_v = info_line(0, GRAU)
        info_theta = info_line(1, ORANGE)
        info_s = info_line(2, GRUEN)
        info_v_new = info_line(3, BLAU)
        info_v.set_text(f"v = ({vector[0]:.2f}, {vector[1]:.2f})")

        new_artists = [grid_new, ellipse, *e1_new, *e2_new, *v_new, arc, arc_label,
                       info_theta, info_s, info_v_new]

        def update(s, angle, active):
            for artist in new_artists:
                artist.set_visible(active)
            for shaft, _head, _label in originals:
                shaft.arrow_patch.set_linestyle((0, (4, 3)) if active else "-")
            circle_orig.set_linestyle("--" if active else "-")
            if not active:
                return

            M = matrix_at(s, angle)
            grid_new.set_segments([(M @ line).T for line in grid])
            ellipse.set_data(*(M @ circle))
            move_arrow(e1_new, M @ e1)
            move_arrow(e2_new, M @ e2)
            move_arrow(v_new, M @ vector)

            phi = s * angle
            show_arc = abs(phi) > 0.5
            arc.set_visible(show_arc)
            arc_label.set_visible(show_arc)
            arc.theta1, arc.theta2 = sorted([0, phi])
            mid = np.radians(phi / 2)
            arc_label.set_position((0.85 * np.cos(mid), 0.85 * np.sin(mid)))

            result = M @ vector
            info_theta.set_text(f"θ = {phi:.0f}°")
            info_s.set_text(f"s₁ = {1 + s * (sx - 1):.2f}   s₂ = {1 + s * (sy - 1):.2f}")
            info_v_new.set_text(f"v' = ({result[0]:.2f}, {result[1]:.2f})")

        return fig, update
    return (make_scene,)


@app.cell
def _(ease, make_scene, mo, run_button, theta_slider, time):
    # ===== 6. Anzeige und Animation =====
    DURATION = 2.5  # Dauer der Animation in Sekunden

    _fig, _update = make_scene()
    _angle = theta_slider.value

    if run_button.value:
        _t0 = time.perf_counter()
        while (_s := (time.perf_counter() - _t0) / DURATION) < 1:
            _update(ease(_s), _angle, active=True)
            mo.output.replace(_fig)
        _update(1, _angle, active=True)
    else:
        _update(0, _angle, active=False)
    _fig
    return


if __name__ == "__main__":
    app.run()
