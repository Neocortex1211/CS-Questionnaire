# Nen Hexagon Cognition Test

A ~18-minute test that places a person on the six-type Nen hexagon (Enhancer, Transmuter, Conjurer,
Specialist, Manipulator, Emitter) as continuous percentages. Built for fun and self-reflection among
friends; it is not a validated instrument.

## Files

- `app.py`: the Streamlit app (screens, flow, results page).
- `content.py`: every item, scenario and stimulus, plus the result texts. Edit wording here.
- `scoring.py`: the scoring model, pure Python with no Streamlit, so it can be tested or reused.

## The battery

| # | Section | Paradigm | Feeds |
|---|---|---|---|
| 1 | Lines in frames (8 trials) | Framed-line test, absolute vs relative (Kitayama et al. 2003) | Context at perception; flexibility (accuracy in both modes = "mobile", Witkin) |
| 2 | What would you do? part 1 (5) | Best–worst choice among six Nen operations | Direct Nen scores (dominant input) |
| 3 | Shapes made of shapes (8) | Global/local similarity (Kimchi 1992), with response time | Integration and Rule at perception |
| 4 | Which two go together? (10) | Taxonomic vs thematic triads (Ji, Zhang & Nisbett 2004) | Context and Rule at concept formation |
| 5 | Remote links (7) | Compound remote associates + "insight or step by step?" report | Yin/laterality; Rule at higher-order cognition |
| 6 | What would you do? part 2 (5) | Best–worst, continued | Direct Nen scores |
| 7 | Does it count? (12) | Category width (Pettigrew 1958; Gardner et al. 1959) | Integration at concept formation; Yin |
| 8 | How many meanings? (6) | Ambiguity / unit filtering (Neurotypology lexicality) | Yin |
| 9 | Leanings (22 + check + 4) | FICS-style bipolar −10..+10 scenarios (Ho & Kozhevnikov 2023) and metastyle items | All 12 matrix cells; the three Nen axes; flexibility |

## Scoring in brief

1. Every input is scaled to −1..+1 and placed in a 4 × 3 matrix (Context, Rule, Integration, Locus ×
   Perception, Concept formation, Higher-order cognition), with metastyle as a separate superordinate
   score, as Ho & Kozhevnikov (2023) found it to behave. Sign convention follows that paper.
2. Three Nen axes are scored alongside: Yang↔Yin (robust/concrete/linear vs sensitive/abstract/lateral),
   static↔dynamic, burst↔accumulate.
3. Each Nen type has a prototype in this 7-D space (`PROTOTYPES` in `scoring.py`). Similarity to each
   prototype is combined with the direct best–worst scores (`OPS_WEIGHT`, `PROFILE_WEIGHT`) and turned
   into percentages by a softmax whose temperature rises with metastyle.
4. The results page shows the hexagon, the six percentages, the three axes, the style matrix, raw task
   results, quality flags (attention check, very fast completion) and CSV/JSON downloads.

Simulated "pure" responders score about 85–90% on their own type; with the operation task held
neutral, the profile layer alone spills over to hexagon neighbours, as the model predicts.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Add `?dev=1` to the URL to get a "simulate random answers" button on the welcome page.
Finished sessions are appended to `responses/responses.csv` when run locally.

## Deploy free

Push the folder (including `.streamlit/`) to a public GitHub repo, then create an app at
https://share.streamlit.io with `app.py` as the main file.

## What would make it better

- Norms: percentages are absolute, not relative to other people. After ~50 friends, z-scoring each
  dimension against the group would make the matrix far more meaningful.
- Calibration: the prototypes and weights are theory-driven guesses. With data, fit them (e.g. a
  multinomial model predicting the best–worst type from the other measures).
- Reliability: two behavioural tasks per cell would follow the papers more closely; Locus currently
  rests on sliders only.
