"""Gemini orqali matnda narkotik kontentni aniqlash."""
import asyncio
import json
import logging

from app.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

_MODEL = "gemini-2.5-flash"
_client = None

_SYSTEM_PROMPT = """Sen narkotik kontentni aniqlovchi moderator'sen. Sizga raqamlangan matnlar beriladi.
Har bir matnda narkotik moddalar bilan bog'liq so'z, ibora, yashirin belgi yoki tarqatish/sotish belgilari bor-yo'qligini aniqla.

Narkotik moddalar:
- Klassik: marixuana, hashish, kokain, geroin, opium, morfin, MDMA/ekstazi, amfetamin, metamfetamin, LSD, ketamin, mefedron, "tuz/soli"
- Tibbiy preparatlar suiiste'mol kontekstida: tramadol, lirika (pregabalin), kodein, sirop
- Ko'cha jaranglari (o'zbek, rus, ingliz): "dur", "plan", "boshka", "qoq", "stuff", "косяк", "трава", "марка", "соль", "скорость", "винт", "герыч", "фен", "мука", "weed", "blunt", "shrooms"
- Tarqatish belgilari: "tashlab ketdim", "klad", "joy", "koordinata", "ko'p miqdorda mavjud", narx + tana qismi, telegram bot link bilan "buyurtma"

YOLG'ON POZITIVDAN saqlan:
- "Aspirin tabletkasi", "kasalxona dori-darmoni" — narkotik EMAS
- "Marafon yugurish" — narkotik EMAS
- "Plan tuzdik" (oddiy reja) — narkotik EMAS
- Kontekstdan kelib chiqib qaror qil

JSON formatda javob ber. Boshqa hech narsa yozma:
{
  "results": [
    {
      "index": 1,
      "is_drug_related": true yoki false,
      "confidence": "low" yoki "medium" yoki "high",
      "reason": "qisqa sabab, faqat true bo'lganda",
      "flagged_words": ["topilgan so'zlar"]
    }
  ]
}"""


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not GEMINI_API_KEY:
        return None
    try:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
        return _client
    except Exception as e:
        logger.exception("Gemini client init failed: %s", e)
        return None


def _empty_result(idx: int) -> dict:
    return {"index": idx, "is_drug_related": False, "confidence": "low",
            "reason": "", "flagged_words": []}


def _analyze_sync(texts: list[str]) -> list[dict]:
    client = _get_client()
    if not client:
        logger.warning("Gemini client mavjud emas (GEMINI_API_KEY o'rnatilmaganmi?)")
        return [_empty_result(i + 1) for i in range(len(texts))]

    numbered = "\n\n---\n\n".join(
        f"#{i + 1}:\n{(t or '').strip()[:3000]}" for i, t in enumerate(texts)
    )
    full_prompt = f"{_SYSTEM_PROMPT}\n\nMatnlar:\n{numbered}"

    try:
        from google.genai import types
        response = client.models.generate_content(
            model=_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        data = json.loads(response.text)
        results = data.get("results", [])
        # Indekslarga ko'ra to'ldirish (ba'zilari yo'qolib qolishi mumkin)
        by_index = {r.get("index"): r for r in results if isinstance(r, dict)}
        return [by_index.get(i + 1, _empty_result(i + 1)) for i in range(len(texts))]
    except Exception as e:
        logger.exception("Gemini analyze xatolik: %s", e)
        return [_empty_result(i + 1) for i in range(len(texts))]


async def analyze(texts: list[str]) -> list[dict]:
    """Matnlar ro'yxatini analiz qiladi. Har biri uchun bitta natija."""
    if not texts:
        return []
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _analyze_sync, texts)
