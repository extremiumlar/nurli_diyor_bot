# TIZIM BRIFI — AI AGENT UCHUN
### Nuriddin Building & Metsys Group HR-bot tizimi
**Holat: 2026-08-14** · Bu hujjat AI agentga tizimni tushuntirish va **g'oya olish** uchun

---

# 0. SENGA NIMA KERAK (o'qishdan oldin)

Sen bu tizimni **tushunishing** va **rivojlantirish g'oyalarini berishing** kerak.

Bu hujjat sizga beradi: (1) biz nima qurganimiz, (2) qanday g'oyalar bilan
qurganimiz va nega aynan shunday, (3) hozir nima ishlayapti, (4) nima
ishlamayapti/yo'q, (5) qanday cheklovlar ichida ishlayapmiz.

**Muhim:** g'oyalaring shu cheklovlarga sig'ishi kerak (11-bo'lim). "Redis
qo'shamiz", "mikroservis qilamiz", "React panel yozamiz" — bu muhitda
ishlamaydi. Shuningdek biznes qoidalarini (3-bo'lim) buzadigan g'oya rad etiladi.

⚠️ Bu hujjatdagi raqamlar 2026-08-14 holatiga. Kod bilan ishlaganingda
haqiqiy holatni tekshir.

---

# 1. BIZNES: KIM, NIMA UCHUN

**Nuriddin Building** — O'zbekistondagi qurilish kompaniyasi. Ishchi kuchi
doimiy kerak: prorab, kran mashinisti, buxgalter, IT, HR, dizayner va h.k.

**Muammo:** an'anaviy ishga qabul sekin va noaniq — nomzod qo'ng'iroq qiladi,
HR qo'lda yozib oladi, CV yig'ilmaydi, kim yaxshiroq — bilib bo'lmaydi.

**Yechim:** Telegram bot orqali **to'liq avtomatlashtirilgan ariza qabul va
saralash**. Nomzod botda ariza to'ldiradi, kasbiy testdan o'tadi, video
yuboradi; tizim ball qo'yadi; HR tayyor, reytinglangan ro'yxatni ko'radi.

**Uch toifa foydalanuvchi:**

| Kim | Soni | Nima qiladi |
|---|---|---|
| **Nomzod** (eng muhim) | 1200+ start, 664 ariza | Vakansiya tanlaydi, ma'lumot to'ldiradi, test/yozma javob beradi, video yuboradi |
| **HR** | 1 hr_admin + 3 super_admin | Nomzodlarni ko'radi, video ko'radi, ball qo'yadi, tasdiqlaydi/rad etadi, Excel oladi |
| **Dasturchi** | 1 | Deploy, nosozlik tuzatish |

**Real hajm:** 24 vakansiya, **664 ariza**, baza ~890 KB. O'yinchoq loyiha emas —
har bir bug real odamlarning ish topish imkoniyatiga ta'sir qiladi.

---

# 2. ASOSIY G'OYA: 3 BOSQICHLI SARALASH

Tizimning yuragi — bu. Har bir nomzod uch bosqichdan o'tadi va **19 ballik**
shkalada baholanadi:

```
┌─ 1-BOSQICH: MA'LUMOT (ball yo'q) ────────────────────────┐
│  Vakansiya tanlash → rozilik → ~10 qadam:                 │
│  ism, telefon, manzil, yosh, tillar, ma'lumot darajasi,   │
│  tajriba, qo'shimcha ko'nikma, RASM, kutgan maosh         │
└───────────────────────────────────────────────────────────┘
                          ↓
┌─ 2-BOSQICH: KASBIY SAVOLLAR (15 ball) ───────────────────┐
│  3 ta yopiq test  (A/B/C variant, har biri 0/1/3 ball) → 9│
│  2 ta yozma savol (erkin matn, 0-3 ball)              → 6│
└───────────────────────────────────────────────────────────┘
                          ↓
┌─ 3-BOSQICH: VIDEO (4 ball) ──────────────────────────────┐
│  30-60 soniya video-vizitka, rolga xos savolga javob      │
│  Ballni HR odam qo'yadi (nutq, ishonch, mazmun)           │
└───────────────────────────────────────────────────────────┘
                          ↓
              JAMI 19 ball → foizga aylantiriladi
              🟢 ≥73%   🟡 47-72%   🔴 <47%
```

## 2.1 Nega ball emas, FOIZ

Chunki har vakansiya bosqichlarni o'chirib qo'yishi mumkin (2.2). Agar
vakansiyada video o'chiq bo'lsa — maksimal ball 15, boshqasida 19. Xom ballni
solishtirish adolatsiz bo'lardi. Shuning uchun har arizada `max_total` saqlanadi
va reyting **foiz** bo'yicha chiqadi.

## 2.2 Bosqichlarni admin boshqaradi — 3 rejim

Har vakansiya uchun **ikkita sozlama**, har biri 3 holatda:

| | 🔴 majburiy | 🟡 ixtiyoriy | ⚫️ o'chirilgan |
|---|---|---|---|
| **Savollar** | savolsiz ariza yakunlanmaydi | "o'tkazib yuborish" tugmasi bor, o'tkazsa 0 ball | umuman so'ralmaydi, maksimal balldan chiqadi |
| **Video** | videosiz ariza yakunlanmaydi | o'tkazsa 0 ball | umuman so'ralmaydi |

Natijada maksimal ball avtomatik o'zgaradi: 19 / 15 / 4 / 0.

Sozlash: bitta vakansiya uchun ham, **ommaviy** (hammasi yoki tanlanganlari)
ham — Sozlamalar menyusidan.

## 2.3 Buzib bo'lmaydigan qoida: «AVTO-SARALASH BOR, AVTO-RAD YO'Q»

AI ham, bot ham **hech qachon** nomzodni o'zi rad etmaydi. Ular faqat ball
qo'yadi va xulosa yozadi. Yakuniy qaror — **faqat HR odamning qo'lida**.

Bu shunchaki texnik cheklov emas, kompaniyaning qadriyati: odam taqdiri
haqidagi qarorni mashina qabul qilmasligi kerak.

---

# 3. BUZIB BO'LMAYDIGAN QOIDALAR

G'oya bularni buzsa — qanchalik chiroyli bo'lmasin, rad etiladi.

1. **Avto-rad yo'q** (2.3).
2. **Nomzod ma'lumoti yo'qolmaydi.** Rad etilgan nomzod ham bazada qoladi
   (`status='rejected'`), o'chirilmaydi.
3. **Nomzod jimgina yo'qolmasligi kerak.** Xato bo'lsa nomzod buni bilishi
   shart. `except: pass` bilan yutilgan xato — eng yomon holat: nomzod
   "yubordim" deb o'ylaydi, HR esa hech narsa ko'rmaydi.
4. **Interfeys to'liq o'zbekcha (lotin).**
5. **Nomzod tajribasi HR qulayligidan ustun.** Ikkisi to'qnashsa — nomzod
   tomonini tanlaymiz.

---

# 4. HOZIR NIMA ISHLAYAPTI (to'liq ro'yxat)

## 4.1 Nomzod tomoni

- ✅ `/start` → menyu: **🏢 Biz haqimizda** · **📝 Ariza topshirish** · aloqa
- ✅ Majburiy obuna tekshiruvi (Telegram kanal + Instagram havolasi)
- ✅ **Vakansiya avval tanlanadi**, keyin ma'lumot so'raladi
- ✅ Rozilik ekrani: "3 bosqich, ~10-15 daqiqa, oxirida video kerak" deb
  ogohlantiradi
- ✅ 10 qadamlik ma'lumot yig'ish (validatsiya bilan: telefon formati,
  matn bo'lmagan input, yopilgan vakansiya)
- ✅ Test savollari: variantlar **xabar ichida to'liq matn**, tugmalarda
  faqat A/B/C harflar (uzun matn tugmaga sig'maydi)
- ✅ Variantlar har safar **aralashtiriladi** (javobni yodlab olmasin)
- ✅ Yozma javoblar, video/video-note qabul qilish
- ✅ Kunlik takroriy ariza cheklovi
- ✅ Har qadamda "❌ Bekor qilish"

## 4.2 HR/admin paneli (`/admin`)

- ✅ **Vakansiyalar**: qo'shish, tahrirlash, yopish/ochish, o'chirish
- ✅ **Arizalar**: ro'yxat (sahifalab), kartochka, CV/rasm yuklab olish
- ✅ **Nomzod qidiruvi** — bir so'rovda ko'p nomzod:
  `3 7 12` · `1-15` (oraliq) · `Ali, Hasan` (ismlar) · telefon bo'lagi ·
  aralash (`1-5, Sardor, 20`). Natija avval qisqa ro'yxat, keyin kerakligini
  ochasan. Qidiruv rejimi yopilmaydi — ketma-ket yozaverasan
- ✅ **Nomzod kartochkasi ustidan barcha amallar** (`cd:` tugmalari):
  videoni ko'rish, test javoblarini ko'rish, yozma javoblarni ko'rish,
  ball qo'yish (yozma 0-3, video 0-4), AI baholash, qayta baholash,
  tasdiqlash/rad etish (tasdiq so'rovi bilan), qarorni bekor qilish
- ✅ **Savollarni boshqarish** (`vq:`): shablondan yuklash, avtomatik
  biriktirish (kasb nomiga qarab), bitta savolni tahrirlash, variant
  tahrirlash, savol qo'shish/o'chirish, **AI bilan yangi savol generatsiya**
- ✅ **Bosqich sozlamalari** (`vs:`, `bs:`): bitta vakansiya yoki ommaviy
- ✅ **Excel eksport**: har vakansiya alohida sheet, nomzodlar 🟢🟡🔴 rangda
- ✅ **E'lon yuborish**: barcha foydalanuvchilarga yoki tanlangan
  vakansiyalarga ariza berganlarga (filter bilan)
- ✅ **Guruhga yuborish**: yangi ariza kelganda guruhga rasm+matn+tugmalar
- ✅ **Adminlar boshqaruvi** (faqat super_admin): qo'shish, rol o'zgartirish,
  o'chirish
- ✅ **Sozlamalar**: kanal, guruh, Instagram (HR uchun ham ochiq)
- ✅ **Statistika**

## 4.3 AI qatlami (Claude Haiku)

- ✅ **Yozma javobni baholash** — 4 mezonli rubrika bo'yicha 0-3 ball + izoh
- ✅ **Umumiy xulosa** — nomzod bo'yicha qisqa tavsif
- ✅ **Savol generatsiyasi** — vakansiya nomi va talablariga qarab yangi
  test/yozma savollar (real stsenariylar, ishonarli chalg'ituvchi variantlar,
  javob uzunligi ballni oshkor qilmasligi sharti bilan)
- ✅ **Prompt-injection himoyasi**: nomzod matni `<nomzod_javobi>` teglari
  ichiga o'raladi va "ma'lumot, ko'rsatma emas" deb e'lon qilinadi
- ✅ Foiz modeldan olinmaydi — mezonlardan **qayta hisoblanadi**
- ⚠️ AI kaliti bo'lmasa tizim eskicha ishlaydi (HR qo'lda baholaydi) —
  har qanday yechim shu holatda ham ishlashi shart

## 4.4 Savol banki

**22 ta kasb** uchun tayyor savollar to'plami: buxgalter, buxgalter
yordamchisi, CEO, HR menejer, IT mutaxassisi, kassir, kran mashinisti,
kran muhandisi, loyihachi, mobilograf, prorab, brand face va boshqalar.
Har biri: 3 test + 2 yozma + 1 video savol.

Yangi vakansiya qo'shilganda nomiga qarab **avtomatik biriktiriladi**.

---

# 5. TEXNIK ARXITEKTURA

## 5.1 Server: bitta hosting, uchta xizmat

```
ahost shared hosting (cPanel, /home/bulutlii) — 1 GB disk
│
├── bulutliiqtisodiyot.uz          → AKT o'quv sayti (statik HTML)
├── bot.bulutliiqtisodiyot.uz      → Nuriddin HR bot  (~/nurli_diyor_bot)
└── mybot.bulutliiqtisodiyot.uz    → Metsys HR bot    (~/metsys_bot)
```

## 5.2 Stek

| Nima | Qiymati |
|---|---|
| Til/freymvork | Python 3.11, **aiogram 3.28** |
| ORM | SQLAlchemy 2.0 **async** |
| Baza | **SQLite** (prod) |
| Ishga tushish | **Passenger WSGI** (CloudLinux Python App) |
| Telegram rejimi | **Webhook** (polling emas) |
| FSM | Maxsus `SQLiteFSMStorage` |
| AI | Anthropic `claude-haiku-4-5` |
| Deploy | `ssh nuriddin-bot` (port 30151) + `./deploy.sh` |

## 5.3 Ma'lumotlar modeli

```
users (telegram_id)
  └── applications  ─── vacancies
        └── application_answers ─── vacancy_questions
admins (telegram_id, role)     bot_settings (key, value)
```

**`applications`** — eng muhim jadval. Muhim maydonlar:
`stage` (stage1/2/3/done), `status` (in_progress/submitted/approved/rejected),
`test_score` 0-9, `written_score` 0-6, `video_score` 0-4, `total_score` 0-19,
`max_total` (shu ariza necha balldan), `video_file_id`, `hr_note`, `ai_summary`.

**Rollar:** `super_admin` (to'liq) · `hr_admin` (HR ishlari) · `project_admin`
(ishlatilmaydi).

## 5.4 Metsys Group — ikkinchi nusxa

Xuddi shu kod boshqa kompaniya uchun: bot `@HR_CHI_BOT`, alohida baza, faqat
brend nomi farq qiladi. Bugun (2026-08-14) deploy qilindi, bazasi hali bo'sh.

⚠️ **Bu takrorlanish (fork) — kelajakda muammo bo'lishi mumkin:** bitta
tuzatishni ikki joyga qo'lda ko'chirish kerak. Bu **g'oya berish uchun yaxshi
maydon** (ko'p-ijarachi arxitektura?).

---

# 6. BIZ QANDAY ISHLAYMIZ: TAHLIL TIZIMI (meta-tizim)

Bu loyihaning o'ziga xos jihati — biz **muammolarni tahlil qilish tizimini
ham qurdik**. Chunki AI agentlar muammoga yuzaki yechim berib o'tib ketardi.

## 6.1 Tuzilishi

```
AI_TAHLIL_PROTOKOLI.md     Tahlilchi agent uchun: loyiha konteksti + A→L
                           majburiy 12 bosqich (dalil → ssenariy → ildiz
                           zanjiri → ta'sir → qarindosh joylar → nega
                           aniqlanmadi → variantlar → cheklovlar → qadamlar
                           → xavf → tekshiruv → o'z-o'zini tekshirish)

AI_TEKSHIRUV_PROTOKOLI.md  Tekshiruvchi agent uchun: T1–T8 audit — har
                           iqtibosni kodni ochib solishtiradi, ildizni
                           mustaqil qazadi, qarshi misol izlaydi, soxta ✅
                           ni fosh qiladi

tahlil/INDEX.md            71 bandning yagona holat jadvali
tahlil/ILDIZLAR.md         Tasdiqlangan tub sabablar reyestri (R1, R2, R3...)
tahlil/<BAND>.md           Har bandning to'liq tahlili + tekshiruv tarixi
```

## 6.2 Ish sikli

```
Tahlilchi → tahlil/<BAND>.md → Tekshiruvchi (boshqa agent, toza kontekst)
                                    ↓
                        ✅ QABUL          ❌ QAYTARILDI
                     kodga joriy       tahlilchi tuzatadi → qayta
```

**Bu tizim ishlayapti:** 3 banddan **2 tasi birinchi tekshiruvda qaytarildi**
va ikkalasida ham **real xavfsizlik teshigi** topildi (quyida S1, S2).

## 6.3 Asosiy g'oya: 71 ta muammo ortida ~8-10 ta ildiz

Bandma-band yamoq qo'yish o'rniga **tub sabablarni** aniqlaymiz. Hozircha
uchtasi tasdiqlangan va yopilgan:

| Ildiz | Nima | Nechta band |
|---|---|---|
| **R1** | Javob "hodisa" deb modellashtirilgan, "holat" emas — DB'da "1 savol = 1 javob" cheklovi yo'q edi | C2 |
| **R2** | Tashqi kirish nuqtasi (webhook) autentifikatsiyasiz — har kim soxta so'rov bilan super_admin bo'lardi | S1 |
| **R3** | Markazlashgan avtorizatsiya qatlami yo'q (default-allow) — 10 handlerda ruxsat tekshiruvi unutilgan edi | S2 |

---

# 7. BUGUN NIMA TUZATILDI (misol sifatida — chuqurlik namunasi)

## R1 — dublikat javoblar
Nomzod test tugmasini ikki marta bossa (yoki ikki worker poyga qilsa) bitta
savolga ikkita javob yozilardi → ball 9 dan oshib reyting buzilardi.
**Yechim:** partial UNIQUE indeks + idempotent yozuv (`ON CONFLICT DO NOTHING`)
+ migratsiya (dublikatlarni tozalash, baholangani afzal) + chegara-signal.

## R2 — webhook himoyasi
Bot kelgan so'rov Telegram'danmi — tekshirmasdi. Manzilni bilgan har kim
`curl` bilan soxta update yuborib, `from_user.id` ga super-admin ID qo'yib,
664 nomzodning CV/PII sini olishi mumkin edi.
**Yechim:** Telegram `secret_token` + WSGI'da `hmac.compare_digest` → 403.
Deploy tartibi maxsus (fail-open) tanlandi — bot bir soniya ham uzilmadi.

## R3 — admin panelga markaziy himoya
10 ta handler ruxsat tekshirmasdi — oddiy foydalanuvchi `get_cv:1` yuborib
CV yuklab olardi.
**Yechim:** `AdminGuardMiddleware` (default-deny). Chegara `is_hr` —
"rol bormi" emas (birinchi urinishda aynan shu xato qilingan va tekshiruvchi
uni ushlab qolgan).

---

# 8. NIMA ISHLAMAYDI / YO'Q (ochiq muammolar)

**Holat:** 71 banddan ✅ 24 tuzatilgan · 🟡 7 qisman · ❌ **40 ochiq**.

## 8.1 Xavfsizlik (qolgan)
- **S3** 🟡 HTML-injection: `html.escape` hamma joyda emas (`admin.py` da yo'q)
- **S4** ❌ Postgres paroli ochiq holda git tarixida (`app/test_db.py`)

## 8.2 Ma'lumot yo'qolishi
- **D1** ❌ Vakansiya o'chirilsa bog'liq arizalar ham **qaytarib bo'lmas**
  o'chadi, tasdiq so'ralmaydi

## 8.3 Concurrency (bir vaqtda ishlash)
- **C1** ❌ Webhook retry dedup yo'q — uzoq amal (broadcast) 60s dan oshsa
  Telegram update'ni qayta yuboradi → e'lon 2-3 marta ketadi
- **C3** ❌ FSM `update_data` atomik emas — lost update
- **C4** ❌ SQLite FSM'da WAL/busy_timeout yo'q — "database is locked"
- **C5** ❌ Ball yozish va qayta hisoblash alohida tranzaksiyada — ikki HR
  bir vaqtda baholasa biri ikkinchisini bekor qiladi

## 8.4 Nomzod tajribasi (UX) — eng ko'p ochiq band
- **FU2** Progress ko'rsatkichi yo'q ("Bosqich 2/3 · Savol 2/5")
- **FU4** "Bekor qilish" tasdiqsiz — 15 qadam bir teginishda o'chadi
- **FU5** **Orqaga qaytish yo'q** — bitta xato = qaytadan boshlash
- **FU7** Rasm majburiy, sababi tushuntirilmaydi, o'tkazib bo'lmaydi
- **FU8** 🟡 Video qo'rqinchli to'siq — namuna/skript yo'q, qayta yozib
  ko'rish yo'q
- **FU9** **Til tanlash yo'q** — faqat o'zbekcha lotin (ruszabon/kirill
  nomzod umuman foydalana olmaydi)
- **FU10** Nomzod o'z ariza holatini keyin ko'ra olmaydi — "ko'rib
  chiqilmoqda" dan keyin abadiy sukunat
- **FU11** Yakuniy "ko'rib chiqish" ekrani yo'q — ko'r-ko'rona yuboriladi
- **FU13** Yozma javob qoralamasi saqlanmaydi
- **FU14** Maosh erkin matn — "5 mln", "5000000", "kelishamiz" aralash

## 8.5 HR tajribasi
- **FH1** 🟡 Bitta nomzodni baholash ko'p teginish talab qiladi
- **FH3** Telefonga bir teginishda qo'ng'iroq qilib bo'lmaydi
- **FH4** `hr_note` maydoni bazada bor, lekin **UI da yozish tugmasi yo'q**
- **FH5** Yangi va ko'rilgan nomzod farqlanmaydi, status filtri yo'q
- **FH7** Video alohida xabar bo'lib keladi — ball qo'yishda kontekst yo'qoladi

## 8.6 Infra
- **I2** `bot.py` (lokal) prod bilan mos emas — screening router yo'q, ya'ni
  **saralash oqimi lokalda umuman sinalmaydi**, buglar faqat prodda chiqadi
- **I3/I4** O'lik kod: `client.py` (loyihalar/lidlar), userbot, channel_reader
- **I5** 🟡 Monitoring/alert yo'q — xatolar jimgina yutiladi
- **I6** Config validatsiyasi yo'q
- **I7** **Test va CI umuman yo'q**
- **I9** N+1 so'rovlar
- **FD3** Nomzod holatini ko'radigan diagnostika buyrug'i yo'q
- **FD5** **Funnel/metrika yo'q** — nomzodlar qaysi qadamda tashlab ketishini
  bilmaymiz, UX muammolarini ko'r-ko'rona topamiz

---

# 9. TARIX: QANDAY G'OYALAR BILAN KELDIK

Tizim bir zumda paydo bo'lmagan — g'oyalar ketma-ket sinalgan:

1. **Boshida:** oddiy ariza yig'uvchi bot (ism, telefon, CV). Saralash yo'q.
2. **"Vakansiyalar" tugmasi olib tashlandi** — ikki xil kirish yo'li ikki xil
   tajriba berardi (menyudan kirsang kasb 6-qadamda, tugmadan kirsang umuman
   yo'q). Endi bitta yo'l: **avval vakansiya, keyin ma'lumot**.
3. **3 bosqichli saralash joriy etildi** (2-bo'lim) — HR hujjatidagi
   metodologiya asosida.
4. **Savollar kasbga bog'landi** — 22 rol uchun bank, nomiga qarab avtomatik
   biriktirish.
5. **Alohida "saralash paneli" olib tashlandi** — HR ikki xil ro'yxat
   o'rtasida adashardi. Endi barcha amallar **nomzod kartochkasi ustidagi
   inline tugmalarda**.
6. **Reyting Excel'ga ko'chirildi** — har vakansiya alohida sheet, rangli.
   Telegram ro'yxatidan ko'ra HR uchun qulayroq.
7. **AI qo'shildi** — avval faqat yozma javoblarni baholash, keyin savol
   generatsiyasi ham. Prinsip: **AI yordamchi, hakam emas**.
8. **Bosqichlar sozlanadigan qilindi** — hamma vakansiya uchun bir xil talab
   noto'g'ri edi (kran mashinistiga yozma savol shart emas).
9. **Tahlil tizimi qurildi** (6-bo'lim) — chunki AI agentlar yuzaki yechim
   berardi.

---

# 10. NIMA YAXSHI ISHLAYAPTI (buzmaslik kerak)

G'oya berayotganda bularni buzma:

- **Vakansiya-avval oqimi** — nomzod nima uchun ariza berayotganini biladi
- **A/B/C tugma + xabarda to'liq matn** — uzun variantlar tugmaga sig'maydi
- **Variantlarni aralashtirish** — javob yodlab olinmaydi
- **Foizli reyting** — har xil maksimal balllar adolatli solishtiriladi
- **Kartochka ustidagi inline tugmalar** — HR bitta joyda hamma ishni qiladi
- **Excel rangli eksport** — HR eng ko'p ishlatadigan narsa
- **AI kaliti bo'lmasa ham ishlaydi** — AI ixtiyoriy qatlam
- **deploy.sh** — bitta buyruq: zaxira → pull → migratsiya → restart

---

# 11. CHEKLOVLAR — G'OYA SHULARGA SIG'ISHI KERAK

| # | Cheklov | Ma'nosi |
|---|---|---|
| 1 | **Shared hosting** (cPanel, CloudLinux) | Docker yo'q, root yo'q, systemd yo'q |
| 2 | **Disk atigi 1 GB** | Hozir 387 MB band. Video/rasm saqlash mumkin emas — faqat Telegram `file_id` |
| 3 | **Redis/Celery/navbat yo'q** | Tashqi xizmat talab qiladigan yechim ishlamaydi |
| 4 | **Doimiy jarayon yo'q** | Passenger so'rov kelganda uyg'otadi, bo'sh turganda o'ldiradi. Xotiradagi holat yo'qoladi |
| 5 | **Bir nechta worker bo'lishi mumkin** | Global o'zgaruvchi/dict bilan holat saqlash noto'g'ri |
| 6 | **Webhook 60 soniya** | Uzoq amal (1200+ userga broadcast) update'ni retry'ga olib keladi |
| 7 | **SQLite** | Og'ir parallel yozuv uchun mo'ljallanmagan |
| 8 | **Telegram limitlari** | Xabar 4096 belgi, tugma matni ~28-30 belgi, `callback_data` 64 bayt |
| 9 | **Cron bor** | Haftalik tozalash ishlayapti — ya'ni fon vazifalari mumkin |
| 10 | **AI ixtiyoriy** | Kalitsiz ham to'liq ishlashi kerak |
| 11 | **Migratsiya qoidasi** | Faqat xom SQL, idempotent, dialektga mos (ORM modeliga bog'lanmaydi) |

---

# 12. SENDAN NIMA KUTAMIZ

Tizimni tushunganingdan keyin **g'oyalar** ber. Foydali g'oyaning belgilari:

✅ **Yaxshi g'oya:**
- Aniq muammoni yechadi (kimning, qanday og'rig'i)
- 11-bo'limdagi cheklovlarga sig'adi
- 3-bo'limdagi qoidalarni buzmaydi
- 10-bo'limdagi ishlayotgan narsani buzmaydi
- Ta'siri o'lchanadi ("nomzodlarning tashlab ketishi kamayadi" — qanday
  o'lchaymiz?)
- Kuchi baholangan (kichik/o'rta/katta)

❌ **Foydasiz g'oya:**
- "Zamonaviy arxitektura kerak", "refaktoring qiling"
- Mikroservis, Kubernetes, React panel, Redis, alohida server
- "AI nomzodni avtomatik rad etsin"
- Bu tizimga bog'lanmagan umumiy maslahat

## Qaysi yo'nalishlarda g'oya kutamiz

1. **Nomzod tashlab ketishini kamaytirish** — 17 qadamlik oqim uzun,
   video qo'rqinchli. Qanday qilib tugatish foizini oshiramiz?
2. **HR ish tezligi** — 664 nomzodni ko'rib chiqish qancha vaqt oladi?
   Qanday qisqartiramiz?
3. **Saralash sifati** — 19 ballik model adolatlimi? Nima yetishmayapti?
4. **AI ni chuqurroq ishlatish** — hozir faqat baholash va savol
   generatsiyasi. Yana qayerda foydali bo'lardi (avto-rad qilmasdan)?
5. **Ikki nusxa muammosi** — Nuriddin va Metsys bir xil kod, qo'lda
   ko'chiriladi. Ko'p-ijarachi (multi-tenant) qilish arziydimi?
6. **Ko'rinmaydigan narsalar** — funnel/metrika yo'q. Nimani o'lchash kerak?
7. **Nomzod bilan aloqa** — ariza berganidan keyin abadiy sukunat. Nima
   qilish mumkin?

## Javob formati

Har g'oya uchun:
```
G'OYA: <bir jumla>
MUAMMO: <kimning qanday og'rig'ini yechadi>
QANDAY ISHLAYDI: <mexanizm, 2-4 jumla>
KUCHI: kichik / o'rta / katta
TA'SIR: <nima yaxshilanadi va buni qanday o'lchaymiz>
XAVF: <nima buzilishi mumkin>
CHEKLOVLAR: <11-bo'limdagi qaysi bandlarga tegadi va sig'adimi>
```

Avval **eng katta ta'sirli 3-5 ta** g'oyani ber, keyin qolganini.
Agar tizim haqida noaniq narsa bo'lsa — taxmin qilma, **so'ra**.
