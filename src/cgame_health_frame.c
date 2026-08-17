/* cgame_health_frame.c
 * Sets cg_health_frame + digit shaders from current HP for hud_health.urc
 * Frames: textures/hud/health_0 .. health_100 in steps of 5.
 */

#include "cg_local.h"

static int last_bucket = -1;
static int last_health = -1;

static const char *const health_frames[21] = {
    "textures/hud/health_0",   "textures/hud/health_5",   "textures/hud/health_10",
    "textures/hud/health_15",  "textures/hud/health_20",  "textures/hud/health_25",
    "textures/hud/health_30",  "textures/hud/health_35",  "textures/hud/health_40",
    "textures/hud/health_45",  "textures/hud/health_50",  "textures/hud/health_55",
    "textures/hud/health_60",  "textures/hud/health_65",  "textures/hud/health_70",
    "textures/hud/health_75",  "textures/hud/health_80",  "textures/hud/health_85",
    "textures/hud/health_90",  "textures/hud/health_95",  "textures/hud/health_100",
};

static const char *const digit_shaders[10] = {
    "textures/hud/digit_0", "textures/hud/digit_1", "textures/hud/digit_2", "textures/hud/digit_3",
    "textures/hud/digit_4", "textures/hud/digit_5", "textures/hud/digit_6", "textures/hud/digit_7",
    "textures/hud/digit_8", "textures/hud/digit_9",
};

static const char *digit_empty = "textures/hud/digit_empty";

static int CG_HealthFrame_Bucket(int health)
{
    if (health < 0) {
        health = 0;
    }
    if (health > 100) {
        health = 100;
    }
    return (health / 5) * 5;
}

static void CG_HealthFrame_SetDigits(int health)
{
    int hundreds;
    int tens;
    int ones;

    if (health < 0) {
        health = 0;
    }
    if (health > 100) {
        health = 100;
    }

    hundreds = health / 100;
    tens     = (health / 10) % 10;
    ones     = health % 10;

    cgi.Cvar_Set("cg_health_d2", hundreds ? digit_shaders[hundreds] : digit_empty);
    cgi.Cvar_Set("cg_health_d1", (health >= 10) ? digit_shaders[tens] : digit_empty);
    cgi.Cvar_Set("cg_health_d0", digit_shaders[ones]);
}

void CG_HealthFrame_Init(void)
{
    cgi.Cvar_Get("cg_health_frame", "textures/hud/health_100", 0);
    cgi.Cvar_Get("cg_health_d2", "textures/hud/digit_1", 0);
    cgi.Cvar_Get("cg_health_d1", "textures/hud/digit_0", 0);
    cgi.Cvar_Get("cg_health_d0", "textures/hud/digit_0", 0);
    cgi.Cvar_Set("cg_health_frame", "textures/hud/health_100");
    CG_HealthFrame_SetDigits(100);
    last_bucket = -1;
    last_health = -1;
}

void CG_HealthFrame_Frame(void)
{
    int health;
    int bucket;
    int idx;

    if (!cg.snap) {
        return;
    }

    /* STAT_HEALTH is already 0..100 percent of max HP */
    health = cg.snap->ps.stats[STAT_HEALTH];
    if (health < 0) {
        health = 0;
    }
    if (health > 100) {
        health = 100;
    }

    if (health != last_health) {
        last_health = health;
        CG_HealthFrame_SetDigits(health);
    }

    bucket = CG_HealthFrame_Bucket(health);
    if (bucket == last_bucket) {
        return;
    }
    last_bucket = bucket;

    idx = bucket / 5;
    if (idx < 0) {
        idx = 0;
    }
    if (idx > 20) {
        idx = 20;
    }
    cgi.Cvar_Set("cg_health_frame", health_frames[idx]);
}
