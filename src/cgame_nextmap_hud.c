/* cgame_nextmap_hud.c
 * Next-map panel under the compass. Uses sv_maplist from CS_SERVERINFO.
 */

#include "cg_local.h"

typedef struct {
    const char *id;
    const char *name_shader;
    const char *shot_shader;
} nextmap_art_t;

static const nextmap_art_t nextmap_art[] = {
    {"mohdm1", "textures/hud/nextmap_name_mohdm1", "textures/hud/nextmap_shot_mohdm1"},
    {"mohdm2", "textures/hud/nextmap_name_mohdm2", "textures/hud/nextmap_shot_mohdm2"},
    {"mohdm3", "textures/hud/nextmap_name_mohdm3", "textures/hud/nextmap_shot_mohdm3"},
    {"mohdm4", "textures/hud/nextmap_name_mohdm4", "textures/hud/nextmap_shot_mohdm4"},
    {"mohdm5", "textures/hud/nextmap_name_mohdm5", "textures/hud/nextmap_shot_mohdm5"},
    {"mohdm6", "textures/hud/nextmap_name_mohdm6", "textures/hud/nextmap_shot_mohdm6"},
    {"mohdm7", "textures/hud/nextmap_name_mohdm7", "textures/hud/nextmap_shot_mohdm7"},
    {"objdm1", "textures/hud/nextmap_name_objdm1", "textures/hud/nextmap_shot_objdm1"},
    {"objdm2", "textures/hud/nextmap_name_objdm2", "textures/hud/nextmap_shot_objdm2"},
    {"objdm3", "textures/hud/nextmap_name_objdm3", "textures/hud/nextmap_shot_objdm3"},
    {"objdm4", "textures/hud/nextmap_name_objdm4", "textures/hud/nextmap_shot_objdm4"},
    {"objdm5", "textures/hud/nextmap_name_objdm5", "textures/hud/nextmap_shot_objdm5"},
};

static const char *name_unknown = "textures/hud/nextmap_name_unknown";
static const char *shot_empty   = "textures/hud/nextmap_shot_empty";

static char     last_key[MAX_QPATH];
static qboolean last_shown;

static void CG_NextMapHud_Strip(const char *in, char *out, int outSize)
{
    const char *slash;
    const char *dollar;
    int         len;

    if (!in) {
        out[0] = 0;
        return;
    }

    if (!Q_stricmpn(in, "maps/", 5)) {
        in += 5;
    }

    slash = strrchr(in, '/');
    if (slash) {
        in = slash + 1;
    }

    dollar = strchr(in, '$');
    if (dollar) {
        len = (int)(dollar - in);
    } else {
        len = (int)strlen(in);
    }

    if (len >= outSize) {
        len = outSize - 1;
    }
    memcpy(out, in, len);
    out[len] = 0;
}

static const nextmap_art_t *CG_NextMapHud_Art(const char *id)
{
    int i;

    for (i = 0; i < (int)ARRAY_LEN(nextmap_art); i++) {
        if (!Q_stricmp(id, nextmap_art[i].id)) {
            return &nextmap_art[i];
        }
    }
    return NULL;
}

static void CG_NextMapHud_Pick(const char *current, const char *maplist, const char *voted, char *out, int outSize)
{
    char        buf[1024];
    char        cur[MAX_QPATH];
    char        tok[MAX_QPATH];
    char        first[MAX_QPATH];
    const char *p;
    const char *end;
    int         len;
    qboolean    found;

    out[0] = 0;
    CG_NextMapHud_Strip(current, cur, sizeof(cur));

    if (voted && voted[0] && Q_stricmpn(voted, "vstr ", 5) && Q_stricmpn(voted, "restart", 7)) {
        CG_NextMapHud_Strip(voted, out, outSize);
        if (out[0]) {
            return;
        }
    }

    if (!maplist || !maplist[0]) {
        Q_strncpyz(out, cur, outSize);
        return;
    }

    Q_strncpyz(buf, maplist, sizeof(buf));
    first[0] = 0;
    found    = qfalse;
    p        = buf;

    while (*p) {
        while (*p == ' ' || *p == ',' || *p == '\n' || *p == '\r' || *p == '\t') {
            p++;
        }
        if (!*p) {
            break;
        }
        end = p;
        while (*end && *end != ' ' && *end != ',' && *end != '\n' && *end != '\r' && *end != '\t') {
            end++;
        }
        len = (int)(end - p);
        if (len >= (int)sizeof(tok)) {
            len = (int)sizeof(tok) - 1;
        }
        memcpy(tok, p, len);
        tok[len] = 0;
        p        = end;

        CG_NextMapHud_Strip(tok, tok, sizeof(tok));
        if (!tok[0]) {
            continue;
        }
        if (!first[0]) {
            Q_strncpyz(first, tok, sizeof(first));
        }
        if (found) {
            Q_strncpyz(out, tok, outSize);
            return;
        }
        if (!Q_stricmp(tok, cur)) {
            found = qtrue;
        }
    }

    if (first[0]) {
        Q_strncpyz(out, first, outSize);
    } else {
        Q_strncpyz(out, cur, outSize);
    }
}

void CG_NextMapHud_Init(void)
{
    cgi.Cvar_Get("cg_nextmap_name_img", "textures/hud/nextmap_name_mohdm7", 0);
    cgi.Cvar_Get("cg_nextmap_shot_img", "textures/hud/nextmap_shot_mohdm7", 0);
    cgi.Cvar_Get("nextmap", "", 0);
    last_key[0]  = 0;
    last_shown   = qfalse;
    cgi.Cvar_Set("cg_nextmap_name_img", name_unknown);
    cgi.Cvar_Set("cg_nextmap_shot_img", shot_empty);
}

void CG_NextMapHud_Frame(void)
{
    const char         *info;
    const char         *maplist;
    const char         *current;
    const char         *voted;
    const nextmap_art_t *art;
    char                next[MAX_QPATH];
    qboolean            show;

    if (!cg.snap || !cg_hud->integer || cgs.gametype == GT_SINGLE_PLAYER) {
        if (last_shown) {
            cgi.Cmd_Execute(EXEC_NOW, "ui_removehud hud_nextmap\n");
            cgi.UI_HideMenu("hud_nextmap", qtrue);
            last_shown = qfalse;
        }
        return;
    }

    show = qtrue;
    if (show) {
        cgi.Cmd_Execute(EXEC_NOW, "ui_addhud hud_nextmap\n");
        last_shown = qtrue;
    }

    info    = CG_ConfigString(CS_SERVERINFO);
    current = Info_ValueForKey(info, "mapname");
    maplist = Info_ValueForKey(info, "sv_maplist");
    voted   = cgi.Cvar_Get("nextmap", "", 0)->string;
    if (!voted) {
        voted = "";
    }

    CG_NextMapHud_Pick(current, maplist, voted, next, sizeof(next));
    if (!strcmp(last_key, next)) {
        return;
    }
    Q_strncpyz(last_key, next, sizeof(last_key));

    art = CG_NextMapHud_Art(next);
    if (art) {
        cgi.Cvar_Set("cg_nextmap_name_img", art->name_shader);
        cgi.Cvar_Set("cg_nextmap_shot_img", art->shot_shader);
    } else {
        cgi.Cvar_Set("cg_nextmap_name_img", name_unknown);
        cgi.Cvar_Set("cg_nextmap_shot_img", shot_empty);
    }
}
