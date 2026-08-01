# -*- coding: utf-8 -*-
"""
AI orqali vakansiya savollarini yaratish — «NURIDDIN BUILDING» HR-bot.

Admin yangi vakansiya qo'shganda (masalan «Elektrik», «Haydovchi») tayyor
shablon bo'lmasa, Claude shu lavozim uchun kompaniya formatida savol to'plami
yaratadi: 3 ta test (0/1/3) + 2 ta yozma + 1 ta majburiy video-savol.

Admin natijani ko'radi, tasdiqlaydi yoki qayta yaratadi. Har bir savolni
keyin qo'lda ham tahrirlash mumkin.
"""
import json
import logging

from app.config import ANTHROPIC_API_KEY, AI_MODEL

log = logging.getLogger(__name__)


GENERATOR_PROMPT = """Sen — «Nuriddin Building» qurilish kompaniyasining HR metodologisisan.
Vazifang: berilgan lavozim uchun nomzodlarni saralash savollarini yaratish.

═══ NIMA YARATASAN ═══
Aynan quyidagilar, boshqa hech narsa:
• 3 ta TEST savoli — har birida 3 ta variant (3 ball, 1 ball, 0 ball)
• 2 ta YOZMA savol — nomzod matn yozadi, keyin 0-3 ball beriladi
• 1 ta VIDEO savoli — nomzod 30-60 soniya video javob beradi

═══ TEST SAVOLLARI QOIDALARI (eng muhim qism) ═══

1) HAR SAVOL — REAL ISH VAZIYATI, ta'rif so'ramaydi.
   YAXSHI: "Obyektga zudlik bilan sement kerak, doimiy yetkazib beruvchida
   yo'q; boshqasida bor, lekin 30% qimmat va sifati noma'lum. Nima qilasiz?"
   YOMON: "Ta'minotchining vazifasi nima?"
   Vaziyatda aniq tafsilot bo'lsin: raqam, muddat, bosim o'tkazayotgan tomon,
   yoki qarama-qarshi talab. Nomzod tanlov qilishga majbur bo'lsin.

2) NOTO'G'RI VARIANTLAR HAM ISHONARLI BO'LSIN.
   Bu eng muhim qoida. 1 va 0 ballik variantlar "ahmoqona" ko'rinmasin —
   ular amalda ko'p uchraydigan, tushunarli, lekin kamroq to'g'ri yo'llar
   bo'lsin. Faqat sohani chinakam biladigan odam 3 ballikni ajrata olsin.
   • 3 ball — kasbiy jihatdan eng to'g'ri: sababni aniqlaydi, tizimli
     yondashadi, xavfsizlik/sifat/qonunni buzmaydi
   • 1 ball — qisman to'g'ri: ko'p ishlatiladigan tezkor yo'l, natija beradi
     lekin sababni yechmaydi yoki xatarni qoldiradi
   • 0 ball — yaroqsiz: mas'uliyatdan qochish, xavfsizlik/qoidani buzish,
     yoki muammoni e'tiborsiz qoldirish

3) JAVOB UZUNLIGI BALLNI OSHKOR QILMASIN.
   Bu qat'iy talab. Agar 3 ballik javob doim eng uzun bo'lsa, nomzod
   mazmunni o'qimay eng uzunini tanlaydi va test ma'nosini yo'qotadi.
   Uch variant uzunligi TAXMINAN TENG bo'lsin (farq 30% dan oshmasin).
   Kerak bo'lsa 3 ballikni qisqartir yoki 1/0 ballikni to'ldir.

4) SOHA TILIDA YOZ. Lavozimga xos atama, hujjat, asbob, normani ishlat
   (masalan qurilishda: ShNQ, dalolatnoma, smeta, brakovka; sotuvda: CRM,
   konversiya, lid). Lekin atamani tushuntirma — biladigan odam tushunsin.

5) BIRINCHI VARIANT DOIM 3 BALL bo'lsin (bot o'zi aralashtirib chiqaradi).

═══ YOZMA SAVOLLAR ═══
• 1-savol — FIKR VA MANTIQ: nomzod qanday ishlashini qadam-baqadam
  tushuntirsin ("...ni qanday boshqarasiz? Qadam-baqadam yozing")
• 2-savol — quyidagilardan biri, lavozimga qaysi mosligiga qarab:
  - AI AMALIY: shu ishda AIdan qanday foydalanishi (ofis/raqamli rollarga)
  - MOTIVATSIYA: aniq shaxsiy tajriba, raqam bilan (ishchi/jismoniy rollarga)
Savol aniq bo'lsin, "o'zingiz haqingizda gapiring" kabi umumiy bo'lmasin.

═══ VIDEO SAVOLI ═══
Nomzodning shu lavozimdagi REAL tajribasini yoki ko'nikmasini ochadigan bitta
savol. 30-60 soniyada javob berish mumkin bo'lsin.
DIQQAT: "Avval o'zingizni tanishtiring" degan qismni YOZMA — botning o'zi
uni qo'shadi. Faqat savolning o'zini yoz.
Front-office rollarda (sotuv, operator) ko'nikmani ko'rsatishni so'rash mumkin
("Meni 30 soniyada shu mahsulotni olishga ko'ndiring").

═══ TIL ═══
Hammasi O'ZBEK TILIDA (lotin). Sodda, tushunarli, rasmiy uslub.

═══ CHIQISH ═══
Faqat so'ralgan JSON. Har savol matni savol belgisi bilan tugasin."""


QUESTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "lavozim": {"type": "string"},
        "test": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "savol": {"type": "string"},
                    "javob_3": {"type": "string"},
                    "javob_1": {"type": "string"},
                    "javob_0": {"type": "string"},
                },
                "required": ["savol", "javob_3", "javob_1", "javob_0"],
                "additionalProperties": False,
            },
        },
        "yozma": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "savol": {"type": "string"},
                    "turi": {"type": "string", "enum": ["mantiq", "ai", "motivatsiya"]},
                },
                "required": ["savol", "turi"],
                "additionalProperties": False,
            },
        },
        "video": {"type": "string"},
    },
    "required": ["lavozim", "test", "yozma", "video"],
    "additionalProperties": False,
}


def is_enabled() -> bool:
    if not ANTHROPIC_API_KEY:
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except ImportError:
        return False


async def generate_questions(title: str, requirements: str | None = None) -> dict | None:
    """Lavozim uchun savol to'plamini yaratadi.

    Qaytaradi QUESTION_BANK formatidagi dict:
      {"title", "test": [{"text","options":[{"text","score"}]}],
       "written": [{"text","rubric"}], "video": "..."}
    Xato bo'lsa None.
    """
    if not is_enabled():
        return None

    from app.ai_grader import _extract_json
    from app.question_bank import RUBRIC_LOGIC, RUBRIC_AI, RUBRIC_MOTIVATION

    req = f"\nLavozim talablari: {requirements}" if requirements else ""
    user = (
        f"Lavozim nomi: {title}{req}\n\n"
        f"Shu lavozim uchun qoidalar bo'yicha savol to'plamini yarat va JSON qaytar."
    )

    try:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY, timeout=90.0, max_retries=2)
        kwargs = dict(
            model=AI_MODEL,
            max_tokens=4000,
            system=GENERATOR_PROMPT,
            messages=[{"role": "user", "content": user}],
        )
        try:
            resp = await client.messages.create(
                **kwargs,
                output_config={"format": {"type": "json_schema", "schema": QUESTIONS_SCHEMA}},
            )
        except TypeError:
            resp = await client.messages.create(**kwargs)
        except Exception as e:
            if "output_config" in str(e) or "json_schema" in str(e):
                resp = await client.messages.create(**kwargs)
            else:
                raise

        if getattr(resp, "stop_reason", None) == "refusal":
            log.warning("Savol yaratish rad etildi")
            return None

        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        data = _extract_json(text)
    except Exception as e:
        log.warning("Savol yaratish xatosi: %s", e)
        return None

    if not data:
        return None

    # ── Natijani bank formatiga o'giramiz va tekshiramiz ──────────────
    rubrics = {"mantiq": RUBRIC_LOGIC, "ai": RUBRIC_AI, "motivatsiya": RUBRIC_MOTIVATION}
    tests = []
    for t in (data.get("test") or [])[:3]:
        q = (t.get("savol") or "").strip()
        o3 = (t.get("javob_3") or "").strip()
        o1 = (t.get("javob_1") or "").strip()
        o0 = (t.get("javob_0") or "").strip()
        if not (q and o3 and o1 and o0):
            continue
        tests.append({
            "text": q,
            "options": [
                {"text": o3, "score": 3},
                {"text": o1, "score": 1},
                {"text": o0, "score": 0},
            ],
        })

    written = []
    for w in (data.get("yozma") or [])[:2]:
        q = (w.get("savol") or "").strip()
        if not q:
            continue
        written.append({"text": q, "rubric": rubrics.get(w.get("turi"), RUBRIC_LOGIC)})

    video = (data.get("video") or "").strip()

    # To'liq bo'lmasa qaytarmaymiz — admin qayta urinadi
    if len(tests) != 3 or len(written) != 2 or not video:
        log.warning("Savol to'plami to'liq emas: test=%d yozma=%d video=%s",
                    len(tests), len(written), bool(video))
        return None

    return {"title": title, "test": tests, "written": written, "video": video}


def preview_text(data: dict) -> str:
    """Yaratilgan savollarni admin ko'rishi uchun matn (HTML)."""
    import html
    e = lambda s: html.escape(str(s or ""))
    LET = ["A", "B", "C"]
    out = [f"📋 <b>{e(data.get('title'))}</b> — savol to'plami\n"]

    out.append("🧠 <b>TEST SAVOLLARI</b> (nomzodga ballar ko'rinmaydi)")
    for i, t in enumerate(data["test"], start=1):
        out.append(f"\n<b>{i}.</b> {e(t['text'])}")
        for j, o in enumerate(t["options"]):
            out.append(f"  <b>{LET[j]})</b> {e(o['text'])} — <i>{o['score']} ball</i>")

    out.append("\n✍️ <b>YOZMA SAVOLLAR</b> (har biri 0-3 ball)")
    for i, w in enumerate(data["written"], start=1):
        out.append(f"\n<b>{i}.</b> {e(w['text'])}")

    out.append(f"\n🎥 <b>VIDEO-SAVOL</b> (0-4 ball)\n{e(data['video'])}")
    out.append("\n<i>Jami: test 9 + yozma 6 + video 4 = 19 ball</i>")
    return "\n".join(out)
