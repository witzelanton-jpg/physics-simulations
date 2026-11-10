import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _(GRUEN, LILA, ORANGE, farbig, mo):
    mo.md(f"""
    # Herleitung des totalen Differentials: von der Sekante zur Tangente

    Für eine Fläche $z = f(x, y)$ betrachten wir den Punkt $P = (x_0, y_0, f(x_0, y_0))$.
    Mit **Herleitung abspielen** läuft die Herleitung in drei Schritten ab:

    1. **$y$ festhalten** ({farbig("Schnitt bei y = y₀", ORANGE)}): Die Sekante durch $P$
       und $Q = (x_0 + h,\\, y_0)$ wird für $h \\to 0$ zur Tangente. Ihre Steigung ist
       die partielle Ableitung $\\dfrac{{\\partial f}}{{\\partial x}}$.
    2. **$x$ festhalten** ({farbig("Schnitt bei x = x₀", LILA)}): Genauso ergibt sich
       $\\dfrac{{\\partial f}}{{\\partial y}}$.
    3. Beide Tangenten spannen die {farbig("Tangentialebene", GRUEN)} auf. Sie liefert das
       **totale Differential**
       $$ dz = \\frac{{\\partial f}}{{\\partial x}}\\,dx + \\frac{{\\partial f}}{{\\partial y}}\\,dy, $$
       die beste lineare Näherung für die Änderung $\\Delta f$.
    """)
    return


@app.cell
def _():
    import time
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    return mo, np, plt, time


@app.cell
def _():
    # ===== Farben =====
    ORANGE = "#ff8c00"  # x-Richtung (y festgehalten)
    LILA = "#9467bd"    # y-Richtung (x festgehalten)
    GRUEN = "#2ca02c"   # Tangentialebene, totales Differential
    ROT = "#d62728"     # Fehler zwischen Δf und dz

    def farbig(text, color):
        """Färbt normalen Text (Markdown/HTML)."""
        return f'<span style="color:{color}">{text}</span>'

    def tex(formel, color):
        """Färbt einen Teil einer LaTeX-Formel."""
        return r"\textcolor{" + color + "}{" + formel + "}"
    return GRUEN, LILA, ORANGE, ROT, farbig, tex


@app.cell
def _(mo, np):
    # ===== 1. Eingabe =====
    FUNKTIONEN = {
        "Paraboloid: f = (x² + y²)/2": (lambda x, y: (x**2 + y**2) / 2,
                                         r"\frac{x^2 + y^2}{2}"),
        "Sattel: f = x·y": (lambda x, y: x * y, r"x\,y"),
        "Welle: f = sin(x)·cos(y)": (lambda x, y: np.sin(x) * np.cos(y),
                                     r"\sin(x)\cos(y)"),
        "Hügel: f = 2·exp(-(x² + y²)/2)": (lambda x, y: 2 * np.exp(-(x**2 + y**2) / 2),
                                            r"2\,e^{-(x^2 + y^2)/2}"),
    }
    funktion = mo.ui.dropdown(list(FUNKTIONEN), value="Paraboloid: f = (x² + y²)/2",
                              label="Funktion")
    x0_slider = mo.ui.slider(-1.5, 1.5, step=0.1, value=0.8, show_value=True, label="x₀")
    y0_slider = mo.ui.slider(-1.5, 1.5, step=0.1, value=0.6, show_value=True, label="y₀")
    azim_slider = mo.ui.slider(-180, 180, step=5, value=-55, show_value=True,
                               label="Blickwinkel (horizontal)")
    elev_slider = mo.ui.slider(0, 90, step=5, value=25, show_value=True,
                               label="Blickwinkel (Höhe)")
    run_button = mo.ui.run_button(label="▶ Herleitung abspielen")
    mo.vstack([
        funktion,
        mo.hstack([x0_slider, y0_slider], justify="start"),
        mo.hstack([azim_slider, elev_slider], justify="start"),
        run_button,
    ])
    return (
        FUNKTIONEN,
        azim_slider,
        elev_slider,
        funktion,
        run_button,
        x0_slider,
        y0_slider,
    )


@app.cell
def _(FUNKTIONEN, funktion, x0_slider, y0_slider):
    # ===== 2. Funktion, Punkt und partielle Ableitungen =====
    f, f_tex = FUNKTIONEN[funktion.value]
    x0, y0 = x0_slider.value, y0_slider.value
    z0 = f(x0, y0)

    _H = 1e-5  # numerische Ableitung (zentraler Differenzenquotient)
    fx = (f(x0 + _H, y0) - f(x0 - _H, y0)) / (2 * _H)
    fy = (f(x0, y0 + _H) - f(x0, y0 - _H)) / (2 * _H)
    return f, f_tex, fx, fy, x0, y0, z0


@app.cell
def _(GRUEN, LILA, ORANGE, f_tex, fx, fy, mo, run_button, tex, x0, y0, z0):
    # ===== 3. Formeln =====
    _fx = tex(rf"\frac{{\partial f}}{{\partial x}} = {fx:.3f}", ORANGE)
    _fy = tex(rf"\frac{{\partial f}}{{\partial y}} = {fy:.3f}", LILA)
    _dz = tex(rf"dz = {fx:.3f}\,dx {'+' if fy >= 0 else '-'} {abs(fy):.3f}\,dy", GRUEN)
    if run_button.value:
        _out = mo.md(
            rf"""
            $$ f(x, y) = {f_tex}, \qquad P = ({x0:g},\ {y0:g},\ {z0:.3f}) $$

            $$
            {tex(r"\frac{\partial f}{\partial x}", ORANGE)} =
            \lim_{{h \to 0}} \frac{{f(x_0 + h, y_0) - f(x_0, y_0)}}{{h}}, \qquad
            {tex(r"\frac{\partial f}{\partial y}", LILA)} =
            \lim_{{k \to 0}} \frac{{f(x_0, y_0 + k) - f(x_0, y_0)}}{{k}}
            $$

            $$ {_fx}, \qquad {_fy}, \qquad {_dz} $$
            """
        )
    else:
        _out = mo.md(rf"$$ f(x, y) = {f_tex}, \qquad P = ({x0:g},\ {y0:g},\ {z0:.3f}) $$"
                     " — klicke auf **Herleitung abspielen**.")
    _out
    return


@app.cell
def _(np):
    def ease(s):
        """Sanftes Anfahren und Abbremsen: s läuft von 0 bis 1."""
        return (1 - np.cos(np.pi * s)) / 2
    return (ease,)


@app.cell
def _(
    GRUEN,
    LILA,
    ORANGE,
    ROT,
    azim_slider,
    ease,
    elev_slider,
    f,
    fx,
    fy,
    np,
    plt,
    x0,
    y0,
    z0,
):
    # ===== 4. Szene =====
    L = 2.0
    H_START = 1.3   # Startabstand der Sekante
    H_ENDE = 0.01   # "fast null"
    DX = DY = 0.6   # Schritt für das totale Differential in Phase 3

    _g = np.linspace(-L, L, 40)
    gx, gy = np.meshgrid(_g, _g)
    gz = f(gx, gy)
    z_lo, z_hi = gz.min(), gz.max()
    _pad = 0.15 * (z_hi - z_lo + 1e-9)
    z_lo, z_hi = z_lo - _pad, z_hi + _pad

    def im_bild(x, y, z):
        """Punkte außerhalb des Bildquaders ausblenden (NaN = Lücke)."""
        z = np.array(z, dtype=float)
        aus = (np.abs(x) > L) | (np.abs(y) > L) | (z < z_lo) | (z > z_hi)
        z[aus] = np.nan
        return x, y, z

    def make_scene():
        fig = plt.figure(figsize=(9, 8), dpi=80)
        ax = fig.add_subplot(projection="3d", computed_zorder=False)
        ax.set_xlim(-L, L)
        ax.set_ylim(-L, L)
        ax.set_zlim(z_lo, z_hi)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.view_init(elev=elev_slider.value, azim=azim_slider.value)

        ax.plot_surface(gx, gy, gz, color="lightgray", alpha=0.45, edgecolor="gray",
                        lw=0.2, zorder=1)
        ax.plot([x0], [y0], [z0], "o", color="black", ms=7, zorder=20)
        ax.text(x0, y0, z0 + 0.08 * (z_hi - z_lo), "P", fontsize=13, zorder=21)

        t = np.linspace(-L, L, 200)
        # Schnittebenen und Schnittkurven
        _pz = np.array([[z_lo, z_lo], [z_hi, z_hi]])
        plane_y = ax.plot_surface(np.array([[-L, L], [-L, L]]), np.full((2, 2), y0), _pz,
                                  color=ORANGE, alpha=0.12, zorder=2)
        plane_x = ax.plot_surface(np.full((2, 2), x0), np.array([[-L, L], [-L, L]]), _pz,
                                  color=LILA, alpha=0.12, zorder=2)
        curve_x, = ax.plot(*im_bild(t, np.full_like(t, y0), f(t, y0)), color=ORANGE,
                           lw=2.5, zorder=10)
        curve_y, = ax.plot(*im_bild(np.full_like(t, x0), t, f(x0, t)), color=LILA,
                           lw=2.5, zorder=10)

        # Sekanten (werden zu Tangenten) und Punkte Q
        sec_x, = ax.plot([], [], [], color=ORANGE, lw=2.8, ls="--", zorder=12)
        sec_y, = ax.plot([], [], [], color=LILA, lw=2.8, ls="--", zorder=12)
        q_x, = ax.plot([], [], [], "o", color=ORANGE, ms=9, mec="black", zorder=13)
        q_y, = ax.plot([], [], [], "o", color=LILA, ms=9, mec="black", zorder=13)

        # Tangentialebene: z = z0 + fx (x - x0) + fy (y - y0)
        _tp = np.linspace(-0.9, 0.9, 2)
        tx, ty = np.meshgrid(x0 + _tp, y0 + _tp)
        tangent_plane = ax.plot_surface(tx, ty, z0 + fx * (tx - x0) + fy * (ty - y0),
                                        color=GRUEN, alpha=0.0, zorder=5)
        # Totales Differential: dz (auf der Ebene) gegen Δf (auf der Fläche)
        x1, y1 = x0 + DX, y0 + DY
        dz = fx * DX + fy * DY
        df = f(x1, y1) - z0
        dz_line, = ax.plot([x1, x1], [y1, y1], [z0, z0 + dz], color=GRUEN, lw=3, zorder=14)
        err_line, = ax.plot([x1, x1], [y1, y1], [z0 + dz, z0 + df], color=ROT, lw=3,
                            zorder=14)
        base, = ax.plot([x0, x1, x1], [y0, y0, y1], [z0, z0, z0], color="black", lw=1,
                        ls=":", zorder=14)

        def info_line(row, color):
            return fig.text(0.03, 0.95 - 0.035 * row, "", color=color, fontsize=12)
        info1 = info_line(0, ORANGE)
        info2 = info_line(1, LILA)
        info3 = info_line(2, GRUEN)
        info4 = info_line(3, ROT)

        def sekante(richtung, h):
            """Gerade durch P und Q = P + h·Richtung auf der Fläche."""
            if richtung == "x":
                m = (f(x0 + h, y0) - z0) / h
                tau = np.linspace(-1.2, 1.6, 30)
                return (x0 + tau, np.full_like(tau, y0), z0 + m * tau), \
                       (x0 + h, y0, f(x0 + h, y0)), m
            m = (f(x0, y0 + h) - z0) / h
            tau = np.linspace(-1.2, 1.6, 30)
            return (np.full_like(tau, x0), y0 + tau, z0 + m * tau), \
                   (x0, y0 + h, f(x0, y0 + h)), m

        def update(s, active):
            """s von 0 bis 1, drei Phasen: x-Sekante, y-Sekante, Tangentialebene."""
            for artist in [plane_y, plane_x, curve_x, curve_y, sec_x, sec_y, q_x, q_y,
                           dz_line, err_line, base]:
                artist.set_visible(False)
            for line in (info1, info2, info3, info4):
                line.set_text("")
            tangent_plane.set_alpha(0.0)
            if not active:
                return

            # Phase 1: y festhalten, h -> 0
            p1 = np.clip(s * 3, 0, 1)
            h = H_START + (H_ENDE - H_START) * ease(p1)
            pts, q, m = sekante("x", h)
            sec_x.set_data_3d(*im_bild(*pts))
            q_x.set_data_3d([q[0]], [q[1]], [q[2]])
            for artist in [plane_y, curve_x, sec_x]:
                artist.set_visible(True)
            q_x.set_visible(p1 < 1)
            sec_x.set_linestyle("-" if p1 >= 1 else "--")
            info1.set_text(f"y = {y0:g} fest:  Δf/Δx = {m:.3f}  (h = {h:.2f})"
                           + ("  →  ∂f/∂x" if p1 >= 1 else ""))
            if s < 1 / 3:
                return

            # Phase 2: x festhalten, k -> 0
            p2 = np.clip(s * 3 - 1, 0, 1)
            k = H_START + (H_ENDE - H_START) * ease(p2)
            pts, q, m = sekante("y", k)
            sec_y.set_data_3d(*im_bild(*pts))
            q_y.set_data_3d([q[0]], [q[1]], [q[2]])
            plane_y.set_visible(False)
            for artist in [plane_x, curve_y, sec_y]:
                artist.set_visible(True)
            q_y.set_visible(p2 < 1)
            sec_y.set_linestyle("-" if p2 >= 1 else "--")
            info2.set_text(f"x = {x0:g} fest:  Δf/Δy = {m:.3f}  (k = {k:.2f})"
                           + ("  →  ∂f/∂y" if p2 >= 1 else ""))
            if s < 2 / 3:
                return

            # Phase 3: Tangentialebene und totales Differential
            p3 = ease(np.clip(s * 3 - 2, 0, 1))
            plane_x.set_visible(False)
            tangent_plane.set_alpha(0.4 * p3)
            for artist in [dz_line, err_line, base]:
                artist.set_visible(p3 > 0.5)
            info3.set_text(f"dz = ∂f/∂x·dx + ∂f/∂y·dy = {fx:.2f}·{DX} + {fy:.2f}·{DY}"
                           f" = {dz:.3f}")
            info4.set_text(f"tatsächlich Δf = {df:.3f}   (Fehler {df - dz:+.3f},"
                           " wird für kleine dx, dy vernachlässigbar)")

        return fig, update
    return (make_scene,)


@app.cell
def _(make_scene, mo, run_button, time):
    # ===== 5. Anzeige und Animation =====
    DURATION = 9.0  # drei Phasen à 3 Sekunden

    _fig, _update = make_scene()
    if run_button.value:
        _t0 = time.perf_counter()
        while (_s := (time.perf_counter() - _t0) / DURATION) < 1:
            _update(_s, active=True)
            mo.output.replace(_fig)
        _update(1, active=True)
    else:
        _update(0, active=False)
    _fig
    return


if __name__ == "__main__":
    app.run()
