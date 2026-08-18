/* cgame_waiting_hud.c
 * Top-center "WAITING FOR PLAYERS" until 2 non-spectator clients are connected.
 */

#include "cg_local.h"

#define WAITING_NEEDED 2
#define WAITING_COUNT_MAX 16

static int last_n = -1;

static int CG_WaitingHud_NumPlayers(void)
{
    int         i;
    int         n;
    int         team;
    const char *cs;
    const char *name;

    n = 0;
    for (i = 0; i < MAX_CLIENTS; i++) {
        cs = CG_ConfigString(CS_PLAYERS + i);
        if (!cs || !cs[0]) {
            continue;
        }

        name = Info_ValueForKey(cs, "name");
        if (!name || !name[0]) {
            continue;
        }

        team = atoi(Info_ValueForKey(cs, "team"));
        if (team == TEAM_SPECTATOR) {
            continue;
        }

        n++;
    }

    return n;
}

static void CG_WaitingHud_Hide(void)
{
    cgi.Cmd_Execute(EXEC_NOW, "ui_removehud hud_waiting\n");
    cgi.UI_HideMenu("hud_waiting", qtrue);
}

static void CG_WaitingHud_Show(void)
{
    cgi.Cmd_Execute(EXEC_NOW, "ui_addhud hud_waiting\n");
}

void CG_WaitingHud_Init(void)
{
    cgi.Cvar_Get("cg_waiting_count_img", "textures/hud/waiting_count_1", 0);
    cgi.Cvar_Set("cg_waiting_count_img", "textures/hud/waiting_count_1");
    last_n = -1;
    CG_WaitingHud_Hide();
}

void CG_WaitingHud_Frame(void)
{
    int      n;
    qboolean show;
    char     buf[64];

    if (!cg.snap || !cg_hud->integer || cgs.gametype == GT_SINGLE_PLAYER) {
        CG_WaitingHud_Hide();
        return;
    }

    n    = CG_WaitingHud_NumPlayers();
    show = (n < WAITING_NEEDED);

    if (n != last_n) {
        last_n = n;
        if (n < 0) {
            n = 0;
        }
        if (n > WAITING_COUNT_MAX) {
            n = WAITING_COUNT_MAX;
        }
        Com_sprintf(buf, sizeof(buf), "textures/hud/waiting_count_%i", n);
        cgi.Cvar_Set("cg_waiting_count_img", buf);
    }

    if (show) {
        CG_WaitingHud_Show();
    } else {
        CG_WaitingHud_Hide();
    }
}
