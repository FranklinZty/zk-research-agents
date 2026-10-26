#!/usr/bin/env python3
"""P02 -- prover-time breakdown as horizontal stacked bars (instead of pies).

Pattern: one row per prover, one segment per proving phase (witness generation,
commitment, sum-check / quotient, opening), identical phase order and colour in
every row; total at the bar end; a single bracket states the headline ratio.
The caption states the timing scope (here: witness generation included, setup and
preprocessing excluded) and the common soundness level.  Pies make cross-method
comparison impossible -- use this.  SYNTHETIC DATA.
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "style"))
import palette as P
import numpy as np


def make(venue="lncs", outdir=ROOT / "examples"):
    stages = ["witness", "commit", "sum-check / quotient", "open"]
    methods = ["Baseline A", "Baseline B", "Ours"]
    t = np.array([[1.1, 9.4, 5.6, 2.7],
                  [1.1, 6.0, 5.9, 2.0],
                  [1.1, 2.4, 4.1, 0.9]])     # seconds, synthetic
    fig, ax = P.figure(venue, width="full", aspect=0.30)
    y = np.arange(len(methods))[::-1]
    left = np.zeros(len(methods))
    for j, s in enumerate(stages):
        ax.barh(y, t[:, j], left=left, height=0.62, color=P.CATEGORICAL[j], label=s,
                edgecolor="white", linewidth=0.8, hatch=P.HATCHES[j] if j == 3 else None)
        left += t[:, j]
    for yi, tot in zip(y, left):
        ax.text(tot + 0.2, yi, f"{tot:.1f} s", va="center", fontsize="small")
    ratio = left[0] / left[-1]
    ax.annotate("", xy=(left[-1], y[-1] - 0.42), xytext=(left[0], y[-1] - 0.42),
                arrowprops=dict(arrowstyle="<->", color=P.INK_2, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text((left[0] + left[-1]) / 2, y[-1] - 0.5, f"{ratio:.1f}" + r"$\times$ faster", ha="center", va="top",
            fontsize="small", color=P.INK)
    ax.set_yticks(y, methods)
    ax.set_xlabel("prover time (s), witness generation included")
    ax.set_xlim(0, left.max() * 1.12)
    ax.set_ylim(y[-1] - 0.95, y[0] + 0.5)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.tick_params(axis="y", length=0)
    ax.legend(ncols=4, loc="lower left", bbox_to_anchor=(0, 1.0), fontsize="small")
    return P.save(fig, "p02_breakdown_stacked", outdir)


if __name__ == "__main__":
    P.cli(make, __doc__)
