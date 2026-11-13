"""Assets for: capitalism, socialism, liberalism (same style as draw_ep02)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw_ep02 import C, O, W, svg, person  # noqa: E402

SKY = "#0EB7F8"


def arm(x1, y1, x2, y2, col):
    return (f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{O}" stroke-width="56" stroke-linecap="round"/>'
            f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{col}" stroke-width="36" stroke-linecap="round"/>')


def legs(col, shoe=O):
    return (f'<rect x="80" y="430" width="65" height="230" fill="{col}" {W}/><rect x="155" y="430" width="65" height="230" fill="{col}" {W}/>'
            f'<path d="M66 655 h85 v32 h-95 Z" fill="{shoe}" {W}/><path d="M149 655 h85 l10 32 h-95 Z" fill="{shoe}" {W}/>')


# ---------------- capitalism ----------------
def shop(color, sign_icon, closed=False):
    awn = ""
    for i in range(6):
        x = 40 + i * 70
        awn += f'<path d="M{x} 170 h70 v40 a35 30 0 0 1 -70 0 Z" fill="{color if i % 2 == 0 else C["white"]}" {W}/>'
    b = (f'<rect x="50" y="200" width="400" height="260" fill="{C["cream"]}" {W}/>'
         f'<rect x="60" y="60" width="380" height="100" rx="16" fill="{C["suit"]}" {W}/>' + sign_icon + awn)
    if closed:
        b += (f'<rect x="80" y="250" width="340" height="200" fill="{C["dgray"]}" {W}/>'
              + "".join(f'<line x1="80" y1="{y}" x2="420" y2="{y}" stroke="{O}" stroke-width="6"/>' for y in range(280, 450, 30))
              + f'<path d="M160 270 L340 430 M340 270 L160 430" stroke="{C["red"]}" stroke-width="30" stroke-linecap="round"/>')
    else:
        b += (f'<rect x="90" y="270" width="150" height="120" fill="{C["lblue"]}" {W}/>'
              f'<rect x="290" y="270" width="110" height="190" fill="{C["brown"]}" {W}/>'
              f'<circle cx="380" cy="370" r="8" fill="{O}"/>')
    b += f'<rect x="30" y="455" width="440" height="25" fill="{C["dgray"]}" {W}/>'
    return svg(500, 490, b)


def burger_sign():
    return (f'<path d="M200 125 Q205 80 250 80 Q295 80 300 125 Z" fill="{C["dgold"]}" {W}/>'
            f'<rect x="198" y="125" width="104" height="14" rx="6" fill="{C["brown"]}" {W}/>'
            f'<path d="M200 140 h100 q0 18 -50 18 q-50 0 -50 -18 Z" fill="{C["dgold"]}" {W}/>')


def referee():
    b = f'<path d="M80 165 Q150 140 220 165 L235 440 H65 Z" fill="{C["white"]}" {W}/>'
    for x in (100, 140, 180):
        b += f'<rect x="{x}" y="165" width="22" height="270" fill="{O}"/>'
    b += f'<path d="M80 165 Q150 140 220 165 L235 440 H65 Z" fill="none" {W}/>'
    b += legs(C["suit"], C["white"])
    b += arm(85, 190, 55, 330, C["white"]) + f'<circle cx="55" cy="340" r="22" fill="{C["skin"]}" {W}/>'
    b += arm(215, 190, 205, 140, C["white"])
    b += f'<circle cx="200" cy="120" r="20" fill="{C["skin"]}" {W}/><rect x="180" y="96" width="44" height="22" rx="10" fill="{C["gold"]}" {W}/>'
    b += f'<path d="M150 150 L195 105" stroke="{C["red"]}" stroke-width="6"/>'
    return person(b, hair="#3B2A20")


def phone(icon):
    b = (f'<rect x="30" y="20" width="240" height="460" rx="40" fill="{C["suit"]}" {W}/>'
         f'<rect x="50" y="70" width="200" height="350" rx="12" fill="{C["lblue"]}" {W}/>'
         f'<rect x="120" y="38" width="60" height="12" rx="6" fill="{C["dgray"]}"/>'
         f'<circle cx="150" cy="450" r="14" fill="{C["dgray"]}" {W}/>' + icon)
    return svg(300, 500, b)


def apple_icon():
    return (f'<path d="M150 180 Q110 150 85 185 Q60 230 95 300 Q120 345 150 325 Q180 345 205 300 Q240 230 215 185 Q190 150 150 180 Z" fill="{C["red"]}" {W}/>'
            f'<path d="M150 180 Q148 150 160 130" fill="none" {W}/>'
            f'<path d="M160 145 Q190 120 205 140 Q180 160 160 145 Z" fill="{C["green"]}" {W}/>')


def star_icon():
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 85 if i % 2 == 0 else 38
        pts.append(f"{150 + r * math.cos(a):.1f},{245 + r * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{C["gold"]}" {W}/>'


def consumer():
    b = (f'<path d="M85 165 Q150 145 215 165 L228 440 H72 Z" fill="{C["gold"]}" {W}/>' + legs(C["blue"], C["white"])
         + arm(85, 190, 60, 330, C["gold"]) + f'<circle cx="60" cy="345" r="22" fill="{C["skin"]}" {W}/>'
         + arm(215, 190, 245, 320, C["gold"])
         + f'<path d="M215 330 h80 l-8 110 h-64 Z" fill="{C["red"]}" {W}/><path d="M232 330 q22 -40 44 0" fill="none" {W}/>'
         + f'<circle cx="245" cy="330" r="22" fill="{C["skin"]}" {W}/>')
    return person(b, hair="#5A3E2B")


# ---------------- socialism ----------------
def circle(col):
    return svg(300, 300, f'<circle cx="150" cy="150" r="125" fill="{col}" {W}/>'
                         f'<path d="M80 110 Q110 60 160 55" fill="none" stroke="{C["white"]}" stroke-width="16" stroke-linecap="round" opacity="0.7"/>')


def hospital():
    return svg(460, 460,
               f'<rect x="60" y="120" width="340" height="310" fill="{C["white"]}" {W}/>'
               f'<rect x="40" y="100" width="380" height="40" fill="{C["lblue"]}" {W}/>'
               f'<rect x="180" y="20" width="100" height="100" rx="14" fill="{C["white"]}" {W}/>'
               f'<path d="M230 35 V105 M195 70 H265" stroke="{C["red"]}" stroke-width="22"/>'
               + "".join(f'<rect x="{x}" y="{y}" width="60" height="50" fill="{C["lblue"]}" {W}/>' for x in (95, 305) for y in (180, 270))
               + f'<rect x="190" y="320" width="80" height="110" fill="{SKY}" {W}/>'
               f'<rect x="20" y="425" width="420" height="25" fill="{C["dgray"]}" {W}/>')


def school():
    return svg(460, 460,
               f'<path d="M30 190 L230 70 L430 190 Z" fill="{C["red"]}" {W}/>'
               f'<rect x="60" y="190" width="340" height="230" fill="{C["gold"]}" {W}/>'
               f'<circle cx="230" cy="150" r="28" fill="{C["white"]}" {W}/><path d="M230 135 V150 H242" {W}/>'
               + "".join(f'<rect x="{x}" y="230" width="60" height="60" fill="{C["lblue"]}" {W}/>' for x in (90, 310))
               + f'<rect x="190" y="300" width="80" height="120" fill="{C["brown"]}" {W}/>'
               f'<path d="M250 70 V20 h50 l-10 12 l10 12 h-50" fill="{C["green"]}" {W}/>'
               f'<rect x="20" y="415" width="420" height="25" fill="{C["dgray"]}" {W}/>')


def bus():
    return svg(500, 320,
               f'<rect x="30" y="40" width="440" height="210" rx="30" fill="{C["gold"]}" {W}/>'
               + "".join(f'<rect x="{x}" y="70" width="80" height="70" rx="8" fill="{C["lblue"]}" {W}/>' for x in (60, 160, 260))
               + f'<rect x="360" y="70" width="80" height="150" rx="8" fill="{C["lblue"]}" {W}/>'
               f'<rect x="30" y="170" width="330" height="20" fill="{C["red"]}"/>'
               f'<circle cx="120" cy="260" r="40" fill="{C["suit"]}" {W}/><circle cx="380" cy="260" r="40" fill="{C["suit"]}" {W}/>'
               f'<circle cx="120" cy="260" r="14" fill="{C["gray"]}"/><circle cx="380" cy="260" r="14" fill="{C["gray"]}"/>')


def piggy():
    return svg(460, 380,
               f'<ellipse cx="220" cy="210" rx="170" ry="130" fill="#F4A6B7" {W}/>'
               f'<path d="M120 110 L140 40 L190 90" fill="#F4A6B7" {W}/>'
               f'<ellipse cx="385" cy="200" rx="40" ry="50" fill="#F08AA2" {W}/>'
               f'<circle cx="375" cy="190" r="7" fill="{O}"/><circle cx="395" cy="210" r="7" fill="{O}"/>'
               f'<circle cx="320" cy="150" r="10" fill="{O}"/>'
               f'<rect x="200" y="70" width="80" height="16" rx="8" fill="{O}"/>'
               f'<circle cx="240" cy="40" r="32" fill="{C["gold"]}" {W}/>'
               f'<rect x="120" y="300" width="45" height="60" fill="#F4A6B7" {W}/><rect x="270" y="300" width="45" height="60" fill="#F4A6B7" {W}/>'
               f'<path d="M50 200 q-30 -10 -20 -40" fill="none" {W}/>')


def citizen(shirt, skin=C["skin"], hair=C["hair"]):
    b = (f'<rect x="130" y="150" width="40" height="40" fill="{skin}" {W}/>'
         f'<path d="M60 330 Q60 190 150 180 Q240 190 240 330 Z" fill="{shirt}" {W}/>'
         f'<ellipse cx="150" cy="110" rx="58" ry="66" fill="{skin}" {W}/>'
         f'<path d="M92 105 Q95 40 150 40 Q210 40 208 105 Q190 70 150 75 Q110 70 92 105 Z" fill="{hair}" {W}/>')
    return svg(300, 340, b)


def flag(bg, cross, inner=None):
    b = f'<path d="M30 40 V370" stroke="{O}" stroke-width="16" stroke-linecap="round"/>'
    body = f'<rect x="40" y="40" width="360" height="240" fill="{bg}"/>'
    body += f'<rect x="40" y="135" width="360" height="50" fill="{cross}"/><rect x="140" y="40" width="50" height="240" fill="{cross}"/>'
    if inner:
        body += f'<rect x="40" y="148" width="360" height="24" fill="{inner}"/><rect x="153" y="40" width="24" height="240" fill="{inner}"/>'
    b += body + f'<rect x="40" y="40" width="360" height="240" fill="none" {W}/>'
    return svg(420, 390, b)


# ---------------- liberalism ----------------
def bird():
    return svg(420, 340,
               f'<path d="M80 200 Q120 110 230 130 Q300 140 330 110 L380 120 L340 150 Q330 250 220 260 Q130 265 80 200 Z" fill="{SKY}" {W}/>'
               f'<path d="M170 160 Q200 40 300 30 Q270 120 230 170 Z" fill="#5CCEFA" {W}/>'
               f'<path d="M80 200 L20 170 L40 220 L10 250 L95 225" fill="{SKY}" {W}/>'
               f'<circle cx="330" cy="135" r="8" fill="{O}"/>'
               f'<path d="M380 120 L410 128 L378 140" fill="{C["gold"]}" {W}/>')


def cage_open():
    b = f'<path d="M60 180 Q60 40 200 40 Q340 40 340 180" fill="none" {W}/>'
    for x in range(60, 341, 40):
        if 180 <= x <= 260:
            continue
        b += f'<line x1="{x}" y1="{180 if x in (60, 340) else 90}" x2="{x}" y2="440" {W}/>'
    b += (f'<rect x="40" y="430" width="320" height="30" rx="10" fill="{C["gold"]}" {W}/>'
          f'<path d="M180 180 L110 120 L110 330 L180 390" fill="none" {W}/>'
          f'<circle cx="200" cy="25" r="18" fill="{C["gold"]}" {W}/>')
    return svg(400, 480, b)


def scroll():
    return svg(400, 460,
               f'<rect x="70" y="60" width="260" height="340" fill="{C["cream"]}" {W}/>'
               f'<rect x="40" y="30" width="320" height="50" rx="25" fill="{C["dgold"]}" {W}/>'
               f'<rect x="40" y="380" width="320" height="50" rx="25" fill="{C["dgold"]}" {W}/>'
               + "".join(f'<path d="M110 {y} h180" stroke="{C["gray"]}" stroke-width="12" stroke-linecap="round"/>' for y in (130, 175, 220, 265))
               + f'<circle cx="250" cy="330" r="30" fill="{C["red"]}" {W}/>')


def gavel():
    return svg(460, 400,
               f'<rect x="80" y="320" width="300" height="50" rx="12" fill="{C["brown"]}" {W}/>'
               f'<g transform="rotate(-35 230 180)">'
               f'<rect x="215" y="150" width="30" height="230" rx="10" fill="{C["dgold"]}" {W}/>'
               f'<rect x="130" y="80" width="200" height="90" rx="20" fill="{C["brown"]}" {W}/>'
               f'<rect x="120" y="70" width="30" height="110" rx="8" fill="{C["dgold"]}" {W}/>'
               f'<rect x="310" y="70" width="30" height="110" rx="8" fill="{C["dgold"]}" {W}/></g>')


def briefcase():
    return svg(440, 360,
               f'<path d="M160 90 V50 Q160 30 180 30 H260 Q280 30 280 50 V90" fill="none" {W}/>'
               f'<rect x="30" y="90" width="380" height="240" rx="24" fill="{C["brown"]}" {W}/>'
               f'<path d="M30 180 H410" {W}/><rect x="190" y="160" width="60" height="45" rx="8" fill="{C["gold"]}" {W}/>')


ALL = dict(
    burger_shop=lambda: shop(C["red"], burger_sign()),
    shop_closed=lambda: shop(C["dgray"], burger_sign(), closed=True),
    referee=referee, phone_apple=lambda: phone(apple_icon()), phone_star=lambda: phone(star_icon()),
    consumer=consumer,
    circle_red=lambda: circle(C["red"]), circle_gold=lambda: circle(C["gold"]), circle_sky=lambda: circle(SKY),
    hospital=hospital, school=school, bus=bus, piggy=piggy,
    citizen_a=lambda: citizen(C["green"]), citizen_b=lambda: citizen(C["red"], "#C68B65", "#3B2A20"),
    citizen_c=lambda: citizen(SKY, C["skin"], "#5A3E2B"),
    flag_sweden=lambda: flag("#006AA7", "#FECC02"), flag_norway=lambda: flag("#BA0C2F", "#FFFFFF", "#00205B"),
    bird=bird, cage=cage_open, scroll=scroll, gavel=gavel, briefcase=briefcase,
)

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for n, f in ALL.items():
        open(f"{out}/{n}.svg", "w").write(f())
    print(len(ALL), "svgs")
