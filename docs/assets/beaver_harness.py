"""Regenerate docs/assets/beaver-harness.svg; update the status marks here as parts get built.

    python3 docs/assets/beaver_harness.py > docs/assets/beaver-harness.svg

For the PNG, wrap the SVG in a page that loads Figtree and Google Sans Code from Google
Fonts, then screenshot it with headless Chrome at --window-size=1600,1000 and
--force-device-scale-factor=2.
"""
from xml.sax.saxutils import escape as esc

INK, MUTED, BAND, WHITE, PAGE = "#121314", "#5F646A", "#ECECE6", "#FFFFFF", "#F7F7F4"
FERN, FERN_DARK, FERN_TINT = "#3E6B34", "#2F5E2A", "#DDE8D8"
HUB, HUB_TILE, HUB_TEXT, HUB_MUTED, FERN_LIGHT, GREY = "#2B2E31", "#3A3E42", "#F2F2EF", "#B9BDC2", "#8CC27A", "#8A8F95"
out = []
w = out.append

def text(x, y, s, size=12, fill=INK, weight=None, anchor=None, family=None, ls=None):
    a = f' font-weight="{weight}"' if weight else ""
    a += f' text-anchor="{anchor}"' if anchor else ""
    a += f' font-family="{family}"' if family else ""
    a += f' letter-spacing="{ls}"' if ls else ""
    w(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{a}>{esc(s)}</text>')

def rect(x, y, wd, h, fill, rx=8, extra=""):
    w(f'<rect x="{x}" y="{y}" width="{wd}" height="{h}" rx="{rx}" fill="{fill}"{extra}/>')

def dot(cx, cy, status, dark=False):
    on = FERN_LIGHT if dark else FERN
    if status == "built":
        w(f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="{on}"/>')
    elif status == "next":
        w(f'<circle cx="{cx}" cy="{cy}" r="4" fill="none" stroke="{on}" stroke-width="2"/>')
    else:
        w(f'<circle cx="{cx}" cy="{cy}" r="4" fill="none" stroke="{GREY}" stroke-width="1.5" stroke-dasharray="2 2"/>')

def arrow(x1, y1, x2, y2):
    w(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{GREY}" stroke-width="1.6" marker-end="url(#tip)"/>')

w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="1600" height="1000" role="img" '
  'aria-label="The Beaver harness at the centre: the learner reaches it through five surfaces that follow the same UX rules; '
  'inside, agents, one core library and guards share the learner&#39;s plain-file workspace as the source of truth; the method flows in '
  'from upstream; the learner&#39;s AI projects stay in their own repos, planned, tracked and reviewed by Beaver and observed read-only; '
  'a rigor band checks every change." font-family="Figtree, &#39;Helvetica Neue&#39;, Arial, sans-serif">')
w(f'<defs><marker id="tip" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  f'<path d="M2 1 L9 5 L2 9" fill="none" stroke="{GREY}" stroke-width="1.6"/></marker></defs>')
rect(0, 0, 1600, 1000, PAGE, rx=0)

# Title
text(64, 58, "PROJECT BEAVER", 13, FERN, 700, ls="2.2")
text(64, 96, "The Beaver harness: built around the learner, governing their AI projects", 30, INK, 700, ls="-0.3")
text(64, 126, "The learner builds every step. Beaver plans, tracks and reviews, keeps the next step easy, and keeps the proof honest.", 16, MUTED)

# Experience band (top)
rect(64, 150, 1472, 140, BAND, rx=14)
text(88, 188, "The learner", 17, INK, 700)
text(88, 208, "AI engineer, short on time,", 12.5, MUTED)
text(88, 226, "does every step themselves", 12.5, MUTED)
text(88, 264, "UX rules", 12.5, FERN_DARK, 700)
surfaces = [("Today screen", "one step, Start · 20 min", "next"), ("Terminal", "beaver shows the next step", "next"),
            ("Claude Code", "plugin with skills", "planned"), ("VS Code fork", "the living repo", "built"),
            ("Ask Beaver", "chat on your own key", "planned")]
for i, (t, s, st) in enumerate(surfaces):
    x = 344 + i * 234
    rect(x, 164, 220, 66, WHITE)
    text(x + 14, 190, t, 14.5, INK, 600)
    text(x + 14, 210, s, 12, MUTED)
    dot(x + 206, 178, st)
chips = ["One 25-minute step", "Make it smaller", "Show me how, tagged", "Help level shown",
         "At most 3 nudges a week", "Plain words", "Proof, not points"]
x = 344
for c in chips:
    cw = round(len(c) * 6.7) + 28
    rect(x, 244, cw, 32, FERN_TINT, rx=16)
    text(x + cw / 2, 265, c, 12.5, FERN_DARK, 600, anchor="middle")
    x += cw + 10

# Experience -> hub
arrow(780, 294, 780, 322)
text(794, 313, "same files, same rules", 12, MUTED)

# Method (left)
rect(64, 326, 256, 420, BAND, rx=14)
text(88, 364, "Method", 17, INK, 700)
text(88, 384, "from upstream, by tag", 12.5, MUTED)
method = [("Knowledge base", "ethos · pathos · logos", "planned"), ("Curriculum", "nine FDE modules", "planned"),
          ("Role packs", "from job descriptions", "planned"), ("Ontology", "schemas, evidence levels", "built"),
          ("Templates", "in Beaver's voice", "built")]
for i, (t, s, st) in enumerate(method):
    y = 404 + i * 66
    rect(88, y, 208, 56, WHITE)
    text(102, y + 24, t, 14, INK, 600)
    text(102, y + 43, s, 12, MUTED)
    dot(282, y + 14, st)
arrow(324, 536, 396, 536)
text(360, 527, "flows in", 11.5, MUTED, anchor="middle")
text(360, 553, "by tag", 11.5, MUTED, anchor="middle")

# Hub (centre)
rect(400, 326, 760, 420, HUB, rx=16)
text(428, 364, "Beaver harness", 20, HUB_TEXT, 700)
text(428, 386, "One core, thin clients, files as truth", 13, HUB_MUTED)
cols = [
    ("Agents", [("Assistants", "via AGENTS.md", "built"), ("Beaver chat", "your key", "planned"),
                ("Skills", "6 in v1", "planned"), ("Companion", "weekly", "planned"),
                ("Personal agents", "read-only", "planned")]),
    ("Core library", [("Records", "9 schemas", "built"), ("Validate", "IDs, links", "built"),
                      ("Progress check", "waiting", "next"), ("Home", "anywhere", "next"),
                      ("Repo observer", "read-only", "planned")]),
    ("Guards", [("Never claims for the learner", "", "built"), ("Drafts to generated/ only", "", "built"),
                ("Project repos: read-only", "", "built"), ("A budget per session", "", "planned"),
                ("Provenance on every write", "", "planned")]),
]
for c, (head, tiles) in enumerate(cols):
    x = 428 + c * 240
    text(x, 420, head, 13, HUB_TEXT, 700)
    for i, (t, s, st) in enumerate(tiles):
        y = 432 + i * 42
        rect(x, y, 224, 36, HUB_TILE, rx=7)
        dot(x + 14, y + 18, st, dark=True)
        text(x + 27, y + 23, t, 13, HUB_TEXT, 600)
        if s:
            text(x + 212, y + 23, s, 12, HUB_MUTED, anchor="end")
rect(428, 648, 704, 36, HUB_TILE, rx=7)
w(f'<text x="780" y="671" font-size="13" fill="{HUB_TEXT}" text-anchor="middle">Every agent: '
  f'<tspan fill="{FERN_LIGHT}" font-weight="700">diagnose</tspan>, then scaffold when stuck · push for rigor when they got it · hold back in flow</text>')
rect(428, 694, 704, 40, FERN, rx=7)
text(444, 719, "Workspace, the source of truth", 13, WHITE, 700)
text(1120, 719, "learner/ learning/ projects/ sprints/ evidence/ reflections/ generated/", 11,
     "#E3ECDF", anchor="end", family="'Google Sans Code', 'SF Mono', Menlo, monospace")

# Projects (right)
rect(1240, 326, 296, 420, BAND, rx=14)
text(1264, 364, "Your AI projects", 17, INK, 700)
text(1264, 384, "each in its own repo · example data", 12.5, MUTED)
projects = [("support-copilot", "Brief, then sprint s03", "12 commits since last review"),
            ("llm-judge-harness", "Eval set: 150 real tickets", "CI passing · 1 PR open"),
            ("tool-agent", "Idea card, scorecard drafted", "Not started yet")]
for i, (name, a, b) in enumerate(projects):
    y = 404 + i * 114
    rect(1264, y, 248, 100, WHITE)
    text(1278, y + 28, name, 13.5, INK, 600, family="'Google Sans Code', 'SF Mono', Menlo, monospace")
    text(1278, y + 52, a, 12, MUTED)
    text(1278, y + 72, b, 12, MUTED)
arrow(1164, 478, 1236, 478)
text(1200, 469, "plans,", 11.5, MUTED, anchor="middle")
text(1200, 495, "reviews", 11.5, MUTED, anchor="middle")
arrow(1236, 618, 1164, 618)
text(1200, 609, "observed", 11.5, MUTED, anchor="middle")
text(1200, 635, "read-only", 11.5, MUTED, anchor="middle")

# Rigor -> hub
arrow(780, 778, 780, 750)
text(794, 768, "checks every change", 12, MUTED)

# Rigor band (bottom)
rect(64, 782, 1472, 140, BAND, rx=14)
text(88, 820, "Rigor", 17, INK, 700)
text(88, 840, "checked, not assumed", 12.5, MUTED)
rigor = [("CI gate", "93 tests on every PR;", "a red PR cannot merge", "built"),
         ("Terminal bench", "Claude Code in sealed", "sandboxes, as a learner", "built"),
         ("With vs without", "same moment, measured:", "Beaver pushed for rigor", "built"),
         ("Persona lab", "simulated learners and", "a separate grader", "planned"),
         ("Release acceptance", "every claimed feature", "tested before it ships", "planned")]
for i, (t, a, b, st) in enumerate(rigor):
    x = 344 + i * 234
    rect(x, 798, 220, 108, WHITE)
    text(x + 14, 826, t, 14.5, INK, 600)
    text(x + 14, 850, a, 12, MUTED)
    text(x + 14, 870, b, 12, MUTED)
    dot(x + 206, 812, st)

# Footer
text(64, 966, "github.com/prabakaranc98/project-beaver", 13, MUTED)
dot(1188, 962, "built"); text(1199, 966, "Built", 12.5, MUTED)
dot(1252, 962, "next"); text(1263, 966, "Next", 12.5, MUTED)
dot(1312, 962, "planned"); text(1323, 966, "Planned", 12.5, MUTED)
text(1536, 966, "November 2026", 12.5, MUTED, anchor="end")
w("</svg>")
print("\n".join(out))
