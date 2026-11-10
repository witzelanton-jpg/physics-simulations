import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _(BLAU, GRAU, LILA, ORANGE, farbig, mo):
    mo.md(f"""
    # Eigenvektoren

    Ein **Eigenvektor** $\\vec u$ einer Matrix $A$ wird von $A$ nicht gedreht, sondern
    nur gestreckt: $A\\,\\vec u = \\lambda\\,\\vec u$. Mit **Transformation ausführen**
    wird das ganze Feld von der Einheitsmatrix zu $A$ verformt.
    Die Eigenvektoren {farbig("u₁", ORANGE)} und {farbig("u₂", LILA)} bleiben dabei
    auf ihrer gestrichelten Geraden, der Testvektor {farbig("v", GRAU)} wird zu
    {farbig("v′", BLAU)} und verlässt seine Gerade.
    """)
    return


@app.cell
def _():
    import time
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    return LineCollection, mo, np, plt, time


@app.cell
def _():
    # ===== Farben: einmal festlegen, überall verwenden =====
    GRAU = "#808080"    # Ausgangszustand, Testvektor v
    BLAU = "#1f77b4"    # transformierter Zustand
    ORANGE = "#ff8c00"  # Eigenvektor u1
    LILA = "#9467bd"    # Eigenvektor u2

    def farbig(text, color):
        """Färbt normalen Text (Markdown/HTML)."""
        return f'<span style="color:{color}">{text}</span>'

    def tex(formel, color):
        """Färbt einen Teil einer LaTeX-Formel."""
        return r"\textcolor{" + color + "}{" + formel + "}"
    return BLAU, GRAU, LILA, ORANGE, farbig, tex


@app.cell
def _(mo):
    # ===== 1a. Beispielmatrix wählen =====
    BEISPIELE = {
        "Symmetrisch: zwei Eigenvektoren": [[2, 1], [1, 2]],
        "Streckung entlang der Achsen": [[2.5, 0], [0, 0.5]],
        "Allgemein: schiefe Eigenvektoren": [[1, 1], [0.5, 1.5]],
        "Spiegelung an der Diagonalen": [[0, 1], [1, 0]],
        "Scherung: nur ein Eigenvektor": [[1, 1], [0, 1]],
        "Drehung: keine reellen Eigenvektoren": [[0, -1], [1, 0]],
    }
    beispiel = mo.ui.dropdown(list(BEISPIELE), value="Symmetrisch: zwei Eigenvektoren",
                              label="Beispiel")
    beispiel
    return BEISPIELE, beispiel


@app.cell
def _(BEISPIELE, GRAU, beispiel, farbig, mo):
    # ===== 1b. Matrix und Testvektor eingeben =====
    # Die Startwerte kommen aus dem gewählten Beispiel und lassen sich frei ändern.
    _m = BEISPIELE[beispiel.value]
    a_in = mo.ui.number(-5, 5, step=0.5, value=_m[0][0], label="a")
    b_in = mo.ui.number(-5, 5, step=0.5, value=_m[0][1], label="b")
    c_in = mo.ui.number(-5, 5, step=0.5, value=_m[1][0], label="c")
    d_in = mo.ui.number(-5, 5, step=0.5, value=_m[1][1], label="d")
    x_input = mo.ui.number(-5, 5, step=0.5, value=1.5,
                           label=f"{farbig('v', GRAU)}: e₁-Komponente")
    y_input = mo.ui.number(-5, 5, step=0.5, value=-0.5,
                           label=f"{farbig('v', GRAU)}: e₂-Komponente")
    run_button = mo.ui.run_button(label="▶ Transformation ausführen")

    mo.vstack([
        mo.md(r"Matrix $A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$"),
        mo.hstack([a_in, b_in], justify="start"),
        mo.hstack([c_in, d_in], justify="start"),
        mo.hstack([x_input, y_input], justify="start"),
        run_button,
    ])
    return a_in, b_in, c_in, d_in, run_button, x_input, y_input


@app.cell
def _(a_in, b_in, c_in, d_in, np, x_input, y_input):
    # ===== 2. Matrix, Testvektor und Eigenwerte =====
    A = np.array([[a_in.value, b_in.value],
                  [c_in.value, d_in.value]], dtype=float)
    vector = np.array([x_input.value, y_input.value], dtype=float)

    def real_eigen(A):
        """Reelle Eigenwerte und Eigenvektoren (Länge 1).
        Parallele Eigenvektoren (z. B. bei der Scherung) werden nur einmal gezählt."""
        values, vectors = np.linalg.eig(A)
        result = []
        for lam, u in zip(values, vectors.T):
            if abs(lam.imag) > 1e-9:
                continue  # komplexer Eigenwert -> kein reeller Eigenvektor
            u = np.real(u)
            u = u / np.linalg.norm(u)
            if u[0] < -1e-9 or (abs(u[0]) < 1e-9 and u[1] < 0):
                u = -u  # einheitliche Richtung
            if all(abs(u[0] * w[1] - u[1] * w[0]) > 1e-6 for _, w in result):
                result.append((float(np.real(lam)), u))
        return result

    eigen = real_eigen(A)
    return A, eigen, vector


@app.cell
def _(A, LILA, ORANGE, eigen, mo, np, run_button, tex):
    # ===== 3. Eigenwerte als Formel =====
    _farben = [ORANGE, LILA]
    _A = rf"\begin{{pmatrix}} {A[0,0]:g} & {A[0,1]:g} \\ {A[1,0]:g} & {A[1,1]:g} \end{{pmatrix}}"
    _zeilen = []
    for _i, (_lam, _u) in enumerate(eigen):
        _uu = tex(rf"\vec u_{_i + 1}", _farben[_i])
        _us = tex(rf"\begin{{pmatrix}} {_u[0]:.3f} \\ {_u[1]:.3f} \end{{pmatrix}}", _farben[_i])
        _zeilen.append(
            rf"$$ {_uu} = {_us}, \quad A\,{_uu} = {_lam:.3g}\cdot{_uu} "
            rf"\quad (\lambda_{_i + 1} = {_lam:.3g}) $$"
        )

    if not eigen:
        _text = ("**Keine reellen Eigenwerte:** Diese Matrix dreht jeden Vektor. "
                 "Es gibt keine Richtung, die gleich bleibt.")
    elif np.allclose(A, A[0, 0] * np.eye(2)):
        _text = ("**Vielfaches der Einheitsmatrix:** *Jeder* Vektor ist ein Eigenvektor, "
                 "auch der Testvektor.")
    elif len(eigen) == 1:
        _text = "**Nur ein Eigenvektor:** Alle anderen Richtungen werden gedreht."
    else:
        _text = ""

    if run_button.value:
        _out = mo.md(
            rf"$$ A = {_A} $$" + "\n\n" + "\n\n".join(_zeilen) + "\n\n" + _text +
            "\n\nAlle Zwischenschritte $(1-s)\\,E + s\\,A$ haben **dieselben** "
            "Eigenvektoren, deshalb bleiben sie während der ganzen Animation auf ihrer Geraden."
        )
    else:
        _out = mo.md(rf"$$ A = {_A} $$ — klicke auf **Transformation ausführen**.")
    _out
    return


@app.cell
def _(np):
    # ===== 4. Zeichenhilfen =====
    def make_grid(size):
        """Gitterlinien mit Abstand 1 von -size bis size."""
        lines = []
        for p in range(-size, size + 1):
            lines.append(np.array([[-size, size], [p, p]]))  # horizontal
            lines.append(np.array([[p, p], [-size, size]]))  # vertikal
        return lines

    def make_arrow(ax, tip, color, label, lw=1.5):
        """Vektorpfeil vom Ursprung zur Spitze. Schaft und Spitze sind getrennt,
        damit nur der Schaft gestrichelt werden kann."""
        shaft = ax.annotate("", xy=tip, xytext=(0, 0), zorder=5,
                            arrowprops=dict(arrowstyle="-", color=color, lw=lw,
                                            shrinkA=0, shrinkB=0))
        head = ax.annotate("", xy=tip, xytext=(0, 0), zorder=5,
                           arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
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
        head.set_visible(shaft.get_visible() and n > 1e-3)  # Nullvektor: keine Spitze
        t.set_position(tip + 0.35 * direction)

    def ease(s):
        """Sanftes Anfahren und Abbremsen: s läuft von 0 bis 1."""
        return (1 - np.cos(np.pi * s)) / 2
    return ease, make_arrow, make_grid, move_arrow


@app.cell
def _(
    A,
    BLAU,
    GRAU,
    LILA,
    LineCollection,
    ORANGE,
    eigen,
    make_arrow,
    make_grid,
    move_arrow,
    np,
    plt,
    vector,
):
    # ===== 5. Szene =====
    E = np.eye(2)

    def matrix_at(s):
        """s=0 -> Einheitsmatrix E, s=1 -> A. Dazwischen (1-s)E + sA."""
        return (1 - s) * E + s * A

    # Sichtbereich: groß genug für alle Vektoren am Anfang und am Ende
    _laengen = [np.linalg.norm(vector), np.linalg.norm(A @ vector), 2.0]
    _laengen += [2 * abs(lam) for lam, _ in eigen]
    limit = max(4.5, max(_laengen) + 1)

    # Gitter groß genug wählen, damit es auch gestaucht den Sichtbereich füllt
    _smin = min(np.linalg.svd(matrix_at(s), compute_uv=False)[-1]
                for s in np.linspace(0, 1, 21))
    grid = make_grid(min(40, int(np.ceil(limit * np.sqrt(2) / max(_smin, 0.15))) + 1))

    EIGEN_LAENGE = 2.0  # Eigenvektoren mit Länge 2 zeichnen, damit man sie gut sieht

    def make_scene():
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_aspect("equal")

        ax.add_collection(LineCollection([line.T for line in grid],
                                         color="lightgray", lw=1, zorder=1))
        grid_new = LineCollection([], color=BLAU, lw=1, alpha=0.35, zorder=2)
        ax.add_collection(grid_new)

        # Eigen-Geraden: unendlich lange gestrichelte Linien durch den Ursprung
        farben = [ORANGE, LILA]
        eigen_arrows = []
        for i, (lam, u) in enumerate(eigen):
            far = 3 * limit * u
            ax.plot([-far[0], far[0]], [-far[1], far[1]], color=farben[i],
                    lw=1.2, ls=(0, (6, 4)), alpha=0.8, zorder=3)
            eigen_arrows.append(
                make_arrow(ax, EIGEN_LAENGE * u, farben[i], rf"$\vec{{u}}_{i + 1}$", lw=2.5))

        # Testvektor v: Original (grau) mit seiner Geraden und v' (blau)
        v_line_far = 3 * limit * vector / max(np.linalg.norm(vector), 1e-9)
        v_line, = ax.plot([-v_line_far[0], v_line_far[0]], [-v_line_far[1], v_line_far[1]],
                          color=GRAU, lw=1, ls=":", zorder=3)
        v_orig = make_arrow(ax, vector, GRAU, r"$\vec{v}$")
        v_new = make_arrow(ax, vector, BLAU, r"$\vec{v}\,'$")

        def info_line(row, color):
            return ax.text(0.02, 0.97 - 0.05 * row, "", color=color, transform=ax.transAxes,
                           va="top", zorder=7,
                           bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1))
        infos = [info_line(i, farben[i]) for i in range(len(eigen))]
        info_v = info_line(len(eigen), BLAU)
        if not eigen:
            info_none = info_line(0, "black")
            info_none.set_text("keine reellen Eigenvektoren")

        new_artists = [grid_new, *v_new, info_v]

        def update(s, active):
            for artist in new_artists:
                artist.set_visible(active)
            v_orig[0].arrow_patch.set_linestyle((0, (4, 3)) if active else "-")
            v_line.set_visible(active)
            M = matrix_at(s if active else 0)

            grid_new.set_segments([(M @ line).T for line in grid])
            for i, ((lam, u), arr) in enumerate(zip(eigen, eigen_arrows)):
                # Eigenvektor: A u = λ u, also bleibt er auf seiner Geraden
                move_arrow(arr, M @ (EIGEN_LAENGE * u))
                factor = 1 + (s if active else 0) * (lam - 1)
                infos[i].set_text(f"u{i + 1}: Streckfaktor {factor:.2f} (λ{i + 1} = {lam:.2f})")
            if active:
                move_arrow(v_new, M @ vector)
                vn = M @ vector
                cross = vector[0] * vn[1] - vector[1] * vn[0]
                winkel = np.degrees(np.arctan2(cross, vector @ vn))
                info_v.set_text(f"v' = ({vn[0]:.2f}, {vn[1]:.2f}), gedreht um {winkel:.0f}°")

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
