"""Bake next-map HUD panel, names, and cropped loading-screen thumbs."""
from io import BytesIO
from pathlib import Path
import zipfile
from PIL import Image, ImageDraw, ImageFont

HUD = Path(r"C:\Users\paulh\AppData\Roaming\openmohaa\main\textures\hud")
STOCK_HUD = Path(r"D:\Games\test\MOHAA_STOCK\main\textures\hud")
ROAM_UI = Path(r"C:\Users\paulh\AppData\Roaming\openmohaa\main\ui")
STOCK_UI = Path(r"D:\Games\test\MOHAA_STOCK\main\ui")
PREVIEW = Path(r"D:\Games\test\MOHAA_STOCK\_extracted_ui\nextmap_preview.png")
PAK1 = Path(r"D:\Games\test\MOHAA_STOCK\main\Pak1.pk3")

# Power-of-two sizes, drawn 1:1. GL1 resamples NPOT textures and that blurs HUD text.
PANEL = 128
TEXT_W, TEXT_H = 128, 16
LINE_H = 4
SHOT_W, SHOT_H = 128, 64
PAD = 8
OX, OY = 12, 136

# basename -> (title, pak path)
MAPS = {
    "mohdm1": ("SOUTHERN FRANCE", "textures/mohmenu/dmloading/mohdm1.tga"),
    "mohdm2": ("DESTROYED VILLAGE", "textures/mohmenu/dmloading/mohdm2.tga"),
    "mohdm3": ("REMAGEN", "textures/mohmenu/dmloading/mohdm3.tga"),
    "mohdm4": ("THE CROSSROADS", "textures/mohmenu/dmloading/mohdm4.tga"),
    "mohdm5": ("SNOWY PARK", "textures/mohmenu/dmloading/mohdm5.tga"),
    "mohdm6": ("STALINGRAD", "textures/mohmenu/dmloading/mohdm6.tga"),
    "mohdm7": ("ALGIERS", "textures/mohmenu/dmloading/mohdm7.tga"),
    "objdm1": ("THE HUNT", "textures/mohmenu/objloading/objdm1.tga"),
    "objdm2": ("V2 ROCKET FACILITY", "textures/mohmenu/objloading/objdm2.tga"),
    "objdm3": ("OMAHA BEACH", "textures/mohmenu/objloading/objdm5.tga"),
    "objdm4": ("THE BRIDGE", "textures/mohmenu/objloading/objdm4.tga"),
    "objdm5": ("OMAHA BEACH", "textures/mohmenu/objloading/objdm5.tga"),
}


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


def pick_font(px: int) -> ImageFont.FreeTypeFont:
    for path in (
        Path(r"C:\Windows\Fonts\tahomabd.ttf"),
        Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), px)
    return ImageFont.load_default()


def render_left(text: str, size: tuple[int, int], font_px: int, pad_x: int = 8) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    px = font_px
    font = pick_font(px)
    bbox = d.textbbox((0, 0), text, font=font)
    while px > 9 and (bbox[2] - bbox[0]) > w - pad_x * 2:
        px -= 1
        font = pick_font(px)
        bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = pad_x - bbox[0]
    y = (h - th) // 2 - bbox[1]
    d.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return img


def make_panel() -> Image.Image:
    img = Image.new("RGBA", (PANEL, PANEL), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, PANEL - 1, PANEL - 1), fill=(0, 0, 0, 140))
    return img


def make_line() -> Image.Image:
    img = Image.new("RGBA", (TEXT_W, LINE_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((PAD, 1, TEXT_W - PAD - 1, 1), fill=(220, 220, 220, 220))
    return img


def load_shot(z: zipfile.ZipFile, pak_path: str) -> Image.Image:
    raw = z.read(pak_path)
    src = Image.open(BytesIO(raw)).convert("RGBA")
    w, h = src.size
    crop_h = h // 2
    y0 = max(0, (h - crop_h) // 3)
    inner_w = SHOT_W - PAD * 2
    crop = src.crop((0, y0, w, y0 + crop_h)).convert("RGB").resize((inner_w, SHOT_H), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (SHOT_W, SHOT_H), (0, 0, 0, 0))
    out.paste(crop.convert("RGBA"), (PAD, 0))
    return out


def write_urc(path: Path) -> None:
    hy = OY + 4
    ly = hy + TEXT_H
    ny = ly + LINE_H
    sy = ny + TEXT_H + 8
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""menu "hud_nextmap" 140 272 NONE 1
bgcolor 0 0 0 0
fgcolor 1 1 1 1
align left top

resource
Label
{{
name "nextmappanel"
rect {OX} {OY} {PANEL} {PANEL}
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
shader textures/hud/nextmap_panel
}}

resource
Label
{{
name "nextmapheader"
rect {OX} {hy} {TEXT_W} {TEXT_H}
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
shader textures/hud/nextmap_header
}}

resource
Label
{{
name "nextmapline"
rect {OX} {ly} {TEXT_W} {LINE_H}
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
shader textures/hud/nextmap_line
}}

resource
Label
{{
name "nextmapname"
rect {OX} {ny} {TEXT_W} {TEXT_H}
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_nextmap_name_img"
linkcvartoshader
shader textures/hud/nextmap_name_mohdm7
}}

resource
Label
{{
name "nextmapshot"
rect {OX} {sy} {SHOT_W} {SHOT_H}
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_nextmap_shot_img"
linkcvartoshader
shader textures/hud/nextmap_shot_mohdm7
}}

end.
""",
        encoding="ascii",
        newline="\n",
    )


def main() -> None:
    HUD.mkdir(parents=True, exist_ok=True)
    STOCK_HUD.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(PAK1)
    assets = {
        "nextmap_panel.tga": make_panel(),
        "nextmap_header.tga": render_left("NEXT MAP", (TEXT_W, TEXT_H), 13),
        "nextmap_line.tga": make_line(),
        "nextmap_name_unknown.tga": render_left("UNKNOWN", (TEXT_W, TEXT_H), 12),
        "nextmap_shot_empty.tga": Image.new("RGBA", (SHOT_W, SHOT_H), (0, 0, 0, 0)),
    }
    for key, (title, pak) in MAPS.items():
        assets[f"nextmap_name_{key}.tga"] = render_left(title, (TEXT_W, TEXT_H), 12)
        try:
            assets[f"nextmap_shot_{key}.tga"] = load_shot(z, pak)
        except KeyError:
            print("missing shot", pak)
            assets[f"nextmap_shot_{key}.tga"] = assets["nextmap_shot_empty.tga"]
    z.close()

    for name, img in assets.items():
        save_tga(img, HUD / name)
        save_tga(img, STOCK_HUD / name)
        print("wrote", name, img.size)

    write_urc(ROAM_UI / "hud_nextmap.urc")
    write_urc(STOCK_UI / "hud_nextmap.urc")
    shader = """textures/hud/nextmap_panel
{
    nopicmip
    nomipmaps
    {
        map textures/hud/nextmap_panel.tga
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
    }
}
"""
    for scripts in (
        Path(r"C:\Users\paulh\AppData\Roaming\openmohaa\main\scripts"),
        Path(r"D:\Games\test\MOHAA_STOCK\main\scripts"),
    ):
        scripts.mkdir(parents=True, exist_ok=True)
        (scripts / "hud_nextmap.shader").write_text(shader, encoding="ascii")

    hy = 4
    preview = Image.new("RGBA", (PANEL, 272), (90, 110, 80, 255))
    preview.alpha_composite(assets["nextmap_panel.tga"], (0, OY))
    preview.alpha_composite(assets["nextmap_header.tga"], (0, OY + hy))
    preview.alpha_composite(assets["nextmap_line.tga"], (0, OY + hy + TEXT_H))
    preview.alpha_composite(assets["nextmap_name_mohdm2.tga"], (0, OY + hy + TEXT_H + LINE_H))
    preview.alpha_composite(assets["nextmap_shot_mohdm2.tga"], (0, OY + hy + TEXT_H * 2 + LINE_H + 8))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview.save(PREVIEW)
    print("preview", PREVIEW)


if __name__ == "__main__":
    main()
