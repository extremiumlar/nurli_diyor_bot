# TAHLIL INDEKSI
### Nuriddin Building HR-bot — 71 band bo'yicha tahlil jarayonining yagona holat jadvali

> **Bu fayl — tahlil tizimining xotirasi.** Har seans boshida tahlilchi ham,
> tekshiruvchi ham SHU faylni o'qiydi. Har tahlil/hukmdan keyin tegishli
> qator YANGILANADI (faqat o'z qatoringni o'zgartir, boshqasiga tegma).

## Ustunlar qoidasi

| Ustun | Kim yozadi | Qiymatlar |
|---|---|---|
| Kod holati | faqat foydalanuvchi/dasturchi (yechim joriy etilganda) | ✅ tuzatilgan / 🟡 qisman / ❌ ochiq |
| Tahlil | tahlilchi | ⬜ boshlanmagan → 📝 tahlil tayyor → ♻️ qaytarilgan (tuzatilmoqda) |
| Hukm | faqat tekshiruvchi | — / ✅ QABUL / ❌ QAYTARILDI (n-marta) |
| Ildiz | tahlilchi (hukm ✅ bo'lgach yakuniy) | R1, R2... — ILDIZLAR.md dagi yozuv raqami |
| Variant | tahlilchi | A / B / C — G-bosqichda tanlangani |
| Fayl | tahlilchi | tahlil/<BAND>.md havolasi |

**Tartib qoidasi:** navbatdagi bandni tanlashda ❌ ochiq + Kritik bo'lganlar
birinchi. Tavsiya etilgan boshlanish tartibi: S1 → S2 → S4 → D1 → C1 → C3 → C4 → C5.


## 1. Xavfsizlik

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| S1 | Webhook himoyasiz — istalgan odam super_admin bo'la oladi | Kritik | ❌ ochiq | ⬜ | — | — | — | — |
| S2 | 5 ta handler rol tekshirmaydi — CV/rasm/PII sizadi | Kritik | ❌ ochiq | ⬜ | — | — | — | — |
| S3 | HTML-injection — nomzod ismi xabarni 'o'ldiradi' | Kritik | 🟡 qisman | ⬜ | — | — | — | — |
| S4 | Postgres paroli ochiq holda git'da | Kritik | ❌ ochiq | ⬜ | — | — | — | — |

## 2. Ma'lumot yo'qotish

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| D1 | Vakansiya o'chirish — arizalarni qaytarib bo'lmas o'chiradi | Kritik | ❌ ochiq | ⬜ | — | — | — | — |
| D2 | 'in_progress' qulfi — nomzod butunlay yo'qoladi | Kritik | ✅ tuzatilgan | ⬜ | — | — | — | — |
| D3 | Migratsiya eski arizalarni 'in_progress' qildi | Yuqori | ✅ tuzatilgan | ⬜ | — | — | — | — |

## 3. Concurrency

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| C1 | Webhook retry dedup yo'q — e'lon 2-3 marta ketadi | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| C2 | Test tugmasini 2 marta bosish -> ball 9 dan oshadi | Yuqori | ✅ tuzatilgan | 📝 | ✅ QABUL | R1 | C | [C2.md](C2.md) |
| C3 | FSM update_data atomik emas — lost update | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| C4 | SQLite FSM'da WAL/busy_timeout yo'q — 'database is locked' | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| C5 | recompute_scores alohida tranzaksiya — HR ballari yo'qoladi | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |

## 4. Nomzod oqimi buglari

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| N1 | Eski FSM vacancy_id tozalanmaydi — noto'g'ri vakansiyaga ariza | Yuqori | ✅ tuzatilgan | ⬜ | — | — | — | — |
| N2 | Matn bo'lmagan input (stiker/rasm) oqimni crash qiladi | Yuqori | ✅ tuzatilgan | ⬜ | — | — | — | — |
| N3 | Yopilgan vakansiyaga ariza topshirib bo'ladi | Yuqori | ✅ tuzatilgan | ⬜ | — | — | — | — |
| N4 | Telefon raqami umuman tekshirilmaydi | Yuqori | ✅ tuzatilgan | ⬜ | — | — | — | — |
| N5 | Ko'p xabarli yozma javob noto'g'ri savolga yoziladi | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| N6 | 'stage' ustuni hech qachon stage2/3 bo'lmaydi — resume imkonsiz | O'rta | ✅ tuzatilgan | ⬜ | — | — | — | — |

## 5. HR panel

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| H1 | Rad etish tasdiqsiz va qaytarib bo'lmaydi | O'rta | ✅ tuzatilgan | ⬜ | — | — | — | — |
| H2 | Yangi nomzod xabarida harakat tugmasi yo'q | O'rta | ✅ tuzatilgan | ⬜ | — | — | — | — |
| H3 | 'Arizalar' va 'Saralash' — ikkita ajralgan dunyo | O'rta | 🟡 qisman | ⬜ | — | — | — | — |
| H4 | Status bo'yicha filtr yo'q | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| H5 | 'Rad etilganlar zaxirasi' va'da qilingan, lekin yo'q | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| H6 | Excel eksportda saralash natijasi yo'q | O'rta | ✅ tuzatilgan | ⬜ | — | — | — | — |
| H7 | Vaqtlar UTC/naive — nomuvofiq | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| H8 | Guruh kartochkasi harakatsiz | O'rta | ✅ tuzatilgan | ⬜ | — | — | — | — |
| H9 | Uzun yozma javoblar kartochkani ochilmas qiladi | O'rta | ✅ tuzatilgan | ⬜ | — | — | — | — |
| H10 | Dublikat vakansiyalar | O'rta | ❌ ochiq | ⬜ | — | — | — | — |

## 6. Nomzod UX (kod auditi)

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| NX1 | Oqim ~17 qadam, 'Orqaga' va davom ettirish yo'q | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| NX2 | Nomzod o'z ariza holatini ko'ra olmaydi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| NX3 | Menyu tugmalari oqim o'rtasida ishlaydi (StateFilter yo'q) | O'rta | 🟡 qisman | ⬜ | — | — | — | — |
| NX4 | Rasm majburiy, o'tkazib bo'lmaydi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| NX5 | Video davomiyligi tekshirilmaydi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |

## 7. Infra / dasturchi

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| I1 | echo=True — gigant log + PII log'da | Infra | ✅ tuzatilgan | ⬜ | — | — | — | — |
| I2 | bot.py (lokal) prod bilan mos emas | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| I3 | client.py + Loyiha/Lead moduli — o'lik kod | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| I4 | userbot / channel_reader / role_check — o'lik; requirements shishgan | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| I5 | Monitoring/alert yo'q — xatolar jimgina yutiladi | Infra | 🟡 qisman | ⬜ | — | — | — | — |
| I6 | Config validatsiyasi yo'q — bo'sh env -> tushunarsiz crash | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| I7 | Test va CI umuman yo'q | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| I8 | Deploy qo'lda va sinuvchan; avtomatik backup yo'q | Infra | ✅ tuzatilgan | ⬜ | — | — | — | — |
| I9 | N+1 so'rovlar issiq yo'llarda | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| I10 | Global event loop + pool_pre_ping yo'q | Infra | 🟡 qisman | ⬜ | — | — | — | — |

## 8. Persona: Nomzod

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| FU1 | Jarayon qancha uzunligi oldindan aytilmaydi | Yuqori | ✅ tuzatilgan | ⬜ | — | — | — | — |
| FU2 | Umumiy progress ko'rsatkichi yo'q | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| FU3 | Bir vaqtda ikkita klaviatura chiqadi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| FU4 | 'Bekor qilish' tasdiqsiz — 15 qadam bir teginishda o'chadi | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| FU5 | Orqaga qaytish yo'q — bitta xato = qaytadan boshlash | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| FU6 | Kasb oxirroqda so'raladi; kirish yo'liga qarab tajriba butunlay farq qiladi | O'rta | ✅ tuzatilgan | ⬜ | — | — | — | — |
| FU7 | Rasm majburiy, sababi tushuntirilmaydi, o'tkazib bo'lmaydi | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| FU8 | Video-vizitka juda qo'rqinchli to'siq | Yuqori | 🟡 qisman | ⬜ | — | — | — | — |
| FU9 | Til tanlash yo'q — faqat o'zbekcha (lotin) | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| FU10 | Ariza holatini keyin ko'rib bo'lmaydi | Yuqori | ❌ ochiq | ⬜ | — | — | — | — |
| FU11 | Yakuniy 'ko'rib chiqish' ekrani yo'q | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| FU12 | Test javobini o'zgartirib bo'lmaydi + ikki marta bosish xavfi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| FU13 | Yozma javob — telefonda qoralama saqlanmaydi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| FU14 | Maosh erkin matn — chalkash format | O'rta | ❌ ochiq | ⬜ | — | — | — | — |

## 9. Persona: HR

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| FH1 | Bitta nomzodni baholash juda ko'p teginish | Yuqori | 🟡 qisman | ⬜ | — | — | — | — |
| FH2 | Yangi nomzod xabari tugmasiz — ustiga bosolmayman | Yuqori | ✅ tuzatilgan | ⬜ | — | — | — | — |
| FH3 | Qo'ng'iroq qilish uchun telefonni qo'lda nusxalash kerak | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| FH4 | Nomzodga shaxsiy eslatma/teg qo'yib bo'lmaydi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| FH5 | Yangi va ko'rilgan nomzod farqlanmaydi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| FH6 | Bitta savoldagi xatoni tuzatib bo'lmaydi | O'rta | ✅ tuzatilgan | ⬜ | — | — | — | — |
| FH7 | Video alohida xabar — ball qo'yishda kontekst yo'qoladi | O'rta | ❌ ochiq | ⬜ | — | — | — | — |
| FH8 | Arizalar guruhida filtr/harakat yo'q | O'rta | ❌ ochiq | ⬜ | — | — | — | — |

## 10. Persona: Dasturchi

| ID | Muammo | Og'irlik | Kod holati | Tahlil | Hukm | Ildiz | Variant | Fayl |
|---|---|---|---|---|---|---|---|---|
| FD1 | 'Nega ishlamadi' ni topish qiyin — log dengizi | Infra | ✅ tuzatilgan | ⬜ | — | — | — | — |
| FD2 | Deploy tartibini eslab qolish shart — bittasi unutilsa prod sinadi | Infra | ✅ tuzatilgan | ⬜ | — | — | — | — |
| FD3 | Nomzod holatini ko'radigan buyruq yo'q | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| FD4 | Screeningni lokalda sinab bo'lmaydi | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| FD5 | Funnel/metrika yo'q — UX muammolarini ko'r-ko'rona topamiz | Infra | ❌ ochiq | ⬜ | — | — | — | — |
| FD6 | Savol matnini o'zgartirish har safar kod deploy talab qiladi | Infra | ✅ tuzatilgan | ⬜ | — | — | — | — |

---

## Ildizlar

Ildizlar bu faylda emas — **[ILDIZLAR.md](ILDIZLAR.md)** da yuritiladi
(yagona manba). Bu jadvaldagi "Ildiz" ustuniga faqat `R<N>` raqami yoziladi;
tafsilot, dalil va bandlar xaritasi — reyestrda.
