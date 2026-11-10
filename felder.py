import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full")


@app.cell
def _(BLAU, ROT, farbig, mo):
    mo.md(f"""
    # Felder und Differentialgleichungen: Gravitation und B-Feld

    **Links** das Vektorfeld in 2D (Pfeile = Richtung, Hintergrund = Stärke bzw. Potential),
    **rechts** dieselbe Größe als 3D-Fläche („Heatmap in 3D“).

    Mit **Probeteilchen starten** wird eine **Differentialgleichung** numerisch gelöst:

    - **Gravitation:** Die Probemassen bewegen sich nach $\\ddot{{\\vec r}} = \\vec g(\\vec r)$.
      Das Feld ist ein **Gradientenfeld**, $\\vec g = -\\nabla\\Phi$: Die Pfeile zeigen
      überall „bergab“ im Potentialtrichter rechts.
    - **B-Feld:** Die Punkte folgen den **Feldlinien**, $\\dfrac{{d\\vec r}}{{ds}} =
      \\dfrac{{\\vec B}}{{|\\vec B|}}$. Das B-Feld eines Leiters hat Wirbel, deshalb gibt
      es kein Potential. Rechts ist stattdessen die Feldstärke $|\\vec B|$ als Fläche dargestellt.

    Farben: {farbig("Teilchen und Bahnen", ROT)}, {farbig("Startpunkte", BLAU)}.
    """)
    return


@app.cell
def _():
    import time
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    return LogNorm, mo, np, plt, time


@app.cell
def _():
    # ===== Farben =====
    BLAU = "#1f77b4"  # Startpunkte
    ROT = "#d62728"   # Probeteilchen und ihre Bahnen

    def farbig(text, color):
        """Färbt normalen Text (Markdown/HTML)."""
        return f'<span style="color:{color}">{text}</span>'
    return BLAU, ROT, farbig


@app.cell
def _(mo):
    # ===== 1. Eingabe =====
    # Quellen: (x, y, Stärke). Bei Masse: Stärke = G*M, bei Leitern: Strom
    # (positiv = aus der Bildebene heraus, negativ = hinein).
    BEISPIELE = {
        "Gravitation: eine Masse": ("grav", [(0, 0, 1.0)]),
        "Gravitation: zwei Massen": ("grav", [(-1.5, 0, 1.0), (1.5, 0, 0.6)]),
        "B-Feld: gerader Leiter": ("mag", [(0, 0, 1.0)]),
        "B-Feld: zwei Leiter, Ströme entgegengesetzt": ("mag", [(-1.5, 0, 1.0), (1.5, 0, -1.0)]),
        "B-Feld: zwei Leiter, Ströme gleichgerichtet": ("mag", [(-1.5, 0, 1.0), (1.5, 0, 1.0)]),
    }
    beispiel = mo.ui.dropdown(list(BEISPIELE), value="Gravitation: eine Masse", label="Beispiel")
    v0_slider = mo.ui.slider(0, 1.5, step=0.05, value=0.8, show_value=True,
                             label="Startgeschwindigkeit (× Kreisbahngeschwindigkeit, nur Gravitation)")
    run_button = mo.ui.run_button(label="▶ Probeteilchen starten")
    mo.vstack([beispiel, v0_slider, run_button])
    return BEISPIELE, beispiel, run_button, v0_slider


@app.cell
def _(BEISPIELE, beispiel, mo, np):
    # ===== 2. Physik: Feld und Potential =====
    art, quellen = BEISPIELE[beispiel.value]
    quellen = np.array(quellen, dtype=float)
    EPS = 0.3   # Glättung: verhindert unendliche Werte direkt an der Quelle
    L = 4.0     # Bildausschnitt von -L bis L

    def feld(x, y, eps=EPS):
        """Feldvektor an den Punkten (x, y). Funktioniert auch mit ganzen Arrays.
        eps: Glättung (für die Bahnrechnung wird ein kleinerer Wert verwendet)."""
        fx, fy = np.zeros_like(x, dtype=float), np.zeros_like(y, dtype=float)
        for qx, qy, k in quellen:
            dx, dy = x - qx, y - qy
            r2 = dx**2 + dy**2 + eps**2
            if art == "grav":
                # g = -G M (r - r_i) / |r - r_i|^3  (zeigt zur Masse hin)
                fx -= k * dx / r2**1.5
                fy -= k * dy / r2**1.5
            else:
                # B = μ0 I / (2π) * (ẑ × (r - r_i)) / |r - r_i|^2  (mit μ0 I/(2π) = k)
                fx += k * (-dy) / r2
                fy += k * dx / r2
        return fx, fy

    def potential(x, y):
        """Gravitationspotential Φ = -Σ G M / |r - r_i|."""
        phi = np.zeros_like(x, dtype=float)
        for qx, qy, k in quellen:
            phi -= k / np.sqrt((x - qx)**2 + (y - qy)**2 + EPS**2)
        return phi

    def hoehe(x, y):
        """Was als 3D-Fläche gezeigt wird: Potential (Gravitation) oder |B| (B-Feld)."""
        if art == "grav":
            return potential(x, y)
        bx, by = feld(x, y)
        return np.sqrt(bx**2 + by**2)

    if art == "grav":
        _formel = (r"$$ \Phi(\vec r) = -\sum_i \frac{G M_i}{|\vec r - \vec r_i|}, \qquad "
                   r"\vec g = -\nabla \Phi, \qquad \ddot{\vec r} = \vec g(\vec r) $$")
    else:
        _formel = (r"$$ \vec B(\vec r) = \sum_i \frac{\mu_0 I_i}{2\pi}\,"
                   r"\frac{\hat z \times (\vec r - \vec r_i)}{|\vec r - \vec r_i|^2}, \qquad "
                   r"\frac{d\vec r}{ds} = \frac{\vec B}{|\vec B|} $$")
    mo.md(_formel)
    return L, art, feld, hoehe, quellen


@app.cell
def _(art, feld, np, quellen, v0_slider):
    # ===== 3. Differentialgleichung numerisch lösen (vorab, dann nur abspielen) =====
    SCHRITTE = 1500

    def loese_gravitation():
        """Newton: r'' = g(r), gelöst mit dem Velocity-Verlet-Verfahren."""
        winkel = np.radians(np.arange(0, 360, 60) + 15)
        r0 = 2.8
        pos = np.array([r0 * np.cos(winkel), r0 * np.sin(winkel)])  # Form (2, n)
        gm_gesamt = quellen[:, 2].sum()
        v_kreis = np.sqrt(gm_gesamt / r0)
        vel = v0_slider.value * v_kreis * np.array([-np.sin(winkel), np.cos(winkel)])
        dt = 0.02
        bahn = np.empty((SCHRITTE, 2, len(winkel)))
        aktiv = np.ones(len(winkel), dtype=bool)
        acc = np.array(feld(*pos, eps=0.02))  # fast ungeglättet -> geschlossene Ellipsen
        for i in range(SCHRITTE):
            bahn[i] = pos
            neu_pos = pos + vel * dt + 0.5 * acc * dt**2
            neu_acc = np.array(feld(*neu_pos, eps=0.02))
            neu_vel = vel + 0.5 * (acc + neu_acc) * dt
            # Teilchen, die in eine Masse stürzen, bleiben dort liegen
            for qx, qy, _k in quellen:
                aktiv &= np.hypot(neu_pos[0] - qx, neu_pos[1] - qy) > 0.2
            pos = np.where(aktiv, neu_pos, pos)
            vel = np.where(aktiv, neu_vel, 0)
            acc = np.where(aktiv, neu_acc, 0)
        return bahn

    def loese_feldlinien():
        """Feldlinie: dr/ds = B/|B|, gelöst mit dem Runge-Kutta-Verfahren (RK4)."""
        if len(quellen) == 1:
            start = np.array([[0.7, 1.3, 2.0, 2.8, 3.5, -1.0],
                              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
        else:
            start = np.array([[-0.5, -1.0, -2.3, -3.3, 1.0, 2.6],
                              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])

        def richtung(p):
            bx, by = feld(*p)
            b = np.sqrt(bx**2 + by**2) + 1e-12
            return np.array([bx / b, by / b])

        ds = 0.02
        pos = start.astype(float)
        bahn = np.empty((SCHRITTE, 2, start.shape[1]))
        for i in range(SCHRITTE):
            bahn[i] = pos
            k1 = richtung(pos)
            k2 = richtung(pos + 0.5 * ds * k1)
            k3 = richtung(pos + 0.5 * ds * k2)
            k4 = richtung(pos + ds * k3)
            pos = pos + ds / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        return bahn

    bahnen = loese_gravitation() if art == "grav" else loese_feldlinien()
    return (bahnen,)


@app.cell
def _(BLAU, L, LogNorm, ROT, art, bahnen, feld, hoehe, np, plt, quellen):
    # ===== 4. Szene =====
    # Hintergrund / 3D-Fläche
    _n = 120
    gx, gy = np.meshgrid(np.linspace(-L, L, _n), np.linspace(-L, L, _n))
    gz = hoehe(gx, gy)
    # Pfeile (normiert: Länge zeigt nur die Richtung, die Farbe die Stärke)
    qx, qy = np.meshgrid(np.linspace(-L, L, 21), np.linspace(-L, L, 21))
    fx, fy = feld(qx, qy)
    fbetrag = np.sqrt(fx**2 + fy**2) + 1e-12
    # gröberes Netz für die 3D-Fläche (schneller zu zeichnen)
    sx, sy = np.meshgrid(np.linspace(-L, L, 36), np.linspace(-L, L, 36))
    sz = hoehe(sx, sy)
    z_min, z_max = sz.min(), sz.max()

    def make_scene():
        fig = plt.figure(figsize=(14, 6.5), dpi=80)
        ax2d = fig.add_subplot(1, 2, 1)
        # computed_zorder=False: die Teilchenspuren werden immer vor der Fläche gezeichnet
        ax3d = fig.add_subplot(1, 2, 2, projection="3d", computed_zorder=False)

        # --- 2D: Heatmap + Pfeile ---
        if art == "grav":
            ax2d.imshow(gz, extent=(-L, L, -L, L), origin="lower", cmap="viridis",
                        alpha=0.85)
            ax2d.set_title("Gravitationsfeld g (Pfeile) und Potential Φ (Farbe)",
                           fontsize=11)
        else:
            ax2d.imshow(gz, extent=(-L, L, -L, L), origin="lower", cmap="magma",
                        norm=LogNorm(vmin=gz.min(), vmax=gz.max()), alpha=0.85)
            ax2d.set_title("Magnetfeld B (Pfeile) und Feldstärke |B| (Farbe)", fontsize=11)
        ax2d.quiver(qx, qy, fx / fbetrag, fy / fbetrag, color="white", alpha=0.85,
                    scale=28, width=0.004)
        for x0, y0, k in quellen:
            if art == "grav":
                ax2d.plot(x0, y0, "o", color="black", ms=6 + 6 * k)
            else:
                # Punkt = Strom aus der Ebene heraus, Kreuz = in die Ebene hinein
                ax2d.plot(x0, y0, "o", mfc="white", mec="black", ms=14)
                ax2d.plot(x0, y0, "." if k > 0 else "x", color="black", ms=8)
        ax2d.set_xlim(-L, L)
        ax2d.set_ylim(-L, L)
        ax2d.set_aspect("equal")

        # --- 3D: Fläche als "Heatmap in 3D" ---
        ax3d.plot_surface(sx, sy, sz, cmap="viridis" if art == "grav" else "magma",
                          rstride=1, cstride=1, linewidth=0, antialiased=False, alpha=0.8,
                          zorder=1)
        ax3d.set_title("Potential Φ(x, y)" if art == "grav" else "Feldstärke |B|(x, y)",
                       fontsize=11)
        ax3d.set_xlim(-L, L)
        ax3d.set_ylim(-L, L)
        ax3d.set_zlim(z_min, z_max)
        ax3d.view_init(elev=30, azim=-60)

        # --- Probeteilchen ---
        n_teilchen = bahnen.shape[2]
        ax2d.plot(*bahnen[0], "o", color=BLAU, ms=5, zorder=4)
        spuren_2d = [ax2d.plot([], [], color=ROT, lw=1.5, zorder=5)[0]
                     for _ in range(n_teilchen)]
        punkte_2d, = ax2d.plot([], [], "o", color=ROT, ms=7, mec="white", zorder=6)
        spuren_3d = [ax3d.plot([], [], [], color=ROT, lw=1.5, zorder=10)[0]
                     for _ in range(n_teilchen)]
        punkte_3d, = ax3d.plot([], [], [], "o", color=ROT, ms=6, mec="white", zorder=11)

        def update(s, active):
            for artist in [*spuren_2d, punkte_2d, *spuren_3d, punkte_3d]:
                artist.set_visible(active)
            if not active:
                return
            i = max(1, int(s * (len(bahnen) - 1)))
            spur = bahnen[:i + 1].copy()
            # Punkte außerhalb des Bildausschnitts nicht zeichnen (NaN = Lücke)
            draussen = (np.abs(spur[:, 0]) > L) | (np.abs(spur[:, 1]) > L)
            spur[:, 0][draussen] = np.nan
            spur[:, 1][draussen] = np.nan
            for k in range(n_teilchen):
                x, y = spur[:, 0, k], spur[:, 1, k]
                spuren_2d[k].set_data(x, y)
                # im 3D-Bild auf der Fläche (leicht darüber, damit man sie sieht)
                z = np.clip(hoehe(x, y), z_min, z_max) + 0.02 * (z_max - z_min)
                spuren_3d[k].set_data_3d(x, y, z)
            x, y = spur[-1, 0], spur[-1, 1]
            punkte_2d.set_data(x, y)
            z = np.clip(hoehe(x, y), z_min, z_max) + 0.02 * (z_max - z_min)
            punkte_3d.set_data_3d(x, y, z)

        return fig, update
    return (make_scene,)


@app.cell
def _(make_scene, mo, run_button, time):
    # ===== 5. Anzeige und Animation =====
    DURATION = 8.0  # Sekunden

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
