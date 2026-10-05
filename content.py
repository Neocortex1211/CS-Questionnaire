"""Item content for the Nen Hexagon Cognition Test."""

# ------------------------------------------------------------------ 1. Framed line (Kitayama et al., 2003)
# (stimulus frame px, line px, response frame px). Lines always fit both frames.
FRAME_TRIALS = [
    (150, 60, 100), (100, 55, 160), (130, 85, 90), (90, 30, 150),
]

# ------------------------------------------------------------------ 2. Global / local similarity (Kimchi, 1992)
GLOBAL_SHAPES = ["square", "triangle", "circle", "cross"]
LOCAL_SHAPES = ["dot", "box", "tri", "plus"]
GL_TRIALS = [  # (target global, target local, other global, other local)
    ("square", "tri", "circle", "plus"), ("triangle", "dot", "cross", "box"),
    ("circle", "plus", "triangle", "tri"), ("cross", "box", "square", "dot"),
    ("square", "plus", "triangle", "dot"), ("circle", "box", "cross", "tri"),
    ("triangle", "tri", "square", "box"), ("cross", "dot", "circle", "plus"),
]

# ------------------------------------------------------------------ 3. Triads (Ji, Zhang & Nisbett, 2004)
TRIADS = [  # target, taxonomic partner, thematic partner
    ("Monkey", "Panda", "Banana"), ("Teacher", "Doctor", "Homework"), ("Train", "Bus", "Tracks"),
    ("Cow", "Chicken", "Grass"), ("Piano", "Guitar", "Concert hall"), ("Rain", "Snow", "Umbrella"),
    ("Bee", "Butterfly", "Honey"), ("Nurse", "Police officer", "Hospital"),
    ("Notebook", "Magazine", "Pencil"), ("Hammer", "Screwdriver", "Nail"),
]

# ------------------------------------------------------------------ 4. Category width (Pettigrew; Gardner et al.)
CATEGORY_ITEMS = [
    "Is chess a sport?", "Is a hot dog a sandwich?", "Is a podcast a kind of radio?",
    "Is a virus alive?", "Is a cave a home?", "Is graffiti art?", "Is a hammock a bed?",
    "Is a smartphone a computer?", "Is soup a drink?", "Is a meme a kind of literature?",
    "Is a rug furniture?", "Is a robot vacuum a pet?",
]

# ------------------------------------------------------------------ 5. Remote links (compound remote associates)
REMOTE_ITEMS = [  # cues, accepted answers
    (("cottage", "swiss", "cake"), ["cheese"]),
    (("cream", "skate", "water"), ["ice"]),
    (("falling", "actor", "dust"), ["star"]),
    (("dew", "comb", "bee"), ["honey"]),
    (("night", "wrist", "stop"), ["watch"]),
    (("age", "mile", "sand"), ["stone"]),
    (("pine", "crab", "sauce"), ["apple"]),
]
REMOTE_SECONDS = 30

# ------------------------------------------------------------------ 6. Meanings (unit filtering, Neurotypology)
AMBIGUOUS = [
    "Visiting relatives can be boring.",
    "I saw the man with the telescope.",
    "The chicken is ready to eat.",
    "A door standing alone in an empty field.",
    "The river remembers.",
    "She kept the key.",
]

# ------------------------------------------------------------------ 7. Nen operations (best-worst scaling)
OPS_SCENARIOS = [
    ("You inherit a plain old wooden chair.", {
        "enh": "Sand and oil it until it's the best possible version of the chair it already is.",
        "tra": "Turn it into something else: a plant stand, a shelf, a sculpture.",
        "con": "Use it as a starting idea to design and build a chair entirely my own.",
        "spe": "Start wondering about its maker, the tree, and what keeping old things means.",
        "man": "Work out what role it should play so the whole room works better.",
        "emi": "Pass it on to someone who'll use it, or move it to where it gets used.",
    }),
    ("A group project has stalled.", {
        "enh": "Double down on my own part and do it so well it sets the pace.",
        "tra": "Reframe the problem so it looks like one we already know how to solve.",
        "con": "Write a clear plan with roles, rules and deadlines.",
        "spe": "Map every hidden factor behind the stall; it's rarely one thing.",
        "man": "Quietly rearrange who talks to whom and what's rewarded, so momentum returns by itself.",
        "emi": "Get everyone moving today: call people, hand out tasks, push things out the door.",
    }),
    ("You're learning a new skill, say an instrument.", {
        "enh": "Practise the basics again and again until they're rock solid.",
        "tra": "Bend it toward what I already know, and play my favourite songs in my own way.",
        "con": "Build my own method and set of exercises from scratch.",
        "spe": "Dive into the theory, history and links to other arts.",
        "man": "Set up a routine and environment that make practice happen automatically.",
        "emi": "Play for people and jam early; learn by doing it out loud.",
    }),
    ("A friend is upset.", {
        "enh": "Be simply, steadily there: honest and present.",
        "tra": "Help them see the situation in a different light.",
        "con": "Help them make a concrete plan, or create something that marks a fresh start.",
        "spe": "Explore the layers with them and what this connects to.",
        "man": "Gently shift their circumstances: the right people, a changed routine.",
        "emi": "Take them out somewhere: new scenery, movement, something to do.",
    }),
    ("A strong new idea hits you.", {
        "enh": "Commit to it fully and push it as far as it goes.",
        "tra": "Twist it: what if it applied to something completely different?",
        "con": "Write it down precisely, with its rules and conditions.",
        "spe": "Let it branch into ten more ideas.",
        "man": "Think about whom it would influence and where to place it so it spreads.",
        "emi": "Tell people right away and throw it into the world.",
    }),
    ("You're in an argument and you disagree.", {
        "enh": "State my position plainly and hold it.",
        "tra": "Redefine the terms until the disagreement looks different.",
        "con": "Build a structured case, step by step.",
        "spe": "Show how both sides are partly right and the issue is more complex.",
        "man": "Steer the conversation so they reach my view on their own.",
        "emi": "Move on: change the subject, act instead of talking.",
    }),
    ("Your room or desk is a mess.", {
        "enh": "Clean it thoroughly, the way it's supposed to be.",
        "tra": "Repurpose things: this jar becomes a pen holder.",
        "con": "Design a complete storage system.",
        "spe": "Notice what the mess says about the last few weeks.",
        "man": "Change my habits so mess can't build up again.",
        "emi": "Move things out: boxes to storage, give away, relocate.",
    }),
    ("You're playing a strategy game.", {
        "enh": "Master one strong strategy and execute it with full force.",
        "tra": "Use pieces in unconventional ways nobody expects.",
        "con": "Build an engine or combo of my own design.",
        "spe": "Get absorbed in the game's hidden systems and meta.",
        "man": "Read opponents and lure them into bad positions.",
        "emi": "Attack early and fast, and keep up pressure from a distance.",
    }),
    ("Your neighbourhood has a litter problem.", {
        "enh": "Just start picking it up myself, every day.",
        "tra": "Turn the litter into something: an art piece, a resource.",
        "con": "Found a new initiative with its own rules and structure.",
        "spe": "Research why it happens: economics, psychology, design.",
        "man": "Change incentives: where the bins are, social norms, small rewards.",
        "emi": "Organise a haul-away day and get it out of there.",
    }),
    ("You're writing a story.", {
        "enh": "One hero, one goal, told with full intensity.",
        "tra": "Take a familiar tale and transform it into something new.",
        "con": "Build the world and its system of magic first.",
        "spe": "Weave many interlocking threads and symbols.",
        "man": "Focus on schemes: how characters steer events and each other.",
        "emi": "Fast action and journeys: things in motion.",
    }),
]

# ------------------------------------------------------------------ 8. Style sliders
# Slider from -10 (left statement) to +10 (right statement); right = positive pole of `dim`.
SLIDER_ITEMS = [
    # Context: + independent
    {"id": "ctx_p", "dim": "CTX", "level": "P", "q": "Judging whether a picture hangs straight:",
     "left": "I go by how it lines up with the furniture and ceiling.", "right": "I go by my own sense of vertical, whatever the room does."},
    {"id": "ctx_cf", "dim": "CTX", "level": "CF", "q": "Learning a new word:",
     "left": "I grasp it through the sentences and situations it shows up in.", "right": "I want its exact definition, apart from any example."},
    {"id": "ctx_hoc", "dim": "CTX", "level": "HoC", "q": "You're asked to give a talk at a neighbourhood event. Choosing a topic:",
     "left": "I pick what this audience will find interesting.", "right": "I pick what I'm an expert in."},
    # Rule: + rule-based
    {"id": "rule_p", "dim": "RULE", "level": "P", "q": "Looking for a friend in a crowded photo:",
     "left": "I let my eyes wander until they jump out.", "right": "I scan row by row, systematically."},
    {"id": "rule_cf", "dim": "RULE", "level": "CF", "q": "Sorting a pile of mixed objects:",
     "left": "I group what feels like it belongs together.", "right": "I decide on a sorting rule first, then apply it."},
    {"id": "rule_hoc", "dim": "RULE", "level": "HoC", "q": "Choosing between two job offers:",
     "left": "I sleep on it and go with my gut.", "right": "I list criteria, weight them and score each option."},
    # Integration: + compartmentalised
    {"id": "comp_p", "dim": "COMP", "level": "P", "q": "Looking at a painting:",
     "left": "I take it in as one overall impression.", "right": "I go over it part by part."},
    {"id": "comp_cf", "dim": "COMP", "level": "CF", "q": "Taking notes:",
     "left": "I draw links and arrows between everything.", "right": "I keep separate, ordered points."},
    {"id": "comp_hoc", "dim": "COMP", "level": "HoC", "q": "Preparing for an exam:",
     "left": "I try to see the big picture and how topics connect.", "right": "I master each topic separately, one after another."},
    # Locus: + internal
    {"id": "loc_p", "dim": "LOC", "level": "P", "q": "Something in a scene looks a bit 'off':",
     "left": "I check whether others notice it too.", "right": "I trust my own eyes."},
    {"id": "loc_cf", "dim": "LOC", "level": "CF", "q": "Forming a view on an unfamiliar topic:",
     "left": "I start from what people I trust think.", "right": "I work it out from my own understanding."},
    {"id": "loc_hoc", "dim": "LOC", "level": "HoC", "q": "You have a first draft of something important. Next:",
     "left": "I ask someone what I should add or change.", "right": "I keep editing it myself to make it better."},
    # Yin: + sensitive / abstract / lateral / reflexive
    {"id": "yin_1", "dim": "YIN", "q": "Small changes in mood, noise or light:",
     "left": "barely register with me.", "right": "I pick them up, sometimes too much."},
    {"id": "yin_2", "dim": "YIN", "q": "The ideas I enjoy most:",
     "left": "ones I can touch, test or use right away.", "right": "ideas about ideas: patterns behind patterns."},
    {"id": "yin_3", "dim": "YIN", "q": "When I think something through:",
     "left": "I follow one line to its end.", "right": "it branches; one idea opens five more."},
    {"id": "check", "dim": "CHECK", "q": "Attention check:",
     "left": "Please move this slider", "right": "all the way to this side (+10)."},
    {"id": "yin_4", "dim": "YIN", "q": "After a mistake:",
     "left": "I shrug and keep going.", "right": "I replay it and ask what it says about me."},
    # Static vs dynamic: + dynamic
    {"id": "dyn_1", "dim": "DYN", "q": "Your motorbike starts making a strange rattling noise. You:",
     "left": "stop and inspect it at rest for loose or broken parts.", "right": "ride it and listen to how it behaves in motion."},
    {"id": "dyn_2", "dim": "DYN", "q": "To understand a person, I mostly want to know:",
     "left": "what they're like: values, character, what they stand for.", "right": "how they act and change across situations."},
    {"id": "dyn_3", "dim": "DYN", "q": "A plan is:",
     "left": "a structure to get right before starting.", "right": "a direction I keep adjusting as things move."},
    # Slow vs burst: + accumulate / regulate
    {"id": "slow_1", "dim": "SLOW", "q": "My natural work rhythm:",
     "left": "intense bursts, then rest.", "right": "steady, regulated effort every day."},
    {"id": "slow_2", "dim": "SLOW", "q": "When something old no longer works:",
     "left": "clear it away fast and start fresh.", "right": "rebuild it gradually, keeping what still holds."},
    {"id": "slow_3", "dim": "SLOW", "q": "In a group, I tend to:",
     "left": "raise the energy: spark, push, accelerate.", "right": "steady the energy: pace, calm, sustain."},
]

META_ITEMS = [
    {"id": "meta_ctx", "q": "I can easily switch between focusing on a thing by itself and reading it through its context, when the situation calls for it."},
    {"id": "meta_rule", "q": "I can switch between gut feeling and step-by-step analysis depending on the problem."},
    {"id": "meta_comp", "q": "I can move between the big picture and the separate parts as needed."},
    {"id": "meta_loc", "q": "I can switch between trusting my own judgement and drawing on others' input as needed."},
]

# ------------------------------------------------------------------ Results text (from our model)
TYPE_TEXT = {
    "enh": {"name": "Enhancer", "style": "Axial-Intensive", "key": "樸 the uncarved block",
            "formula": "Become more fully what you already are: one line, followed all the way.",
            "thinks": "Concrete and robust. Strong priors that shrug off noise; reduces error by acting until the world matches the prediction.",
            "failure": "Linear entrapment: when the line fails, pushing harder on the same line.",
            "growth": "Let one trait change (Transmuter) and let something leave your hands (Emitter)."},
    "tra": {"name": "Transmuter", "style": "Attributive-Metamorphic", "key": "化 transformation",
            "formula": "Keep the thing; rewrite its nature. Metaphor as an operation.",
            "thinks": "Changes the description rather than the world: reappraisal, conceptual blending, unusual affordances.",
            "failure": "Groundlessness: everything becomes swappable, promises included.",
            "growth": "Commit to one property (Enhancer) and build something with fixed rules (Conjurer)."},
    "con": {"name": "Conjurer", "style": "Nominative-Constructive", "key": "名 naming into being",
            "formula": "Name it into being and bind it with rules.",
            "thinks": "Structure learning: designs widely, then locks the design into precise conditions. Restriction buys power.",
            "failure": "The dogmatic model: rules that close the system off from the world.",
            "growth": "Let constructions bend (Transmuter) and grow branches you didn't plan (Specialist)."},
    "spe": {"name": "Specialist", "style": "Convolutive-Emergent", "key": "玄 / 混沌 mystery, chaos",
            "formula": "Unfold everything a thing could also be.",
            "thinks": "Metacognitive and porous: many loose hypotheses at once, high sensitivity, needs one fixed anchor.",
            "failure": "Lateral overload: spiralling, seeing patterns in noise.",
            "growth": "Anchor in a system (Conjurer) or a purpose (Manipulator)."},
    "man": {"name": "Manipulator", "style": "Configural-Regulative", "key": "勢 configuration",
            "formula": "Leave the thing; arrange what it's for. Set up the board so the outcome follows.",
            "thinks": "Planning over long horizons, modelling other minds, steering by constraint and feedback loops.",
            "failure": "Hierarchical control: the illusion of mastering a living system.",
            "growth": "Act directly (Emitter) and let the system surprise you (Specialist)."},
    "emi": {"name": "Emitter", "style": "Projective-Kinetic", "key": "遠 / 反 going far, returning",
            "formula": "Send it outward and let it return changed. Thinking by moving.",
            "thinks": "Action first: externalises thought, tracks the situation in real time, works in bursts.",
            "failure": "Scatter and over-externalising: nothing processed within.",
            "growth": "Stay with yourself (Enhancer) and plan the trajectory (Manipulator)."},
}

TYPE_COLOURS = {"enh": "#C8402F", "tra": "#7A4FB0", "con": "#2C6FB7",
                "spe": "#1F8A70", "man": "#B88A1E", "emi": "#D2691E"}
