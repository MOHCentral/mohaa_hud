"""Bake condensed waiting-HUD text (title, needed, count) as 1:1 TGA labels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HUD = Path(r"C:\Users\paulh\AppData\Roaming\openmohaa\main\textures\hud")
STOCK_HUD = Path(r"D:\Games\test\MOHAA_STOCK\main\textures\hud")
ROAM_UI = Path(r"C:\Users\paulh\AppData\Roaming\openmohaa\main\ui")
STOCK_UI = Path(r"D:\Games\test\MOHAA_STOCK\main\ui")
PREVIEW = Path(r"D:\Games\test\MOHAA_STOCK\_extracted_ui\waiting_preview.png")

WAITING_NEEDED = 2
COUNT_MAX = 16
TITLE_SIZE = (512, 64)
NEEDED_SIZE = (512, 32)
COUNT_SIZE = (256, 32)
SS = 3  # supersample


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
    candidates = [
        Path(r"C:\Windows\Fonts\ARIALNB.TTF"),
        Path(r"C:\Windows\Fonts\arialnb.ttf"),
        Path(r"C:\Windows\Fonts\ARIALN.TTF"),
        Path(r"C:\Windows\Fonts\bahnschrift.ttf"),
        Path(r"C:\Windows\Fonts\seguisb.ttf"),
        Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            font = ImageFont.truetype(str(path), px)
            applied = "Regular"
            if path.name.lower().startswith("bahnschrift") and hasattr(font, "get_variation_names"):
                try:
                    names = [n.decode() if isinstance(n, bytes) else str(n) for n in font.get_variation_names()]
                    for want in ("SemiBold Condensed", "Bold Condensed", "Condensed"):
                        if want in names:
                            font.set_variation_by_name(want)
                            applied = want
                            break
                except Exception as exc:
                    print("variation failed", exc)
            print(f"font {path.name} {px}px [{applied}]")
            return font
    return ImageFont.load_default()


def render_line(text: str, size: tuple[int, int], font_px: int) -> Image.Image:
    w, h = size
    sw, sh = w * SS, h * SS
    font = pick_font(font_px * SS)
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = dummy.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (sw - tw) // 2 - bbox[0]
    y = (sh - th) // 2 - bbox[1]

    shadow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((x + SS, y + SS), text, font=font, fill=(0, 0, 0, 210))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=SS * 0.65))

    fill = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    ImageDraw.Draw(fill).text((x, y), text, font=font, fill=(255, 255, 255, 255))

    out = Image.alpha_composite(shadow, fill)
    return out.resize((w, h), Image.Resampling.LANCZOS)


def write_urc(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """menu "hud_waiting" 512 136 NONE 1
bgcolor 0 0 0 0
fgcolor 1 1 1 1
align centerx top

resource
Label
{
name "waitingtitle"
rect 0 4 512 64
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
shader textures/hud/waiting_title
}

resource
Label
{
name "waitingneeded"
rect 0 64 512 32
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
shader textures/hud/waiting_needed
}

resource
Label
{
name "waitingcount"
rect 128 98 256 32
fgcolor 1.00 1.00 1.00 1.00
bgcolor 0.00 0.00 0.00 0.00
borderstyle "NONE"
linkcvar "cg_waiting_count_img"
linkcvartoshader
shader textures/hud/waiting_count_1
}

end.
""",
        encoding="ascii",
        newline="\n",
    )


def main() -> None:
    HUD.mkdir(parents=True, exist_ok=True)
    STOCK_HUD.mkdir(parents=True, exist_ok=True)

    assets = {
        "waiting_title.tga": render_line("WAITING FOR PLAYERS", TITLE_SIZE, 30),
        "waiting_needed.tga": render_line("PLAYERS NEEDED: 2", NEEDED_SIZE, 18),
        "waiting_count_empty.tga": Image.new("RGBA", COUNT_SIZE, (0, 0, 0, 0)),
    }
    for n in range(COUNT_MAX + 1):
        assets[f"waiting_count_{n}.tga"] = render_line(f"{n} / {WAITING_NEEDED}", COUNT_SIZE, 18)

    for name, img in assets.items():
        save_tga(img, HUD / name)
        save_tga(img, STOCK_HUD / name)
        print(f"wrote {name} {img.size}")

    write_urc(ROAM_UI / "hud_waiting.urc")
    write_urc(STOCK_UI / "hud_waiting.urc")

    preview = Image.new("RGBA", (512, 136), (70, 85, 100, 255))
    for img, xy in (
        (assets["waiting_title.tga"], (0, 4)),
        (assets["waiting_needed.tga"], (0, 64)),
        (assets["waiting_count_1.tga"], (128, 98)),
    ):
        preview.alpha_composite(img, xy)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview.save(PREVIEW)
    print("preview", PREVIEW)


if __name__ == "__main__":
    main()
