#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  NURIDDIN BUILDING HR-BOT — DEPLOY
#
#  Foydalanish (cPanel Terminal):
#      cd ~/nurli_diyor_bot && ./deploy.sh
#
#  Bajaradi: zaxira -> kod yangilash -> paketlar -> migratsiyalar -> restart
#  Biror qadam xato bersa TO'XTAYDI (yarim holatda qolmaydi).
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

APP_DIR="/home/bulutlii/nurli_diyor_bot"
VENV="/home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate"
KEEP_BACKUPS=10

cd "$APP_DIR"

step() { printf '\n\033[1;36m▶ %s\033[0m\n' "$1"; }
ok()   { printf '\033[1;32m  ✔ %s\033[0m\n' "$1"; }
warn() { printf '\033[1;33m  ! %s\033[0m\n' "$1"; }
die()  { printf '\n\033[1;31m✘ XATO: %s\033[0m\n' "$1" >&2; exit 1; }

# ── 1. Zaxira ──────────────────────────────────────────────────────
step "Bazadan zaxira nusxa"
if [ -f bot.db ]; then
    BACKUP="bot.db.backup_$(date +%F_%H%M%S)"
    cp bot.db "$BACKUP" || die "zaxira olinmadi"
    ok "$BACKUP ($(du -h "$BACKUP" | cut -f1))"
    # Eski zaxiralarni tozalash (oxirgi $KEEP_BACKUPS tasi qoladi)
    ls -1t bot.db.backup_* 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm -f
else
    warn "bot.db topilmadi — zaxira o'tkazildi"
fi

# ── 2. Kodni yangilash ─────────────────────────────────────────────
step "Kodni yangilash (git pull)"
BEFORE=$(git rev-parse --short HEAD)
git pull origin main || die "git pull ishlamadi"
AFTER=$(git rev-parse --short HEAD)
if [ "$BEFORE" = "$AFTER" ]; then
    ok "Yangilanish yo'q ($AFTER)"
else
    ok "$BEFORE -> $AFTER"
    git log --oneline "$BEFORE..$AFTER" | sed 's/^/    /'
fi

# ── 3. Virtualenv ──────────────────────────────────────────────────
step "Virtualenv"
[ -f "$VENV" ] || die "virtualenv topilmadi: $VENV"
# shellcheck disable=SC1090
source "$VENV"
ok "$(python --version 2>&1)"

# ── 4. Paketlar ────────────────────────────────────────────────────
step "Paketlarni tekshirish"
if ! python -c "import anthropic" 2>/dev/null; then
    pip install -q anthropic && ok "anthropic o'rnatildi"
else
    ok "Barcha paket joyida"
fi

# ── 5. Migratsiyalar ───────────────────────────────────────────────
step "Migratsiyalar"
for m in migrate_v2 migrate_v3 migrate_v4 migrate_v5 migrate_v6; do
    [ -f "$m.py" ] || continue
    out=$(python "$m.py" 2>&1 | grep -Ev "INFO sqlalchemy|^\s*(SELECT|FROM|WHERE|UPDATE|INSERT|\[|\()" || true)
    if echo "$out" | grep -q "tugadi"; then
        changed=$(echo "$out" | grep -c "^OK:" || true)
        if [ "$changed" -gt 0 ]; then
            ok "$m — $changed ta o'zgarish"
            echo "$out" | grep "^OK:" | sed 's/^/    /'
        else
            ok "$m — o'zgarishsiz"
        fi
    else
        echo "$out" | tail -5
        die "$m ishlamadi"
    fi
done

# ── 6. Restart ─────────────────────────────────────────────────────
step "Botni qayta ishga tushirish"
mkdir -p tmp && touch tmp/restart.txt
ok "Passenger restart signali yuborildi"

# ── 7. Tekshiruv ───────────────────────────────────────────────────
step "Tekshiruv"
python - <<'PY' 2>/dev/null || true
import asyncio
from app.database.connect import engine
import app.database.crud as crud

async def main():
    vs = await crud.get_all_vacancies()
    apps = await crud.get_applications()
    no_q = 0
    for v in vs:
        if await crud.count_vacancy_questions(v.id) == 0:
            no_q += 1
    print(f"  Vakansiyalar: {len(vs)} ta ({no_q} tasida savol yo'q)")
    print(f"  Arizalar: {len(apps)} ta")
    await engine.dispose()

asyncio.run(main())
PY

printf '\n\033[1;32m═══ ✅ DEPLOY TUGADI ═══\033[0m\n'
printf 'Botni Telegramda sinab ko\047ring: /admin\n\n'
