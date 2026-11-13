import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw_ep02 import C, O, W, svg, person  # noqa: E402

SKY = "#0EB7F8"


def voter(shirt, skin=C["skin"], hair=C["hair"]):
    b = (f'<rect x="130" y="150" width="40" height="40" fill="{skin}" {W}/>'
         # raised right arm (behind body)
         f'<path d="M200 220 L246 62" stroke="{O}" stroke-width="56" stroke-linecap="round"/>'
         f'<path d="M200 220 L246 62" stroke="{shirt}" stroke-width="36" stroke-linecap="round"/>'
         f'<circle cx="248" cy="48" r="26" fill="{skin}" {W}/>'
         f'<path d="M60 330 Q60 190 150 180 Q240 190 240 330 Z" fill="{shirt}" {W}/>'
         f'<ellipse cx="150" cy="110" rx="58" ry="66" fill="{skin}" {W}/>'
         f'<path d="M92 105 Q95 40 150 40 Q210 40 208 105 Q190 70 150 75 Q110 70 92 105 Z" fill="{hair}" {W}/>')
    return svg(300, 340, b)


def pizza():
    b = f'<path d="M200 380 L40 70 Q200 0 360 70 Z" fill="{C["gold"]}" {W}/>'
    b += f'<path d="M40 70 Q200 0 360 70 L345 100 Q200 35 55 100 Z" fill="{C["brown"]}" {W}/>'
    for x, y in ((150, 140), (250, 150), (200, 230), (170, 300 - 60)):
        b += f'<circle cx="{x}" cy="{y}" r="24" fill="{C["red"]}" {W}/>'
    return svg(400, 400, b)


def burger():
    return svg(400, 360,
               f'<path d="M50 160 Q60 30 200 30 Q340 30 350 160 Z" fill="{C["dgold"]}" {W}/>'
               f'<path d="M120 80 l8 8 M200 65 l8 8 M270 90 l8 8" {W}/>'
               f'<path d="M40 165 Q120 205 200 170 Q280 205 360 165 L360 185 H40 Z" fill="{C["green"]}" {W}/>'
               f'<rect x="45" y="185" width="310" height="55" rx="25" fill="{C["brown"]}" {W}/>'
               f'<path d="M50 240 h300 l-20 25 h-260 Z" fill="{C["gold"]}" {W}/>'
               f'<path d="M50 270 h300 Q340 330 200 330 Q60 330 50 270 Z" fill="{C["dgold"]}" {W}/>')


def ballot_box():
    return svg(460, 460,
               f'<path d="M60 140 L230 80 L400 140 L230 200 Z" fill="{C["lblue"]}" fill-opacity="0.85" {W}/>'
               f'<path d="M190 130 L270 105" stroke="{O}" stroke-width="18" stroke-linecap="round"/>'
               f'<path d="M60 140 V390 L230 450 V200 Z" fill="{C["lblue"]}" fill-opacity="0.6" {W}/>'
               f'<path d="M400 140 V390 L230 450 V200 Z" fill="#7FC8E0" fill-opacity="0.7" {W}/>'
               f'<rect x="100" y="250" width="70" height="70" rx="8" transform="skewY(20)" fill="{C["white"]}" {W}/>'
               f'<path d="M300 300 l30 30 l50 -60" fill="none" stroke="{SKY}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>')


def ballot():
    return svg(260, 320,
               f'<path d="M20 20 H190 L240 70 V300 H20 Z" fill="{C["white"]}" {W}/>'
               f'<path d="M190 20 V70 H240" fill="{C["gray"]}" {W}/>'
               f'<rect x="50" y="110" width="40" height="40" rx="6" fill="none" {W}/>'
               f'<path d="M58 128 l12 14 l26 -34" fill="none" stroke="{SKY}" stroke-width="10" stroke-linecap="round"/>'
               f'<path d="M115 130 h90 M50 200 h150 M50 250 h120" stroke="{C["gray"]}" stroke-width="10" stroke-linecap="round"/>')


def parliament():
    b = (f'<path d="M150 190 Q250 30 350 190 Z" fill="{SKY}" {W}/>'
         f'<path d="M250 70 V5" {W}/><path d="M252 8 h60 l-12 16 l12 16 h-60 Z" fill="{C["gold"]}" {W}/>'
         f'<rect x="60" y="190" width="380" height="40" fill="{C["cream"]}" {W}/>')
    for x in (90, 160, 230, 300, 370, 410):
        b += f'<rect x="{x}" y="230" width="34" height="150" fill="{C["white"]}" {W}/>'
    b += (f'<rect x="40" y="380" width="420" height="34" fill="{C["gray"]}" {W}/>'
          f'<rect x="20" y="414" width="460" height="30" fill="{C["dgray"]}" {W}/>')
    return svg(500, 450, b)


def president():
    b = (f'<path d="M80 165 Q150 140 220 165 L240 440 H60 Z" fill="{C["suit"]}" {W}/>'
         f'<path d="M125 160 L150 230 L175 160 Z" fill="{C["white"]}" {W}/>'
         f'<path d="M150 175 L140 280 L150 295 L160 280 Z" fill="{SKY}" {W}/>'
         f'<path d="M95 175 L215 420 L190 430 L80 200 Z" fill="{C["gold"]}" {W}/>'
         f'<rect x="78" y="430" width="65" height="230" fill="{C["suit"]}" {W}/><rect x="157" y="430" width="65" height="230" fill="{C["suit"]}" {W}/>'
         f'<path d="M66 660 h85 v30 h-95 Z" fill="{O}"/><path d="M149 660 h85 l10 30 h-95 Z" fill="{O}"/>'
         f'<path d="M80 175 L45 330 L80 340 L105 200" fill="{C["suit"]}" {W}/><circle cx="62" cy="345" r="22" fill="{C["skin"]}" {W}/>'
         f'<path d="M215 185 L265 90" stroke="{O}" stroke-width="56" stroke-linecap="round"/>'
         f'<path d="M215 185 L265 90" stroke="{C["suit"]}" stroke-width="36" stroke-linecap="round"/>'
         f'<circle cx="268" cy="78" r="24" fill="{C["skin"]}" {W}/>')
    return person(b, hair="#4A4A4A")


def speech():
    return svg(420, 360,
               f'<path d="M40 50 Q40 20 70 20 H350 Q380 20 380 50 V230 Q380 260 350 260 H160 L80 330 L100 260 H70 Q40 260 40 230 Z" fill="{C["white"]}" {W}/>'
               f'<path d="M100 100 h220 M100 150 h220 M100 200 h140" stroke="{SKY}" stroke-width="16" stroke-linecap="round"/>')


def shield():
    return svg(400, 460,
               f'<path d="M200 20 L370 80 Q380 320 200 440 Q20 320 30 80 Z" fill="{SKY}" {W}/>'
               f'<path d="M200 60 L330 105 Q335 300 200 395 Z" fill="#5CCEFA" />'
               f'<path d="M200 20 L370 80 Q380 320 200 440 Q20 320 30 80 Z" fill="none" {W}/>'
               f'<path d="M130 230 l50 50 l95 -110" fill="none" stroke="{C["white"]}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>')


def padlock():
    return svg(400, 500,
               f'<path d="M100 230 V150 Q100 40 200 40 Q300 40 300 150 V230" fill="none" stroke="{O}" stroke-width="70" stroke-linecap="round"/>'
               f'<path d="M100 230 V150 Q100 40 200 40 Q300 40 300 150 V230" fill="none" stroke="{C["gray"]}" stroke-width="50" stroke-linecap="round"/>'
               f'<rect x="40" y="210" width="320" height="270" rx="30" fill="{C["dgray"]}" {W}/>'
               f'<rect x="40" y="210" width="320" height="50" rx="20" fill="{C["gray"]}" {W}/>'
               f'<circle cx="200" cy="330" r="34" fill="{O}"/><path d="M185 335 h30 l10 80 h-50 Z" fill="{O}"/>')


ALL = dict(voter_green=lambda: voter(C["green"]), voter_red=lambda: voter(C["red"], skin="#C68B65", hair="#3B2A20"),
           pizza=pizza, burger=burger, ballot_box=ballot_box, ballot=ballot, parliament=parliament,
           president=president, speech=speech, shield=shield, padlock=padlock)

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for n, f in ALL.items():
        open(f"{out}/{n}.svg", "w").write(f())
    print(len(ALL), "svgs")
