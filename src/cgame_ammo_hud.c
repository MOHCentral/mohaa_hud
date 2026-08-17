/* cgame_ammo_hud.c
 * Clip/reserve digits, fire-mode text, weapon icon, magazine tick strip.
 */

#include "cg_local.h"

#define AMMO_TICK_MAX 20

static const char *const digit_shaders[10] = {
    "textures/hud/ammo_digit_0", "textures/hud/ammo_digit_1", "textures/hud/ammo_digit_2",
    "textures/hud/ammo_digit_3", "textures/hud/ammo_digit_4", "textures/hud/ammo_digit_5",
    "textures/hud/ammo_digit_6", "textures/hud/ammo_digit_7", "textures/hud/ammo_digit_8",
    "textures/hud/ammo_digit_9",
};

static const char *digit_empty = "textures/hud/ammo_digit_empty";

static int  last_clip    = -1;
static int  last_reserve = -1;
static int  last_ticks   = -1;
static char last_mode[24];
static char last_icon[64];

static void CG_AmmoHud_SetDigits(const char *left, const char *mid, const char *right, int value, qboolean leftAlign)
{
    int hundreds;
    int tens;
    int ones;

    if (value < 0) {
        cgi.Cvar_Set(left, digit_empty);
        cgi.Cvar_Set(mid, digit_empty);
        cgi.Cvar_Set(right, digit_empty);
        return;
    }
    if (value > 999) {
        value = 999;
    }

    hundreds = value / 100;
    tens     = (value / 10) % 10;
    ones     = value % 10;

    if (leftAlign) {
        if (value >= 100) {
            cgi.Cvar_Set(left, digit_shaders[hundreds]);
            cgi.Cvar_Set(mid, digit_shaders[tens]);
            cgi.Cvar_Set(right, digit_shaders[ones]);
        } else if (value >= 10) {
            cgi.Cvar_Set(left, digit_shaders[tens]);
            cgi.Cvar_Set(mid, digit_shaders[ones]);
            cgi.Cvar_Set(right, digit_empty);
        } else {
            cgi.Cvar_Set(left, digit_shaders[ones]);
            cgi.Cvar_Set(mid, digit_empty);
            cgi.Cvar_Set(right, digit_empty);
        }
    } else {
        cgi.Cvar_Set(left, (value >= 100) ? digit_shaders[hundreds] : digit_empty);
        cgi.Cvar_Set(mid, (value >= 10) ? digit_shaders[tens] : digit_empty);
        cgi.Cvar_Set(right, digit_shaders[ones]);
    }
}

static const char *CG_AmmoHud_FireMode(const char *weapon)
{
    if (!weapon || !weapon[0]) {
        return "";
    }
    if (!Q_stricmp(weapon, "BAR") || !Q_stricmp(weapon, "Thompson") || !Q_stricmp(weapon, "MP40")
        || !Q_stricmp(weapon, "StG 44")) {
        return "AUTOMATIC";
    }
    if (!Q_stricmp(weapon, "Shotgun")) {
        return "PUMP";
    }
    if (!Q_stricmp(weapon, "Bazooka") || !Q_stricmp(weapon, "Panzerschreck")) {
        return "SINGLE";
    }
    if (!Q_stricmp(weapon, "Frag Grenade") || !Q_stricmp(weapon, "Stielhandgranate")) {
        return "THROWN";
    }
    if (Q_stristr(weapon, "Sniper") || !Q_stricmp(weapon, "Mauser KAR 98K") || !Q_stricmp(weapon, "KAR98 - Sniper")) {
        return "BOLT";
    }
    return "SEMI";
}

static const char *CG_AmmoHud_Icon(const char *weapon)
{
    if (!weapon || !weapon[0]) {
        return "textures/hud/ammo_icon_empty";
    }
    if (!Q_stricmp(weapon, "BAR")) {
        return "textures/hud/ammo_weap_bar";
    }
    if (!Q_stricmp(weapon, "StG 44")) {
        return "textures/hud/ammo_weap_mp44";
    }
    if (!Q_stricmp(weapon, "Thompson")) {
        return "textures/hud/ammo_weap_thompson";
    }
    if (!Q_stricmp(weapon, "MP40")) {
        return "textures/hud/ammo_weap_mp40";
    }
    if (!Q_stricmp(weapon, "Shotgun")) {
        return "textures/hud/ammo_weap_shotgun";
    }
    if (!Q_stricmp(weapon, "Colt 45")) {
        return "textures/hud/ammo_weap_colt";
    }
    if (!Q_stricmp(weapon, "Walther P38")) {
        return "textures/hud/ammo_weap_p38";
    }
    if (!Q_stricmp(weapon, "Hi-Standard Silenced")) {
        return "textures/hud/ammo_weap_silenced";
    }
    if (!Q_stricmp(weapon, "Bazooka")) {
        return "textures/hud/ammo_weap_bazooka";
    }
    if (!Q_stricmp(weapon, "Panzerschreck")) {
        return "textures/hud/ammo_weap_panzerschreck";
    }
    if (!Q_stricmp(weapon, "Frag Grenade")) {
        return "textures/hud/ammo_weap_m2frag";
    }
    if (!Q_stricmp(weapon, "Stielhandgranate")) {
        return "textures/hud/ammo_weap_steilhandgranate";
    }
    if (!Q_stricmp(weapon, "Mauser KAR 98K")) {
        return "textures/hud/ammo_weap_kar98";
    }
    if (!Q_stricmp(weapon, "KAR98 - Sniper")) {
        return "textures/hud/ammo_weap_kar98sniper";
    }
    if (!Q_stricmp(weapon, "M1 Garand")) {
        return "textures/hud/ammo_weap_garand";
    }
    if (!Q_stricmp(weapon, "Springfield '03 Sniper")) {
        return "textures/hud/ammo_weap_springfield";
    }
    return "textures/hud/ammo_weap_rifle";
}

void CG_AmmoHud_Init(void)
{
    cgi.Cvar_Get("cg_ammo_c2", "textures/hud/ammo_digit_empty", 0);
    cgi.Cvar_Get("cg_ammo_c1", "textures/hud/ammo_digit_empty", 0);
    cgi.Cvar_Get("cg_ammo_c0", "textures/hud/ammo_digit_0", 0);
    cgi.Cvar_Get("cg_ammo_r2", "textures/hud/ammo_digit_empty", 0);
    cgi.Cvar_Get("cg_ammo_r1", "textures/hud/ammo_digit_empty", 0);
    cgi.Cvar_Get("cg_ammo_r0", "textures/hud/ammo_digit_empty", 0);
    cgi.Cvar_Get("cg_fire_mode", "", 0);
    cgi.Cvar_Get("cg_weap_icon", "textures/hud/ammo_icon_empty", 0);
    cgi.Cvar_Get("cg_ammo_ticks", "textures/hud/ammo_ticks_0", 0);

    CG_AmmoHud_SetDigits("cg_ammo_c2", "cg_ammo_c1", "cg_ammo_c0", 0, qtrue);
    CG_AmmoHud_SetDigits("cg_ammo_r2", "cg_ammo_r1", "cg_ammo_r0", -1, qtrue);
    cgi.Cvar_Set("cg_fire_mode", "");
    cgi.Cvar_Set("cg_weap_icon", "textures/hud/ammo_icon_empty");
    cgi.Cvar_Set("cg_ammo_ticks", "textures/hud/ammo_ticks_0");

    last_clip        = -1;
    last_reserve     = -1;
    last_ticks       = -1;
    last_mode[0]     = 0;
    last_icon[0]     = 0;
}

void CG_AmmoHud_Frame(void)
{
    int         clip;
    int         reserve;
    int         maxclip;
    int         maxammo;
    int         ammo;
    int         shown;
    int         maxshown;
    int         ticks;
    const char *weapon;
    const char *mode;
    const char *icon;
    char        tickshader[64];

    if (!cg.snap) {
        return;
    }

    ammo    = cg.snap->ps.stats[STAT_AMMO];
    maxammo = cg.snap->ps.stats[STAT_MAXAMMO];
    clip    = cg.snap->ps.stats[STAT_CLIPAMMO];
    maxclip = cg.snap->ps.stats[STAT_MAXCLIPAMMO];

    if (maxclip > 0) {
        shown     = clip;
        maxshown  = maxclip;
        reserve   = ammo;
    } else {
        shown     = ammo;
        maxshown  = maxammo;
        reserve   = -1;
    }

    if (shown != last_clip) {
        last_clip = shown;
        CG_AmmoHud_SetDigits("cg_ammo_c2", "cg_ammo_c1", "cg_ammo_c0", shown < 0 ? 0 : shown, qtrue);
    }
    if (reserve != last_reserve) {
        last_reserve = reserve;
        CG_AmmoHud_SetDigits("cg_ammo_r2", "cg_ammo_r1", "cg_ammo_r0", reserve, qtrue);
    }

    if (maxshown > 0) {
        ticks = (shown * AMMO_TICK_MAX + maxshown / 2) / maxshown;
        if (ticks < 0) {
            ticks = 0;
        }
        if (ticks > AMMO_TICK_MAX) {
            ticks = AMMO_TICK_MAX;
        }
        if (shown > 0 && ticks < 1) {
            ticks = 1;
        }
    } else {
        ticks = 0;
    }

    if (ticks != last_ticks) {
        last_ticks = ticks;
        Com_sprintf(tickshader, sizeof(tickshader), "textures/hud/ammo_ticks_%d", ticks);
        cgi.Cvar_Set("cg_ammo_ticks", tickshader);
    }

    weapon = "";
    if (cg.snap->ps.activeItems[1] >= 0) {
        weapon = CG_ConfigString(CS_WEAPONS + cg.snap->ps.activeItems[1]);
    }

    mode = CG_AmmoHud_FireMode(weapon);
    if (strcmp(last_mode, mode)) {
        Q_strncpyz(last_mode, mode, sizeof(last_mode));
        cgi.Cvar_Set("cg_fire_mode", mode);
    }

    icon = CG_AmmoHud_Icon(weapon);
    if (strcmp(last_icon, icon)) {
        Q_strncpyz(last_icon, icon, sizeof(last_icon));
        cgi.Cvar_Set("cg_weap_icon", icon);
    }
}
