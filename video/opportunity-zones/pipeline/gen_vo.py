#!/usr/bin/env python3
"""Generate voiceover sections with Piper (en_US-joe-medium) and print durations."""
import subprocess, json, os, wave

MODEL = "/usr/local/lib/python3.11/dist-packages/joe_us_piper_voice/data/en_US-joe-medium.onnx"
CFG = MODEL + ".json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vo")
os.makedirs(OUT, exist_ok=True)

SECTIONS = {
    "s1_opening": (
        "Opportunity Zones are federally designated areas, created to encourage long-term "
        "investment into growing communities. Investors who reinvest eligible capital gains "
        "into a Qualified Opportunity Fund may benefit from valuable tax advantages, while "
        "supporting economic development."
    ),
    "s2a_usedc_hq": (
        "U.S. Energy Development Corporation has spent more than forty five years designing "
        "and managing direct investment opportunities for accredited investors and "
        "institutional partners."
    ),
    "s2b_usedc_ops": (
        "The firm has participated in more than four thousand wells across thirteen states "
        "and Canada, while deploying over four billion dollars on behalf of its partners."
    ),
    "s3_timeline": (
        "After realizing a capital gain, investors generally have one hundred and eighty days "
        "to invest in a Qualified Opportunity Fund. During the investment period, capital is "
        "deployed into qualified Opportunity Zone property. The original gain is deferred "
        "until the earlier of the investment being sold, or December thirty first, twenty "
        "twenty six. If the investment is held for at least ten years, appreciation on the "
        "Qualified Opportunity Fund investment may qualify for exclusion from federal capital "
        "gains tax."
    ),
    "s4_tax": (
        "A unique feature of Opportunity Zone investing is the potential for a year-end, "
        "independent valuation. During the early stages of development, that valuation may be "
        "lower than the original purchase price, potentially resetting an investor's basis, "
        "and increasing future upside. Investors who maintain their investment for at least "
        "ten years may also qualify to exclude federal capital gains tax on the appreciation "
        "of the Opportunity Fund investment itself."
    ),
    "s5_closing": (
        "Opportunity Zones combine long-term investing with community development, and unique "
        "tax planning opportunities. Through disciplined energy investments and decades of "
        "operational experience, U.S. Energy Development Corporation continues helping "
        "investors participate in these strategies with confidence."
    ),
}

durs = {}
for name, text in SECTIONS.items():
    out = os.path.join(OUT, name + ".wav")
    subprocess.run(
        ["python3", "-m", "piper", "--model", MODEL, "--config", CFG,
         "--length-scale", "0.85", "--sentence-silence", "0.30",
         "--output-file", out, "--", text],
        check=True, capture_output=True)
    with wave.open(out) as w:
        durs[name] = round(w.getnframes() / w.getframerate(), 3)

print(json.dumps(durs, indent=2))
with open(os.path.join(OUT, "durations.json"), "w") as f:
    json.dump(durs, f, indent=2)
