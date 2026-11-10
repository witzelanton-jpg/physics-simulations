import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _(BLAU, GRAU, GRUEN, ROT, farbig, mo):
    mo.md(f"""
    # Determinante als Fläche

    Die Determinante gibt an, **um welchen Faktor eine Matrix Flächen verändert**.
    Das {farbig("Einheitsquadrat", GRAU)} (Fläche 1) aus $\\vec e_1$ und $\\vec e_2$ wird
    zum Parallelogramm aus $A\\vec e_1$ und $A\\vec e_2$. Seine Fläche ist genau $|\\det A|$.
    Dasselbe gilt für jede andere Form, hier für den {farbig("Klecks", BLAU)}: Seine Fläche
    wird ebenfalls mit $|\\det A|$ multipliziert.

    Die Farbe zeigt das Vorzeichen: {farbig("grün", GRUEN)} heißt $\\det A > 0$
    (Orientierung bleibt), {farbig("rot", ROT)} heißt $\\det A < 0$ (die Ebene wird
    „umgeklappt“, $\\vec e_1$ und $\\vec e_2$ tauschen ihre Reihenfolge).
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
    # ===== Farben: einmal festlegen, überall verwenden =====
    GRAU = "#808080"   # Ausgangszustand
    BLAU = "#1f77b4"   # transformierter Zustand, Klecks
    GRUEN = "#2ca02c"  # det > 0
    ROT = "#d62728"    # det < 0

    def farbig(text, color):
        """Färbt normalen Text (Markdown/HTML)."""
        return f'<span style="color:{color}">{text}</span>'

    def tex(formel, color):
        """Färbt einen Teil einer LaTeX-Formel."""
        return r"\textcolor{" + color + "}{" + formel + "}"
    return BLAU, GRAU, GRUEN, ROT, farbig, tex


@app.cell
def _(mo):
    # ===== 1a. Beispielmatrix wählen =====
    BEISPIELE = {
        "Streckung: det = 3": [[1.5, 0], [0, 2]],
        "Scherung: det = 1 (Fläche bleibt!)": [[1, 1.5], [0, 1]],
        "Drehung: det = 1": [[0.6, -0.8], [0.8, 0.6]],
        "Allgemein: det = 2.5": [[2, 1], [0.5, 1.5]],
        "Spiegelung: det = -1": [[1, 0], [0, -1]],
        "Stauchung: det = 0.25": [[0.5, 0], [0, 0.5]],
        "Singulär: det = 0": [[1, 2], [0.5, 1]],
    }
    beispiel = mo.ui.dropdown(list(BEISPIELE), value="Allgemein: det = 2.5", label="Beispiel")
    beispiel
    return BEISPIELE, beispiel


@app.cell
def _(BEISPIELE, beispiel, mo):
    # ===== 1b. Matrix eingeben =====
    _m = BEISPIELE[beispiel.value]
    a_in = mo.ui.number(-4, 4, step=0.25, value=_m[0][0], label="a")
    b_in = mo.ui.number(-4, 4, step=0.25, value=_m[0][1], label="b")
    c_in = mo.ui.number(-4, 4, step=0.25, value=_m[1][0], label="c")
    d_in = mo.ui.number(-4, 4, step=0.25, value=_m[1][1], label="d")
    run_button = mo.ui.run_button(label="▶ Transformation ausführen")

    mo.vstack([
        mo.md(r"Matrix $A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$"),
        mo.hstack([a_in, b_in], justify="start"),
        mo.hstack([c_in, d_in], justify="start"),
        run_button,
    ])
    return a_in, b_in, c_in, d_in, run_button


@app.cell
def _(a_in, b_in, c_in, d_in, np):
    # ===== 2. Matrix und Determinante =====
    A = np.array([[a_in.value, b_in.value],
                  [c_in.value, d_in.value]], dtype=float)
    det_A = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
    return A, det_A


@app.cell
def _(A, GRUEN, ROT, det_A, mo, run_button, tex):
    # ===== 3. Determinante als Formel =====
    _farbe = GRUEN if det_A >= 0 else ROT
    _A = rf"\begin{{pmatrix}} {A[0,0]:g} & {A[0,1]:g} \\ {A[1,0]:g} & {A[1,1]:g} \end{{pmatrix}}"
    if run_button.value:
        _det = tex(rf"{det_A:.3g}", _farbe)
        _out = mo.md(
            rf"""
            $$
            \det {_A} = a\,d - b\,c = {A[0,0]:g}\cdot{A[1,1]:g} - {A[0,1]:g}\cdot{A[1,0]:g} = {_det}
            $$

            Jede Fläche wird mit $|\det A| = {abs(det_A):.3g}$ multipliziert.
            """
        )
    else:
        _out = mo.md(rf"$$ A = {_A} $$ — klicke auf **Transformation ausführen**.")
    _out
    return


@app.cell
def _(np):
    # ===== 4. Mathematik und Zeichenhilfen =====
    def make_grid(size):
        """Gitterlinien mit Abstand 1 von -size bis size."""
        lines = []
        for p in range(-size, size + 1):
            lines.append(np.array([[-size, size], [p, p]]))  # horizontal
            lines.append(np.array([[p, p], [-size, size]]))  # vertikal
        return lines

    def signed_area(points):
        """Vorzeichenbehaftete Fläche eines Polygons (Gaußsche Trapezformel).
        points: Array der Form (2, n)."""
        x, y = points
        return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)

    def make_arrow(ax, tip, color, label):
        """Vektorpfeil vom Ursprung zur Spitze. Schaft und Spitze getrennt."""
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
        direction = tip / n if n > 1e-9 else np.array([1.0, 0.0])
        shaft.xy = tip
        head.xy = tip
        head.xyann = tip - 0.01 * direction
        t.set_position(tip + 0.35 * direction)

    def ease(s):
        """Sanftes Anfahren und Abbremsen: s läuft von 0 bis 1."""
        return (1 - np.cos(np.pi * s)) / 2
    return ease, make_arrow, make_grid, move_arrow, signed_area


@app.cell
def _(
    A,
    BLAU,
    GRAU,
    GRUEN,
    LineCollection,
    Polygon,
    ROT,
    make_arrow,
    make_grid,
    move_arrow,
    np,
    plt,
    signed_area,
):
    # ===== 5. Szene =====
    E = np.eye(2)

    def matrix_at(s):
        """s=0 -> Einheitsmatrix E, s=1 -> A."""
        return (1 - s) * E + s * A

    # Einheitsquadrat und "Klecks" (eine glatte, unregelmäßige Form)
    square = np.array([[0, 1, 1, 0], [0, 0, 1, 1]], dtype=float)
    _phi = np.linspace(0, 2 * np.pi, 160, endpoint=False)
    _r = 0.9 + 0.25 * np.sin(3 * _phi) + 0.15 * np.cos(2 * _phi + 1)
    blob = np.array([-2.2 + _r * np.cos(_phi), 1.8 + _r * np.sin(_phi)])
    blob_area = signed_area(blob)

    # Sichtbereich: alles muss am Anfang und am Ende hineinpassen
    _pts = np.hstack([square, blob, A @ square, A @ blob])
    limit = max(4.5, np.abs(_pts).max() + 1)
    _smin = min(np.linalg.svd(matrix_at(s), compute_uv=False)[-1]
                for s in np.linspace(0, 1, 21))
    grid = make_grid(min(40, int(np.ceil(limit * np.sqrt(2) / max(_smin, 0.15))) + 1))

    def make_scene():
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_aspect("equal")

        ax.add_collection(LineCollection([line.T for line in grid],
                                         color="lightgray", lw=1, zorder=1))
        grid_new = LineCollection([], color=BLAU, lw=1, alpha=0.3, zorder=2)
        ax.add_collection(grid_new)

        # Ausgangsformen (grau)
        ax.add_patch(Polygon(square.T, closed=True, facecolor=GRAU, alpha=0.25,
                             edgecolor=GRAU, lw=1.5, ls="--", zorder=3))
        ax.add_patch(Polygon(blob.T, closed=True, facecolor="none",
                             edgecolor=GRAU, lw=1.5, ls="--", zorder=3))
        ax.text(*(blob.mean(axis=1) + [0, -1.4]), f"Fläche {blob_area:.2f}", color=GRAU,
                ha="center", fontsize=10, zorder=6)
        e1_orig = make_arrow(ax, [1, 0], GRAU, r"$\vec{e}_1$")
        e2_orig = make_arrow(ax, [0, 1], GRAU, r"$\vec{e}_2$")

        # Transformierte Formen
        para = Polygon(square.T, closed=True, alpha=0.35, lw=2, zorder=4)
        ax.add_patch(para)
        blob_new = Polygon(blob.T, closed=True, facecolor=BLAU, alpha=0.3,
                           edgecolor=BLAU, lw=2, zorder=4)
        ax.add_patch(blob_new)
        para_text = ax.text(0, 0, "", ha="center", va="center", fontsize=12,
                            fontweight="bold", zorder=7)
        e1_new = make_arrow(ax, [1, 0], BLAU, r"$A\vec{e}_1$")
        e2_new = make_arrow(ax, [0, 1], BLAU, r"$A\vec{e}_2$")

        def info_line(row, color):
            return ax.text(0.02, 0.97 - 0.05 * row, "", color=color, transform=ax.transAxes,
                           va="top", zorder=8,
                           bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
        info_det = info_line(0, GRUEN)
        info_square = info_line(1, GRUEN)
        info_blob = info_line(2, BLAU)

        new_artists = [grid_new, para, blob_new, para_text, *e1_new, *e2_new,
                       info_det, info_square, info_blob]

        def update(s, active):
            for artist in new_artists:
                artist.set_visible(active)
            for arr in (e1_orig, e2_orig):
                arr[0].arrow_patch.set_linestyle((0, (4, 3)) if active else "-")
            if not active:
                return

            M = matrix_at(s)
            det = M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0]
            color = GRUEN if det >= 0 else ROT

            grid_new.set_segments([(M @ line).T for line in grid])
            sq = M @ square
            para.set_xy(sq.T)
            para.set_facecolor(color)
            para.set_edgecolor(color)
            para_text.set_position(sq.mean(axis=1))
            para_text.set_text(f"{abs(det):.2f}")
            para_text.set_color(color)
            move_arrow(e1_new, M[:, 0])
            move_arrow(e2_new, M[:, 1])

            bl = M @ blob
            blob_new.set_xy(bl.T)
            area_now = abs(signed_area(bl))

            for line in (info_det, info_square):
                line.set_color(color)
            info_det.set_text(f"det = {det:.2f}" + ("   (umgeklappt)" if det < 0 else ""))
            info_square.set_text(f"Fläche Parallelogramm = |det| = {abs(det):.2f}")
            info_blob.set_text(f"Fläche Klecks: {blob_area:.2f} → {area_now:.2f}"
                               f"   (Faktor {area_now / blob_area:.2f})")

        return fig, update
    return (make_scene,)


@app.cell
def _(ease, make_scene, mo, run_button, time):
    # ===== 6. Anzeige und Animation =====
    DURATION = 2.5  # Dauer der Animation in Sekunden

    _fig, _update = make_scene()
    if run_button.value:
        _t0 = time.perf_counter()
        while (_s := (time.perf_counter() - _t0) / DURATION) < 1:
            _update(ease(_s), active=True)
            mo.output.replace(_fig)
        _update(1, active=True)
    else:
        _update(0, active=False)
    _fig
    return


if __name__ == "__main__":
    app.run()
