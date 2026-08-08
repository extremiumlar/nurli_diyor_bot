# AI AGENT UCHUN TAHLIL PROTOKOLI
### Nuriddin Building HR-bot — muammolarni ildizigacha tahlil qilish tizimi

> **Bu faylni AI agentga to'liq bering.** Undan keyin bitta band raqamini
> yuboring (masalan `S2` yoki `1.1`). Agent shu bandni protokol bo'yicha
> to'liq tahlil qiladi va TO'XTAYDI. `keyingisi` deganingizda keyingisiga o'tadi.

---

# 0-QISM — SENING ROLING VA MAQSADING

Sen **tizim tahlilchisisan**, tuzatuvchi emas.

Vazifang: berilgan bitta muammoni **ildizigacha tushunish**, keyin **ideal
yechim rejasini** bosqichma-bosqich berish. Kod yozishing mumkin, lekin
faqat yechim rejasining bir qismi sifatida — tahlilsiz kod yozish taqiqlanadi.

**Sen baholanadigan mezon:** javobing shu tizimni bilmagan boshqa dasturchi
uchun ham savolsiz bajariladigan darajada aniq bo'lishi. "Tushunarli, lekin
nima qilishni bilmadim" — muvaffaqiyatsizlik.

**Eng katta xavf — yuzakilik.** Sen ko'p marta simptomni ildiz deb ataysan
va birinchi xayolingga kelgan yechim bilan o'tib ketasan. Bu protokol aynan
shuning oldini olish uchun yozilgan. Protokolning har bir bo'limi — sen
odatda tashlab ketadigan bosqichni majburiy qiladigan to'siq.

**⚖️ Bilib qo'y: javobing mustaqil auditdan o'tadi.** Sen yozgan har bir
tahlilni **alohida tekshiruvchi agent** (`AI_TEKSHIRUV_PROTOKOLI.md`) oladi
va uni RAD ETISHGA harakat qiladi: har bir `fayl:qator` iqtibosingni kodni
ochib solishtiradi, E-bosqich qidiruv naqshlaringni qayta ishlatadi va o'zinikini
qo'shadi, ildiz zanjiringni mustaqil qazib chiqadi, yechimingga qarshi misol
izlaydi va L-jadvalingdagi har bir ✅ dan dalil talab qiladi. **Soxta ✅ —
eng og'ir buzilish** sifatida alohida qayd etiladi. Tekshirilmagan da'vo
yozish — vaqtni ikki marta yo'qotish: baribir qaytariladi.

---

# 1-QISM — LOYIHA HAQIDA TO'LIQ MA'LUMOT

Tahlil qilishdan oldin bu qismni to'liq o'qi. Aksariyat yuzaki javoblar
kontekstni bilmaslikdan kelib chiqadi.

## 1.1 Tizim nima qiladi

**Nuriddin Building** — qurilish kompaniyasi. HR-bot Telegram orqali ishlaydi
va ish o'rniga nomzod yig'ish, saralash va HR ga yetkazish uchun xizmat qiladi.

**Tizimdan 3 toifa odam foydalanadi:**

| Kim | Nima qiladi | Qayerda |
|---|---|---|
| **Nomzod** (eng ko'p, eng muhim) | Vakansiya tanlaydi, ma'lumot to'ldiradi, test/yozma savollarga javob beradi, video yuboradi | Telegram bot, telefon ekrani |
| **HR** | Nomzodlarni ko'radi, videoni ko'radi, ball qo'yadi, tasdiqlaydi/rad etadi, Excel yuklab oladi | `/admin` paneli |
| **Dasturchi** | Deploy qiladi, nosozlikni tuzatadi | cPanel Terminal, SSH yo'q |

**Real hajm (2026-08-07 holatiga):** 24 ta vakansiya, **613 ta ariza**,
`bot.db` ≈ 728 KB. Ya'ni bu o'yinchoq loyiha emas — har bir bug real
odamlarning ish topish imkoniyatiga ta'sir qiladi.

## 1.2 Buzib bo'lmaydigan biznes qoidalari

Bu qoidalar buzilsa — yechim noto'g'ri, qanchalik chiroyli bo'lmasin.

1. **«Avto-saralash bor, avto-rad yo'q.»** AI yoki bot HECH QACHON nomzodni
   o'zi rad etmaydi. AI faqat ball qo'yadi va xulosa yozadi; yakuniy qaror
   — faqat HR odamning qo'lida. Har qanday "past ballni avtomatik rad etamiz"
   taklifi — qoidabuzarlik.
2. **Nomzod ma'lumoti yo'qolmaydi.** Rad etilgan nomzod ham bazada qoladi
   (`status='rejected'`), o'chirilmaydi. Har qanday `DELETE` taklifi alohida
   asoslanishi kerak.
3. **Nomzod jimgina yo'qolmasligi kerak.** Xato yuz bersa nomzod buni bilishi
   shart. `except: pass` bilan yutilgan xato — eng yomon holat, chunki nomzod
   "yubordim" deb o'ylaydi, HR esa hech narsa ko'rmaydi.
4. **Interfeys to'liq o'zbekcha (lotin).** Har qanday yangi matn ham o'zbekcha.
5. **Nomzodning tajribasi HR qulayligidan ustun.** Ikki tomon o'rtasida
   tanlov bo'lsa — nomzod tomonini tanla.

## 1.3 Texnologiya va ishga tushish muhiti

Bu qism yechim **amalda bajarilishi mumkinmi** degan savolga javob beradi.
Ko'p yuzaki yechimlar aynan shu yerda qulaydi.

| Nima | Qiymati |
|---|---|
| Til / freymvork | Python 3.11.15, **aiogram 3.x** |
| ORM | SQLAlchemy 2.0 **async** (`async_sessionmaker`) |
| Baza (prod) | **SQLite** — `~/nurli_diyor_bot/bot.db` |
| Baza (lokal) | Postgres (eskirgan, prod bilan bir xil emas) |
| Hosting | **cPanel shared hosting** (ahost, `de.ahost.cloud`) |
| Ishga tushish | **Passenger WSGI** — `passenger_wsgi.py` |
| Telegram rejimi | **Webhook** (`POST /webhook`), long-polling YO'Q |
| FSM saqlash | Maxsus `SQLiteFSMStorage` (`app/fsm_storage.py`) — **sinxron `sqlite3`** |
| Restart | `touch tmp/restart.txt` |
| Deploy | `./deploy.sh` (zaxira → git pull → venv → migratsiya → restart) |

### Muhitning QATTIQ cheklovlari — yechim shularga sig'ishi shart

- ❌ **SSH yo'q.** Barcha portlar yopiq. Faqat cPanel Terminal.
- ❌ **Redis yo'q, Celery yo'q, fon-worker yo'q.** "Navbatga qo'yamiz" tipidagi
  yechim ishlamaydi, agar u tashqi xizmat talab qilsa.
- ❌ **Doimiy ishlaydigan jarayon yo'q.** Passenger ilovani so'rov kelganda
  uyg'otadi va bo'sh turganda o'ldiradi. Xotiradagi (`in-memory`) holat
  ishonchsiz — istalgan payt yo'qoladi.
- ⚠️ **Bir nechta worker bo'lishi mumkin.** Passenger bir necha jarayon
  ko'tarishi mumkin — ular bitta `bot.db` fayliga yozadi. Global o'zgaruvchi,
  `set` yoki `dict` orqali holat saqlash — noto'g'ri.
- ⚠️ **Webhook bitta `loop.run_until_complete()` ichida ishlaydi.** Uzoq amal
  (broadcast, Excel) butun so'rovni bloklaydi va Telegram 60s dan keyin
  update ni **qayta yuboradi**.
- ⚠️ **Xato yutiladi.** `passenger_wsgi.py:52` da `except Exception` bor —
  har qanday xato `stderr` ga yozilib, foydalanuvchiga **200 OK** qaytadi.

## 1.4 Fayllar xaritasi

```
nurli_diyor_bot/
├── passenger_wsgi.py        59   PROD kirish nuqtasi. Bot, Dispatcher,
│                                 4 ta router, webhook. Xatoni yutadi.
├── bot.py                   ~40  LOKAL kirish nuqtasi (polling).
│                                 ⚠️ screening_admin router YO'Q — shuning
│                                 uchun saralash lokalda sinalmaydi.
├── deploy.sh               113   Yagona deploy buyrug'i.
├── migrate_v2..v6.py             Idempotent migratsiyalar.
├── add_vacancy.py           98   CLI: vakansiya + savollarni biriktirish.
├── check_screening.py       56   Diagnostika: qaysi vakansiyada savol bor.
│
├── app/
│   ├── config.py            31   .env dan sozlamalar.
│   ├── fsm_storage.py       80   SQLite FSM. ⚠️ sinxron sqlite3,
│   │                             WAL yo'q, busy_timeout yo'q.
│   ├── utils.py             75   broadcast va yordamchilar.
│   ├── question_bank.py    940   22 ta kasb uchun savol banki + ball/foiz/
│   │                             rang mantiqi (MAX_*, PCT_*, _eff_max).
│   ├── ai_grader.py        511   Claude bilan yozma javob va umumiy baho.
│   ├── ai_questions.py     242   Claude bilan yangi savol generatsiyasi.
│   │
│   ├── database/
│   │   ├── connect.py       ~30  engine, async_session, SQL_ECHO.
│   │   ├── models.py       167   Barcha jadvallar.
│   │   └── crud.py         728   Barcha DB amallari.
│   │
│   ├── handlers/
│   │   ├── start.py         99   /start, asosiy menyu.
│   │   ├── jobseeker.py    912   NOMZOD OQIMI — vakansiya→ma'lumot→
│   │   │                         test→yozma→video→yakun.
│   │   ├── admin.py       1714   Admin panel: vakansiya, ariza, qidiruv,
│   │   │                         e'lon, Excel, adminlar.
│   │   ├── screening_admin.py 1278  Savollar (vq:), nomzod kartochkasi
│   │   │                         (cd:), bosqich sozlamalari (vs:, bs:).
│   │   └── client.py       271   Loyihalar/lidlar. ⚠️ prod da ULANMAGAN.
│   │
│   ├── keyboards/inline.py 611   Barcha inline klaviaturalar.
│   ├── keyboards/reply.py        Reply klaviaturalar.
│   ├── middleware/subscription.py 68  Majburiy obuna tekshiruvi.
│   ├── middlewares/role_check.py  31  ⚠️ deyarli ishlatilmaydi.
│   └── states/                   FSM holatlari.
└── userbot/                      Telethon userbot (asosiy oqimga tegmaydi).
```

⚠️ `middleware/` va `middlewares/` — **ikkita alohida papka**. Bu chalkashlik
manbasi; tahlilda qaysi biri haqida gapirayotganingni aniq yoz.

## 1.5 Ma'lumotlar modeli (`app/database/models.py`)

Asosiy jadvallar va ular orasidagi bog'lanish:

```
users (id: telegram_id)
  └── applications (user_id, vacancy_id)
        └── application_answers (application_id, question_id)

vacancies (id)
  ├── vacancy_questions (vacancy_id, qtype)
  └── applications (vacancy_id)

admins (telegram_id, role)      bot_settings (key, value)
```

### `applications` — eng muhim jadval

| Maydon | Ma'nosi | Ehtiyot bo'l |
|---|---|---|
| `stage` | `stage1` \| `stage2` \| `stage3` \| `done` | oqim qayerda to'xtaganini ko'rsatadi |
| `status` | `in_progress` \| `submitted` \| `approved` \| `rejected` | **`in_progress` — chala ariza**, HR ko'rmaydi |
| `test_score` | 0–9 | `NULL` = hali baholanmagan |
| `written_score` | 0–6 | `NULL` = hali baholanmagan |
| `video_score` | 0–4 | HR qo'yadi |
| `total_score` | 0–19 | `recompute_scores()` hisoblaydi |
| `max_total` | shu ariza necha balldan | **`0` ham haqiqiy qiymat!** `or MAX_TOTAL` yozish — bug |
| `video_is_note` | dumaloq video-xabarmi | yuborishda muhim |
| `ai_summary` | AI xulosasi | |
| `hr_note` | HR izohi | maydon bor, lekin UI da yozish tugmasi yo'q |

### `vacancies` — bosqichlarni boshqarish

`questions_mode` va `video_mode`, har biri: `required` | `optional` | `off`.
Bu ikkovi **maksimal ballni o'zgartiradi** (`stage_max()`):

| questions_mode | video_mode | max_total |
|---|---|---|
| required/optional | required/optional | 19 |
| required/optional | off | 15 |
| off | required/optional | 4 |
| off | off | **0** |

Shuning uchun ballarni solishtirganda **foiz** ishlatiladi (`score_pct()`),
xom ball emas.

## 1.6 Nomzod oqimi (hozirgi holat)

```
/start
  └ 🏢 Biz haqimizda | 📝 Ariza topshirish | 📞 Aloqa
       │
       ├ [Majburiy obuna tekshiruvi — SubscriptionMiddleware]
       │
       ├ 1) VAKANSIYA TANLASH  (inline)
       ├ 2) Rozilik ekrani  ("3 bosqich, 10-15 daqiqa, oxirida video")
       │
       ├ 3) 1-BOSQICH — ma'lumotlar (~10 qadam):
       │      ism → telefon → manzil → yosh → tillar → ma'lumot →
       │      tajriba → qo'shimcha ko'nikma → RASM → kutgan maosh
       │
       ├ 4) 2-BOSQICH — savollar   [questions_mode ga bog'liq]
       │      3 ta test (A/B/C tugma, 0/1/3 ball)  → 9 ball
       │      2 ta yozma (matn)                    → 6 ball
       │
       ├ 5) 3-BOSQICH — video      [video_mode ga bog'liq]
       │      30–60 soniya, video yoki video_note  → 4 ball (HR qo'yadi)
       │
       └ 6) YAKUN → HR ga xabar + guruhga xabar (rasm + matn + inline tugmalar)
```

**Muhim:** har bir qadamda pastda `❌ Bekor qilish` reply tugmasi turadi va
tasdiqsiz hammasini o'chiradi. Orqaga qaytish yo'q.

## 1.7 Rollar va ruxsat

`app/handlers/admin.py:33` — `get_role(user_id)`:

- `super_admin` — `.env` dagi `SUPER_ADMIN_ID` yoki `admins` jadvalida
- `hr_admin` — `admins` jadvalida
- `project_admin` — `admins` jadvalida (loyihalar uchun)

`is_hr(role)` = `role in ("hr_admin", "super_admin")` (`admin.py:40`).

⚠️ **Tekshiruv markazlashmagan** — har bir handler o'zi tekshiradi va
unutish oson. `middlewares/role_check.py` bor, lekin ishlatilmaydi.
Ya'ni ruxsat modeli **default-allow**, `default-deny` emas.

## 1.8 Callback prefikslari (routing xaritasi)

| Prefiks | Fayl | Nima uchun |
|---|---|---|
| `apply:` | jobseeker | vakansiyaga ariza boshlash |
| `edu:` | jobseeker | ma'lumot darajasi tanlash |
| `stage:` | jobseeker/screening | bosqich amallari |
| `as:` | admin | ariza qidiruvi natijalari |
| `vann:` | admin | e'lon (announcement) |
| `cd:` | screening_admin | nomzod kartochkasi (video, testlar, ball, qaror) |
| `vq:` | screening_admin | vakansiya savollari (yuklash, tahrirlash, o'chirish) |
| `vs:` | screening_admin | bitta vakansiya bosqich sozlamalari |
| `bs:` | screening_admin | ommaviy bosqich sozlamalari |
| `subscribe:` / `unsubscribe:` | client | loyiha obunasi |

⚠️ Telegram `callback_data` **64 baytdan oshmaydi**. Yangi prefiks
o'ylaganda shuni hisobga ol.

## 1.9 Baholash modeli (`app/question_bank.py:855+`)

```python
MAX_TEST = 9      # 3 savol × 3 ball
MAX_WRITTEN = 6   # 2 savol × 3 ball
MAX_VIDEO = 4
MAX_TOTAL = 19

PCT_GREEN_MIN  = 73   # yashil
PCT_YELLOW_MIN = 47   # sariq, pastrog'i qizil
```

Test javoblari 0 / 1 / 3 ball. Ranglar Excel eksportida ishlatiladi
(`excel_fill_for()`), har vakansiya alohida sheet.

## 1.10 AI qatlami

- Kalit: `.env` → `ANTHROPIC_API_KEY`; model: `claude-haiku-4-5`
- Kalit **bo'lmasa tizim eskicha ishlaydi** — HR qo'lda baholaydi.
  Har qanday yechim AI o'chiq holatda ham ishlashi shart.
- `ai_grader.py` — yozma javobni 4 mezon bo'yicha baholaydi, foizni
  modeldan olmaydi, mezonlardan **qayta hisoblaydi**.
- Nomzod matni `<nomzod_javobi>` teglari ichiga o'raladi va **ma'lumot**
  sifatida e'lon qilinadi (prompt-injection himoyasi). Bu himoyani
  zaiflashtiradigan yechim taklif qilma.

## 1.11 Migratsiya va deploy — QATTIQ QOIDALAR

Bu qoidalar real avariyalardan keyin yozilgan.

1. **Migratsiya ORM modellaridan FOYDALANMAYDI.** Faqat xom `text()` SQL.
   Sabab: `models.py` yakuniy sxemani aks ettiradi, baza esa migratsiya
   paytida oraliq holatda — ORM ishlatgan migratsiya
   `no such column: applications.max_total` bilan qulaydi (aynan shunday
   bo'lgan).
2. **Har bir migratsiya idempotent** — ikki marta ishlasa ham xato bermaydi.
3. **Dialektni tekshir.** SQLite va Postgres har xil: `PRAGMA`, `BOOLEAN
   DEFAULT 0`, `DATETIME` — Postgres da ishlamaydi.
4. **Migratsiya har doim yakuniy xabar chiqarsin** va **chiqish kodi** bilan
   muvaffaqiyatni bildirsin. `deploy.sh` matnni grep qilmaydi, exit code ga
   qaraydi.
5. **Deploy dan oldin baza zaxirasi majburiy** (`deploy.sh` avtomatik oladi).

## 1.12 Kod konvensiyalari

- Barcha foydalanuvchi matni HTML ga qo'yilishdan oldin `esc()` /
  `html.escape()` dan o'tishi kerak (hozir hamma joyda emas — bu bug).
- Telegram xabari **4096 belgi** — uzun matn `_send_long()` bilan bo'linadi.
- Inline tugma matni ~**28–30 belgi** dan oshsa kesiladi — `cut()` yordamchisi.
- Izohlar va UI matni — **o'zbekcha**. Kod nomlari inglizcha.
- Yangi ustun qo'shilsa: `models.py` + yangi `migrate_vN.py` + `deploy.sh`
  ro'yxatiga qo'shish — uchalasi birga.

---

# 2-QISM — TAHLIL PROTOKOLI

## 2.0 Asosiy qoida — BITTA BAND, BITTA JAVOB

Men senga bir vaqtda **faqat bitta band** beraman.

- Faqat o'sha band ustida ishla.
- Boshqa bandlarga o'tma, ularni "bu yerga ham tegishli" deb umumlashtirma.
- Bir necha band berilsa ham — har biriga **alohida to'liq protokol** qo'lla,
  birlashtirma.
- Javob oxirida **TO'XTA** va `Keyingi band uchun tayyorman` deb yoz.
  Men `keyingisi` demaguncha davom etma.

**Chuqurlikni kamaytirma.** Band "kichik" ko'rinsa ham barcha bosqichlarni
bajar — kichik bandlar aynan shuning uchun yillab tuzatilmay qoladi.

---

## A-BOSQICH — DALIL YIG'ISH (taxmin qilish taqiqlanadi)

Kodni **haqiqatan o'qi**. Xotiradan yoki nom bo'yicha taxmin qilma.

Yozilishi shart:
- Kamida **2 ta** tegishli joy: `fayl.py:qator` + o'sha qatorlarning **haqiqiy kodi**
- Muammoga aloqador ma'lumot sxemasi (qaysi jadval, qaysi ustun)
- Agar kodni o'qiy olmasang — `❗ O'QIY OLMADIM: <fayl>` deb yoz va
  nima kerakligini so'ra. **Taxminga asoslangan tahlil qilma.**

> Bu bosqichni o'tkazib yuborsang, keyingi hamma narsa xayoliy bo'ladi.

---

## B-BOSQICH — TAKRORLASH SSENARIYSI

Muammo aynan qanday yuz beradi:

```
Kim:              (nomzod / HR / super_admin / tashqi hujumchi)
Boshlang'ich holat: (masalan: ariza stage2 da, savollar biriktirilgan)
Qadamlar:         1) ...  2) ...  3) ...
Kutilgan natija:  ...
Haqiqiy natija:   ...
Chastota:         (har safar / faqat poyga holatida / kuniga ~N marta)
Ko'rinadimi:      (foydalanuvchi xatoni ko'radimi yoki jimgina yutiladimi)
```

❌ "Ba'zan xato bo'lishi mumkin" — javob emas.
✅ "Nomzod 4-qadamda stiker yuborsa, `message.text` `None` bo'ladi va
`.strip()` `AttributeError` beradi; webhook uni yutadi, nomzodga hech
qanday javob kelmaydi."

---

## C-BOSQICH — ILDIZ ZANJIRI (kamida 4 ta "NEGA")

```
Simptom:  ...
  Nega? → ...                                    (fayl:qator)
  Nega? → ...                                    (fayl:qator)
  Nega? → ...                                    (fayl:qator)
  Nega? → ...                                    (fayl:qator)
ILDIZ:    ...
ILDIZ TURI: [quyidagi ro'yxatdan tanla]
```

### To'xtash sharti — zanjirni faqat shu 6 turdan biriga yetganda to'xtat

| # | Ildiz turi | Belgisi |
|---|---|---|
| 1 | **Noto'g'ri taxmin** | Kod dunyo haqida noto'g'ri narsa deb o'ylaydi ("foydalanuvchi doim matn yuboradi", "faqat bitta worker bor") |
| 2 | **Yo'q bo'lgan qatlam** | Validatsiya / ruxsat / tranzaksiya / dedup qatlami umuman qurilmagan |
| 3 | **Buzilgan shartnoma** | Ikki qism bir-biridan har xil narsa kutadi (ORM ↔ migratsiya, FSM ↔ DB) |
| 4 | **Egasiz holat** | Bir ma'lumotni ikki joy boshqaradi, kelishuv yo'q (FSM va DB, ikki worker) |
| 5 | **Default noto'g'ri tomonga qaragan** | Xavfsiz bo'lmagan holat sukut bo'yicha ("tekshirilmasa — ruxsat", "status default `in_progress`") |
| 6 | **Model haqiqatga mos emas** | Ma'lumot modeli real jarayonni ifodalamaydi (bitta maydon ikki ma'noda ishlatiladi) |

### ❌ Bular ILDIZ EMAS — bu simptomning boshqacha aytilishi

- "Chunki kodda tekshiruv yo'q" → **nega yo'q?** Kim qo'shishi kerak edi,
  nega unutildi, boshqa qayerda ham unutilgan?
- "Chunki dasturchi unutgan" → **nega unutish mumkin edi?** Tizim buni
  eslatmaydimi? (bu 2-tur: yo'q bo'lgan qatlam)
- "Chunki bu eski kod" → tarix sabab emas.
- "Chunki SQLite sekin" → o'lchadingmi? Sekinlik simptom bo'lishi mumkin.

### Ildiz reyestri bilan ishlash (majburiy yakuniy qadam)

Ildizga yetganingdan keyin **`tahlil/ILDIZLAR.md`** ni och:

1. **Mos yozuv (R1, R2...) bormi?** Bo'lsa — ildizingni `R<N>` deb belgila
   va bandning zanjiri o'sha mexanizmga ulanishini **kod bilan isbotla**
   ("o'xshaydi" — rad etiladi). Reyestr yozuviga bandingni qo'shib qo'y.
   ⚠️ Havola A→L dan ozod qilmaydi — faqat C-bosqich qisqaradi.
2. **Yo'q bo'lsa** — yangi `R<N>` yozuvi yarat (reyestrdagi shablon bilan).
   Yaratishdan oldin mavjudlarini sinchiklab ko'r — dublikat ildiz yaratish
   tekshiruvchi tomonidan qaytariladi.
3. Reyestrdagi **gipotezalar (G-yozuvlar) ildiz emas** — ularga havola qilib
   bo'lmaydi. Tahliling gipotezani tasdiqlasa, uni to'liq R yozuviga aylantir;
   rad etsa — o'chirib, sababini qayd et.

---

## D-BOSQICH — TA'SIR DOIRASI (raqam bilan)

```
Kimga zarar:        ...
Nechta yozuv/odam:  ... (613 ta ariza, 24 ta vakansiya — realdan hisobla)
Qaytarib bo'ladimi: ha / yo'q — nega
Jimgina yuz beradimi: ha / yo'q
Ma'lumot yo'qoladimi: ha / yo'q
Xavfsizlikka ta'sir: ha / yo'q
Eng yomon holat:    ...
```

"Ko'p foydalanuvchiga ta'sir qiladi" — o'lchov emas. Raqam ber yoki
"o'lchay olmadim, sababi: ..." deb yoz.

---

## E-BOSQICH — QARINDOSH JOYLAR (majburiy qidiruv)

Bitta joyni tuzatib, xuddi shu ildizli 4 ta joyni qoldirish — **yuzaki yechim**.

```
Qidiruv 1: <naqsh>   → topildi: fayl:qator, fayl:qator
Qidiruv 2: <naqsh>   → topildi: ...
Xulosa:    N ta qarindosh joy bor / boshqa joy yo'q
```

Qidirgan **naqshingni ham yoz** — men uni tekshira olishim uchun.
Hech narsa topmasang: "qidirdim, `<naqsh>` bo'yicha boshqa joy yo'q"
deb aniq yoz. Bu bosqichni sukut bilan o'tkazib yuborish — protokol buzilishi.

---

## F-BOSQICH — NEGA BU ANIQLANMAY QOLDI

Bu bosqich muammoning **jarayondagi ildizini** ochadi.

```
Nega test tutmadi:     (test yo'q / lokal muhit prod dan farq qiladi / ...)
Nega monitoring ko'rmadi: (xato yutiladi / log yo'q / ...)
Nega code review o'tkazib yubordi: (naqsh ko'rinmaydi / ...)
Buni kelajakda qanday tutamiz: ...
```

Misol: `bot.py` da `screening_admin` router yo'q → saralash oqimi lokalda
umuman ishga tushmaydi → bug faqat prodda chiqadi. Bu **texnik bug emas,
lekin barcha saralash buglarining ko'payishiga sabab**.

---

## G-BOSQICH — YECHIM VARIANTLARI (kamida 3 ta)

```
A) YUZAKI — simptomni yopadi
   Nima qiladi: ...
   Kuchi: S
   ❗ NEGA YETARLI EMAS: ...        ← bu qatorni majburan yoz

B) O'RTA — sababni qisman yo'qotadi
   Nima qiladi: ...
   Kuchi: M
   Nimani hal qilmaydi: ...

C) ILDIZLI — sababni butunlay yo'qotadi
   Nima qiladi: ...
   Kuchi: M / L
   Nimani hal qilmaydi: ...
```

**Sen A variantni o'zing yozib, o'zing rad etishing shart.** Shundan keyin
yuzaki javob bilan o'tib keta olmaysan.

Agar oxir-oqibat A ni tanlasang — nega C amalga oshmasligini
(1.3-bo'limdagi cheklovlarga tayanib) ochiq asosla.

---

## H-BOSQICH — CHEKLOVLARGA MOSLIK TEKSHIRUVI

Tanlagan yechimni loyihaning haqiqiy cheklovlariga solishtir. Har biriga
✅ / ❌ / — (aloqasi yo'q) qo'y va ❌ bo'lsa yechimni o'zgartir.

| # | Cheklov | Mos |
|---|---|---|
| 1 | Bir nechta worker bilan ishlaydimi (global holat ishlatmaydimi)? | |
| 2 | Passenger ilovani o'ldirsa yashaydimi (xotirada holat yo'qmi)? | |
| 3 | Webhook 60s limitiga sig'adimi? | |
| 4 | SQLite da ishlaydimi (faqat Postgres funksiyasi emasmi)? | |
| 5 | Tashqi xizmat (Redis/Celery/cron) talab qilmaydimi? | |
| 6 | Migratsiya kerak bo'lsa — xom SQL, idempotent, dialektga mosmi? | |
| 7 | AI kaliti bo'lmaganda ham ishlaydimi? | |
| 8 | «Avto-rad yo'q» qoidasini buzmaydimi? | |
| 9 | Mavjud 613 ta arizani buzmaydimi? | |
| 10 | Telegram limitlariga sig'adimi (4096 belgi, 64 bayt callback, 30 tugma)? | |
| 11 | Nomzod uchun qadam sonini oshirmaydimi? | |
| 12 | UI matni o'zbekchami? | |

---

## I-BOSQICH — QADAMMA-QADAM YECHIM

Boshqa dasturchi savolsiz bajaradigan darajada aniq yoz:

```
Qadam 1 — fayl: app/handlers/admin.py:907, funksiya: get_cv()
  Hozir:  <haqiqiy kod>
  Bo'ladi: <yangi kod>
  Nega:   <bir jumla>

Qadam 2 — ...
```

❌ "Validatsiya qo'shish kerak"
✅ "`app/handlers/jobseeker.py:255` da `app_get_age()` boshiga
`if not message.text: return await message.answer("...")` qo'shiladi"

Agar yechim bir necha faylga tegsa — **tartibni ko'rsat** (avval qaysi,
keyin qaysi) va oraliq holatda tizim ishlab turishini tekshir.

---

## J-BOSQICH — XAVF, MIGRATSIYA, ROLLBACK

```
Nimani sindirishi mumkin:  ...
Mavjud ma'lumot bilan nima bo'ladi: ...
Migratsiya kerakmi:        ha/yo'q — kerak bo'lsa qaysi migrate_vN
Deploy tartibi muhimmi:    ...
Rollback yo'li:            ...
Zaxira yetarlimi:          ...
```

---

## K-BOSQICH — TEKSHIRUV REJASI

Yechim ishlaganini **qanday isbotlaymiz**:

```
Sinov 1 (asosiy holat):   qadamlar → kutilgan natija
Sinov 2 (chegara holati): qadamlar → kutilgan natija
Sinov 3 (regressiya):     eski xatti-harakat buzilmaganini qanday ko'ramiz
Prodda tekshirish:        (xavfsiz usul — real nomzod ma'lumotiga tegmasdan)
```

❌ "Sinab ko'rish kerak" — javob emas.

---

## L-BOSQICH — O'Z-O'ZINI TEKSHIRISH DARVOZASI

Javobni yuborishdan **oldin** o'zingni tekshir. Natijani javob oxiriga
jadval qilib qo'sh. Birortasi ❌ bo'lsa — **YUBORMA**, o'sha bosqichga
qaytib chuqurlashtir.

| # | Savol | ✅/❌ |
|---|---|---|
| 1 | Haqiqiy kodni o'qidimmi (taxmin emas)? | |
| 2 | Takrorlash ssenariysi bajarib ko'rsa bo'ladigan darajadami? | |
| 3 | Ildiz zanjirida kamida 4 ta "nega" bormi? | |
| 4 | Oxirgi "nega" 6 ta ildiz turidan biriga yetdimi? | |
| 5 | Ta'sir doirasi raqam bilan o'lchandimi? | |
| 6 | Qarindosh joylarni qidirdimmi (naqsh yozildimi)? | |
| 7 | "Nega aniqlanmay qoldi" bo'limi to'ldirildimi? | |
| 8 | Yuzaki variantni yozib, nega yetmasligini asosladimmi? | |
| 9 | 12 ta cheklov jadvali to'ldirildimi? | |
| 10 | Qadamlarda aniq fayl/funksiya/kod bormi? | |
| 11 | Rollback va migratsiya yozildimi? | |
| 12 | Tekshiruv qadamlari bajariladigan darajadami? | |

---

# 3-QISM — TAQIQLANGAN JAVOBLAR

Quyidagilar **avtomatik rad etiladi** — javobing qaytariladi:

| Taqiqlangan | Nega |
|---|---|
| "`try/except` qo'shish kerak" | Xatoni yashirish — sababni yo'qotmaydi. Bu tizimda aynan shu bug manbai. |
| "Validatsiya qo'shish kerak" | Qayerda, qanday, qaysi funksiyada — aytilmagan |
| "Refaktoring qilish kerak" / "arxitekturani yaxshilash" | O'lchanmaydigan gap |
| "Best practice bo'yicha ..." | Bu tizimga bog'lanmagan umumiy maslahat |
| `fayl:qator` siz aytilgan har qanday da'vo | Tekshirib bo'lmaydi |
| Bir nechta bandni bitta yechim bilan yopish | Har band alohida ildizga ega |
| "Redis/Celery ishlatamiz" — cheklovni tekshirmasdan | Bu muhitda mumkin emas (1.3) |
| "Past ballni avtomatik rad etamiz" | Biznes qoidasini buzadi (1.2) |
| Kodni ko'rmasdan yozilgan tahlil | Xayoliy |

## Yuzakilikning erta belgilari (o'zingda sezsang — to'xta va qayt)

- Ildiz zanjiring 2 ta "nega" da tugadi
- E-bosqichda hech narsa qidirmading
- Yechiming bitta funksiyaga bitta `if` qo'shishdan iborat
- 12 ta cheklovning hech biri "aloqasi yo'q" dan boshqa emas
- Javobing 40 qatordan qisqa

---

# 4-QISM — CHUQURLIK NAMUNASI

Farqni ko'rsatish uchun bitta real band.

### Band: `C2 — Test tugmasini 2 marta bosish → ball 9 dan oshadi`

#### ❌ YUZAKI JAVOB (bunday qilma)

> Muammo: `create_answer` dedup qilmaydi. Yechim: `application_answers`
> jadvaliga `UNIQUE(application_id, question_id)` qo'shish kerak.

Nega yomon: kodni ko'rsatmadi, ildizga tushmadi, mavjud dublikatlar bilan
nima bo'lishini aytmadi, `question_id` `NULL` bo'lishi mumkinligini
sezmadi, migratsiya rejasi yo'q, boshqa qayerda shunday muammo borligini
qidirmadi.

#### ✅ CHUQUR JAVOB (skelet)

- **A. Dalil:** `jobseeker.py:558` (callback → `create_answer`),
  `crud.py:499` (`create_answer` — faqat `INSERT`), `models.py:136`
  (`ApplicationAnswer` — `question_id` **nullable**, unique yo'q).
- **B. Ssenariy:** nomzod sekin internetda variantni ikki marta bosadi →
  ikkita `INSERT` → `recompute_scores()` ikkalasini qo'shadi → `test_score`
  11 bo'ladi → `total_score` 19 dan oshadi → foiz 100% dan yuqori →
  Excel da yashil, aslida o'rtacha nomzod.
- **C. Ildiz zanjiri:** ... → `create_answer` yozuvni identifikatsiya
  qilmaydi → chunki javob "hodisa" deb modellashtirilgan, "holat" emas →
  **ILDIZ TURI 6: model haqiqatga mos emas** (bitta savolga bitta javob
  bo'lishi kerak, lekin model cheksiz javobga ruxsat beradi).
- **D. Ta'sir:** 613 arizadan nechtasida dublikat borligini SQL bilan
  o'lchash mumkin — javobda aniq so'rov beriladi.
- **E. Qarindosh joylar:** `create_*` chaqiruvlari orasida dedupsizlari;
  `cd:` va `apply:` callbacklarida ham takror bosish himoyasi yo'qmi.
- **F. Nega aniqlanmadi:** lokal `bot.py` da screening router yo'q →
  bu oqim umuman sinalmagan.
- **G. Variantlar:** A) tugmani bosgandan keyin o'chirish (faqat UI —
  poyga qoladi) ❗yetarli emas, B) `UNIQUE` + `INSERT OR IGNORE`,
  C) callback ichiga savol indeksini kiritib eskirgan bosishni rad etish
  + `UNIQUE` (ildizli).
- **H–L:** mavjud dublikatlarni migratsiyada tozalash (qaysi qatorni
  qoldirish qoidasi bilan), `question_id IS NULL` holati, rollback,
  sinov qadamlari.

Farq — bir xil g'oyaning "aytilgani" va "isbotlangani" orasida.

---

# 5-QISM — JAVOB SHABLONI

Har bir javobni aynan shu tartibda ber:

```markdown
# <BAND ID> — <sarlavha>

## A. Dalil
## B. Takrorlash ssenariysi
## C. Ildiz zanjiri
   ILDIZ TURI: <1–6>
   REYESTR: R<N> (mavjud/yangi) — ILDIZLAR.md bilan bog'lanish
## D. Ta'sir doirasi
## E. Qarindosh joylar
## F. Nega aniqlanmay qoldi
## G. Yechim variantlari (A/B/C)
## H. Cheklovlarga moslik (12 ta)
## I. Qadamma-qadam yechim
## J. Xavf, migratsiya, rollback
## K. Tekshiruv rejasi
## L. O'z-o'zini tekshirish darvozasi

**Ishonch:** Yuqori / O'rta / Past
**Tekshira olmadim:** ...

Keyingi band uchun tayyorman.
```

---

# 6-QISM — ISH SIKLI VA BOSHLASH

## Ikki rolli sikl

Har bir band shu sikldan o'tadi:

```
1. TAHLILCHI (sen):  bandni A→L bo'yicha tahlil qiladi
                     va javobni tahlil/<BAND>.md fayliga yozadi
                          │
2. TEKSHIRUVCHI:     alohida agent AI_TEKSHIRUV_PROTOKOLI.md bo'yicha
   (boshqa agent)    tahlilni T1–T8 auditidan o'tkazadi
                          │
              ┌───────────┴───────────┐
        ✅ QABUL                ❌ QAYTARILADI
   keyingi bandga o'tiladi     tahlilchi FAQAT ko'rsatilgan
                               bosqichlarni tuzatib qayta beradi
                               (sikl 2-qadamga qaytadi)
```

Tahlilchi sifatida sen:
- Tekshiruvchidan qaytgan topshiriqni bahslashmasdan ko'rib chiq: haq bo'lsa —
  tuzat; nohaq deb hisoblasang — dalil bilan javob yoz (foydalanuvchi hakam).
- Tekshiruvchining ishini o'zing bajarma (o'zingga o'zing "QABUL" hukmi
  chiqarish taqiqlanadi) — L-jadval sening ichki nazorating, T1–T8 esa
  tashqi audit; ikkalasi har xil odam (agent) tomonidan bajarilishi shart.

## Arxiv — tizimning doimiy xotirasi (majburiy)

Chat seansi tugasa bilim yo'qoladi; arxiv esa qoladi. Shuning uchun:

**Har seans BOSHIDA (birinchi banddan oldin):**
1. `tahlil/INDEX.md` ni o'qi — qaysi bandlar tahlil qilingan, qaysilari
   qaytarilgan, jarayon qayerda turganini bilib ol.
2. `tahlil/ILDIZLAR.md` ni o'qi — tasdiqlangan ildizlar (R) va gipotezalar (G)
   bilan tanish; C-bosqichda ular bilan ishlash qoidasi o'sha yerda va
   C-bosqich oxirida yozilgan.
3. Berilgan bandga qarindosh bo'lishi mumkin bo'lgan, avval ✅ QABUL olgan
   tahlillar bo'lsa (`tahlil/<BAND>.md`) — ularni ham o'qi. Ildiz mos kelsa
   havola qil, lekin **moslikni kod bilan qayta isbotla** — "o'xshaydi" degani
   bilan o'tib ketma.

**Har tahlildan KEYIN:**
1. To'liq javobni `tahlil/<BAND>.md` ga yoz — `tahlil/README.md` dagi shablon
   bo'yicha (frontmatter + A→L + bo'sh TEKSHIRUV TARIXI bo'limi).
   `TEKSHIRUV TARIXI` bo'limiga o'zing hech narsa yozma — u tekshiruvchiniki.
2. `tahlil/INDEX.md` da **faqat o'z qatoringni** yangila:
   Tahlil → 📝, Ildiz/Variant/Fayl ustunlarini to'ldir. Boshqa qatorlarga
   va "Kod holati" ustuniga tegma.
3. `tahlil/ILDIZLAR.md` ni yangila: mavjud R ga banding qo'shildi yoki yangi
   R yaratildi (C-bosqich qoidasi bo'yicha). Hukm ✅ QABUL bo'lgach — gipoteza
   ishlatilgan bo'lsa uni R ga aylantirish va "Ildiz → bandlar xaritasi"
   jadvalini yangilashni unutma.

Fayl yoza olmaydigan muhitda bo'lsang — javobni to'liq chatda qoldir va
foydalanuvchidan saqlashni so'ra; INDEX yangilanishini ham matn ko'rinishida
ber ("INDEX.md ga: S1 qatori → 📝, ildiz 2, variant C").

## Boshlash

Bu faylni o'qib bo'lgach:

1. `Tayyor` deb yoz.
2. Loyiha haqida **noaniq qolgan 1–3 savolingni** ber (agar bo'lsa).
3. Mendan birinchi bandni so'ra.

Keyin men band beraman — sen A→L bosqichlarni to'liq bajarasan,
`tahlil/<BAND>.md` ga yozasan va TO'XTAYSAN.
