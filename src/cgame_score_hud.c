/* cgame_score_hud.c
 * Digit shaders for Allies (stat 21) / Axis (stat 25) and cg_round_time.
 */

#include "cg_local.h"

static const char *const digit_shaders[10] = {
    "textures/hud/digit_0", "textures/hud/digit_1", "textures/hud/digit_2", "textures/hud/digit_3",
    "textures/hud/digit_4", "textures/hud/digit_5", "textures/hud/digit_6", "textures/hud/digit_7",
    "textures/hud/digit_8", "textures/hud/digit_9",
};

static const char *digit_empty = "textures/hud/digit_empty";

static int  last_allies = -1;
static int  last_axis   = -1;
static char last_time[16];

static void CG_ScoreHud_SetDigits(const char *left, const char *mid, const char *right, int value, qboolean leftAlign)
{
    int hundreds;
    int tens;
    int ones;

    if (value < 0) {
        value = 0;
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

void CG_ScoreHud_Init(void)
{
    cgi.Cvar_Get("cg_score_a2", "textures/hud/digit_0", 0);
    cgi.Cvar_Get("cg_score_a1", "textures/hud/digit_empty", 0);
    cgi.Cvar_Get("cg_score_a0", "textures/hud/digit_empty", 0);
    cgi.Cvar_Get("cg_score_x2", "textures/hud/digit_empty", 0);
    cgi.Cvar_Get("cg_score_x1", "textures/hud/digit_empty", 0);
    cgi.Cvar_Get("cg_score_x0", "textures/hud/digit_0", 0);
    cgi.Cvar_Get("cg_round_time", "0:00", 0);
    CG_ScoreHud_SetDigits("cg_score_a2", "cg_score_a1", "cg_score_a0", 0, qtrue);
    CG_ScoreHud_SetDigits("cg_score_x2", "cg_score_x1", "cg_score_x0", 0, qfalse);
    cgi.Cvar_Set("cg_round_time", "0:00");
    last_allies  = -1;
    last_axis    = -1;
    last_time[0] = 0;
}

void CG_ScoreHud_Frame(void)
{
    int         allies;
    int         axis;
    const char *timestr;
    char        buf[16];

    if (!cg.snap) {
        return;
    }

    allies = cg.snap->ps.stats[STAT_KILLS];
    axis   = cg.snap->ps.stats[STAT_HIGHEST_SCORE];
    if (allies < 0) {
        allies = 0;
    }
    if (axis < 0) {
        axis = 0;
    }

    if (allies != last_allies) {
        last_allies = allies;
        CG_ScoreHud_SetDigits("cg_score_a2", "cg_score_a1", "cg_score_a0", allies, qtrue);
    }
    if (axis != last_axis) {
        last_axis = axis;
        CG_ScoreHud_SetDigits("cg_score_x2", "cg_score_x1", "cg_score_x0", axis, qfalse);
    }

    timestr = "0:00";
    if (cg.matchStartTime == -1) {
        timestr = "--:--";
    } else if (cgs.gametype != GT_LIBERATION && cgs.matchEndTime) {
        int sec = (cgs.matchEndTime - cg.time) / 1000;
        if (sec < 0) {
            sec = 0;
        }
        Com_sprintf(buf, sizeof(buf), "%d:%02d", sec / 60, sec % 60);
        timestr = buf;
    }

    if (strcmp(last_time, timestr)) {
        Q_strncpyz(last_time, timestr, sizeof(last_time));
        cgi.Cvar_Set("cg_round_time", timestr);
    }
}
