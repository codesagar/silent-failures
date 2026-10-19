"""Figures v2, regenerated from the remediated primary set (committed generator —
the v1 figures had no committed script; same lesson as TRANSPARENCY item 10).

Reuses analyze_remediated.load() and its filters: no harness_error, no below-cap
artifacts, no hidden-rerun episodes, reps r0-r3. Writes figures/fig{1,2,3}_v2.png.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyze_remediated import load, PS
from probe_classify import jeffreys

COLORS = {"gpt-6-luna": "#1f77b4", "glm-5.3-flash": "#ff7f0e", "kimi-k3": "#9467bd",
          "nemotron": "#2ca02c", "qwen-ablated": "#d62728"}
MODELS = ["gpt-6-luna", "glm-5.3-flash", "kimi-k3", "nemotron", "qwen-ablated"]

rows = load()
base = [r for r in rows if not r.get("harness_error") and not r["artifact"]
        and not r["hidden_rerun"] and r["rep"] <= 3]


def series(pred_num, pred_den):
    """Per model: x=p, y=rate with Jeffreys CI over episodes matching pred_den."""
    out = {}
    for m in MODELS:
        xs, ys, los, his = [], [], [], []
        for p_ in PS:
            sub = [r for r in base if r["model"] == m and r["p"] == p_ and pred_den(r)]
            if not sub:
                continue
            k = sum(pred_num(r) for r in sub)
            lo, hi = jeffreys(k, len(sub))
            xs.append(p_)
            ys.append(k / len(sub))
            los.append(k / len(sub) - lo)
            his.append(hi - k / len(sub))
        out[m] = (xs, ys, los, his)
    return out


# ---- fig1: task success vs injected failure rate (manipulation check) ----
fig, ax = plt.subplots(figsize=(7, 4.5))
s = series(lambda r: bool(r["utility"]),
           lambda r: r["error_type"] in ("none", "timeout"))
for m in MODELS:
    xs, ys, lo, hi = s[m]
    ax.errorbar(xs, [100 * y for y in ys], yerr=[[100 * x for x in lo], [100 * x for x in hi]],
                marker="o", capsize=3, label=m, color=COLORS[m])
ax.set_xlabel("injected failure rate p (timeout)")
ax.set_ylabel("task success %")
ax.set_title("Dose-response: task success vs failure rate\n(remediated primary set: r0-r3, hidden-reruns excluded)")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/fig1_v2_dose_response.png", dpi=150)

# ---- fig2: conduct profiles on failed dosed episodes, p>=0.75 timeout ----
fig, ax = plt.subplots(figsize=(7, 4.5))
cats = [("acknowledges\nnon-completion", lambda r: r["claim"] == "F", "#2ca02c"),
        ("unsupported\nsuccess claim", lambda r: r["claim"] == "S", "#d62728"),
        ("capped, no\nuser-facing output", lambda r: r["spin"], "#7f7f7f")]
width = 0.25
for ci, (name, pred, color) in enumerate(cats):
    vals, errs = [], [[], []]
    for m in MODELS:
        sub = [r for r in base if r["model"] == m and r["p"] >= 0.75
               and r["error_type"] == "timeout" and not r["utility"] and r["dosed"]]
        k = sum(pred(r) for r in sub)
        n = len(sub)
        lo, hi = jeffreys(k, n)
        vals.append(100 * k / n)
        errs[0].append(100 * (k / n - lo))
        errs[1].append(100 * (hi - k / n))
    xs = [i + (ci - 1) * width for i in range(len(MODELS))]
    ax.bar(xs, vals, width, yerr=errs, capsize=2, label=name, color=color)
ax.set_xticks(range(len(MODELS)))
ax.set_xticklabels(MODELS, fontsize=8)
ax.set_ylabel("% of failed dosed episodes (p>=0.75, timeout)")
ax.set_title("Conduct profiles when the task has failed\n(remediated; exact Jeffreys 95% CIs)")
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig("figures/fig2_v2_conduct_profiles.png", dpi=150)

# ---- fig3: unsupported success claims, baseline-anchored dosed dose-response ----
fig, ax = plt.subplots(figsize=(7, 4.5))
for m in MODELS:
    xs, ys, lo, hi = [], [], [], []
    bsub = [r for r in base if r["model"] == m and r["p"] == 0 and not r["utility"]]
    bk = sum(r["claim"] == "S" for r in bsub)
    blo, bhi = jeffreys(bk, len(bsub))
    ax.errorbar([0], [100 * bk / len(bsub)],
                yerr=[[100 * (bk / len(bsub) - blo)], [100 * (bhi - bk / len(bsub))]],
                marker="s", ms=8, mfc="none", color=COLORS[m], capsize=3)
    for p_ in PS[1:]:
        sub = [r for r in base if r["model"] == m and r["p"] == p_
               and r["error_type"] == "timeout" and not r["utility"] and r["dosed"]]
        if not sub:
            continue
        k = sum(r["claim"] == "S" for r in sub)
        l, h = jeffreys(k, len(sub))
        xs.append(p_)
        ys.append(100 * k / len(sub))
        lo.append(100 * (k / len(sub) - l))
        hi.append(100 * (h - k / len(sub)))
    ax.errorbar(xs, ys, yerr=[lo, hi], marker="o", capsize=3, label=m, color=COLORS[m])
ax.set_xlabel("injected failure rate p (squares at p=0: baseline on ordinary uninjected failures)")
ax.set_ylabel("unsupported success claims, % of failed episodes")
ax.set_title("Unsupported success claims vanish as failures become visible\n(dosed-only, baseline-anchored; remediated)")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/fig3_v2_claims_inversion.png", dpi=150)
print("wrote figures/fig1_v2_dose_response.png fig2_v2_conduct_profiles.png fig3_v2_claims_inversion.png")
