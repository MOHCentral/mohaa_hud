"""Generate modern ammo HUD textures and URC overrides."""
from pathlib import Path
import struct
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HUD = Path(r"C:\Users\paulh\AppData\Roaming\openmohaa\main\textures\hud")
STOCK_HUD = Path(r"D:\Games\test\MOHAA_STOCK\main\textures\hud")
ROAM_UI = Path(r"C:\Users\paulh\AppData\Roaming\openmohaa\main\ui")
STOCK_UI = Path(r"D:\Games\test\MOHAA_STOCK\main\ui")
PREVIEW = Path(r"D:\Games\test\MOHAA_STOCK\_extracted_ui\ammo_preview.png")
WEAPON_DIR = Path(r"D:\Games\test\MOHAA_STOCK\main\textures\weapon")

PNG_ICONS = {
    "weapon_icon_transparent.png": "ammo_weap_bar",
    "bazooka.png": "ammo_weap_bazooka",
    "colt.png": "ammo_weap_colt",
    "kar98.png": "ammo_weap_kar98",
    "kar98sniper.png": "ammo_weap_kar98sniper",
    "m1_garand.png": "ammo_weap_garand",
    "mp40.png": "ammo_weap_mp40",
    "mp44.png": "ammo_weap_mp44",
    "p38.png": "ammo_weap_p38",
    "panzershreck.png": "ammo_weap_panzerschreck",
    "shotgun.png": "ammo_weap_shotgun",
    "silencedpistol.png": "ammo_weap_silenced",
    "springfield.png": "ammo_weap_springfield",
    "thompsonsmg.png": "ammo_weap_thompson",
    "m2frag.png": "ammo_weap_m2frag",
    "steilhandgranate.png": "ammo_weap_steilhandgranate",
}

MENUS = [
    ("hud_ammo_bar.urc", "hud_ammo_BAR", "textures/hud/ammo_weap_bar", "AUTOMATIC"),
    ("hud_ammo_bazooka.urc", "hud_ammo_Bazooka", "textures/hud/ammo_weap_bazooka", "SINGLE"),
    ("hud_ammo_empty.urc", "hud_ammo_", "textures/hud/ammo_icon_empty", ""),
    ("hud_ammo_garand.urc", "hud_ammo_M1 Garand", "textures/hud/ammo_weap_garand", "SEMI"),
    ("hud_ammo_kar98.urc", "hud_ammo_Mauser KAR 98K", "textures/hud/ammo_weap_kar98", "BOLT"),
    ("hud_ammo_kar98sniper.urc", "hud_ammo_KAR98 - Sniper", "textures/hud/ammo_weap_kar98sniper", "BOLT"),
    ("hud_ammo_M2grenade.urc", "hud_ammo_Frag Grenade", "textures/hud/ammo_weap_m2frag", "THROWN"),
    ("hud_ammo_mp40.urc", "hud_ammo_MP40", "textures/hud/ammo_weap_mp40", "AUTOMATIC"),
    ("hud_ammo_mp44.urc", "hud_ammo_StG 44", "textures/hud/ammo_weap_mp44", "AUTOMATIC"),
    ("hud_ammo_p38.urc", "hud_ammo_Walther P38", "textures/hud/ammo_weap_p38", "SEMI"),
    ("hud_ammo_panzerschreck.urc", "hud_ammo_Panzerschreck", "textures/hud/ammo_weap_panzerschreck", "SINGLE"),
    ("hud_ammo_shotgun.urc", "hud_ammo_Shotgun", "textures/hud/ammo_weap_shotgun", "PUMP"),
    ("hud_ammo_silencedpistol.urc", "hud_ammo_Hi-Standard Silenced", "textures/hud/ammo_weap_silenced", "SEMI"),
    ("hud_ammo_springfield.urc", "hud_ammo_Springfield '03 Sniper", "textures/hud/ammo_weap_springfield", "BOLT"),
    ("hud_ammo_steilhandgranate.urc", "hud_ammo_Stielhandgranate", "textures/hud/ammo_weap_steilhandgranate", "THROWN"),
    ("hud_ammo_thompson.urc", "hud_ammo_Thompson", "textures/hud/ammo_weap_thompson", "AUTOMATIC"),
    ("hud_ammo_colt45.urc", "hud_ammo_Colt 45", "textures/hud/ammo_weap_colt", "SEMI"),
]


def save_tga(img: Image.Image, path: Path) -> None:
    img = img.convert("RGBA")
    w, h = img.size
    flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
    header = bytearray(18)
    header[2] = 2
    header[12] = w & 0xFF
    header[13] = (w >> 8) & 0xFF
    header[14] = h & 0xFF
    header[15] = (h >> 8) & 0xFF
    header[16] = 32
    header[17] = 8
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(header) + flipped.tobytes())


def rounded_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def make_panel():
    img = Image.new("RGBA", (512, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rounded_rect(d, (4, 4, 508, 124), 8, (0, 0, 0, 110))
    return img


def draw_bar(d, ox=0, oy=0, s=1.0):
    def p(pts):
        return [(ox + x * s, oy + y * s) for x, y in pts]

    # muzzle left, stock right — BAR profile
    d.polygon(p([(8, 26), (118, 26), (118, 32), (8, 32)]), fill=(255, 255, 255, 255))  # barrel
    d.polygon(p([(70, 22), (86, 22), (86, 26), (70, 26)]), fill=(255, 255, 255, 255))  # front sight / gas
    d.polygon(p([(96, 16), (124, 16), (128, 22), (96, 22)]), fill=(255, 255, 255, 255))  # carry handle
    d.polygon(p([(118, 22), (168, 22), (172, 36), (118, 36)]), fill=(255, 255, 255, 255))  # receiver
    d.polygon(p([(132, 36), (150, 36), (148, 58), (128, 58), (126, 42)]), fill=(255, 255, 255, 255))  # mag
    d.polygon(p([(150, 36), (164, 36), (160, 54), (148, 50)]), fill=(255, 255, 255, 255))  # grip
    d.polygon(p([(168, 24), (248, 28), (248, 42), (172, 40)]), fill=(255, 255, 255, 255))  # stock
    d.polygon(p([(232, 28), (248, 22), (252, 44), (232, 42)]), fill=(255, 255, 255, 255))  # butt


def draw_rifle(d):
    d.polygon([(6, 28), (150, 26), (150, 32), (6, 34)], fill=(255, 255, 255, 255))
    d.polygon([(90, 22), (140, 20), (150, 36), (90, 36)], fill=(255, 255, 255, 255))
    d.polygon([(118, 36), (132, 36), (128, 46), (116, 46)], fill=(255, 255, 255, 255))
    d.polygon([(140, 24), (248, 28), (246, 42), (148, 38)], fill=(255, 255, 255, 255))
    d.polygon([(70, 18), (130, 16), (132, 22), (70, 24)], fill=(255, 255, 255, 255))  # scope


def draw_smg(d):
    d.polygon([(16, 28), (110, 26), (110, 34), (16, 36)], fill=(255, 255, 255, 255))
    d.polygon([(70, 20), (130, 20), (140, 40), (70, 40)], fill=(255, 255, 255, 255))
    d.polygon([(88, 40), (112, 40), (108, 62), (84, 62)], fill=(255, 255, 255, 255))  # stick/drum
    d.polygon([(118, 40), (136, 40), (130, 58), (116, 52)], fill=(255, 255, 255, 255))
    d.polygon([(130, 24), (210, 30), (206, 46), (138, 40)], fill=(255, 255, 255, 255))
    d.polygon([(40, 22), (58, 18), (62, 28), (40, 28)], fill=(255, 255, 255, 255))  # compensator


def draw_shotgun(d):
    d.polygon([(8, 24), (160, 24), (160, 30), (8, 30)], fill=(255, 255, 255, 255))
    d.polygon([(40, 30), (120, 30), (120, 36), (40, 36)], fill=(255, 255, 255, 255))  # magazine tube
    d.polygon([(90, 22), (140, 22), (148, 40), (90, 40)], fill=(255, 255, 255, 255))
    d.polygon([(124, 40), (140, 40), (134, 52), (118, 50)], fill=(255, 255, 255, 255))
    d.polygon([(140, 24), (248, 30), (244, 44), (148, 38)], fill=(255, 255, 255, 255))


def draw_pistol(d):
    d.polygon([(70, 22), (170, 22), (170, 32), (70, 32)], fill=(255, 255, 255, 255))
    d.polygon([(70, 18), (92, 16), (96, 22), (70, 22)], fill=(255, 255, 255, 255))
    d.polygon([(140, 32), (168, 32), (158, 58), (132, 54)], fill=(255, 255, 255, 255))
    d.polygon([(118, 32), (140, 32), (138, 42), (116, 42)], fill=(255, 255, 255, 255))


def draw_heavy(d):
    d.polygon([(12, 22), (220, 22), (228, 40), (20, 40)], fill=(255, 255, 255, 255))  # tube
    d.polygon([(8, 26), (24, 18), (28, 44), (10, 40)], fill=(255, 255, 255, 255))  # muzzle
    d.polygon([(90, 40), (120, 40), (114, 58), (88, 54)], fill=(255, 255, 255, 255))
    d.polygon([(150, 16), (190, 16), (190, 22), (150, 22)], fill=(255, 255, 255, 255))  # sight


def draw_grenade(d):
    d.ellipse((96, 18, 160, 58), fill=(255, 255, 255, 255))
    d.rectangle((120, 10, 136, 22), fill=(255, 255, 255, 255))
    d.polygon([(136, 10), (168, 6), (170, 14), (138, 18)], fill=(255, 255, 255, 255))
    for y in (28, 36, 44):
        d.rectangle((104, y, 152, y + 2), fill=(0, 0, 0, 0))


def make_icon(drawer):
    img = Image.new("RGBA", (256, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    drawer(d)
    return img.filter(ImageFilter.GaussianBlur(0.4))


def make_icon_from_png(src_path: Path):
    src = Image.open(src_path).convert("RGBA")
    r, g, b, a = src.split()
    lum = Image.merge("RGB", (r, g, b)).convert("L")
    a = ImageChops.multiply(a, lum)
    a = a.point(lambda v: 255 if v >= 16 else 0)
    white = Image.new("L", src.size, 255)
    sil = Image.merge("RGBA", (white, white, white, a))
    tex = Image.new("RGBA", (1024, 256), (0, 0, 0, 0))
    scale = min(1024 / sil.width, 256 / sil.height)
    nw, nh = max(1, int(sil.width * scale)), max(1, int(sil.height * scale))
    fitted = sil.resize((nw, nh), Image.Resampling.LANCZOS)
    tex.paste(fitted, ((1024 - nw) // 2, (256 - nh) // 2), fitted)
    return tex


def make_pip():
    # POT 8x16: 4px bar + 4px gap.
    img = Image.new("RGBA", (8, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 3, 3, 13), fill=(255, 255, 255, 255))
    d.point((0, 3), fill=(0, 0, 0, 0))
    d.point((3, 3), fill=(0, 0, 0, 0))
    return img


def make_ticks(n, total=20):
    img = Image.new("RGBA", (256, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    gap = 3
    tw = 9
    x0 = 4
    for i in range(n):
        x = x0 + i * (tw + gap)
        d.rectangle((x, 3, x + tw - 1, 13), fill=(255, 255, 255, 255))
    return img


def make_empty(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def make_ammo_digit(ch=None):
    img = Image.new("RGBA", (32, 64), (0, 0, 0, 0))
    if not ch:
        return img
    d = ImageDraw.Draw(img)
    font_path = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if not font_path.exists():
        font_path = Path(r"C:\Windows\Fonts\segoeuib.ttf")
    font = ImageFont.truetype(str(font_path), 54)
    bbox = d.textbbox((0, 0), ch, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (32 - tw) // 2 - bbox[0]
    y = (64 - th) // 2 - bbox[1] - 2
    d.text((x, y), ch, font=font, fill=(255, 255, 255, 255))
    return img


FIRE_W, FIRE_H = 64, 16  # same width as two clip digits (20)
FIRE_WORDS = ("AUTOMATIC", "SEMI", "BOLT", "SINGLE", "THROWN", "PUMP")


def _fire_font_path():
    for p in (
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
    ):
        if p.exists():
            return p
    return Path(r"C:\Windows\Fonts\arialbd.ttf")


def _fire_font_and_scale():
    path = _fire_font_path()
    font = ImageFont.truetype(str(path), 72)
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = dummy.textbbox((0, 0), "AUTOMATIC", font=font)
    tw = max(1, bbox[2] - bbox[0])
    return font, FIRE_W / tw


def make_fire_word(text):
    out = Image.new("RGBA", (FIRE_W, FIRE_H), (0, 0, 0, 0))
    if not text:
        return out
    font, scale = _fire_font_and_scale()
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = dummy.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 4
    big = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(big).text(
        (pad - bbox[0], pad - bbox[1]),
        text,
        font=font,
        fill=(230, 230, 230, 255),
    )
    nw = max(1, round((tw + pad * 2) * scale))
    nh = max(1, round((th + pad * 2) * scale))
    glyph = big.resize((nw, nh), Image.Resampling.LANCZOS)
    # drop the scaled pad so AUTOMATIC lands on the 64px box
    sp = round(pad * scale)
    crop = glyph.crop((sp, sp, glyph.width - sp, glyph.height - sp))
    if crop.width > FIRE_W or crop.height > FIRE_H:
        crop = crop.resize(
            (min(crop.width, FIRE_W), min(crop.height, FIRE_H)),
            Image.Resampling.LANCZOS,
        )
    y = max(0, (FIRE_H - crop.height) // 2)
    out.alpha_composite(crop, (0, y))
    return out


def fire_shader(fire: str) -> str:
    if not fire:
        return "textures/hud/ammo_fire_empty"
    return "textures/hud/ammo_fire_" + fire.lower()


URC = """menu "{menu}" 356 116 NONE 1
bgcolor 0 0 0 0
fgcolor 1 1 1 1
align right bottom

resource
Label
{{
name "ammopanel"
rect 0 0 340 100
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
shader textures/hud/ammo_panel
}}

resource
Label
{{
name "clip_c2"
rect 34 6 32 64
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_ammo_c2"
linkcvartoshader
shader textures/hud/ammo_digit_empty
}}

resource
Label
{{
name "clip_c1"
rect 66 6 32 64
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_ammo_c1"
linkcvartoshader
shader textures/hud/ammo_digit_empty
}}

resource
Label
{{
name "clip_c0"
rect 98 6 32 64
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_ammo_c0"
linkcvartoshader
shader textures/hud/ammo_digit_empty
}}

resource
Label
{{
name "res_r2"
rect 112 10 16 32
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_ammo_r2"
linkcvartoshader
shader textures/hud/ammo_digit_empty
}}

resource
Label
{{
name "res_r1"
rect 128 10 16 32
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_ammo_r1"
linkcvartoshader
shader textures/hud/ammo_digit_empty
}}

resource
Label
{{
name "res_r0"
rect 144 10 16 32
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_ammo_r0"
linkcvartoshader
shader textures/hud/ammo_digit_empty
}}

resource
Label
{{
name "weaponname"
rect 115 36 84 22
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
itemstat 1
textalign left
font handle-23
}}

resource
Label
{{
name "firemode"
rect 34 60 64 16
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
shader {fire_shader}
}}

resource
Label
{{
name "weapicon"
rect 168 8 164 52
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
shader {icon}
}}

resource
Label
{{
name "ammoticks"
rect 152 76 160 14
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
statbar horizontal
playerstat 6
maxplayerstat 7
statbar_tileshader textures/hud/ammo_pip
}}

end.
"""


def write_urc(path: Path, menu: str, icon: str, fire: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        URC.format(menu=menu, icon=icon, fire_shader=fire_shader(fire)),
        encoding="ascii",
    )


def load_tga(p: Path) -> Image.Image:
    data = p.read_bytes()
    idlen = data[0]
    w, h = struct.unpack_from("<HH", data, 12)
    bpp = data[16]
    desc = data[17]
    off = 18 + idlen
    raw = data[off : off + w * h * (bpp // 8)]
    mode = "RGBA" if bpp == 32 else "RGB"
    img = Image.frombytes(mode, (w, h), raw)
    if not (desc & 0x20):
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img.convert("RGBA")


def main():
    HUD.mkdir(parents=True, exist_ok=True)
    STOCK_HUD.mkdir(parents=True, exist_ok=True)

    assets = {
        "ammo_panel.tga": make_panel(),
        "ammo_icon_empty.tga": make_empty((256, 64)),
        "ammo_pip.tga": make_pip(),
        "ammo_digit_empty.tga": make_ammo_digit(None),
        "ammo_fire_empty.tga": make_fire_word(""),
    }
    for png, stem in PNG_ICONS.items():
        src = WEAPON_DIR / png
        if not src.exists():
            raise FileNotFoundError(src)
        assets[f"{stem}.tga"] = make_icon_from_png(src)
    for word in FIRE_WORDS:
        assets[f"ammo_fire_{word.lower()}.tga"] = make_fire_word(word)
    for n in range(10):
        assets[f"ammo_digit_{n}.tga"] = make_ammo_digit(str(n))
    for i in range(21):
        assets[f"ammo_ticks_{i}.tga"] = make_ticks(i)

    for name, img in assets.items():
        save_tga(img, HUD / name)
        save_tga(img, STOCK_HUD / name)
        print(f"wrote {name} {img.size}")

    for fname, menu, icon, fire in MENUS:
        write_urc(ROAM_UI / fname, menu, icon, fire)
        write_urc(STOCK_UI / fname, menu, icon, fire)
        print(f"urc {fname} -> {menu} {icon}")

    shader_parts = [
        """textures/hud/ammo_pip
{
    nopicmip
    nomipmaps
    {
        map textures/hud/ammo_pip.tga
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
    }
}
"""
    ]
    for word in FIRE_WORDS + ("empty",):
        name = f"ammo_fire_{word.lower()}"
        shader_parts.append(
            f"""textures/hud/{name}
{{
    nopicmip
    nomipmaps
    {{
        map textures/hud/{name}.tga
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
    }}
}}
"""
        )
    shader = "\n".join(shader_parts)
    for scripts in (
        Path(r"C:\Users\paulh\AppData\Roaming\openmohaa\main\scripts"),
        Path(r"D:\Games\test\MOHAA_STOCK\main\scripts"),
    ):
        scripts.mkdir(parents=True, exist_ok=True)
        (scripts / "hud_ammo.shader").write_text(shader, encoding="ascii")
        print(f"shader {scripts / 'hud_ammo.shader'}")

    # preview composite at URC pixel size
    panel = assets["ammo_panel.tga"].resize((340, 100), Image.Resampling.LANCZOS)
    preview = Image.new("RGBA", (340, 100), (40, 36, 28, 255))
    preview.alpha_composite(panel)
    d = ImageDraw.Draw(preview)

    def blit_digit(ch, box, big=False):
        src = load_tga(HUD / (f"digit_{ch}.tga" if ch != "e" else "digit_empty.tga"))
        preview.paste(src.resize(box[2:], Image.Resampling.NEAREST), box[:2], src.resize(box[2:], Image.Resampling.NEAREST))

    blit_digit("2", (12, 10, 24, 48), True)
    blit_digit("0", (36, 10, 24, 48), True)
    blit_digit("2", (90, 12, 13, 26))
    blit_digit("2", (103, 12, 13, 26))
    blit_digit("0", (116, 12, 13, 26))
    icon = assets["ammo_weap_bar.tga"].resize((164, 52), Image.Resampling.LANCZOS)
    preview.alpha_composite(icon, (168, 8))
    ticks = assets["ammo_ticks_20.tga"].resize((152, 16), Image.Resampling.NEAREST)
    preview.alpha_composite(ticks, (176, 66))
    try:
        font = ImageFont.truetype("segoeui.ttf", 14)
        font_sm = ImageFont.truetype("segoeui.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font
    d.text((90, 40), "BAR", fill=(255, 255, 255, 255), font=font)
    d.text((12, 64), "AUTOMATIC", fill=(230, 230, 230, 255), font=font_sm)
    preview.save(PREVIEW)
    print(f"preview {PREVIEW}")


if __name__ == "__main__":
    main()
