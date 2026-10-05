"""
Scoring model for the Nen Hexagon Cognition Test.

Everything here is pure Python (no Streamlit) so it can be tested and reused.

Layer 1  Kozhevnikov et al. (2014) / Ho & Kozhevnikov (2023) style matrix:
         4 families x 3 levels (+ one metastyle), scored -1..+1 internally and
         shown on the FICS-like -10..+10 scale.
         Sign convention follows Ho & Kozhevnikov (2023): positive = context-
         independent, rule-based, compartmentalised, internal locus ("scientific"
         poles); negative = context-dependent, intuitive, integrative, external.
Layer 2  The three Nen-model axes from our framework:
         YIN  (+ sensitive / abstract / lateral   vs  - robust / concrete / linear)
         DYN  (+ dynamic: things in motion       vs  - static: things at rest)
         SLOW (+ accumulate / regulate (Yin half) vs  - burst / expend (Yang half))
Layer 3  Six Nen prototypes in that 7-dimensional space, combined with the
         direct best-worst "operation" task, turned into percentages.
"""
import math

TYPES = ["Enhancer", "Transmuter", "Conjurer", "Specialist", "Manipulator", "Emitter"]
KEYS = ["enh", "tra", "con", "spe", "man", "emi"]
# angle on the Nen chart (degrees, counter-clockwise from the right; Enhancer at the top)
ANGLES = {"enh": 90, "tra": 30, "con": -30, "spe": -90, "man": 210, "emi": 150}
OPPOSITE = {"enh": "spe", "spe": "enh", "tra": "man", "man": "tra", "con": "emi", "emi": "con"}

FAMILIES = ["CTX", "RULE", "COMP", "LOC"]
FAMILY_NAMES = {
    "CTX": ("Context", "context-dependent", "context-independent"),
    "RULE": ("Rule", "intuitive", "rule-based"),
    "COMP": ("Integration", "integrative", "compartmentalised"),
    "LOC": ("Locus", "external locus", "internal locus"),
}
LEVELS = ["P", "CF", "HoC"]
LEVEL_NAMES = {"P": "Perception", "CF": "Concept formation", "HoC": "Higher-order cognition"}
NEN_DIMS = ["YIN", "DYN", "SLOW"]
DIM_ORDER = FAMILIES + NEN_DIMS
DIM_WEIGHTS = {"CTX": 1.0, "RULE": 1.0, "COMP": 1.0, "LOC": 1.0, "YIN": 1.3, "DYN": 1.3, "SLOW": 1.3}

# Prototype of each Nen style in the 7-D space (order = DIM_ORDER).
# Derived from the model: content side = context-independent, internal, static;
# context side = context-dependent, external, dynamic; Yang half = burst; Yin half = accumulate;
# Enhancer = robust/concrete/single-line; Specialist = sensitive/abstract/integrative.
PROTOTYPES = {
    #        CTX   RULE  COMP  LOC   YIN   DYN   SLOW
    "enh": [0.3, 0.0, 0.6, 0.5, -1.0, 0.0, -0.6],
    "tra": [0.6, -0.6, 0.3, 0.4, -0.4, -0.8, -0.6],
    "con": [0.7, 0.8, 0.3, 0.6, 0.4, -0.8, 0.7],
    "spe": [0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.4],
    "man": [-0.7, 0.6, -0.3, -0.4, 0.4, 0.8, 0.7],
    "emi": [-0.6, -0.6, 0.0, -0.6, -0.4, 0.8, -0.7],
}

OPS_WEIGHT = 2.4      # direct operation task (dominant, as requested)
PROFILE_WEIGHT = 2.2  # distance to prototypes in the style space


def clip(x, lo=-1.0, hi=1.0):
    return max(lo, min(hi, x))


def wmean(pairs):
    """Weighted mean of (value, weight) pairs, ignoring None values."""
    pairs = [(v, w) for v, w in pairs if v is not None]
    tw = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / tw if tw else 0.0


# ---------------------------------------------------------------- task indices
def frame_line_indices(trials):
    """trials: dicts with mode ('abs'|'rel'), response, correct.
    Returns (context_independence -1..1, mobility 0..1, abs_err, rel_err)."""
    def err(mode):
        e = [abs(t["response"] - t["correct"]) / t["correct"] for t in trials if t["mode"] == mode]
        return sum(e) / len(e) if e else None
    a, r = err("abs"), err("rel")
    if a is None or r is None:
        return None, None, a, r
    ctx = clip((r - a) / (r + a + 0.04))          # better at absolute than relative = context-independent
    mobility = clip(1 - ((a + r) / 2) / 0.30, 0, 1)  # accurate in both modes = mobile (Witkin)
    return ctx, mobility, a, r


def global_local_indices(trials):
    """trials: dicts with choice ('global'|'local'), rt (s).
    Returns (compartmentalisation -1..1, impulsivity -1..1, global share, median rt)."""
    if not trials:
        return None, None, None, None
    g = sum(t["choice"] == "global" for t in trials) / len(trials)
    rts = sorted(t["rt"] for t in trials)
    med = rts[len(rts) // 2]
    impulsivity = clip((4.0 - med) / 3.0)
    return clip(1 - 2 * g), impulsivity, g, med


def triad_index(trials):
    """Share of taxonomic (rule/category) pairings -> -1..1."""
    if not trials:
        return None, None
    t = sum(x["choice"] == "taxonomic" for x in trials) / len(trials)
    return 2 * t - 1, t


def category_width(answers):
    """answers: values 0, 0.5, 1 (no / partly / yes). Broad categories -> +1."""
    if not answers:
        return None, None
    w = sum(answers) / len(answers)
    return clip(2 * w - 1), w


def remote_indices(trials):
    """trials: dicts with correct (bool), how ('insight'|'analysis'|'none').
    Returns (lateral -1..1, intuitive -1..1 or None, accuracy, insight share)."""
    if not trials:
        return None, None, None, None
    acc = sum(t["correct"] for t in trials) / len(trials)
    solved = [t for t in trials if t["correct"]]
    ins = (sum(t["how"] == "insight" for t in solved) / len(solved)) if solved else None
    lateral = clip((acc - 0.4) / 0.4)
    intuitive = clip(2 * ins - 1) if ins is not None else None
    return lateral, intuitive, acc, ins


def ambiguity_index(counts):
    """counts: number of meanings noticed (1..4). More meanings -> +1 (low unit filtering)."""
    if not counts:
        return None, None
    m = sum(counts) / len(counts)
    return clip((m - 2.0) / 1.5), m


def operation_scores(scenarios):
    """scenarios: dicts with best, worst (type keys). Returns key -> -1..1."""
    n = max(len(scenarios), 1)
    out = {k: 0.0 for k in KEYS}
    for s in scenarios:
        out[s["best"]] += 1
        out[s["worst"]] -= 1
    return {k: v / n for k, v in out.items()}


# ---------------------------------------------------------------- full profile
def build_profile(data, slider_items):
    """data keys: sliders {id: -10..10}, meta {id: 0..10}, frame, gl, triads, catw, remote, amb, ops."""
    sl = data["sliders"]
    by = {}
    for it in slider_items:
        if it["dim"] == "CHECK" or it["id"] not in sl:
            continue
        by.setdefault((it["dim"], it.get("level")), []).append(sl[it["id"]] / 10.0)

    def s(dim, level=None):
        v = by.get((dim, level))
        return sum(v) / len(v) if v else None

    fr_ctx, fr_mob, abs_err, rel_err = frame_line_indices(data["frame"])
    gl_comp, gl_imp, gl_share, gl_rt = global_local_indices(data["gl"])
    tri, tri_share = triad_index(data["triads"])
    cw, cw_share = category_width(data["catw"])
    lat, intu, rat_acc, ins_share = remote_indices(data["remote"])
    amb, amb_mean = ambiguity_index(data["amb"])

    cells = {
        ("CTX", "P"): wmean([(s("CTX", "P"), 1), (fr_ctx, 1.5)]),
        ("CTX", "CF"): wmean([(s("CTX", "CF"), 1), (tri, 0.75)]),
        ("CTX", "HoC"): wmean([(s("CTX", "HoC"), 1)]),
        ("RULE", "P"): wmean([(s("RULE", "P"), 1), (-gl_imp if gl_imp is not None else None, 0.5)]),
        ("RULE", "CF"): wmean([(s("RULE", "CF"), 1), (tri, 0.5)]),
        ("RULE", "HoC"): wmean([(s("RULE", "HoC"), 1), (-intu if intu is not None else None, 0.75)]),
        ("COMP", "P"): wmean([(s("COMP", "P"), 1), (gl_comp, 1.5)]),
        ("COMP", "CF"): wmean([(s("COMP", "CF"), 1), (-cw if cw is not None else None, 1)]),
        ("COMP", "HoC"): wmean([(s("COMP", "HoC"), 1)]),
        ("LOC", "P"): wmean([(s("LOC", "P"), 1)]),
        ("LOC", "CF"): wmean([(s("LOC", "CF"), 1)]),
        ("LOC", "HoC"): wmean([(s("LOC", "HoC"), 1)]),
    }
    fam = {f: sum(cells[(f, l)] for l in LEVELS) / 3 for f in FAMILIES}

    meta_vals = list(data["meta"].values())
    meta_self = sum(meta_vals) / len(meta_vals) / 10 if meta_vals else None
    metastyle = wmean([(meta_self, 2), (fr_mob, 1)])

    dims = dict(fam)
    dims["YIN"] = wmean([(s("YIN"), 2), (lat, 1), (amb, 1), (cw, 0.5)])
    dims["DYN"] = wmean([(s("DYN"), 1)])
    dims["SLOW"] = wmean([(s("SLOW"), 1)])

    ops = operation_scores(data["ops"])
    return {
        "cells": cells, "families": fam, "metastyle": metastyle, "dims": dims, "ops": ops,
        "tasks": {
            "frame_abs_error": abs_err, "frame_rel_error": rel_err, "frame_context_index": fr_ctx,
            "frame_mobility": fr_mob, "global_share": gl_share, "global_median_rt": gl_rt,
            "taxonomic_share": tri_share, "category_width": cw_share, "remote_accuracy": rat_acc,
            "insight_share": ins_share, "meanings_noticed": amb_mean,
        },
    }


def nen_percentages(profile):
    d = profile["dims"]
    tw = sum(DIM_WEIGHTS.values())
    sims, logits = {}, {}
    for k in KEYS:
        dist = sum(DIM_WEIGHTS[n] * (d[n] - p) ** 2 for n, p in zip(DIM_ORDER, PROTOTYPES[k])) / tw
        sims[k] = -dist
        logits[k] = OPS_WEIGHT * profile["ops"][k] + PROFILE_WEIGHT * sims[k]
    # flexible people (high metastyle) spread across more types: higher temperature
    tau = 0.7 + 0.6 * profile["metastyle"]
    m = max(logits.values())
    ex = {k: math.exp((v - m) / tau) for k, v in logits.items()}
    tot = sum(ex.values())
    pct = {k: 100 * v / tot for k, v in ex.items()}
    x = sum(pct[k] / 100 * math.cos(math.radians(ANGLES[k])) for k in KEYS)
    y = sum(pct[k] / 100 * math.sin(math.radians(ANGLES[k])) for k in KEYS)
    return {"pct": pct, "similarity": sims, "logits": logits, "tau": tau,
            "x": x, "y": y, "purity": math.hypot(x, y)}


def round_percentages(pct):
    """Largest-remainder rounding so the six integers add up to exactly 100."""
    floors = {k: int(math.floor(v)) for k, v in pct.items()}
    rest = 100 - sum(floors.values())
    for k in sorted(pct, key=lambda k: pct[k] - floors[k], reverse=True)[:rest]:
        floors[k] += 1
    return floors


def manga_affinity(primary):
    """Hunter x Hunter learning rule: own 100, neighbours 80, two steps 60, opposite 40."""
    idx = KEYS.index(primary)
    out = {}
    for i, k in enumerate(KEYS):
        step = min((i - idx) % 6, (idx - i) % 6)
        out[k] = [100, 80, 60, 40][step]
    return out
