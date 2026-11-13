import os
O = "#1E1E2E"  # outline
W = 'stroke="%s" stroke-width="10" stroke-linejoin="round" stroke-linecap="round"' % O
C = dict(green="#5DBB63", dgreen="#3E8E41", lgreen="#8FD694", gold="#FFD166", dgold="#E9B44C",
         red="#E63946", skin="#E8B796", white="#FFFFFF", gray="#B8C0CC", dgray="#7A8494",
         blue="#457B9D", lblue="#A8DADC", brown="#9C6B4E", suit="#2B2D42", hair="#F4C430", cream="#F6E7C8")


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{body}</svg>'


def gear(c=C["green"]):
    import math
    pts = []
    for i in range(32):
        a = i / 32 * 2 * math.pi
        r = 175 if (i // 2) % 2 == 0 else 140
        pts.append(f"{200 + r * math.cos(a):.1f},{200 + r * math.sin(a):.1f}")
    return svg(400, 400, f'<polygon points="{" ".join(pts)}" fill="{c}" {W}/>'
                         f'<circle cx="200" cy="200" r="95" fill="{C["dgreen"]}" {W}/>'
                         f'<circle cx="200" cy="200" r="42" fill="{C["white"]}" {W}/>')


def wheat():
    b = ""
    for dx, rot in ((-40, -14), (0, 0), (40, 14)):
        g = f'<g transform="rotate({rot} 200 560)">'
        g += f'<line x1="{200+dx}" y1="560" x2="{200+dx}" y2="190" {W}/>'
        for k in range(6):
            y = 120 + k * 40
            g += f'<ellipse cx="{200+dx-22}" cy="{y+12}" rx="18" ry="30" transform="rotate(-25 {200+dx-22} {y+12})" fill="{C["gold"]}" {W}/>'
            g += f'<ellipse cx="{200+dx+22}" cy="{y+12}" rx="18" ry="30" transform="rotate(25 {200+dx+22} {y+12})" fill="{C["gold"]}" {W}/>'
        g += f'<ellipse cx="{200+dx}" cy="95" rx="16" ry="30" fill="{C["gold"]}" {W}/></g>'
        b += g
    b += f'<rect x="150" y="420" width="100" height="34" rx="10" fill="{C["red"]}" {W}/>'
    return svg(400, 600, b)


def factory():
    b = (f'<rect x="250" y="40" width="60" height="220" fill="{C["dgray"]}" {W}/>'
         f'<rect x="340" y="80" width="55" height="180" fill="{C["dgray"]}" {W}/>'
         f'<rect x="246" y="40" width="68" height="28" fill="{C["red"]}" {W}/>'
         f'<rect x="336" y="80" width="63" height="26" fill="{C["red"]}" {W}/>'
         f'<circle cx="300" cy="20" r="0"/>'
         f'<path d="M40 470 V250 L150 310 V250 L260 310 V250 L370 310 V250 L460 300 V470 Z" fill="{C["green"]}" {W}/>'
         f'<rect x="30" y="460" width="440" height="30" rx="8" fill="{C["dgreen"]}" {W}/>')
    for x in (80, 190, 300):
        b += f'<rect x="{x}" y="350" width="60" height="50" rx="6" fill="{C["lblue"]}" {W}/>'
    b += f'<rect x="395" y="360" width="50" height="100" rx="6" fill="{C["brown"]}" {W}/>'
    return svg(500, 500, b)


def fence():
    b = f'<rect x="20" y="90" width="560" height="22" fill="{C["dgray"]}" {W}/><rect x="20" y="180" width="560" height="22" fill="{C["dgray"]}" {W}/>'
    for x in range(40, 580, 60):
        b += f'<path d="M{x} 250 V50 L{x+15} 25 L{x+30} 50 V250 Z" fill="{C["suit"]}" {W}/>'
    b += (f'<path d="M270 135 v-30 a30 30 0 0 1 60 0 v30" fill="none" {W}/>'
          f'<rect x="250" y="130" width="100" height="85" rx="12" fill="{C["gold"]}" {W}/>'
          f'<circle cx="300" cy="165" r="10" fill="{O}"/><rect x="295" y="165" width="10" height="25" fill="{O}"/>')
    return svg(600, 270, b)


def person(body, extra="", hair=C["hair"], skin=C["skin"], hat=None):
    """faceless character: head + neck; body supplied (300x700 canvas)."""
    head = f'<rect x="130" y="120" width="40" height="40" fill="{skin}" {W}/>' + body
    head += f'<ellipse cx="150" cy="85" rx="58" ry="66" fill="{skin}" {W}/>'
    if hat:
        head += hat
    elif hair:
        head += f'<path d="M92 80 Q95 15 150 15 Q210 15 208 80 Q190 45 150 50 Q110 45 92 80 Z" fill="{hair}" {W}/>'
    return svg(300, 700, head + extra)


def owner():
    b = (f'<path d="M80 165 Q150 140 220 165 L240 440 H60 Z" fill="{C["suit"]}" {W}/>'
         f'<path d="M125 160 L150 230 L175 160 Z" fill="{C["white"]}" {W}/>'
         f'<path d="M150 175 L138 300 L150 320 L162 300 Z" fill="{C["red"]}" {W}/>'
         f'<rect x="78" y="430" width="65" height="230" fill="{C["suit"]}" {W}/><rect x="157" y="430" width="65" height="230" fill="{C["suit"]}" {W}/>'
         f'<rect x="60" y="425" width="180" height="22" fill="{O}"/><rect x="138" y="426" width="24" height="20" fill="{C["gold"]}" {W}/>'
         f'<path d="M66 660 h85 v30 h-95 Z" fill="{O}"/><path d="M149 660 h85 l10 30 h-95 Z" fill="{O}"/>'
         # crossed arms
         f'<path d="M70 250 Q60 330 230 345 L225 300 Q120 300 110 250 Z" fill="{C["suit"]}" {W}/>'
         f'<path d="M230 250 Q240 330 70 345 L75 300 Q180 300 190 250 Z" fill="{C["suit"]}" {W}/>'
         f'<circle cx="232" cy="322" r="22" fill="{C["white"]}" {W}/><circle cx="68" cy="322" r="22" fill="{C["white"]}" {W}/>')
    return person(b)


def worker(prop):
    b = (f'<path d="M85 165 Q150 145 215 165 L232 450 H68 Z" fill="{C["green"]}" {W}/>'
         f'<rect x="110" y="200" width="80" height="90" rx="8" fill="{C["dgreen"]}" {W}/>'
         f'<line x1="110" y1="170" x2="120" y2="210" {W}/><line x1="190" y1="170" x2="180" y2="210" {W}/>'
         f'<rect x="76" y="440" width="68" height="220" fill="{C["green"]}" {W}/><rect x="156" y="440" width="68" height="220" fill="{C["green"]}" {W}/>'
         f'<path d="M66 655 h85 v32 h-95 Z" fill="{C["brown"]}" {W}/><path d="M149 655 h85 l10 32 h-95 Z" fill="{C["brown"]}" {W}/>')
    hat = f'<path d="M88 75 Q90 18 150 16 Q210 18 212 75 Z" fill="{C["gold"]}" {W}/><rect x="80" y="68" width="140" height="18" rx="9" fill="{C["dgold"]}" {W}/>'
    if prop == "wrench":
        b += (f'<path d="M85 175 L40 330 L70 340 L110 200" fill="{C["green"]}" {W}/><circle cx="55" cy="345" r="22" fill="{C["skin"]}" {W}/>'
              f'<path d="M215 175 L255 320 L230 330 L195 200" fill="{C["green"]}" {W}/><circle cx="245" cy="335" r="22" fill="{C["skin"]}" {W}/>'
              f'<rect x="240" y="300" width="22" height="150" rx="8" fill="{C["gray"]}" {W}/><path d="M232 450 h38 v40 h-12 v-22 h-14 v22 h-12 Z" fill="{C["gray"]}" {W}/>')
    else:
        b += (f'<path d="M85 175 L60 290 L100 300 L110 200" fill="{C["green"]}" {W}/>'
              f'<path d="M215 175 L240 290 L200 300 L190 200" fill="{C["green"]}" {W}/>'
              f'<rect x="55" y="250" width="190" height="130" rx="6" fill="{C["brown"]}" {W}/>'
              f'<line x1="150" y1="250" x2="150" y2="300" {W}/><rect x="125" y="250" width="50" height="22" fill="{C["cream"]}" {W}/>'
              f'<circle cx="62" cy="310" r="20" fill="{C["skin"]}" {W}/><circle cx="238" cy="310" r="20" fill="{C["skin"]}" {W}/>')
    return person(b, hat=hat, skin="#C68B65")


def coins():
    b = ""
    for i in range(5):
        y = 300 - i * 50
        b += f'<ellipse cx="200" cy="{y+30}" rx="140" ry="40" fill="{C["dgold"]}" {W}/><rect x="60" y="{y}" width="280" height="30" fill="{C["dgold"]}" stroke="none"/>'
        b += f'<line x1="60" y1="{y}" x2="60" y2="{y+30}" {W}/><line x1="340" y1="{y}" x2="340" y2="{y+30}" {W}/>'
        b += f'<ellipse cx="200" cy="{y}" rx="140" ry="40" fill="{C["gold"]}" {W}/>'
    b += f'<text x="200" y="118" font-size="60" font-family="Arial Black,Arial" font-weight="900" text-anchor="middle" fill="{C["dgold"]}">$</text>'
    return svg(400, 400, b)


def gov():
    b = (f'<path d="M250 20 V95" {W}/><path d="M250 22 h80 l-15 22 l15 22 h-80 Z" fill="{C["red"]}" {W}/>'
         f'<path d="M30 200 L250 95 L470 200 Z" fill="{C["cream"]}" {W}/>'
         f'<rect x="40" y="200" width="420" height="38" fill="{C["gray"]}" {W}/>')
    for x in (70, 160, 250, 340, 430):
        b += f'<rect x="{x-22}" y="238" width="44" height="200" fill="{C["white"]}" {W}/>'
    b += (f'<rect x="20" y="438" width="460" height="34" fill="{C["gray"]}" {W}/>'
          f'<rect x="0" y="472" width="500" height="28" fill="{C["dgray"]}" {W}/>'
          f'<circle cx="250" cy="160" r="22" fill="{C["gold"]}" {W}/>')
    return svg(500, 505, b)


def farm():
    b = (f'<path d="M10 330 Q250 260 490 330 V420 H10 Z" fill="{C["green"]}" {W}/>'
         f'<path d="M60 380 Q250 330 440 380" fill="none" stroke="{C["dgreen"]}" stroke-width="10"/>'
         f'<rect x="120" y="170" width="200" height="190" fill="{C["red"]}" {W}/>'
         f'<path d="M100 175 L220 80 L340 175 Z" fill="{C["brown"]}" {W}/>'
         f'<rect x="185" y="250" width="70" height="110" fill="{C["white"]}" {W}/>'
         f'<path d="M185 250 L255 360 M255 250 L185 360" {W}/>'
         f'<rect x="200" y="160" width="40" height="40" fill="{C["white"]}" {W}/>'
         f'<rect x="360" y="190" width="70" height="170" rx="30" fill="{C["gray"]}" {W}/>')
    return svg(500, 430, b)


def bread():
    return svg(400, 300, f'<path d="M40 200 Q20 80 200 70 Q380 80 360 200 Q360 250 300 250 H100 Q40 250 40 200 Z" fill="{C["dgold"]}" {W}/>'
                         f'<path d="M120 110 l30 40 M190 100 l30 45 M260 110 l30 40" {W}/>')


def house():
    return svg(400, 400, f'<path d="M30 190 L200 40 L370 190 Z" fill="{C["red"]}" {W}/>'
                         f'<rect x="70" y="190" width="260" height="180" fill="{C["cream"]}" {W}/>'
                         f'<rect x="170" y="260" width="70" height="110" fill="{C["brown"]}" {W}/>'
                         f'<rect x="95" y="225" width="55" height="55" fill="{C["lblue"]}" {W}/>'
                         f'<rect x="265" y="225" width="45" height="45" fill="{C["lblue"]}" {W}/>')


def book():
    return svg(400, 300, f'<path d="M200 60 Q120 20 30 40 V250 Q120 230 200 270 Z" fill="{C["white"]}" {W}/>'
                         f'<path d="M200 60 Q280 20 370 40 V250 Q280 230 200 270 Z" fill="{C["white"]}" {W}/>'
                         f'<path d="M20 60 V270 Q120 250 200 285 Q280 250 380 270 V60" fill="none" stroke="{C["blue"]}" stroke-width="14"/>'
                         f'<path d="M70 100 h90 M70 140 h90 M70 180 h70 M240 100 h90 M240 140 h90 M240 180 h70" stroke="{C["gray"]}" stroke-width="10" stroke-linecap="round"/>')


def scale():
    b = (f'<rect x="185" y="90" width="30" height="390" fill="{C["dgold"]}" {W}/>'
         f'<path d="M110 520 h180 l-30 -40 h-120 Z" fill="{C["dgold"]}" {W}/>'
         f'<rect x="40" y="90" width="320" height="24" rx="10" fill="{C["gold"]}" {W}/>'
         f'<circle cx="200" cy="80" r="26" fill="{C["gold"]}" {W}/>'
         f'<path d="M60 114 L20 280 M60 114 L100 280 M340 114 L300 280 M340 114 L380 280" {W}/>'
         f'<path d="M5 280 h110 a55 40 0 0 1 -110 0 Z" fill="{C["gold"]}" {W}/>'
         f'<path d="M285 280 h110 a55 40 0 0 1 -110 0 Z" fill="{C["gold"]}" {W}/>')
    return svg(400, 540, b)


def thinker():
    b = (f'<path d="M85 165 Q150 145 215 165 L228 440 H72 Z" fill="{C["blue"]}" {W}/>'
         f'<rect x="80" y="430" width="65" height="230" fill="{C["suit"]}" {W}/><rect x="155" y="430" width="65" height="230" fill="{C["suit"]}" {W}/>'
         f'<path d="M66 655 h85 v32 h-95 Z" fill="{C["white"]}" {W}/><path d="M149 655 h85 l10 32 h-95 Z" fill="{C["white"]}" {W}/>'
         f'<path d="M85 175 L55 330 L90 340 L112 200" fill="{C["blue"]}" {W}/><circle cx="72" cy="345" r="22" fill="{C["skin"]}" {W}/>'
         f'<path d="M215 175 L245 290 Q240 310 200 280 L150 200" fill="{C["blue"]}" {W}/>'
         f'<path d="M200 285 L170 175" stroke="{C["blue"]}" stroke-width="38" stroke-linecap="round"/>'
         f'<path d="M200 285 L170 175" fill="none" {W} stroke-opacity="0"/>'
         f'<circle cx="168" cy="160" r="22" fill="{C["skin"]}" {W}/>')
    return person(b, hair="#5A3E2B")


def question():
    return svg(300, 420, f'<path d="M60 130 Q60 30 150 30 Q245 30 245 120 Q245 175 190 205 Q160 222 160 260 V280 H110 V250 Q110 195 160 170 Q195 152 195 120 Q195 80 150 80 Q110 80 110 130 Z" fill="{C["gold"]}" {W}/>'
                         f'<circle cx="135" cy="350" r="35" fill="{C["gold"]}" {W}/>')


ALL = dict(gear=gear, wheat=wheat, factory=factory, fence=fence, owner=owner,
           worker_a=lambda: worker("wrench"), worker_b=lambda: worker("box"), coins=coins,
           gov_building=gov, farm=farm, bread=bread, house=house, book=book, scale=scale,
           thinker=thinker, question=question)

if __name__ == "__main__":
    import sys
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for n, f in ALL.items():
        open(f"{out}/{n}.svg", "w").write(f())
    print(len(ALL), "svgs")
