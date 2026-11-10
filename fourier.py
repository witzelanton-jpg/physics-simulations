import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _(BLAU, GRAU, mo):
    mo.md(f"""
    # Fourier-Transformation: Signal in Schwingungen zerlegen

    Ein Signal entsteht aus bis zu 5 überlagerten Sinusschwingungen
    $x(t) = \\sum_k A_k \\sin(2\\pi f_k t)$. Die **Fourier-Transformation** zerlegt das
    {'<span style="color:' + GRAU + '">Gesamtsignal</span>'} wieder in seine Bestandteile:
    Im **Spektrum** erscheint bei jeder Frequenz $f_k$ ein Ausschlag der Höhe $A_k$.

    Mit **Zerlegung starten** werden die Schwingungen nacheinander herausgelöst. Die
    {'<span style="color:' + BLAU + '">Rekonstruktion</span>'} nähert sich dem Signal an,
    und im Spektrum wachsen die zugehörigen Ausschläge.

    Tipp: Die Startwerte $f_k = 1, 3, 5, 7, 9$ Hz mit $A_k = 1/f_k$ ergeben
    näherungsweise ein **Rechtecksignal**.
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
    # ===== Farben: einmal festlegen, überall verwenden =====
    GRAU = "#808080"  # Gesamtsignal (Ziel)
    BLAU = "#1f77b4"  # Rekonstruktion und Spektrum
    # eine eigene Farbe pro Teilschwingung
    KOMPONENTEN_FARBEN = ["#ff8c00", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    def farbig(text, color):
        """Färbt normalen Text (Markdown/HTML)."""
        return f'<span style="color:{color}">{text}</span>'
    return BLAU, GRAU, KOMPONENTEN_FARBEN, farbig


@app.cell
def _(mo):
    # ===== 1a. Anzahl der Schwingungen =====
    n_slider = mo.ui.slider(1, 5, step=1, value=3, label="Anzahl Schwingungen",
                            show_value=True)
    n_slider
    return (n_slider,)


@app.cell
def _(KOMPONENTEN_FARBEN, farbig, mo):
    # ===== 1b. Frequenzen und Amplituden (immer alle 5 anlegen) =====
    # So bleiben die Einstellungen erhalten, wenn man die Anzahl ändert.
    _f0 = [1, 3, 5, 7, 9]
    freqs = mo.ui.array([
        mo.ui.slider(0.5, 10, step=0.5, value=_f0[k], show_value=True,
                     label=f"{farbig(f'f{k + 1}', KOMPONENTEN_FARBEN[k])} (Hz)")
        for k in range(5)
    ])
    amps = mo.ui.array([
        mo.ui.slider(0, 2, step=0.05, value=round(1 / _f0[k], 2), show_value=True,
                     label=f"{farbig(f'A{k + 1}', KOMPONENTEN_FARBEN[k])}")
        for k in range(5)
    ])
    run_button = mo.ui.run_button(label="▶ Zerlegung starten")
    return amps, freqs, run_button


@app.cell
def _(amps, freqs, mo, n_slider, run_button):
    # ===== 1c. Nur die ersten N Regler anzeigen =====
    mo.vstack(
        [mo.hstack([freqs[k], amps[k]], justify="start") for k in range(n_slider.value)]
        + [run_button]
    )
    return


@app.cell
def _(amps, freqs, mo, n_slider, np):
    # ===== 2. Signal und Spektrum berechnen =====
    N = n_slider.value
    f_k = np.array(freqs.value[:N], dtype=float)
    A_k = np.array(amps.value[:N], dtype=float)

    T_FFT = 4.0   # Messdauer für die FFT (s) -> Frequenzauflösung 1/T = 0.25 Hz
    FS = 200      # Abtastrate (Hz)
    t = np.arange(0, T_FFT, 1 / FS)
    T_SHOW = 2.0  # angezeigter Zeitausschnitt (s)
    show = t < T_SHOW

    # Jede Teilschwingung als eigene Zeile: Form (N, Anzahl Zeitpunkte)
    components = A_k[:, None] * np.sin(2 * np.pi * f_k[:, None] * t[None, :])
    signal = components.sum(axis=0)

    spec_f = np.fft.rfftfreq(len(t), 1 / FS)

    def spectrum(x):
        """Amplitudenspektrum: Höhe des Ausschlags = Amplitude der Schwingung."""
        return 2 * np.abs(np.fft.rfft(x)) / len(x)

    _terme = " + ".join(f"{a:g}\\sin(2\\pi\\cdot{f:g}\\,t)" for f, a in zip(f_k, A_k))
    mo.md(rf"$$ x(t) = {_terme} $$")
    return A_k, N, T_SHOW, components, f_k, show, signal, spec_f, spectrum, t


@app.cell
def _(np):
    def ease(s):
        """Sanftes Anfahren und Abbremsen: s läuft von 0 bis 1."""
        return (1 - np.cos(np.pi * s)) / 2
    return (ease,)


@app.cell
def _(
    A_k,
    BLAU,
    GRAU,
    KOMPONENTEN_FARBEN,
    N,
    T_SHOW,
    components,
    ease,
    f_k,
    np,
    plt,
    show,
    signal,
    spec_f,
    spectrum,
    t,
):
    # ===== 3. Szene =====
    ymax = max(np.abs(signal).max(), A_k.max(), 0.1) * 1.15

    def make_scene():
        # dpi=80: etwas gröber, dafür flüssigere Animation
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 9), dpi=80,
                                            gridspec_kw=dict(height_ratios=[1, 1, 1.1]))
        fig.subplots_adjust(hspace=0.45)

        # Oben: einzelne Schwingungen
        ax1.set_title("Teilschwingungen", loc="left", fontsize=11)
        ax1.set_xlim(0, T_SHOW)
        ax1.set_ylim(-ymax, ymax)
        ax1.set_xlabel("Zeit t (s)")
        ax1.axhline(0, color="lightgray", lw=1)
        comp_lines = [ax1.plot([], [], color=KOMPONENTEN_FARBEN[k], lw=1.5,
                               label=f"f{k + 1} = {f_k[k]:g} Hz")[0] for k in range(N)]
        ax1.legend(loc="upper right", fontsize=8, ncol=min(N, 5))
        hint = ax1.text(T_SHOW / 2, 0, "?", fontsize=40, color="lightgray",
                        ha="center", va="center")

        # Mitte: Gesamtsignal und Rekonstruktion
        ax2.set_title("Signal und Rekonstruktion", loc="left", fontsize=11)
        ax2.set_xlim(0, T_SHOW)
        ax2.set_ylim(-ymax, ymax)
        ax2.set_xlabel("Zeit t (s)")
        ax2.axhline(0, color="lightgray", lw=1)
        ax2.plot(t[show], signal[show], color=GRAU, lw=2.5, alpha=0.6, label="Signal x(t)")
        recon_line, = ax2.plot([], [], color=BLAU, lw=1.5, label="Rekonstruktion")
        ax2.legend(loc="upper right", fontsize=8)

        # Unten: Spektrum
        ax3.set_title("Spektrum (Fourier-Transformation)", loc="left", fontsize=11)
        ax3.set_xlim(0, 11)
        ax3.set_ylim(0, max(A_k.max(), 0.1) * 1.25)
        ax3.set_xlabel("Frequenz f (Hz)")
        ax3.set_ylabel("Amplitude")
        ax3.set_xticks(range(0, 12))
        ax3.grid(alpha=0.3)
        spec_line, = ax3.plot([], [], color=BLAU, lw=1.5)
        peak_dots = [ax3.plot([], [], "o", color=KOMPONENTEN_FARBEN[k], ms=8, zorder=5)[0]
                     for k in range(N)]
        peak_texts = [ax3.text(0, 0, "", color=KOMPONENTEN_FARBEN[k], ha="center",
                               va="bottom", fontsize=9) for k in range(N)]

        def update(s, active):
            """s von 0 bis 1: die Teilschwingungen erscheinen nacheinander."""
            hint.set_visible(not active)
            for artist in [recon_line, spec_line, *comp_lines, *peak_dots, *peak_texts]:
                artist.set_visible(active)
            if not active:
                return

            # Fortschritt jeder einzelnen Schwingung (k-te startet nach k/N der Zeit)
            p = np.array([ease(np.clip(s * N - k, 0, 1)) for k in range(N)])
            current = p[:, None] * components
            recon = current.sum(axis=0)
            for k in range(N):
                comp_lines[k].set_data(t[show], current[k][show])
            recon_line.set_data(t[show], recon[show])

            # Spektrum der bisherigen Rekonstruktion
            amp = spectrum(recon)
            spec_line.set_data(spec_f, amp)
            for k in range(N):
                height = amp[np.argmin(np.abs(spec_f - f_k[k]))]
                peak_dots[k].set_data([f_k[k]], [height])
                peak_dots[k].set_visible(p[k] > 0.01)
                peak_texts[k].set_position((f_k[k], height + 0.04 * ax3.get_ylim()[1]))
                peak_texts[k].set_text(f"{height:.2f}" if p[k] > 0.01 else "")

        return fig, update
    return (make_scene,)


@app.cell
def _(N, make_scene, mo, run_button, time):
    # ===== 4. Anzeige und Animation =====
    DURATION = 1.2 * N + 0.8  # pro Schwingung etwa 1.2 Sekunden

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
