# mohaa_hud

Modern HUD overlay for [OpenMoHAA](https://github.com/openmoh/openmohaa) (Medal of Honor: Allied Assault).

- **Health** — circular segmented meter, live HP digits
- **Score** — Allies / Axis panel with round time
- **Compass** — custom dial, needle, objective markers (WIP)
- **Ammo** — clip / reserve, fire mode, per-weapon silhouettes, magazine ticks
- **Waiting** — top-center “WAITING FOR PLAYERS” until 2 clients join
- **Next map** — name + thumb under the compass from `sv_maplist`

Requires your own copy of the game. This repo is **only** the HUD overlay — no Pak files or game binaries.

## Install (loose files)

Copy these folders into `main/` of the game **or** `%APPDATA%\openmohaa\main\` (Roaming is loaded first):

```
ui/
configs/
scripts/
textures/
```

Add to `autoexec.cfg`:

```
exec configs/healthbar.cfg
```

URC changes need a **full game restart**. `vid_restart` does not reload these menus.

Leave stock Pak textures in place (`healthback`, `compasspain`, `compassobjarrow`).

## cgame (live values)

Drop the files in `src/` into OpenMoHAA `code/cgame/` (except `src/png/`) and hook them:

`cg_local.h`

```c
void CG_HealthFrame_Init(void);
void CG_HealthFrame_Frame(void);
void CG_ScoreHud_Init(void);
void CG_ScoreHud_Frame(void);
void CG_AmmoHud_Init(void);
void CG_AmmoHud_Frame(void);
void CG_WaitingHud_Init(void);
void CG_WaitingHud_Frame(void);
void CG_NextMapHud_Init(void);
void CG_NextMapHud_Frame(void);
```

`cg_main.c` (end of `CG_Init`)

```c
CG_HealthFrame_Init();
CG_ScoreHud_Init();
CG_AmmoHud_Init();
CG_WaitingHud_Init();
CG_NextMapHud_Init();
```

`cg_drawtools.cpp` (start of `CG_Draw2D`)

```c
CG_HealthFrame_Frame();
CG_ScoreHud_Frame();
CG_AmmoHud_Frame();
CG_WaitingHud_Frame();
CG_NextMapHud_Frame();
```

Build **x86** `cgame.dll`. Close the game before overwriting the DLL.

Score HUD extra: in multiplayer, add `ui_addhud hud_score` and remove stock `hud_timelimit` / `hud_fraglimit`. For a board that is Allies-left / Axis-right on every client, `fgame` `UpdateStats` should write Allies kills to `STAT_KILLS` and Axis kills to `STAT_HIGHEST_SCORE`.

## Spectator

The ammo panel is hidden in spectator (including follow). That is a **client** change in `cl_ui.cpp`, not cgame — see `src/cl_ui_ammo_spectator.md`. Rebuild `openmohaa.exe` (and ship `renderer_opengl1.dll` if the client loads the renderer as a DLL).

## Layout notes

| HUD | Size | Align |
| --- | --- | --- |
| Health | 1536×1024 | left bottom |
| Score | 320×88 | right top |
| Compass | 128×128 | left top (stock slot) |
| Ammo | 356×116 | right bottom |
| Waiting | 512×136 | centerx top |
| Next map | 140×272 | left top (under compass) |

Ammo silhouettes: source PNGs in `textures/weapon/`. Rebuild HUD textures with `python tools/_hud_ammo_gen.py` (paths in that script point at a local OpenMoHAA `main/`). Waiting labels: `python tools/_hud_waiting_gen.py`. Next-map thumbs: `python tools/_hud_nextmap_gen.py` (reads stock loading screens from local `Pak1.pk3`).
