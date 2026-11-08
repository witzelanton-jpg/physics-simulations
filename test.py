import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    return mo, np, plt


@app.cell
def _(mo):
    frequenz = mo.ui.slider(0.5, 5, step=0.5, value=1, label="Frequenz (Hz)")
    frequenz
    return (frequenz,)


@app.cell
def _(frequenz, np, plt):
    t = np.linspace(0, 2, 500)
    fig, ax = plt.subplots()
    ax.plot(t, np.sin(2 * np.pi * frequenz.value * t))
    ax.set_xlabel("Zeit (s)")
    fig
    return


if __name__ == "__main__":
    app.run()
