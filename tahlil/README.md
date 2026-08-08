# Tahlil arxivi

Bu papka — tahlil tizimining doimiy xotirasi. Chat seansi tugasa ham bilim
shu yerda qoladi.

## Tuzilishi

```
tahlil/
├── INDEX.md      71 band bo'yicha yagona holat jadvali (kim qayerda)
├── README.md     shu fayl
└── <BAND>.md     har bir band tahlili, masalan S1.md, C2.md
```

## Tahlil fayli shabloni (`<BAND>.md`)

Tahlilchi har tahlilni aynan shu tuzilishda saqlaydi:

```markdown
---
band: S1
sarlavha: <banddagi sarlavha>
sana: <YYYY-MM-DD>
tahlilchi_holati: 📝 tahlil tayyor
ildiz_turi: <1–6>
tanlangan_variant: <A/B/C>
hukm: —
---

# S1 — <sarlavha>

## A. Dalil
... (AI_TAHLIL_PROTOKOLI.md 5-QISM shabloni bo'yicha A→L to'liq)

---
# TEKSHIRUV TARIXI
(bu bo'limga FAQAT tekshiruvchi yozadi; har hukm alohida qo'shiladi,
eskisi o'chirilmaydi)

## Tekshiruv #1 — <sana>
| T1..T8 jadvali |
HUKM: ✅ QABUL / ❌ QAYTARILDI
Topshiriq: ...
```

## Qoidalar

1. **Tahlilchi** faylni yaratadi/yangilaydi, lekin `TEKSHIRUV TARIXI`
   bo'limiga tegmaydi.
2. **Tekshiruvchi** faqat `TEKSHIRUV TARIXI` ga qo'shadi va frontmatterdagi
   `hukm:` qatorini yangilaydi — tahlil matnini o'zgartirmaydi.
3. Har o'zgarishdan keyin tegishli agent **INDEX.md dagi o'z qatorini** ham
   yangilaydi (Tahlil / Hukm / Ildiz / Variant / Fayl ustunlari).
4. Qaytarilgan tahlil tuzatilganda eski matn ustiga yoziladi (tarix git'da
   qoladi), lekin tekshiruv tarixi saqlanadi.
5. Fayl nomi — band ID aynan o'zi: `S1.md`, `FU12.md`.
