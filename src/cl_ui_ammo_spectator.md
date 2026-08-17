# Hide ammo HUD in spectator

The ammo panel is drawn by the **client** (`code/client/cl_ui.cpp`), not `cgame.dll`. Patch OpenMoHAA and rebuild **x86** `openmohaa.exe`.

If you build with `USE_RENDERER_DLOPEN` (default), also build and copy `renderer_opengl1.dll` next to the exe (`BUILD_RENDERER_GL1=ON`).

## 1. Helper (near the other `cl_ui.cpp` statics)

```c
static qboolean UI_PlayerIsSpectating(void)
{
    if (clc.state != CA_ACTIVE) {
        return qfalse;
    }
    return (cl.snap.ps.pm_flags & PMF_SPECTATING) != 0;
}
```

## 2. `UI_Update` — `no_menus` draw path

Only draw ammo when not spectating:

```c
if (hud_ammo && !UI_PlayerIsSpectating()) {
    hud_ammo->ForceShow();
    frame = uWinMan.getFrame();
    hud_ammo->GetContainerWidget()->Display(frame, 1.0);
}
```

## 3. `UI_Update` — normal HUD show (after weapon menu `hud_ammo_` lookup)

```c
if (hud_ammo) {
    if (UI_PlayerIsSpectating()) {
        hud_ammo->ForceHide();
    } else {
        hud_ammo->ForceShow();
    }
}
```

## 4. `UI_Hud_f` toggle

```c
if (hud_ammo) {
    if (hide || UI_PlayerIsSpectating()) {
        hud_ammo->ForceHide();
    } else {
        hud_ammo->ForceShow();
    }
}
```

Works for free spectator and first-person follow (`PMF_SPECTATING` stays set).
