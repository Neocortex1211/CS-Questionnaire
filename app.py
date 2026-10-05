"""
Nen Hexagon Cognition Test
==========================
A ~18-minute test that places you on the six-type Nen hexagon (Enhancer, Transmuter,
Conjurer, Specialist, Manipulator, Emitter) as continuous percentages.

Structure borrowed from the cognitive-style literature:
  * Kozhevnikov, Evans & Kosslyn (2014), Psychological Science in the Public Interest 15:3-33
    (4 style families x levels of processing, plus metastyle)
  * Ho & Kozhevnikov (2023), British Journal of Educational Psychology 93:978-996
    (FICS-style bipolar -10..+10 scenarios, metastyle items)
  * Classic behavioural paradigms: framed-line test (Kitayama et al. 2003), global/local
    similarity (Kimchi 1992), triads (Ji, Zhang & Nisbett 2004), category width
    (Pettigrew 1958), compound remote associates with insight reports.
The Nen layer (axes, prototypes, operation task) comes from our own hexagon model.

NOT a validated instrument. For fun and self-reflection among friends.

Run:        streamlit run app.py
Dev mode:   add ?dev=1 to the URL for a "simulate answers" shortcut.
"""
import datetime
import io
import json
import math
import os
import random
import time
import uuid

import altair as alt
import pandas as pd
import streamlit as st

import content as C
import scoring as S

st.set_page_config(page_title="Nen Hexagon Cognition Test", page_icon="⬡", layout="centered")
DEV = st.query_params.get("dev") == "1"
ss = st.session_state

st.markdown("""
<style>
.block-container {max-width: 760px;}
h1, h2, h3 {letter-spacing: -0.01em;}
.nen-q {font-size: 1.05rem; font-weight: 600; margin: 0.9rem 0 0.1rem 0;}
.nen-pole {font-size: 0.86rem; color: #4A5560; line-height: 1.3;}
.nen-card {border-left: 4px solid var(--c); padding: 0.4rem 0 0.4rem 0.9rem; margin: 0.6rem 0;}
.nen-big {text-align:center; font-size: 1.5rem; font-weight: 600; padding: 0.8rem 0;}
</style>""", unsafe_allow_html=True)

SECTIONS = [  # phase, title, rough minutes
    ("welcome", "Welcome", 0),
    ("frame", "Lines in frames", 2.5),
    ("ops1", "What would you do? (part 1)", 2.5),
    ("gl", "Shapes made of shapes", 1.5),
    ("triads", "Which two go together?", 1.5),
    ("remote", "Remote links", 3.5),
    ("ops2", "What would you do? (part 2)", 2.5),
    ("catw", "Does it count?", 1),
    ("amb", "How many meanings?", 1),
    ("sliders", "Leanings", 4),
    ("results", "Your hexagon", 0),
]
OPS_SPLIT = 5


# =============================================================== state
def init_state():
    if "init" in ss:
        return
    rng = random.Random()
    ss.init = True
    ss.pid = uuid.uuid4().hex[:8]
    ss.started = datetime.datetime.now().isoformat(timespec="seconds")
    ss.t_start = time.time()
    ss.step = 0
    ss.name = ""
    # framed line: two blocks (absolute / relative), order counterbalanced
    modes = ["abs", "rel"]
    rng.shuffle(modes)
    trials = []
    for m in modes:
        idx = list(range(len(C.FRAME_TRIALS)))
        rng.shuffle(idx)
        trials += [{"mode": m, "k": i, "start": rng.randint(15, 70)} for i in idx]
    ss.fl = {"trials": trials, "i": 0, "stage": "intro", "log": []}
    # global/local: randomise which side shows the global match
    ss.gl = {"order": [(t, rng.random() < 0.5) for t in rng.sample(C.GL_TRIALS, len(C.GL_TRIALS))],
             "i": 0, "t0": None, "log": []}
    ss.triad_order = [(t, rng.random() < 0.5) for t in rng.sample(C.TRIADS, len(C.TRIADS))]
    ss.triads = []
    ss.remote = {"order": rng.sample(range(len(C.REMOTE_ITEMS)), len(C.REMOTE_ITEMS)), "i": 0,
                 "t0": None, "log": []}
    ss.ops_order = rng.sample(range(len(C.OPS_SCENARIOS)), len(C.OPS_SCENARIOS))
    ss.ops_opts = {i: rng.sample(S.KEYS, 6) for i in range(len(C.OPS_SCENARIOS))}
    ss.ops_i = 0
    ss.ops = []
    ss.catw = []
    ss.amb = []
    ss.sl = {}
    ss.meta = {}
    ss.sl_page = 0
    ss.saved = False


def phase():
    return SECTIONS[ss.step][0]


def advance():
    ss.step += 1


def restart():
    for k in list(ss.keys()):
        del ss[k]


def header():
    p, title, _ = SECTIONS[ss.step]
    if p in ("welcome", "results"):
        return
    left = sum(m for _, _, m in SECTIONS[ss.step:])
    st.progress(ss.step / (len(SECTIONS) - 1))
    el = int(time.time() - ss.t_start)
    st.caption(f"Section {ss.step} of {len(SECTIONS) - 2}: {title}  ·  elapsed {el // 60}:{el % 60:02d}  ·  "
               f"about {math.ceil(left)} min to go")


# =============================================================== SVG helpers
def svg(inner, w, h):
    return f"<svg width='{w}' height='{h}' viewBox='0 0 {w} {h}' xmlns='http://www.w3.org/2000/svg'>{inner}</svg>"


def frame_svg(size, line, box=200):
    o = (box - size) / 2
    cx = box / 2
    inner = (f"<rect x='{o}' y='{o}' width='{size}' height='{size}' fill='none' stroke='#1C2430' stroke-width='2'/>"
             f"<line x1='{cx}' y1='{o}' x2='{cx}' y2='{o + line}' stroke='#1C2430' stroke-width='3'/>")
    return f"<div style='text-align:center'>{svg(inner, box, box)}</div>"


def global_points(shape, n=16):
    pts = []
    if shape == "square":
        for s in range(4):
            for j in range(4):
                t = -1 + 2 * j / 4
                pts.append([(t, -1), (1, t), (-t, 1), (-1, -t)][s])
    elif shape == "triangle":
        v = [(0, -1), (1, 0.85), (-1, 0.85)]
        for s in range(3):
            a, b = v[s], v[(s + 1) % 3]
            for j in range(5):
                t = j / 5
                pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    elif shape == "circle":
        pts = [(math.cos(2 * math.pi * j / 14), math.sin(2 * math.pi * j / 14)) for j in range(14)]
    elif shape == "cross":
        for j in range(7):
            t = -1 + 2 * j / 6
            pts.append((0, t))
            if j != 3:
                pts.append((t, 0))
    return pts


def local_el(kind, x, y, r=6):
    if kind == "dot":
        return f"<circle cx='{x}' cy='{y}' r='{r}' fill='#1C2430'/>"
    if kind == "box":
        return f"<rect x='{x - r}' y='{y - r}' width='{2 * r}' height='{2 * r}' fill='#1C2430'/>"
    if kind == "tri":
        return f"<polygon points='{x},{y - r} {x + r},{y + r} {x - r},{y + r}' fill='#1C2430'/>"
    return (f"<line x1='{x - r}' y1='{y}' x2='{x + r}' y2='{y}' stroke='#1C2430' stroke-width='3'/>"
            f"<line x1='{x}' y1='{y - r}' x2='{x}' y2='{y + r}' stroke='#1C2430' stroke-width='3'/>")


def compound_svg(gshape, lshape, box=170):
    c, R = box / 2, box * 0.38
    inner = "".join(local_el(lshape, c + R * x, c + R * y) for x, y in global_points(gshape))
    return f"<div style='text-align:center'>{svg(inner, box, box)}</div>"


def hexagon_svg(pct, metastyle, cx_cy):
    W = 440
    c, R = W / 2, 150
    def pt(k, r):
        a = math.radians(S.ANGLES[k])
        return c + r * math.cos(a), c - r * math.sin(a)
    order = S.KEYS
    parts = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(k, R * frac) for k in order))
        parts.append(f"<polygon points='{poly}' fill='none' stroke='#C9D1CC' stroke-width='{1.6 if frac == 1 else 0.8}'/>")
    for k in order:
        x, y = pt(k, R)
        parts.append(f"<line x1='{c}' y1='{c}' x2='{x:.1f}' y2='{y:.1f}' stroke='#C9D1CC' stroke-width='0.8'/>")
    mx = max(pct.values())
    prof = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(k, R * pct[k] / mx) for k in order))
    parts.append(f"<polygon points='{prof}' fill='#1F8A70' fill-opacity='0.22' stroke='#1F8A70' stroke-width='2.2'/>")
    # hub: metastyle (flexibility) as the empty centre
    parts.append(f"<circle cx='{c}' cy='{c}' r='{6 + 26 * metastyle:.1f}' fill='none' stroke='#B8322A' "
                 f"stroke-dasharray='3 3' stroke-width='1.4'/>")
    gx, gy = c + R * cx_cy[0], c - R * cx_cy[1]
    parts.append(f"<circle cx='{gx:.1f}' cy='{gy:.1f}' r='6' fill='#B8322A'/>")
    for k in order:
        x, y = pt(k, R + 34)
        t = C.TYPE_TEXT[k]["name"]
        parts.append(f"<text x='{x:.1f}' y='{y - 4:.1f}' text-anchor='middle' font-size='14' font-weight='600' "
                     f"fill='{C.TYPE_COLOURS[k]}'>{t}</text>"
                     f"<text x='{x:.1f}' y='{y + 13:.1f}' text-anchor='middle' font-size='13' fill='#1C2430'>{pct[k]}%</text>")
    return f"<div style='text-align:center'>{svg(''.join(parts), W, W)}</div>"


# =============================================================== screens
def screen_welcome():
    st.title("The Nen Hexagon Cognition Test")
    st.write(
        "In Hunter × Hunter, every Nen user leans toward one of six categories arranged on a hexagon. "
        "This test treats those six as styles of thinking and places you on the hexagon as a set of "
        "percentages, not a single label. It takes about 18 minutes."
    )
    st.write(
        "You'll do short perception and association tasks (judging lines, shapes, word links), "
        "choose what you'd do in everyday situations, and finish with a set of sliders. "
        "There are no right answers except in two puzzle sections, and even there your approach matters more than your score."
    )
    st.write("Work at a natural pace and answer as you actually are, not as you'd like to be.")
    ss.name = st.text_input("First name or nickname (optional, shown on your results)", value=ss.name)
    st.button("Begin", type="primary", on_click=advance)
    if DEV:
        st.divider()
        st.button("Dev: simulate random answers and jump to results", on_click=simulate)
    st.caption("Not a validated psychological instrument. Built on the structure of published cognitive-style "
               "research and an original Nen–Daoist model of cognition.")


# --------------------------------------------------------------- 1. framed line
def fl_next():
    fl = ss.fl
    t = fl["trials"][fl["i"]]
    stim, line, resp = C.FRAME_TRIALS[t["k"]]
    correct = line if t["mode"] == "abs" else line / stim * resp
    val = ss.get(f"fl_resp_{fl['i']}", t["start"])
    fl["log"].append({"mode": t["mode"], "stim": stim, "line": line, "resp_frame": resp,
                      "response": val, "correct": round(correct, 1)})
    fl["i"] += 1
    if fl["i"] >= len(fl["trials"]):
        advance()
    elif fl["trials"][fl["i"]]["mode"] != t["mode"]:
        fl["stage"] = "intro"
    else:
        fl["stage"] = "show"


def screen_frame():
    fl = ss.fl
    t = fl["trials"][fl["i"]]
    stim, line, resp = C.FRAME_TRIALS[t["k"]]
    if fl["stage"] == "intro":
        st.header("Lines in frames")
        if t["mode"] == "abs":
            st.write("You'll see a square with a line hanging from its top edge. Memorise it, then you'll get a "
                     "square of a **different size**. Draw a line of the **same absolute length** as the original, "
                     "ignoring the new square's size.")
        else:
            st.write("You'll see a square with a line hanging from its top edge. Memorise it, then you'll get a "
                     "square of a **different size**. Draw a line that is the **same proportion** of the new "
                     "square as the original line was of its square.")
        st.write("There are 4 drawings in this round.")
        if st.button("Start", type="primary"):
            fl["stage"] = "show"
            st.rerun()
        return
    rule = "same LENGTH" if t["mode"] == "abs" else "same PROPORTION of the frame"
    if fl["stage"] == "show":
        st.subheader(f"Memorise this ({rule})")
        st.markdown(frame_svg(stim, line), unsafe_allow_html=True)
        if st.button("Got it", type="primary"):
            fl["stage"] = "respond"
            st.rerun()
        return
    st.subheader(f"Now draw it: {rule}")
    key = f"fl_resp_{fl['i']}"
    val = st.slider("Line length", 0, resp, value=min(t["start"], resp), key=key, label_visibility="collapsed")
    st.markdown(frame_svg(resp, val), unsafe_allow_html=True)
    st.button("Confirm", type="primary", on_click=fl_next)


# --------------------------------------------------------------- 2. global / local
def gl_choose(choice):
    g = ss.gl
    rt = time.time() - (g["t0"] or time.time())
    g["log"].append({"trial": g["i"], "choice": choice, "rt": round(rt, 2)})
    g["i"] += 1
    g["t0"] = None
    if g["i"] >= len(g["order"]):
        advance()


def screen_gl():
    g = ss.gl
    st.header("Shapes made of shapes")
    st.write("Which of the two bottom figures is **more similar** to the top one? Go with your first impression.")
    (tg, tl, og, ol), global_left = g["order"][g["i"]]
    if g["t0"] is None:
        g["t0"] = time.time()
    st.markdown(compound_svg(tg, tl), unsafe_allow_html=True)
    glob, loc = (tg, ol), (og, tl)     # global match keeps the big shape; local match keeps the small ones
    left, right = (glob, loc) if global_left else (loc, glob)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(compound_svg(*left, box=150), unsafe_allow_html=True)
        st.button("This one", key=f"gl_l_{g['i']}", use_container_width=True,
                  on_click=gl_choose, args=("global" if global_left else "local",))
    with c2:
        st.markdown(compound_svg(*right, box=150), unsafe_allow_html=True)
        st.button("This one", key=f"gl_r_{g['i']}", use_container_width=True,
                  on_click=gl_choose, args=("local" if global_left else "global",))
    st.caption(f"{g['i'] + 1} of {len(g['order'])}")


# --------------------------------------------------------------- 3. triads
def screen_triads():
    st.header("Which two go together?")
    st.write("For each set of three words, pick the pair that belongs together most naturally. Don't overthink it.")
    with st.form("triads"):
        picks = []
        for j, ((tgt, tax, them), tax_first) in enumerate(ss.triad_order):
            opts = [f"{tgt} & {tax}", f"{tgt} & {them}"]
            if not tax_first:
                opts.reverse()
            st.markdown(f"<div class='nen-q'>{tgt} · {tax} · {them}</div>", unsafe_allow_html=True)
            picks.append((st.radio("pair", opts, index=None, key=f"tri_{j}", horizontal=True,
                                   label_visibility="collapsed"), tgt, tax))
        if st.form_submit_button("Continue", type="primary"):
            if any(p is None for p, _, _ in picks):
                st.warning("Please choose a pair for every set.")
            else:
                ss.triads = [{"target": tgt, "choice": "taxonomic" if p == f"{tgt} & {tax}" else "thematic"}
                             for p, tgt, tax in picks]
                advance()
                st.rerun()


# --------------------------------------------------------------- 4. remote links
def norm(s):
    s = s.strip().lower()
    return s[:-1] if s.endswith("s") and len(s) > 3 else s


def screen_remote():
    r = ss.remote
    st.header("Remote links")
    st.write(f"Find **one word** that links to all three, as a compound or common phrase "
             f"(e.g. *sore · shoulder · sweat* → **cold**). Try to answer within {C.REMOTE_SECONDS} seconds; "
             "your time is recorded. If nothing comes, leave it blank.")
    k = r["order"][r["i"]]
    cues, answers = C.REMOTE_ITEMS[k]
    if r["t0"] is None:
        r["t0"] = time.time()
    st.markdown(f"<div class='nen-big'>{'  ·  '.join(cues)}</div>", unsafe_allow_html=True)
    with st.form(f"rat_{r['i']}", clear_on_submit=True):
        ans = st.text_input("Your word")
        how = st.radio("How did your answer come?",
                       ["It popped into my head suddenly", "I worked through candidates step by step", "I didn't find one"],
                       index=None)
        if st.form_submit_button("Next", type="primary"):
            rt = time.time() - r["t0"]
            if how is None:
                st.warning("Please say how the answer came (or that you didn't find one).")
            else:
                ok = bool(ans) and norm(ans) in [norm(a) for a in answers] and rt <= C.REMOTE_SECONDS + 15
                r["log"].append({"cues": "/".join(cues), "answer": ans, "correct": ok, "rt": round(rt, 1),
                                 "how": {"It popped into my head suddenly": "insight",
                                         "I worked through candidates step by step": "analysis"}.get(how, "none")})
                r["i"] += 1
                r["t0"] = None
                if r["i"] >= len(r["order"]):
                    advance()
                st.rerun()
    st.caption(f"{r['i'] + 1} of {len(r['order'])}")


# --------------------------------------------------------------- 5. Nen operations (best-worst)
def screen_ops(part):
    lo, hi = (0, OPS_SPLIT) if part == 1 else (OPS_SPLIT, len(C.OPS_SCENARIOS))
    i = max(ss.ops_i, lo)
    if i >= hi:
        advance()
        st.rerun()
    sc = ss.ops_order[i]
    prompt, options = C.OPS_SCENARIOS[sc]
    st.header("What would you do?")
    st.write("Pick the response **most** like you and the one **least** like you.")
    st.markdown(f"<div class='nen-big'>{prompt}</div>", unsafe_allow_html=True)
    keys = ss.ops_opts[sc]
    labels = [options[k] for k in keys]
    with st.form(f"ops_{i}"):
        c1, c2 = st.columns(2)
        with c1:
            best = st.radio("Most like me", labels, index=None, key=f"best_{i}")
        with c2:
            worst = st.radio("Least like me", labels, index=None, key=f"worst_{i}")
        if st.form_submit_button("Next", type="primary"):
            if best is None or worst is None:
                st.warning("Please choose both.")
            elif best == worst:
                st.warning("Most and least can't be the same response.")
            else:
                ss.ops.append({"scenario": prompt, "best": keys[labels.index(best)],
                               "worst": keys[labels.index(worst)]})
                ss.ops_i = i + 1
                if ss.ops_i >= hi:
                    advance()
                st.rerun()
    st.caption(f"Scenario {i + 1} of {len(C.OPS_SCENARIOS)}")


# --------------------------------------------------------------- 6. category width
def screen_catw():
    st.header("Does it count?")
    st.write("Quick gut answers. There's no correct answer; we're interested in how wide you draw categories.")
    vals = {"No": 0.0, "Partly": 0.5, "Yes": 1.0}
    with st.form("catw"):
        picks = [st.radio(q, list(vals), index=None, horizontal=True, key=f"cw_{j}")
                 for j, q in enumerate(C.CATEGORY_ITEMS)]
        if st.form_submit_button("Continue", type="primary"):
            if any(p is None for p in picks):
                st.warning("Please answer every item.")
            else:
                ss.catw = [vals[p] for p in picks]
                advance()
                st.rerun()


# --------------------------------------------------------------- 7. ambiguity
def screen_amb():
    st.header("How many meanings?")
    st.write("For each phrase, how many **distinct** meanings or readings do you notice right away?")
    with st.form("amb"):
        picks = [st.radio(f"“{s}”", ["1", "2", "3", "4+"], index=None, horizontal=True, key=f"amb_{j}")
                 for j, s in enumerate(C.AMBIGUOUS)]
        if st.form_submit_button("Continue", type="primary"):
            if any(p is None for p in picks):
                st.warning("Please answer every item.")
            else:
                ss.amb = [4 if p == "4+" else int(p) for p in picks]
                advance()
                st.rerun()


# --------------------------------------------------------------- 8. sliders
SL_PAGES = [C.SLIDER_ITEMS[:8], C.SLIDER_ITEMS[8:16], C.SLIDER_ITEMS[16:]]


def screen_sliders():
    p = ss.sl_page
    st.header("Leanings")
    st.write("Move each slider toward the statement that fits you better. The middle means both fit equally. "
             "The further you go, the stronger the preference.")
    with st.form(f"sl_{p}"):
        for it in SL_PAGES[p]:
            st.markdown(f"<div class='nen-q'>{it['q']}</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.markdown(f"<div class='nen-pole'>◀ {it['left']}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='nen-pole' style='text-align:right'>{it['right']} ▶</div>", unsafe_allow_html=True)
            st.slider(it["id"], -10, 10, 0, key=f"s_{it['id']}", label_visibility="collapsed")
        if p == len(SL_PAGES) - 1:
            st.markdown("<div class='nen-q'>Finally, how flexible are you? (0 = never, 10 = always)</div>",
                        unsafe_allow_html=True)
            for m in C.META_ITEMS:
                st.slider(m["q"], 0, 10, 5, key=f"m_{m['id']}")
        if st.form_submit_button("Finish" if p == len(SL_PAGES) - 1 else "Next", type="primary"):
            for it in SL_PAGES[p]:
                ss.sl[it["id"]] = ss[f"s_{it['id']}"]
            if p == len(SL_PAGES) - 1:
                for m in C.META_ITEMS:
                    ss.meta[m["id"]] = ss[f"m_{m['id']}"]
                advance()
            else:
                ss.sl_page += 1
            st.rerun()


# =============================================================== dev simulation
def simulate():
    rng = random.Random()
    for t in ss.fl["trials"]:
        stim, line, resp = C.FRAME_TRIALS[t["k"]]
        cor = line if t["mode"] == "abs" else line / stim * resp
        ss.fl["log"].append({"mode": t["mode"], "stim": stim, "line": line, "resp_frame": resp,
                             "response": round(cor * rng.uniform(0.7, 1.3)), "correct": round(cor, 1)})
    ss.gl["log"] = [{"trial": i, "choice": rng.choice(["global", "local"]), "rt": round(rng.uniform(1, 5), 2)}
                    for i in range(len(C.GL_TRIALS))]
    ss.triads = [{"target": t[0][0], "choice": rng.choice(["taxonomic", "thematic"])} for t in ss.triad_order]
    ss.remote["log"] = [{"cues": "/".join(C.REMOTE_ITEMS[k][0]), "answer": "", "correct": rng.random() < .4,
                         "rt": 20, "how": rng.choice(["insight", "analysis"])} for k in ss.remote["order"]]
    ss.ops = []
    for sc in ss.ops_order:
        b, w = rng.sample(S.KEYS, 2)
        ss.ops.append({"scenario": C.OPS_SCENARIOS[sc][0], "best": b, "worst": w})
    ss.catw = [rng.choice([0, .5, 1]) for _ in C.CATEGORY_ITEMS]
    ss.amb = [rng.randint(1, 4) for _ in C.AMBIGUOUS]
    ss.sl = {it["id"]: rng.randint(-10, 10) for it in C.SLIDER_ITEMS}
    ss.sl["check"] = 10
    ss.meta = {m["id"]: rng.randint(0, 10) for m in C.META_ITEMS}
    ss.step = len(SECTIONS) - 1


# =============================================================== results
def collect():
    return {"sliders": ss.sl, "meta": ss.meta, "frame": ss.fl["log"], "gl": ss.gl["log"],
            "triads": ss.triads, "catw": ss.catw, "remote": ss.remote["log"], "amb": ss.amb, "ops": ss.ops}


def pole_text(v, neg, pos):
    a = abs(v)
    if a < 1.5:
        return "balanced"
    strength = "slightly" if a < 4 else ("clearly" if a < 7 else "strongly")
    return f"{strength} {pos if v > 0 else neg}"


def type_card(k, pct, label):
    t = C.TYPE_TEXT[k]
    st.markdown(
        f"<div class='nen-card' style='--c:{C.TYPE_COLOURS[k]}'>"
        f"<b>{label}: {t['name']} ({pct}%)</b>, {t['style']} · {t['key']}<br>"
        f"<i>{t['formula']}</i><br>{t['thinks']}<br>"
        f"<span class='nen-pole'>Failure mode: {t['failure']} Growth edge: {t['growth']}</span></div>",
        unsafe_allow_html=True)


def save_locally(row):
    try:
        os.makedirs("responses", exist_ok=True)
        path = os.path.join("responses", "responses.csv")
        pd.DataFrame([row]).to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    except Exception:
        pass


def screen_results():
    data = collect()
    prof = S.build_profile(data, C.SLIDER_ITEMS)
    nen = S.nen_percentages(prof)
    pct = S.round_percentages(nen["pct"])
    ranked = sorted(S.KEYS, key=lambda k: nen["pct"][k], reverse=True)
    primary, second = ranked[0], ranked[1]
    shadow = S.OPPOSITE[primary]

    st.title(f"{ss.name}'s Nen hexagon" if ss.name else "Your Nen hexagon")
    st.markdown(hexagon_svg(pct, prof["metastyle"], (nen["x"], nen["y"])), unsafe_allow_html=True)
    st.caption("Green shape: your six percentages (scaled to your highest). Red dot: your centre of gravity on "
               "the hexagon; the nearer the rim, the more one-sided your profile. Dashed ring: the empty hub, "
               "sized by your flexibility (metastyle).")

    purity = nen["purity"]
    shape = ("a sharply defined profile" if purity > 0.55 else
             "a clear lean with real secondary styles" if purity > 0.3 else
             "a broad, spread-out profile close to the hub")
    st.write(f"You show {shape}. Your strongest style is **{C.TYPE_TEXT[primary]['name']}**, followed by "
             f"**{C.TYPE_TEXT[second]['name']}**.")
    adj = S.manga_affinity(primary)[second] == 80
    st.write("Your top two are neighbours on the hexagon, so they reinforce each other." if adj else
             "Your top two are not neighbours on the hexagon. That's an unusual, stretched profile: "
             "two styles that don't share an axis are both strong in you.")
    type_card(primary, pct[primary], "Primary")
    type_card(second, pct[second], "Secondary")
    type_card(shadow, pct[shadow], "Shadow (opposite)")

    st.subheader("All six")
    df = pd.DataFrame([{"Type": C.TYPE_TEXT[k]["name"], "Percent": pct[k], "c": C.TYPE_COLOURS[k],
                        "Manga affinity": S.manga_affinity(primary)[k]} for k in S.KEYS])
    bars = alt.Chart(df).mark_bar(size=20).encode(
        x=alt.X("Percent:Q", scale=alt.Scale(domain=[0, 100])), y=alt.Y("Type:N", sort=None, title=None),
        color=alt.Color("c:N", scale=None), tooltip=["Type", "Percent"]).properties(height=220)
    st.altair_chart(bars, use_container_width=True)
    st.caption("Manga affinity follows Hunter × Hunter's rule from your primary type: own 100%, neighbours 80%, "
               "two steps away 60%, opposite 40%. In our model this is how easily you can borrow each style.")
    st.dataframe(df[["Type", "Percent", "Manga affinity"]], hide_index=True, use_container_width=True)

    st.subheader("The three Nen axes")
    d = prof["dims"]
    axes = [("Yang ↔ Yin", d["YIN"], "robust, concrete, linear", "sensitive, abstract, lateral"),
            ("Static ↔ Dynamic", d["DYN"], "things at rest (content)", "things in motion (context)"),
            ("Burst ↔ Accumulate", d["SLOW"], "expend, release (Yang half)", "build, regulate (Yin half)")]
    for name, v, neg, pos in axes:
        st.markdown(f"**{name}**: {v * 10:+.1f}, {pole_text(v * 10, neg, pos)}")

    st.subheader("Your cognitive-style matrix")
    st.write("Following Kozhevnikov et al. (2014) and Ho & Kozhevnikov (2023): four style families at three "
             "levels of processing, on a −10 to +10 scale. Negative values lean toward the poles typical of "
             "artists in that research, positive toward those typical of scientists.")
    rows = []
    for f in S.FAMILIES:
        fname, neg, pos = S.FAMILY_NAMES[f]
        for l in S.LEVELS:
            v = round(prof["cells"][(f, l)] * 10, 1)
            rows.append({"Family": f"{fname} ({neg} − / {pos} +)", "Level": S.LEVEL_NAMES[l], "Score": v})
    mdf = pd.DataFrame(rows)
    base = alt.Chart(mdf).encode(x=alt.X("Level:N", sort=[S.LEVEL_NAMES[l] for l in S.LEVELS], title=None),
                                 y=alt.Y("Family:N", sort=None, title=None))
    heat = base.mark_rect().encode(color=alt.Color("Score:Q", scale=alt.Scale(scheme="purpleorange", domain=[-10, 10]),
                                                   legend=None))
    txt = base.mark_text(fontSize=14).encode(text="Score:Q")
    st.altair_chart((heat + txt).properties(height=230), use_container_width=True)
    for f in S.FAMILIES:
        fname, neg, pos = S.FAMILY_NAMES[f]
        st.markdown(f"- **{fname}**: {pole_text(prof['families'][f] * 10, neg, pos)}")
    st.markdown(f"**Metastyle (flexibility)**: {prof['metastyle'] * 10:.1f} / 10")

    st.subheader("Task results")
    tk = prof["tasks"]
    def f(v, pctfmt=False, nd=2):
        return "–" if v is None else (f"{v:.0%}" if pctfmt else f"{v:.{nd}f}")
    tdf = pd.DataFrame([
        ("Lines in frames: error when copying length", f(tk["frame_abs_error"], True), "lower = more context-independent"),
        ("Lines in frames: error when copying proportion", f(tk["frame_rel_error"], True), "lower = better at using context"),
        ("Shapes: chose the global match", f(tk["global_share"], True), "higher = more integrative perception"),
        ("Shapes: median decision time (s)", f(tk["global_median_rt"], nd=1), "faster = more impulsive scanning"),
        ("Triads: category-based pairs", f(tk["taxonomic_share"], True), "higher = rule/category grouping"),
        ("Does it count?: category width", f(tk["category_width"], True), "higher = broader categories"),
        ("Remote links: solved", f(tk["remote_accuracy"], True), "lateral association capacity"),
        ("Remote links: solved by sudden insight", f(tk["insight_share"], True), "higher = more intuitive"),
        ("Meanings noticed per phrase", f(tk["meanings_noticed"], nd=1), "higher = less automatic filtering"),
    ], columns=["Task", "You", "Reading"])
    st.dataframe(tdf, hide_index=True, use_container_width=True)

    elapsed = time.time() - ss.t_start
    warn = []
    if ss.sl.get("check", 0) < 8:
        warn.append("the attention-check slider wasn't moved to +10")
    if elapsed < 8 * 60 and not DEV:
        warn.append(f"the test was finished very quickly ({elapsed / 60:.1f} min)")
    if warn:
        st.warning("Treat these results with extra caution: " + " and ".join(warn) + ".")

    with st.expander("How the percentages are calculated"):
        st.write(
            "Two sources are combined. (1) The best/worst choices in the ten scenarios give each type a direct "
            "score from −1 to +1; this is the dominant input. (2) All other tasks and sliders are scored on seven "
            "dimensions: the four Kozhevnikov style families plus the three Nen axes (Yang↔Yin, static↔dynamic, "
            "burst↔accumulate). Your position is compared with a prototype of each Nen type in that space. "
            "Both are added and passed through a softmax. Higher flexibility (metastyle) spreads the percentages "
            "more evenly, since a flexible thinker draws on more styles. Behavioural tasks feed specific cells: "
            "lines in frames → Context at perception and flexibility; shapes → Integration and Rule at perception; "
            "triads → Context and Rule at concept formation; category width → Integration and Yin; remote links "
            "→ Yin (laterality) and Rule at higher-order cognition; meanings → Yin.")
        st.json({"weights": {"operations": S.OPS_WEIGHT, "profile": S.PROFILE_WEIGHT, "temperature": round(nen["tau"], 2)},
                 "dimensions": {k: round(v, 2) for k, v in prof["dims"].items()},
                 "operation_scores": {k: round(v, 2) for k, v in prof["ops"].items()},
                 "prototype_similarity": {k: round(v, 2) for k, v in nen["similarity"].items()}})

    row = {"participant_id": ss.pid, "name": ss.name, "started": ss.started,
           "minutes": round(elapsed / 60, 1),
           **{f"pct_{C.TYPE_TEXT[k]['name']}": pct[k] for k in S.KEYS},
           **{f"dim_{k}": round(v * 10, 2) for k, v in prof["dims"].items()},
           **{f"cell_{fam}_{lev}": round(v * 10, 2) for (fam, lev), v in prof["cells"].items()},
           "metastyle": round(prof["metastyle"] * 10, 2),
           **{f"ops_{k}": round(v, 2) for k, v in prof["ops"].items()},
           **{f"task_{k}": (round(v, 3) if v is not None else None) for k, v in tk.items()},
           **{f"slider_{k}": v for k, v in ss.sl.items()}, **{f"meta_{k}": v for k, v in ss.meta.items()}}
    if not ss.saved:
        save_locally(row)
        ss.saved = True
    st.subheader("Keep your results")
    buf = io.StringIO()
    pd.DataFrame([row]).to_csv(buf, index=False)
    c1, c2 = st.columns(2)
    c1.download_button("Summary (CSV)", buf.getvalue(), file_name=f"nen_hexagon_{ss.pid}.csv",
                       mime="text/csv", use_container_width=True)
    c2.download_button("Full details (JSON)", json.dumps({"summary": row, "raw": data}, indent=2, default=str),
                       file_name=f"nen_hexagon_{ss.pid}.json", mime="application/json", use_container_width=True)
    st.divider()
    st.caption("A conversation starter, not an assessment. Style structure after Kozhevnikov, Evans & Kosslyn "
               "(2014) and Ho & Kozhevnikov (2023); Nen layer from an original hexagon model.")
    st.button("Start over", on_click=restart)


# =============================================================== router
def main():
    init_state()
    header()
    p = phase()
    {"welcome": screen_welcome, "frame": screen_frame, "ops1": lambda: screen_ops(1), "gl": screen_gl,
     "triads": screen_triads, "remote": screen_remote, "ops2": lambda: screen_ops(2), "catw": screen_catw,
     "amb": screen_amb, "sliders": screen_sliders, "results": screen_results}[p]()


main()
