# ILDIZ REYESTRI
### Nuriddin Building HR-bot — tasdiqlangan tub sabablar ro'yxati

> Maqsad: 71 ta bandning ortida 71 ta emas, **8–10 ta haqiqiy ildiz** turibdi.
> Bu fayl o'sha ildizlarni to'playdi. Tizimni "ideal" qiladigan reja oxirida
> shu reyestrdan chiqadi — bandma-band yamoqlardan emas.

---

## FOYDALANISH QOIDALARI

### Tahlilchi uchun

1. **C-bosqichda ildizga yetganingda avval shu reyestrni ko'r.**
2. **Mos ildiz TOPILSA** (masalan R2):
   - Band tahlilida ildizni `R2` deb belgila va bu bandning zanjiri R2 ga
     qanday ulanishini **kod bilan isbotla** — "o'xshaydi" degani rad etiladi.
     Isbot = shu bandning o'z `fayl:qator` zanjiri + R2 tavsifidagi mexanizm
     aynan shu joyda ham ishlayotganini ko'rsatish.
   - ⚠️ Reyestrga havola **A→L bosqichlardan ozod qilmaydi.** Faqat
     C-bosqich qisqaradi (zanjir R2 ga ulangunicha yoziladi) — qolgan
     bosqichlar to'liq bajariladi. B, D, E, G–K bandga xos bo'lib qoladi.
   - Reyestrdagi R2 yozuviga bandingni qo'shib qo'y (Bandlar qatoriga).
3. **Mos ildiz TOPILMASA:**
   - Yangi yozuv yarat: navbatdagi `R<N>` raqami bilan, quyidagi shablonda.
   - Yangi yozuv yaratishdan oldin mavjudlarini diqqat bilan ko'r — bitta
     ildizni ikki nom bilan ikki marta yozish reyestrni qadrsizlantiradi.
4. Ikki ildizni **birlashtirish** yoki yozuvni **tahrirlash** — faqat dalil
   bilan va o'zgarish sababini yozuv tarixiga qo'shib.

### Tekshiruvchi uchun (T3 ga qo'shimcha)

- Tahlilchi mavjud R ga havola qilgan bo'lsa: **moslik chinmi?** Bandning
  zanjiri haqiqatan o'sha mexanizmga ulanadimi, yoki dangasalik bilan eng
  yaqin yozuvga yopishtirilganmi — kodni ochib tekshir.
- Tahlilchi yangi R yaratgan bo'lsa: **dublikat emasmi?** Mavjud yozuvlar
  bilan solishtir; aslida bir xil bo'lsa — qaytar.
- Gipoteza (G-yozuv) haqiqiy R ga faqat band ✅ QABUL olgandagina aylanadi.

### Yozuv shabloni

```markdown
### R<N> — <qisqa nom>
- **Turi:** <1–6> (<tur nomi>)
- **Tavsif:** bitta xatboshi — mexanizm qanday ishlaydi
- **Asosiy dalil:** fayl:qator, fayl:qator
- **Bandlar:** S2 (✅ QABUL), S3 (📝 tahlilda), ...
- **Tub yechim yo'nalishi:** 1-2 jumla — bu ildizni butunlay yo'qotadigan o'zgarish
- **Holat:** ochiq / qisman yechilgan / yechilgan
- **Tarix:** <sana> yaratildi (<band> tahlilida); <sana> <o'zgarish>
```

---

## REYESTR (tasdiqlangan ildizlar)

### R1 — Nomzod javobi "hodisa" deb modellashtirilgan, "holat" emas
- **Turi:** 6 (model ≠ haqiqat)
- **Tavsif:** Biznes-qoida "1 savol = 1 javob", lekin `application_answers`
  jadvali buni majburlamaydi — UNIQUE cheklov yo'q, `create_answer` shartsiz
  INSERT. Qoida faqat handler'lardagi atomik bo'lmagan tekshiruvlar (test:
  check-then-act; yozma: faqat FSM indeksi) bilan "ushlab turiladi" — ko'p
  workerli muhitda bu yetarli emas. Ballar `sum()` bilan hisoblanadi, shuning
  uchun har dublikat qator reytingni shishiradi.
- **Asosiy dalil:** models.py:136-149 (UNIQUE yo'q), crud.py:632-643
  (shartsiz INSERT), jobseeker.py:631-642 (check-then-act), jobseeker.py:678-695
  (yozma — himoyasiz), jobseeker.py:809-810 (`sum()`)
- **Bandlar:** C2 (✅ QABUL — tahlil/C2.md), N5 (ehtimoliy — tahlil kutilmoqda)
- **Tub yechim yo'nalishi:** partial UNIQUE indeks `(application_id,
  question_id) WHERE question_id IS NOT NULL` + mavjud dublikatlarni tozalash
  + `create_answer` ni idempotent qilish (`ON CONFLICT DO NOTHING`) —
  batafsil reja tahlil/C2.md I-bosqichida.
- **Holat:** ochiq (yechim rejasi tasdiqlangan, kodga joriy etilmagan)
- **Tarix:** 2026-08-08 yaratildi (C2 tahlilida, G6 gipotezasidan
  tasdiqlanib ko'chirildi)

---

## BOSHLANG'ICH GIPOTEZALAR (⚠️ TASDIQLANMAGAN)

Quyidagilar 2026-07-23 auditidan kelib chiqqan **taxminlar** — hali birorta
band protokol bo'yicha tahlil qilinib isbotlangani yo'q. Tahlilchi ular
bilan ishlashi mumkin, lekin:

- Gipotezaga havola qilish mumkin emas — u hali ildiz emas.
- Tahliling gipotezani **tasdiqlasa** — uni yuqoridagi REYESTR ga to'liq
  shablon bilan ko'chir (G raqamini yangi R raqamiga almashtirib) va bu
  bo'limdan o'chir.
- Tahliling gipotezani **rad etsa** — uni o'chirib, sababini shu yerning
  o'zida bir qator bilan qayd et ("G3 rad etildi: <sabab>, qarang
  tahlil/<BAND>.md").

### G1 — Markazlashgan ruxsat qatlami yo'q (default-allow)
- Taxminiy turi: 2 (yo'q qatlam) + 5 (noto'g'ri default)
- Har handler ruxsatni o'zi tekshiradi; unutilgan joyda hamma narsa ochiq.
  `middlewares/role_check.py` bor, lekin ulanmagan.
- Ehtimoliy bandlar: S1, S2, H-guruh qismlari

### G2 — Foydalanuvchi matni uchun escape shartnomasi yo'q
- Taxminiy turi: 2 (yo'q qatlam)
- `esc()` chaqirish har xabar tuzuvchining o'z xotirasiga qoldirilgan;
  markaziy "chiqishda doim escape" qoidasi yo'q.
- Ehtimoliy bandlar: S3

### G3 — Webhook sinxron ishlaydi va xatoni yutadi
- Taxminiy turi: 1 (noto'g'ri taxmin: "har update tez va muvaffaqiyatli
  qayta ishlanadi")
- Uzoq amal → Telegram retry → dublikat; xato → `except` yutadi → 200 OK →
  nomzod jim qoladi. Bitta dizayn qaroridan ikki oila muammo.
- Ehtimoliy bandlar: C1, N2 qoldiqlari, I-guruh qismlari

### G4 — Holatning egasi aniqlanmagan (FSM ↔ DB ↔ workerlar)
- Taxminiy turi: 4 (egasiz holat)
- FSM data butun JSON bo'lib qayta yoziladi, SQLite'da WAL/timeout yo'q,
  bir foydalanuvchi holatini ikki worker bir vaqtda o'zgartira oladi.
- Ehtimoliy bandlar: C3, C4, C5, N5

### G5 — Lokal muhit prod bilan mos emas
- Taxminiy turi: 3 (buzilgan shartnoma: "lokalda ishlasa prodda ham ishlaydi")
- `bot.py` da screening router yo'q; lokal Postgres, prod SQLite. Saralash
  oqimi faqat prodda sinaladi — buglar shuning uchun kech chiqadi.
- Ehtimoliy bandlar: FD4, I-guruh qismlari; ko'p bandlarning F-bosqichida
  "nega aniqlanmadi" javobi ham shu.

*(G6 — 2026-08-08 da C2 tahlili tasdiqlagach R1 ga ko'chirildi.)*

---

## ILDIZ → BANDLAR XARITASI

(✅ QABUL olgan bandlar qo'shilgani sari to'ldiriladi; INDEX.md bilan bir xil
ma'lumot emas — bu yerda faqat tasdiqlanganlar, ildiz kesimida)

| Ildiz | Turi | Bandlar | Holat |
|---|---|---|---|
| R1 — javob "hodisa", "holat" emas | 6 | C2 ✅ | ochiq (reja bor) |
