# -*- coding: utf-8 -*-
"""
Saralash savollari banki — «NURIDDIN BUILDING» HR-bot.

Manba: «HR Bot Video.docx» (kasbiy darajadagi test savollari + har rolga
majburiy video-savol). Bu fayl hujjatdan avtomatik generatsiya qilingan.

Har vakansiya uchun:
  • 3 ta test savoli — variantlar 3 / 1 / 0 ball (eng to'g'ri / qisman / yaroqsiz)
  • 2 ta yozma savol — HR (keyinchalik AI) 0-3 ball beradi
  • 1 ta majburiy video-savol — HR 0-4 ball beradi

Jami: test 9 + yozma 6 + video 4 = 19 ball.
Ball qiymatlari nomzodga KO'RSATILMAYDI; variantlar har safar aralashtiriladi.
"""

# Yozma savollar uchun standart baholash mezonlari
RUBRIC_LOGIC = "Mavzuga aloqadorlik, mantiqiy izchillik va chuqurlik, aniq misol, savodxonlik. (0-3)"
RUBRIC_AI = "Prompt/yechim aniqligi va amaliyligi, AI'dan to'g'ri foydalanish tushunchasi, natijaga yo'naltirilganlik. (0-3)"
RUBRIC_MOTIVATION = "Samimiylik, aniq shaxsiy tajriba/misol, sohaga qiziqish va mas'uliyat hissi. (0-3)"

# Video-savol uchun umumiy ko'rsatma (har rolning o'z savoli oldidan chiqadi)
VIDEO_INTRO = (
    "Avval o'zingizni qisqacha tanishtiring (~10 soniya), so'ng savolga javob bering."
)
VIDEO_RUBRIC = "Nutq va ishonch (0-2) + mazmun va rolga moslik (0-2). Format bahoga ta'sir qilmaydi."

QUESTION_BANK = {
    "ceo": {
        "title": "CEO (Bosh direktor)",
        "test": [
            {
                "text": "Kompaniyada 4 oyga yetadigan naqd pul (runway) qoldi, daromad har oy ~7% pasaymoqda. Investor qo‘shimcha mablag‘ni faqat birlik iqtisodi (unit-economics) barqaror bo‘lsa beradi. Birinchi qadamingiz?",
                "options": [
                    {"text": "Runway’ni uzaytirish uchun eng past qaytimli yo‘nalishlarni to‘xtatib, musbat marja beruvchi yadro biznesga fokuslanaman va investorga LTV/CAC dinamikasini ko‘rsataman", "score": 3},
                    {"text": "Investor ishonchi uchun darhol yangi bozorga chiqib, o‘sish sur’atini (growth) ko‘rsataman", "score": 1},
                    {"text": "Barcha bo‘limlar byudjetini bir tekis 20% qisqartirib, jamoani to‘liq saqlab qolaman", "score": 0},
                ],
            },
            {
                "text": "Bo‘limlar sizga AI generatsiya qilgan prognoz va tahlillar asosida qaror so‘rab kelmoqda. Qanday yondashasiz?",
                "options": [
                    {"text": "AI natijasining manba ma’lumoti va farazlarini tekshirib, o‘z kontekstim bilan solishtiraman; xato narxi yuqori qarorlarda inson tekshiruvini majburiy qilaman", "score": 3},
                    {"text": "AI ko‘p ma’lumotga tayangani uchun tavsiyalarini asosan qabul qilib, tez qaror chiqaraman", "score": 1},
                    {"text": "AI xato qilishi mumkinligi uchun uni deyarli hisobga olmay, asosan intuitsiyaga tayanaman", "score": 0},
                ],
            },
            {
                "text": "Eng ko‘p daromad keltiradigan bo‘lim boshlig‘i (jami sotuvning 35%) jamoada qo‘rquv muhiti yaratmoqda; 3 ta kuchli xodim ariza berdi. Nima qilasiz?",
                "options": [
                    {"text": "Rahbar bilan o‘lchanadigan xatti-harakat maqsadlari va muddat belgilab, natija saqlangan holda madaniyat tuzatilishini talab qilaman; yaxshilanmasa ajrashaman", "score": 3},
                    {"text": "Daromad muhim bo‘lgani uchun hozircha saqlab, ketmoqchi bo‘lgan xodimlarga qo‘shimcha rag‘bat berib ushlab qolaman", "score": 1},
                    {"text": "Madaniyat muhimroq deb, rahbarni tez orada almashtirishga kirishaman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Kompaniyaning 12 oylik o‘sish rejasini shakllantiring: 3 ta yetakchi metrika (masalan LTV/CAC, marja, retention), ularning taxminiy joriy qiymati va aniq maqsadingiz.", "rubric": RUBRIC_LOGIC},
            {"text": "Yillik strategiyani tahlil qilish uchun AIga prompt yozing: rol, kontekst ma’lumoti, aniq vazifa va chiqish formati ko‘rsatilgan.", "rubric": RUBRIC_AI},
        ],
        "video": "Kompaniyani boshqarishda yetakchilik uslubingiz qanday? Birinchi 3 oyda aynan nimaga e’tibor qaratardingiz?",
    },
    "prorab": {
        "title": "Prorab (Qurilish ishlari boshlig‘i)",
        "test": [
            {
                "text": "Monolit ishlar 12 kun orqada. Buyurtmachi jarima bilan bosim o‘tkazmoqda, prognozda 5 kun yomg‘ir. Nima qilasiz?",
                "options": [
                    {"text": "Tanqidiy yo‘lni (critical path) qayta hisoblab, ob-havoga bog‘liq bo‘lmagan ishlarni oldinga suraman, resursni qayta taqsimlab, buyurtmachiga asosli yangi grafik + choralar rejasini beraman", "score": 3},
                    {"text": "Ikki smena joriy qilib, ishchi sonini oshirib, sur’atni majburan tezlashtiraman", "score": 1},
                    {"text": "Kechikish yomg‘ir sabab bo‘lgani uchun jarima haqsizligini yozma bildirib, ob-havo yaxshilanishini kutaman", "score": 0},
                ],
            },
            {
                "text": "Beton quyilgandan keyin havo +32°C, quyosh kuchli. Beton sifatini saqlash uchun nima qilasiz?",
                "options": [
                    {"text": "Betonni parvarish (uxod) qilaman: namlab, yopib, gidratatsiya rejimini saqlayman va zarur bo‘lsa rejim/qo‘shimchani moslashtiraman", "score": 3},
                    {"text": "Ustiga bir marta suv sepib, keyin o‘z holiga qo‘yaman", "score": 1},
                    {"text": "Tez qotishi uchun betonni ochiq, quyoshda qoldiraman", "score": 0},
                ],
            },
            {
                "text": "Yuqori qavatda usta himoya kamarisiz ishlayapti, obyekt topshirishga 2 kun qoldi, brigadir “to‘xtatsak ulgurmaymiz” deyapti. Nima qilasiz?",
                "options": [
                    {"text": "Ishni darhol to‘xtatib, himoya vositasini ta’minlab, yo‘riqnoma o‘tkazaman; xavfsizlik grafik bahonasida chetlab o‘tilmaydi", "score": 3},
                    {"text": "Bugun tugatishga ruxsat berib, ertadan qat’iy nazorat o‘rnataman", "score": 1},
                    {"text": "Usta tajribali bo‘lgani uchun o‘z javobgarligiga qoldiraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "3 brigada parallel ishlayotgan obyektda tanqidiy yo‘l va resurs to‘qnashuvini kunlik qanday boshqarasiz? Qadam-baqadam yozing.", "rubric": RUBRIC_LOGIC},
            {"text": "Obyektda sifat yoki muddatni yaxshilagan aniq tajribangizni avval/keyin ko‘rsatkichi bilan yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Obyektda sifat yoki xavfsizlik uchun qabul qilgan eng muhim qaroringizni ayting — vaziyat qanday edi va nima qildingiz?",
    },
    "texnik_nazoratchi": {
        "title": "Texnik nazoratchi",
        "test": [
            {
                "text": "Monolit ustunda beton himoya qatlami (zashitniy sloy) loyihada 25 mm, obyektda ba’zi joyda 15 mm. Pudratchi “ahamiyatsiz” deyapti, buyurtmachi tez qabulni so‘rayapti. Nima qilasiz?",
                "options": [
                    {"text": "Chetlanishni dalolatnoma va foto bilan qayd qilib, loyihachidan yozma xulosa (kelishish yoki tuzatish) talab qilaman; xulosagacha qabul qilmayman", "score": 3},
                    {"text": "Kichik farq bo‘lgani uchun ro‘yxatga olib, keyingi nazorat sharti bilan qabul qilaman", "score": 1},
                    {"text": "Pudratchi kafolat maktubi bersa, o‘tkazib yuboraman", "score": 0},
                ],
            },
            {
                "text": "Ochiq armatura karkasini qabul qilyapsiz. Birinchi navbatda nimani tekshirasiz?",
                "options": [
                    {"text": "Armatura diametri, qadamlari (shag), anker va ulanish (nahlyost) uzunligini loyiha va ShNQ bilan solishtirib, foto-fiksatsiya qilaman", "score": 3},
                    {"text": "Umumiy ko‘rinishi va zichligini ko‘z bilan baholab, mustahkam ko‘rinsa qabul qilaman", "score": 1},
                    {"text": "Pudratchining ijro sxemasiga (ispolnitelnaya) ishonaman", "score": 0},
                ],
            },
            {
                "text": "Materialning sertifikati va hujjatlari to‘g‘ri, lekin partiyaning bir qismida yoriq va rang farqi bor. Nima qilasiz?",
                "options": [
                    {"text": "Namuna olib laboratoriya sinovini talab qilaman, shubhali partiyani ajratib, natijagacha ishlatishni to‘xtataman", "score": 3},
                    {"text": "Faqat yaroqsiz ko‘ringanini chetga surib, qolganini o‘tkazaman", "score": 1},
                    {"text": "Hujjat joyida bo‘lgani uchun to‘liq qabul qilaman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Yashirin ishlarni (armatura, gidroizolyatsiya, zichlash) qoplashdan oldin qabul qilish tartibini va qaysi hujjatlar rasmiylashtirilishini yozing.", "rubric": RUBRIC_LOGIC},
            {"text": "Hujjat to‘g‘ri, lekin obyekt real holati mos kelmagan holatni aniqlagan tajribangizni yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Ko‘pchilik “o‘tkazib yuboraylik” degan, lekin siz e’tiroz bildirgan holatni ayting — nega qat’iy turdingiz?",
    },
    "kran_muhandisi": {
        "title": "Kran muhandisi",
        "test": [
            {
                "text": "Minora kran yuk-moment cheklovchisi (OGP) ba’zan noto‘g‘ri ishlayotganini sezdingiz, ish grafigi zich. Nima qilasiz?",
                "options": [
                    {"text": "Kranni ishdan chetlab, OGP ni tekshirtiraman/sozlataman; cheklovchi ishlamasa ekspluatatsiya taqiqlanadi, holatni jurnalga yozaman", "score": 3},
                    {"text": "Yukni pasport quvvatidan ancha past tutib, ehtiyotkorlik bilan ishlatib turaman", "score": 1},
                    {"text": "Cheklovchi ba’zan ishlagani uchun keyingi rejali ko‘rikkacha davom ettiraman", "score": 0},
                ],
            },
            {
                "text": "Kran po‘lat arqonini (kanat) qachon almashtirishni nimaga qarab belgilaysiz?",
                "options": [
                    {"text": "Bir qadamda (shag) uzilgan simlar soni, yeyilish, korroziya va deformatsiyani brakovka me’yorlari bo‘yicha tekshirib belgilayman", "score": 3},
                    {"text": "Tashqi ko‘rinishi sezilarli yomonlashsa almashtiraman", "score": 1},
                    {"text": "Faqat ishlab chiqaruvchi ko‘rsatgan muddat o‘tganda almashtiraman", "score": 0},
                ],
            },
            {
                "text": "Shamol tezligi ruxsat etilgan chegaraga yaqinlashdi (14 m/s, chegara 15 m/s), yuk yarim yo‘lda. Nima qilasiz?",
                "options": [
                    {"text": "Yukni eng yaqin xavfsiz joyga tushirib, ishni to‘xtataman va kranni bo‘shatib (flyuger rejimi) qo‘yaman", "score": 3},
                    {"text": "Yukni tezda mo‘ljalga yetkazib, keyin ishni to‘xtataman", "score": 1},
                    {"text": "Chegaraga hali yetmagani uchun ishni davom ettiraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Kranning smenali texnik ko‘rigi checklistini yozing: qaysi tugunlar, cheklovchilar va hujjatlar tekshiriladi?", "rubric": RUBRIC_LOGIC},
            {"text": "Nosozlik yoki metall charchoqni erta aniqlab, avariyaning oldini olgan tajribangizni yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Texnik nosozlik yoki metall charchoqni erta aniqlab, avariyaning oldini olgan holatingizni ayting.",
    },
    "sotuv_menejeri": {
        "title": "Sotuv menejeri",
        "test": [
            {
                "text": "Yirik mijoz og‘zaki “ha” dedi, lekin 2 hafta shartnoma imzolamayapti va qo‘ng‘iroqlarga kech javob beryapti. Nima qilasiz?",
                "options": [
                    {"text": "Asl to‘siqni aniqlash uchun bosimsiz to‘g‘ridan-to‘g‘ri savol beraman (“imzoni nima to‘xtatib turibdi?”), qaror qabul qiluvchi va muddatni aniqlayman", "score": 3},
                    {"text": "Chegirma yoki bonus taklif qilib, imzoga undayman", "score": 1},
                    {"text": "Bosim qilmaslik uchun kutaman, o‘zi tayyor bo‘lganda bog‘lanadi deb", "score": 0},
                ],
            },
            {
                "text": "Voronkangizda 40 ta “issiq” lid bor, lekin vaqt cheklangan. Qaysi biriga birinchi fokuslanasiz?",
                "options": [
                    {"text": "Ehtiyoji tasdiqlangan, byudjeti va qaror qabul qiluvchisi aniq (BANT bo‘yicha yetuk) lidlarga", "score": 3},
                    {"text": "Eng katta summa va’da qilgan lidlarga", "score": 1},
                    {"text": "Eng birinchi murojaat qilgan lidlarga navbat bilan", "score": 0},
                ],
            },
            {
                "text": "Sovuq bazaga (500 kontakt) murojaat matni kerak. AIdan qanday foydalanasiz?",
                "options": [
                    {"text": "Segment va og‘riq nuqtaga moslab bir necha variant generatsiya qilib, kichik guruhda A/B test qilaman, javob berganini shaxsiylashtiraman", "score": 3},
                    {"text": "AIga bitta universal matn yozdirib, hammaga bir xil yuboraman", "score": 1},
                    {"text": "Tayyor shablonni o‘zgartirmay yuboraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Mijoz telefonda jahl bilan shartnomani bekor qilmoqchi. Saqlab qolish uchun ilk 3 gapingizni aynan yozing va nega shunday deganingizni bir jumlada asoslang.", "rubric": RUBRIC_LOGIC},
            {"text": "Sovuq mijozga birinchi xabar uchun AIga prompt yozing: segment, og‘riq nuqta, ohang va chiqish formati ko‘rsatilgan.", "rubric": RUBRIC_AI},
        ],
        "video": "Meni shu yerdayoq, 30 soniyada kompaniya mahsulotini xarid qilishga qiziqtiring.",
    },
    "it_mutaxassisi": {
        "title": "IT mutaxassisi",
        "test": [
            {
                "text": "Ishlab chiqarish bazasi ishlamayapti. Oxirgi zaxira (backup) 6 soatlik, undan keyingi tranzaksiyalar unda yo‘q. Nima qilasiz?",
                "options": [
                    {"text": "Avval tizimni izolyatsiya qilib diagnostika qilaman; zaxiradan tiklashdan oldin 6 soatlik ma’lumot yo‘qolishi va tranzaksiya log‘idan (point-in-time) tiklash imkonini baholab, keyin qaror qilaman", "score": 3},
                    {"text": "Vaqt yo‘qotmaslik uchun darhol 6 soatlik zaxiradan tiklab, ishni yo‘lga qo‘yaman", "score": 1},
                    {"text": "Sababni to‘liq topmaguncha hech narsaga tegmayman", "score": 0},
                ],
            },
            {
                "text": "Botning API kaliti (token) tasodifan GitHub’ga yuklanganini aniqladingiz. Nima qilasiz?",
                "options": [
                    {"text": "Kalitni darhol bekor qilib (revoke) yangisini generatsiya qilaman, log‘lardan suiiste’mol bor-yo‘qligini tekshiraman, sirlarni .env / secret menejerga o‘tkazaman", "score": 3},
                    {"text": "Repozitoriyni privat qilib, o‘sha kommitni o‘chiraman", "score": 1},
                    {"text": "Kalit hali ishlayotgani uchun keyinroq almashtiraman", "score": 0},
                ],
            },
            {
                "text": "Telegram bot foydalanuvchi soni oshib, sekinlashib qoldi. Birinchi qadamingiz?",
                "options": [
                    {"text": "Monitoring bilan tor bo‘g‘inni (DB so‘rovlari, tashqi API, CPU/xotira) o‘lchab aniqlab, so‘ng aniq sababga qarab optimallashtiraman (indeks, kesh, navbat)", "score": 3},
                    {"text": "Serverni kuchliroq tarifga (resurs) ko‘taraman", "score": 1},
                    {"text": "Kodni noldan qayta yozishni boshlayman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Botlar va veb-sayt uzluksizligi uchun monitoring, ogohlantirish (alerting) va zaxiralash tizimini qanday qurasiz? RTO/RPO ni qanday belgilaysiz?", "rubric": RUBRIC_LOGIC},
            {"text": "Kompaniya jarayonidan bittasini avtomatlashtirish yechimingizni yozing: texnologiya steki, integratsiya va kutilgan samara (vaqt/xato).", "rubric": RUBRIC_AI},
        ],
        "video": "Hal qilgan eng murakkab texnik muammoingizni va uni qanday yechganingizni ayting.",
    },
    "mobilograf": {
        "title": "Mobilograf (Video operator)",
        "test": [
            {
                "text": "3 soniyada e’tiborni ushlaydigan Reels kerak. Qaysi yondashuv eng samarali?",
                "options": [
                    {"text": "Kuchli vizual yoki savolli “hook” bilan boshlab, dinamik kadr, tez montaj va subtitr bilan retention’ni ushlab turaman", "score": 3},
                    {"text": "Sifatli, chiroyli, lekin sekin kirish (intro/logotip) bilan boshlayman", "score": 1},
                    {"text": "Jarayonni ketma-ket, montajsiz ko‘rsataman", "score": 0},
                ],
            },
            {
                "text": "Quyoshli kunda tashqarida olyapsiz, kadr juda yorug‘ (peresvet). Nima qilasiz?",
                "options": [
                    {"text": "ISO past qilib, diafragma va zatvor tezligini sozlayman, kerak bo‘lsa ND-filtr ishlataman va yorug‘likka teskari olishdan qochaman", "score": 3},
                    {"text": "Telefonda avtomatik rejimda olib, keyin montajda yorqinlikni tushiraman", "score": 1},
                    {"text": "Shundoq olib, tahrirda tuzataman", "score": 0},
                ],
            },
            {
                "text": "Muddat ertaga ertalab, montaj yarim bo‘ldi, mijoz sifatni talab qilyapti. Nima qilasiz?",
                "options": [
                    {"text": "Ssenariyni eng ta’sirli 3–4 kadrga qisqartirib, tayyor preset/shablon bilan yakuniy sifatni saqlagan holda ustuvor qismni bitiraman", "score": 3},
                    {"text": "Tunab bo‘lsa ham hamma rejalashtirilgan kadrni to‘liq montaj qilaman", "score": 1},
                    {"text": "Sifatni pasaytirib, tez topshiraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Qurilish kompaniyasi uchun 30 kunlik kontent-reja tuzing: 3–4 format, chastota va har birining maqsadi (tanilish, ishonch, lid).", "rubric": RUBRIC_LOGIC},
            {"text": "Bitta Reels ssenariysi uchun AIga prompt yozing: hook, davomiylik, ohang, maqsadli auditoriya va CTA ko‘rsatilgan.", "rubric": RUBRIC_AI},
        ],
        "video": "Bu videoning o‘zini mobilograf sifatida qiziqarli qilib oling (kadr, yorug‘lik, montaj) va o‘zingizni tanishtiring — bu sizning ish namunangiz.",
    },
    "hr_menejer": {
        "title": "HR menejer",
        "test": [
            {
                "text": "2 hafta ichida malakali prorab kerak, oddiy e’lonlar ishlamayapti. Qanday yondashasiz?",
                "options": [
                    {"text": "Aniq profil tuzib, faol sourcing (soha chatlari, tavsiya, raqobatchi xodimlari, yarmarkalar) va target e’lonni birlashtiraman, voronkani kunlik kuzataman", "score": 3},
                    {"text": "Bir nechta ish saytiga pullik e’lon joylab, arizalarni kutaman", "score": 1},
                    {"text": "Ish haqini oshirib e’lon berib, ko‘proq nomzod kelishini kutaman", "score": 0},
                ],
            },
            {
                "text": "AI skrining nomzodlarni ballab beryapti. Undan qanday foydalanasiz?",
                "options": [
                    {"text": "AIni birlamchi tartiblash uchun ishlataman, mezonlar shaffofligi va noxolislik (bias) yo‘qligini tekshiraman, yakuniy qarorni o‘zim ko‘rib chiqaman", "score": 3},
                    {"text": "AI reytingi yuqori 10 nomzodni to‘g‘ridan-to‘g‘ri suhbatga chaqiraman", "score": 1},
                    {"text": "AIga ishonmay, barcha CV ni to‘liq qo‘lda ko‘rib chiqaman", "score": 0},
                ],
            },
            {
                "text": "Ikki kuchli xodim ochiq janjallashdi, biri ketish bilan qo‘rqityapti. Birinchi qadamingiz?",
                "options": [
                    {"text": "Har birini alohida tinglab, faktlar va asl sababni aniqlayman, so‘ng umumiy manfaat asosida aniq kelishuv va kuzatuv belgilayman", "score": 3},
                    {"text": "Darhol umumiy majlis chaqirib, ochiq muhokama qilaman", "score": 1},
                    {"text": "Ketish bilan qo‘rqitgan xodim tomonini olib, ikkinchisiga tanbeh beraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Kadrlar oqimini (turnover) kamaytirish rejasini yozing: 90 kun ichida 3 aniq chora va har birini qaysi ko‘rsatkich bilan o‘lchaysiz.", "rubric": RUBRIC_LOGIC},
            {"text": "1 daqiqalik videodan nomzodni baholash uchun 3 mezon tuzing va har biri uchun 0/1/2/3 ballning konkret mezonini (rubrika) yozing.", "rubric": RUBRIC_LOGIC},
        ],
        "video": "Yaxshi nomzodni qanday ajratasiz? Suhbatda birinchi navbatda nimaga e’tibor berasiz?",
    },
    "rop": {
        "title": "ROP (Sotuv bo‘limi rahbari)",
        "test": [
            {
                "text": "Bo‘lim rejaning 60% ida, oyga 8 kun qoldi. Konversiya normal, lekin lid soni kam. Nima qilasiz?",
                "options": [
                    {"text": "Muammo lid oqimida ekanini aniqlab, marketing bilan lid manbasini kuchaytiraman va bazadagi “uxlab yotgan” lidlarni qayta ishga solaman", "score": 3},
                    {"text": "Har menejerga individual og‘ir reja qo‘yib, kunlik bosim o‘tkazaman", "score": 1},
                    {"text": "Konversiyani oshirish uchun skriptni butunlay o‘zgartiraman", "score": 0},
                ],
            },
            {
                "text": "CRM’da 3 oylik ma’lumot bor. AI bilan nimani birinchi tahlil qilasiz?",
                "options": [
                    {"text": "Voronka bosqichlari bo‘yicha konversiya va “to‘kilish” (drop-off) nuqtasini topib, eng zaif bosqichga skript/jarayon yaxshilashni yo‘naltiraman", "score": 3},
                    {"text": "Har menejerning umumiy sotuv summasini reyting qilaman", "score": 1},
                    {"text": "Faqat yopilgan bitimlar ro‘yxatini chiqaraman", "score": 0},
                ],
            },
            {
                "text": "Yangi menejer 2 haftada natija bermayapti. Nima qilasiz?",
                "options": [
                    {"text": "Qo‘ng‘iroq/uchrashuvlarini tinglab, qaysi bosqichda oqsayotganini aniqlab, nuqtaviy mashq beraman; onboarding maqsadlari realligini qayta ko‘raman", "score": 3},
                    {"text": "Yana bir oy vaqt berib, o‘zi o‘rganishini kutaman", "score": 1},
                    {"text": "Natija bermagani uchun almashtirishga tayyorlanaman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Menejerlar mas’uliyatini oshiruvchi KPI tizimini yozing: 4–5 ko‘rsatkich, ularning vazni va qanday hisoblanishi.", "rubric": RUBRIC_LOGIC},
            {"text": "Rejadan orqada qolgan oyni yopib chiqqan tajribangizni raqamlar (boshlang‘ich %, oxirgi natija, qanday harakat) bilan yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Rejadan orqada qolgan bo‘limni qanday yopib chiqqaningizni ayting — qanday harakat qildingiz va natija qanday bo‘ldi?",
    },
    "buxgalter": {
        "title": "Buxgalter",
        "test": [
            {
                "text": "QQS hisoboti muddati ertaga. Yirik kontragentdan olingan ЭСФ (elektron schyot-faktura) tizimda tasdiqlanmagan. Nima qilasiz?",
                "options": [
                    {"text": "Kontragentdan ЭСФ ni zudlik bilan tasdiqlashini talab qilaman; ulgurmasa o‘sha summani hisobga olmay muddatida topshirib, keyin uточненный (qo‘shimcha) hisobot beraman", "score": 3},
                    {"text": "Summani hisobga olib topshiraman, kontragent keyin tasdiqlaydi deb umid qilaman", "score": 1},
                    {"text": "Kontragent tasdiqlaguncha hisobotni kechiktiraman", "score": 0},
                ],
            },
            {
                "text": "Oy yakunida bank vypiskasi 1C dagi qoldiq bilan mos kelmayapti. Nima qilasiz?",
                "options": [
                    {"text": "Bank vypiskasi va 1C provodkalarini pozitsiya bo‘yicha solishtirib (sverka), farq qayerdaligini topib to‘g‘rilayman", "score": 3},
                    {"text": "1C qoldig‘ini bank raqamiga tenglashtirib, farqni “boshqa xarajat”ga yozaman", "score": 1},
                    {"text": "Farq kichik bo‘lsa, e’tibor bermayman", "score": 0},
                ],
            },
            {
                "text": "Rahbar soliqni kamaytirish uchun soxta xarajat hujjatlarini kiritishni so‘radi. Nima qilasiz?",
                "options": [
                    {"text": "Buni jinoiy/soliq xatari sifatida yozma tushuntirib, mavjud qonuniy imtiyoz va optimallashtirish variantlarini taklif qilaman", "score": 3},
                    {"text": "Ko‘rsatmani bajaraman, lekin javobgarlik rahbarda ekanini yozib qo‘yaman", "score": 1},
                    {"text": "Rahbar aytgani uchun bajaraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Moliyaviy xatar va soliq xatolarining oldini oluvchi ichki nazorat tartibingizni yozing (kim, nimani, qachon tekshiradi).", "rubric": RUBRIC_LOGIC},
            {"text": "Buxgalteriya jarayonidan bittasini avtomatlashtirib vaqt yoki xatoni kamaytirgan taklif yoki tajribangizni yozing.", "rubric": RUBRIC_AI},
        ],
        "video": "Bajargan eng murakkab moliyaviy yoki soliq vazifangizni va uni qanday hal qilganingizni ayting.",
    },
    "kassir": {
        "title": "Kassir",
        "test": [
            {
                "text": "Smena oxirida kassada 150 000 so‘m kamomad. Ertaga inventarizatsiya. Nima qilasiz?",
                "options": [
                    {"text": "Cheklar va operatsiyalarni tartib bilan qayta tekshirib sababini aniqlayman va topilsin-topilmasin rahbariyatga rasmiy (yozma) bildiraman", "score": 3},
                    {"text": "Farqni o‘z pulimdan yopib, hisobni tenglashtiraman", "score": 1},
                    {"text": "Keyingi smenaga o‘tkazib, keyin qarayman", "score": 0},
                ],
            },
            {
                "text": "Terminal orqali to‘lov “muvaffaqiyatli” chiqdi, lekin bankdan tasdiq (chek) kelmadi. Nima qilasiz?",
                "options": [
                    {"text": "Tovarni bermay, tranzaksiya bank hisobidan o‘tganini tasdiqlaguncha kutaman; ikkilanish bo‘lsa qayta o‘tkazmayman", "score": 3},
                    {"text": "Terminal “ha” degani uchun tovarni beraman", "score": 1},
                    {"text": "Mijozdan qayta to‘lashni so‘rayman", "score": 0},
                ],
            },
            {
                "text": "Navbat uzun, mijoz yirik summani naqd beryapti va shoshirmoqda. Nima qilasiz?",
                "options": [
                    {"text": "Xotirjam qayta sanab, detektor bilan tekshirib qabul qilaman — tezlik aniqlikdan ustun emas", "score": 3},
                    {"text": "Mijozga ishonib, tez sanab qabul qilaman", "score": 1},
                    {"text": "Navbat ketmasin deb, sanashni yengil o‘tkazib yuboraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Pul bilan ishlashda kamomad va xatoning oldini oluvchi shaxsiy tartibingizni yozing (smena boshi, davomida, oxirida).", "rubric": RUBRIC_LOGIC},
            {"text": "Kassir ishida halollik va aniqlik nega hal qiluvchi ekanini misol bilan yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Nega pul bilan ishlashda sizga ishonsa bo‘ladi? Aniqlik va halollikni qanday ta’minlaysiz?",
    },
    "targetolog": {
        "title": "Targetolog",
        "test": [
            {
                "text": "Kampaniyada CTR 3% (yaxshi), CPC arzon, lekin 5 kunda atigi 2 ta lid. Byudjet 70% sarflandi. Muammo qayerda va nima qilasiz?",
                "options": [
                    {"text": "Muammo click’dan keyin (landing/offer) deb faraz qilib, landing konversiyasi va lid-forma bosqichini tekshiraman, offer va sahifani A/B test qilaman", "score": 3},
                    {"text": "Auditoriyani kengaytirib, byudjetni oshiraman", "score": 1},
                    {"text": "CTR yaxshi bo‘lsa ham kreativni butunlay almashtiraman", "score": 0},
                ],
            },
            {
                "text": "Ikki kreativni A/B test qilyapsiz. Qachon g‘olibni tanlaysiz?",
                "options": [
                    {"text": "Statistik ishonchli namuna (konversiyalar soni) yig‘ilgach, xarajatga nisbatan natija (CPL/ROAS) bo‘yicha tanlayman", "score": 3},
                    {"text": "1 kun ishlagach, qaysi biri ko‘proq bosilgan bo‘lsa, o‘shani tanlayman", "score": 1},
                    {"text": "O‘zimga chiroyliroq ko‘ringanini qoldiraman", "score": 0},
                ],
            },
            {
                "text": "Reklama kabineti qoidabuzarlik uchun bloklandi. Nima qilasiz?",
                "options": [
                    {"text": "Aniq sababni topib, kreativ/sahifani qoidaga moslab tuzataman, rasmiy apellyatsiya yuboraman va hisob ishonchini (domen, to‘lov) tozalayman", "score": 3},
                    {"text": "Reklamani to‘xtatib, blok o‘zi ochilishini kutaman", "score": 1},
                    {"text": "Yangi Business Manager ochib, aylanib o‘taman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Cheklangan byudjetda maksimal ROI strategiyangizni yozing: auditoriya, offer, kreativ testlash va o‘lchov (CPL/ROAS).", "rubric": RUBRIC_LOGIC},
            {"text": "Oxirgi kampaniyangiz natijalarini raqamlar bilan yozing: byudjet, lidlar, CPL va ROI.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Eng muvaffaqiyatli reklama kampaniyangizni raqamlari (byudjet, lid narxi, natija) bilan ayting.",
    },
    "yuridik_maslahatchi": {
        "title": "Yuridik maslahatchi",
        "test": [
            {
                "text": "Yirik shartnomada cheksiz javobgarlik (неограниченная ответственность) va nizolar chet el sudida ko‘rilishi yozilgan. Ikkinchi tomon shoshiryapti. Nima qilasiz?",
                "options": [
                    {"text": "Xatarni yozma bayon qilib, javobgarlik shiftini (cap) va nizolarni O‘zbekiston yurisdiksiyasi/arbitrajga o‘tkazishni taklif qilaman; kelishilgunicha imzoni kechiktiraman", "score": 3},
                    {"text": "Bandlarni og‘zaki muhokama qilib, ishonch asosida imzolashga rozi bo‘laman", "score": 1},
                    {"text": "Biznes muhim bo‘lgani uchun bandlarni o‘tkazib yuboraman", "score": 0},
                ],
            },
            {
                "text": "Yangi xodim bilan mehnat shartnomasi tuzyapsiz. Nimaga alohida e’tibor berasiz?",
                "options": [
                    {"text": "Sinov muddati, mehnat sharoiti, ish haqi va bekor qilish asoslarini Mehnat kodeksi talablariga muvofiqlashtirib, tomonlar huquqini muvozanatlashtiraman", "score": 3},
                    {"text": "Standart namunani olib, faqat ism va lavozimni o‘zgartiraman", "score": 1},
                    {"text": "Faqat ish haqi kelishilsa, qolganini keyin rasmiylashtiraman", "score": 0},
                ],
            },
            {
                "text": "Kompaniyaga da’vo tushdi, javob muddati 10 kun. Birinchi harakatingiz?",
                "options": [
                    {"text": "Da’vo asosi va dalillarni huquqiy tahlil qilib, muddatida asosli e’tiroz/javob tayyorlayman va kerakli hujjatlarni yig‘aman", "score": 3},
                    {"text": "Ikkinchi tomon bilan sudsiz kelishishga urinib, javobni kechiktiraman", "score": 1},
                    {"text": "Rahbariyat qaror qilsin deb kutaman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Shartnoma imzolashdan oldingi huquqiy tekshiruv (due diligence) tartibingizni yozing: qaysi bandlar va hujjatlar tekshiriladi.", "rubric": RUBRIC_LOGIC},
            {"text": "Amaliyotingizdagi eng murakkab huquqiy holat va uni qanday hal qilganingizni yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Amaliyotingizdagi eng murakkab huquqiy holatni va uni qanday hal qilganingizni ayting.",
    },
    "pto_muhandisi": {
        "title": "PTO muhandisi (Loyiha-smeta bo‘limi)",
        "test": [
            {
                "text": "Loyiha jarayonida metall narxi 18% oshdi, smeta byudjetdan chiqmoqda, buyurtmachi qo‘shimcha to‘lovga rozi emas. Nima qilasiz?",
                "options": [
                    {"text": "Muqobil material/konstruktiv yechim va hajmni qayta ko‘rib, sifatga ta’sir qilmaydigan optimallashtirishni hisob bilan taklif qilaman va o‘zgarishlarni rasmiylashtiraman", "score": 3},
                    {"text": "Yashirin zaxira (rezerv) hisobidan yopib, smetani o‘zgartirmayman", "score": 1},
                    {"text": "Smetani indamay oshirib, keyin tushuntiraman", "score": 0},
                ],
            },
            {
                "text": "Smetada normativ baza va koeffitsientlar to‘g‘ri qo‘llanganini qanday tekshirasiz?",
                "options": [
                    {"text": "Amaldagi resurs normalari (ShNQ/РСН), joriy narx indekslari va nakladnoy/plan-jamg‘arma koeffitsientlarini loyiha hajmiga solishtirib tekshiraman", "score": 3},
                    {"text": "O‘tgan o‘xshash obyekt smetasini nusxalab, narxni yangilayman", "score": 1},
                    {"text": "Umumiy tajriba bo‘yicha chamalab hisoblayman", "score": 0},
                ],
            },
            {
                "text": "Ishchi chizmadagi (rabochiy chertyoj) hajm loyiha smetasidan farq qilyapti. Nima qilasiz?",
                "options": [
                    {"text": "Farqni hujjatlashtirib, loyihachi va buyurtmachi bilan rasmiy o‘zgartirish (izmenenie) kiritib, so‘ng hisobni yangilayman", "score": 3},
                    {"text": "Chizmaga ishonib, o‘zim to‘g‘rilab qo‘yaman", "score": 1},
                    {"text": "Smetaga ishonib, chizmani e’tibormay qoldiraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Smetada xarajat oshib ketishining oldini oluvchi nazorat tizimini yozing (rejadan chetlanishni qanday erta ushlaysiz).", "rubric": RUBRIC_LOGIC},
            {"text": "Smeta yoki hisob jarayonini tezlashtirgan yoki xarajatni kamaytirgan aniq tajribangizni yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Smeta yoki hisob ishida aniqlik va tejamkorlikni qanday ta’minlaganingizni bir misolda ayting.",
    },
    "buxgalter_yordamchisi": {
        "title": "Buxgalter yordamchisi",
        "test": [
            {
                "text": "Katta partiya birlamchi hujjat (nakladnoy) da imzo va muhr yo‘q, bosh buxgalter oy yopilishiga ulgurish uchun kiritishni so‘rayapti. Nima qilasiz?",
                "options": [
                    {"text": "Mas’uldan hujjatni rasmiylashtirtirib, so‘ng kiritaman; ulgurmasa holatni bosh buxgalterga yozma bildirib, uning qaroriga havola qilaman", "score": 3},
                    {"text": "“Keyin tuzatamiz” deb kiritib qo‘yaman va belgilab qo‘yaman", "score": 1},
                    {"text": "Shundoq o‘tkazib yuboraman", "score": 0},
                ],
            },
            {
                "text": "1C ga kirim qilyapsiz, kontragent bazada ikki xil nom bilan takrorlangan (dublikat). Nima qilasiz?",
                "options": [
                    {"text": "Rekvizitlari to‘liq to‘g‘ri kontragentni aniqlab, provodkani unga bog‘layman, dublikatni belgilab, bosh buxgalter bilan birlashtirishni kelishaman", "score": 3},
                    {"text": "Qaysi biri chiqsa, o‘shanga kiritaveraman", "score": 1},
                    {"text": "Yangi uchinchi kontragent ochib kiritaman", "score": 0},
                ],
            },
            {
                "text": "200 ta hujjatni kiritish kerak, charchoq bor. Nima qilasiz?",
                "options": [
                    {"text": "Bloklarga bo‘lib, har blokdan keyin summalarni jami bo‘yicha solishtirib (kontrol) tekshiraman", "score": 3},
                    {"text": "Hammasini kiritib, oxirida bir marta umumiy tekshiraman", "score": 1},
                    {"text": "Tez kiritib, xato bo‘lsa keyin topiladi deb qoldiraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Birlamchi hujjatlar bilan ishlashda xatoning oldini oluvchi shaxsiy tartibingizni yozing.", "rubric": RUBRIC_LOGIC},
            {"text": "Nega buxgalteriyada davom etmoqchisiz va 1–2 yillik aniq maqsadingiz nima?", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Nega buxgalteriya sohasida o‘smoqchisiz? 1–2 yillik aniq maqsadingiz nima?",
    },
    "yordamchi_xodim": {
        "title": "Yordamchi xodim",
        "test": [
            {
                "text": "Ikki rahbar bir vaqtda topshiriq berdi: biri “shu zahoti”, ikkinchisi “bugun kechgacha”. Nima qilasiz?",
                "options": [
                    {"text": "Ikkalasidan muhimlik va real muddatni aniqlab, “shu zahoti”ni birinchi bajaraman va ikkinchisiga qachon tayyor bo‘lishimni aytaman", "score": 3},
                    {"text": "Birinchi aytgan rahbarnikini to‘liq bitirib, keyin ikkinchisiga o‘taman", "score": 1},
                    {"text": "Ikkalasini birdan qilishga urinib, ikkalasini ham yarim qoldiraman", "score": 0},
                ],
            },
            {
                "text": "Topshiriqni bajarding, lekin yo‘l-yo‘lakay boshqa muammoni (masalan, buzuq jihoz) ko‘rib qolding. Nima qilasiz?",
                "options": [
                    {"text": "Topshiriqni tugatib, ko‘rgan muammoni mas’ulga darhol xabar qilaman yoki o‘zim hal qila olsam, hal qilaman", "score": 3},
                    {"text": "Menga aytilmagani uchun e’tibor bermayman", "score": 1},
                    {"text": "Keyin esimga kelsa aytaman", "score": 0},
                ],
            },
            {
                "text": "Sizga ishonib topshirilgan ishni belgilangan vaqtda ulgurmasligingiz aniq bo‘ldi. Nima qilasiz?",
                "options": [
                    {"text": "Ulgurmasligim ma’lum bo‘lishi bilan mas’ulni ogohlantirib, sabab va muqobil yechim taklif qilaman", "score": 3},
                    {"text": "Oxirigacha urinib ko‘rib, ulgurmasam keyin aytaman", "score": 1},
                    {"text": "Aytmayman, o‘zi bilib qoladi", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Bir kunda ko‘p mayda topshiriq bo‘lsa, ularni qanday tartib va nazorat bilan bajarasiz?", "rubric": RUBRIC_LOGIC},
            {"text": "Ishga munosabatingiz va intizomingizni misol bilan qisqacha yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Nega sizga ishonch bilan ish topshirsa bo‘ladi? Mas’uliyat va intizomingizni misol bilan ayting.",
    },
    "kran_mashinisti": {
        "title": "Kran mashinisti",
        "test": [
            {
                "text": "Kuchli shamol (~16 m/s), kran pasporti chegarasi 15 m/s. Brigadir bitta panelni ko‘tarishni shoshirtiryapti. Nima qilasiz?",
                "options": [
                    {"text": "Chegaradan oshgani uchun ishni rad etaman, kranni bo‘shatib (flyuger) qo‘yaman va sababini rasmiy bildiraman", "score": 3},
                    {"text": "Bitta yengil panel bo‘lgani uchun ehtiyot bo‘lib ko‘taraman", "score": 1},
                    {"text": "Brigadir javobgar deb, buyruqni bajaraman", "score": 0},
                ],
            },
            {
                "text": "Smena boshida kranni ishga tushirishdan oldin nimani tekshirasiz?",
                "options": [
                    {"text": "Arqon, tormoz, cheklovchilar (kontsevik/OGP), signal va tirgaklarni (autrigger) vahtaviy jurnal bo‘yicha tekshirib, so‘ng ishlataman", "score": 3},
                    {"text": "Faqat ko‘zga tashlanadigan nosozlik bor-yo‘qligini ko‘raman", "score": 1},
                    {"text": "Ishlab turgani uchun to‘g‘ridan-to‘g‘ri boshlayveraman", "score": 0},
                ],
            },
            {
                "text": "Ko‘tarilayotgan yuk noto‘g‘ri bog‘langanini (strop qiyshiq, og‘irlik markazi siljigan) sezdingiz. Nima qilasiz?",
                "options": [
                    {"text": "Ko‘tarishni to‘xtatib, yukni tushirib, stropalshchik bilan qayta to‘g‘ri bog‘lataman", "score": 3},
                    {"text": "Sekin, ehtiyot bo‘lib ko‘tarib boraman", "score": 1},
                    {"text": "Signalchi ruxsat bergani uchun davom etaman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Kran boshqarishda avariyaning oldini oluvchi qat’iy qoidalaringizni va qaysi holatda ishni rad etishingizni yozing.", "rubric": RUBRIC_LOGIC},
            {"text": "Og‘ir yuk bilan ishlash tajribangiz va xavfsizlik uchun mas’uliyatingizni misol bilan yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Og‘ir yuk bilan ishlash tajribangizni va xavfsizlikka munosabatingizni ayting.",
    },
    "sotuv_operatori": {
        "title": "Sotuv operatori",
        "test": [
            {
                "text": "Mijoz jahl bilan: “to‘lov qildim, buyurtma kelmadi, pulimni qaytaring!” — sizda hozir aniq javob yo‘q. Nima qilasiz?",
                "options": [
                    {"text": "Xotirjam tinglab, muammoni tan olaman, buyurtmani tekshirib aniq keyingi qadam va muddatni aytaman va mas’ulga eskalatsiya qilaman", "score": 3},
                    {"text": "“Tekshiramiz” deb, boshqa bo‘limga ulab yuboraman", "score": 1},
                    {"text": "“Bu mening bo‘limim emas” deb tushuntiraman", "score": 0},
                ],
            },
            {
                "text": "Suhbat davomida mijoz tez gapiryapti va ko‘p ma’lumot beryapti. Nima qilasiz?",
                "options": [
                    {"text": "Asosiy ma’lumotni suhbat davomida CRMga tuzilgan tarzda yozib boraman va tushunganimni qisqa takrorlab tasdiqlataman", "score": 3},
                    {"text": "Suhbatni tugatib, esimda qolganini keyin yozaman", "score": 1},
                    {"text": "Hammasini qog‘ozga yozib, keyin CRMga ko‘chiraman", "score": 0},
                ],
            },
            {
                "text": "Kun bo‘yi 60+ qo‘ng‘iroq, charchadingiz, keyingi mijoz ham xuddi shu savolni beryapti. Nima qilasiz?",
                "options": [
                    {"text": "Har mijoz uchun bu birinchi marta ekanini yodda tutib, bir xil iliqlik va e’tibor bilan javob beraman; skriptdan foydalanaman", "score": 3},
                    {"text": "Charchaganim uchun javobni qisqartirib, quruq beraman", "score": 1},
                    {"text": "Ohangimni o‘zgartirmasdan, zerikkan tarzda javob beraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Mijozning qiyin yoki shubhali savoliga (masalan raqobatchi bilan solishtirish) ishonchli javob berish uslubingizni yozing.", "rubric": RUBRIC_LOGIC},
            {"text": "Mijozni jalb qilishda asosiy kuchli tomoningiz nima? Misol bilan yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Asabiy, jahli chiqqan mijoz bilan qanday muomala qilishingizni ko‘rsating (istasangiz vaziyatni o‘ynab bering).",
    },
    "brand_face": {
        "title": "Brand Face (Kompaniya qiyofasi)",
        "test": [
            {
                "text": "Prodyuser matnsiz, faqat mavzu berib, jonli improvizatsiya so‘radi va kamera yozyapti. Nima qilasiz?",
                "options": [
                    {"text": "10–15 soniyada kirish–asosiy fikr–yakun (CTA) tuzib, tabiiy va ishonch bilan gapiraman; kichik xatoda ham to‘xtamay davom etaman", "score": 3},
                    {"text": "Bir necha kalit gapni yozib olib, so‘ng gapiraman", "score": 1},
                    {"text": "Tayyor matn bo‘lmasa, noqulay his qilib, gapira olmayman", "score": 0},
                ],
            },
            {
                "text": "Ssenariy sizga zerikarli va auditoriyaga tegmaydigandek tuyuldi. Nima qilasiz?",
                "options": [
                    {"text": "Aniq sabab va muqobil kreativ variantni prodyuserga taklif qilib, kelishilgach jonli chiqish qilaman", "score": 3},
                    {"text": "Aytilganini bajaraman, o‘z fikrimni bildirmayman", "score": 1},
                    {"text": "Yoqmagani uchun sust, ishtiyoqsiz suratga tushaman", "score": 0},
                ],
            },
            {
                "text": "Videongiz ostida ochiq tuhmat va haqoratli izohlar ko‘paydi. Nima qilasiz?",
                "options": [
                    {"text": "Xotirjam, professional va faktga asoslangan javob beraman yoki jamoa bilan yagona pozitsiyani (javob berish/bermaslik) kelishaman", "score": 3},
                    {"text": "Barcha salbiy izohni o‘chirib tashlayman", "score": 1},
                    {"text": "Keskin, hissiy javob qaytaraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Kompaniya imidjini mustahkamlashda Brand Face sifatidagi rolingizni va o‘ziga xos uslubingizni tasvirlang.", "rubric": RUBRIC_LOGIC},
            {"text": "1 daqiqalik video-vizitka uchun qisqa ssenariy yozing: o‘zingizni qanday ochasiz, asosiy g‘oya va yakun.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Kamera oldida o‘zingizni erkin tanishtiring va shu kompaniyani auditoriyaga qiziqarli qilib taqdim eting — bu sizning namunangiz.",
    },
    "sayhun_sotuvchi": {
        "title": "Sayhun bozorda sotuvchi",
        "test": [
            {
                "text": "Mijoz mahsulotni tanladi, lekin narxni eshitib ikkilanmoqda. Nima qilasiz?",
                "options": [
                    {"text": "Ehtiyoji va byudjetini so‘rab, aynan mos variantni (arzonroq yoki sifatliroq) taklif qilib, afzalligini narxga bog‘lab tushuntiraman", "score": 3},
                    {"text": "Darrov eng arzon mahsulotni ko‘rsataman", "score": 1},
                    {"text": "“Narxi shu” deb, o‘zi qaror qilishini kutaman", "score": 0},
                ],
            },
            {
                "text": "Mahsulot qoldig‘i to‘satdan tugab qolmasligi uchun nima qilasiz?",
                "options": [
                    {"text": "Kunlik savdo va qoldiqni hisoblab, tez sotiladiganini oldindan buyurtma qilib, javonni to‘ldirib turaman", "score": 3},
                    {"text": "Tugaganini ko‘rganda buyurtma beraman", "score": 1},
                    {"text": "Ta’minot o‘zi keladi deb, qoldiqni kuzatmayman", "score": 0},
                ],
            },
            {
                "text": "Kun oxirida kassa hisobi mahsulot qoldig‘iga mos kelmadi. Nima qilasiz?",
                "options": [
                    {"text": "Cheklar, savdo va qoldiqni solishtirib, farq qayerdan chiqqanini aniqlab, egasiga bildiraman", "score": 3},
                    {"text": "Kichik farq bo‘lsa, o‘z hisobimdan tenglashtiraman", "score": 1},
                    {"text": "E’tibor bermay, ertaga qarayman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Bozordagi raqobatda mijozni aynan sizdan xarid qilishga qanday undaysiz? Aniq usul yozing.", "rubric": RUBRIC_LOGIC},
            {"text": "Savdoda erishgan eng yaxshi natijangiz yoki mijoz bilan qiziqarli voqeani yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Meni 30 soniyada bitta mahsulotni sotib olishga ko‘ndiring — real savdo qilib ko‘rsating.",
    },
    "taminotchi": {
        "title": "Ta’minotchi",
        "test": [
            {
                "text": "Obyektga zudlik bilan sement kerak, doimiy yetkazib beruvchida yo‘q; boshqasida bor, lekin 30% qimmat va sifati noma’lum. Nima qilasiz?",
                "options": [
                    {"text": "Bir vaqtda bir necha muqobil manbani tekshirib, sifat sertifikatini so‘rab, narx-muddat-sifat bo‘yicha eng maqbulini tanlayman va rahbarni xabardor qilaman", "score": 3},
                    {"text": "Ish to‘xtamasin deb, qimmat va noma’lum sifatlisini darrov olaman", "score": 1},
                    {"text": "“Borida yo‘q ekan” deb kutaman", "score": 0},
                ],
            },
            {
                "text": "Yetkazib beruvchi katta partiyaga arzon narx berdi, lekin to‘lovni 100% oldindan talab qilyapti. Nima qilasiz?",
                "options": [
                    {"text": "Narx yaxshi bo‘lsa ham, sifat va yetkazishni kafolatlaydigan shartnoma va bosqichli to‘lov (avans + qolgani yetkazilgach) ni kelishaman", "score": 3},
                    {"text": "Arzon bo‘lgani uchun oldindan to‘liq to‘layman", "score": 1},
                    {"text": "Ishonchsiz deb, umuman voz kechaman", "score": 0},
                ],
            },
            {
                "text": "Kelgan material qisman sifatsiz, ish shoshilinch, qaytarish 2 kun ketadi. Nima qilasiz?",
                "options": [
                    {"text": "Yaroqli qismini aktlab qabul qilib, sifatsizini qaytaraman va yetishmaganini muqobil manbadan zudlik bilan qoplab, rahbarni xabardor qilaman", "score": 3},
                    {"text": "Shoshilinch bo‘lgani uchun sifatsizini ham ishlatishga beraman", "score": 1},
                    {"text": "Rahbarga aytmasdan hammasini qabul qilaman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Ta’minotda tezkorlik, narx va sifatni bir vaqtda qanday muvozanatlaysiz? Muqobil manba bazasini qanday shakllantirasiz?", "rubric": RUBRIC_LOGIC},
            {"text": "Eng murakkab yoki shoshilinch buyurtmani muvaffaqiyatli bajarganingizni misol bilan yozing.", "rubric": RUBRIC_MOTIVATION},
        ],
        "video": "Eng murakkab yoki shoshilinch buyurtmani qanday bajarganingizni ayting — qayerdan, qanday topdingiz?",
    },
    "loyihachi": {
        "title": "Loyihachi (Arxitektor-loyihachi)",
        "test": [
            {
                "text": "Buyurtmachi ustunsiz, ochiq katta zal xohlaydi, lekin bu konstruktiv jihatdan qimmat va murakkab yechim talab qiladi. Nima qilasiz?",
                "options": [
                    {"text": "Buyurtmachi asosiy maqsadini aniqlab, bir necha muqobil konstruktiv yechimni (katta oraliq to‘sin/farma, monolit rigel) narx va imkoniyat bilan taqqoslab taklif qilaman", "score": 3},
                    {"text": "Buyurtmachi xohlagani uchun ustunsiz variantni to‘g‘ridan-to‘g‘ri loyihalayveraman", "score": 1},
                    {"text": "Murakkab bo‘lgani uchun o‘zim ustun qo‘shib, buyurtmachiga keyin tushuntiraman", "score": 0},
                ],
            },
            {
                "text": "Arxitektura, konstruktiv va muhandislik (suv, shamollatish, elektr) bo‘limlari chizmalarida to‘qnashuv (kolliziya) bor. Qanday aniqlab, hal qilasiz?",
                "options": [
                    {"text": "BIM modelida kolliziyalarni avtomatik tekshirib (clash detection), tegishli bo‘lim mutaxassislari bilan muvofiqlashtirib hal qilaman", "score": 3},
                    {"text": "Chizmalarni qo‘lda ustma-ust qo‘yib solishtiraman va topilganini to‘g‘rilayman", "score": 1},
                    {"text": "Har bo‘lim o‘z chizmasiga javobgar deb, alohida ishlayveraman", "score": 0},
                ],
            },
            {
                "text": "Loyihani ekspertizaga topshirishga 3 kun qoldi, lekin evakuatsiya yo‘li kengligi yong‘in xavfsizligi normasidan tor ekanini payqadingiz. Nima qilasiz?",
                "options": [
                    {"text": "Xatoni darhol tuzatib, ShNQ va yong‘in xavfsizligi talabiga moslashtiraman — bu ekspertizadan o‘tmaydi va hayotga xavf soladi", "score": 3},
                    {"text": "Hozircha shunday topshirib, ekspertiza izohi kelsa keyin tuzataman", "score": 1},
                    {"text": "Farq kichik bo‘lgani uchun o‘tkazib yuboraman", "score": 0},
                ],
            },
        ],
        "written": [
            {"text": "Loyihani boshlashdan oldin buyurtmachi topshirig‘i (TZ) va uchastka sharoitini qanday tahlil qilasiz? Qaysi ma’lumot va cheklovlarni (grunt, kommunikatsiya, normativ) yig‘asiz?", "rubric": RUBRIC_LOGIC},
            {"text": "Loyihalashda AIdan qanday foydalanasiz (variant generatsiya, hisob, xato/kolliziya tekshirish)? Bitta aniq misol yoki prompt yozing.", "rubric": RUBRIC_AI},
        ],
        "video": "Ishtirok etgan yoki mustaqil ishlagan loyihangizni ayting — g‘oyasi qanday edi, qanday muammoni yechdi va aynan sizning hissangiz nima bo‘ldi?",
    },
}


# ── Vakansiya nomini shablonga avtomatik moslashtirish ─────────────────────
# (qidiruv_iborasi, bank_kaliti) — eng ANIQ (uzun/maxsus) iboralar birinchi.
MATCH_RULES = [
    ("bosh direktor", "ceo"),
    (" ceo ", "ceo"),
    ("general direktor", "ceo"),
    (" direktor ", "ceo"),
    ("texnik nazorat", "texnik_nazoratchi"),
    ("loyihachi", "loyihachi"),
    ("arxitektor", "loyihachi"),
    ("arxitek", "loyihachi"),
    ("loyiha muhandis", "loyihachi"),
    ("kran muhandis", "kran_muhandisi"),
    ("kran mashinist", "kran_mashinisti"),
    ("kranchik", "kran_mashinisti"),
    ("kran operator", "kran_mashinisti"),
    ("prorab", "prorab"),
    ("buxgalter yordamchi", "buxgalter_yordamchisi"),
    ("yordamchi buxgalter", "buxgalter_yordamchisi"),
    ("buxgalter", "buxgalter"),
    ("kassir", "kassir"),
    ("targetolog", "targetolog"),
    ("target", "targetolog"),
    ("yurid", "yuridik_maslahatchi"),
    ("yurist", "yuridik_maslahatchi"),
    ("advokat", "yuridik_maslahatchi"),
    (" pto ", "pto_muhandisi"),
    ("smeta", "pto_muhandisi"),
    ("mobilograf", "mobilograf"),
    ("videograf", "mobilograf"),
    ("video operator", "mobilograf"),
    ("hr menejer", "hr_menejer"),
    (" hr ", "hr_menejer"),
    (" rop ", "rop"),
    ("sotuv bolimi rahbari", "rop"),
    ("sotuv rahbari", "rop"),
    ("sotuv menejer", "sotuv_menejeri"),
    ("sotuv operator", "sotuv_operatori"),
    ("sayhun", "sayhun_sotuvchi"),
    ("brand face", "brand_face"),
    ("brend yuz", "brand_face"),
    ("qiyofa", "brand_face"),
    ("taminot", "taminotchi"),
    ("yordamchi xodim", "yordamchi_xodim"),
    ("yordamchi hodim", "yordamchi_xodim"),
    ("dasturchi", "it_mutaxassisi"),
    ("developer", "it_mutaxassisi"),
    ("programmist", "it_mutaxassisi"),
    (" it ", "it_mutaxassisi"),
    ("operator", "sotuv_operatori"),
    ("menejer", "sotuv_menejeri"),
    ("manager", "sotuv_menejeri"),
    ("sotuvchi", "sotuv_menejeri"),
    ("sotuv", "sotuv_menejeri"),
    ("yordamchi", "yordamchi_xodim"),
]


def _normalize_title(title: str) -> str:
    s = (title or "").lower()
    for ch in "'\u02bc`\u2019\u2018":
        s = s.replace(ch, "")
    return " " + " ".join(s.split()) + " "


def match_bank_key(title: str) -> str | None:
    """Vakansiya nomiga eng mos QUESTION_BANK kalitini qaytaradi (topilmasa None)."""
    norm = _normalize_title(title)
    for phrase, key in MATCH_RULES:
        if phrase in norm:
            return key
    return None


# ── Ball va rang ───────────────────────────────────────────────────────────
MAX_TEST = 9
MAX_WRITTEN = 6
MAX_VIDEO = 4
MAX_TOTAL = 19

COLOR_GREEN_MIN = 14   # yashil >= 14 (19 balldan)
COLOR_YELLOW_MIN = 9   # sariq 9-13, qizil <= 8

# Bosqichlar o'chirilgan bo'lsa maksimal ball o'zgaradi (masalan 15 yoki 4).
# Shuning uchun rang FOIZ bo'yicha aniqlanadi — chegaralar 19 ballik
# tizimdan olingan: 14/19 = 73.7%, 9/19 = 47.4%
PCT_GREEN_MIN = 73
PCT_YELLOW_MIN = 47


STAGE_ON = ("required", "optional")   # bosqich baholanadi (ixtiyoriy bo'lsa ham)


def stage_max(questions_mode, video_mode: str) -> int:
    """Vakansiya sozlamalariga qarab maksimal ball.

    Ixtiyoriy bosqich ham maksimalga kiradi — nomzodga imkoniyat berilgan,
    o'tkazib yuborsa 0 ball oladi.
    `questions_mode` eski bool qiymatni ham qabul qiladi (moslik uchun).
    """
    if isinstance(questions_mode, bool):   # eski chaqiruvlar uchun
        questions_mode = "required" if questions_mode else "off"
    total = 0
    if questions_mode in STAGE_ON:
        total += MAX_TEST + MAX_WRITTEN
    if video_mode in STAGE_ON:
        total += MAX_VIDEO
    return total


def score_pct(total: int | None, max_total: int | None) -> int | None:
    """Ballni foizga o'giradi."""
    if total is None or not max_total:
        return None
    return round(total * 100 / max_total)

# Excel uchun rang kodlari (ARGB, openpyxl)
XL_GREEN = "C6EFCE"
XL_YELLOW = "FFEB9C"
XL_RED = "FFC7CE"
XL_GREY = "E7E9EB"


def _eff_max(max_total: int | None) -> int:
    """max_total=0 — baholanadigan bosqich yo'q (0 ni 19 ga aylantirmaymiz)."""
    return MAX_TOTAL if max_total is None else max_total


def color_for(total: int | None, max_total: int | None = MAX_TOTAL) -> str:
    """Rang teg. max_total berilmasa 19 ballik tizim deb hisoblanadi."""
    pct = score_pct(total, _eff_max(max_total))
    if pct is None:
        return "\u26aa\ufe0f"
    if pct >= PCT_GREEN_MIN:
        return "\U0001f7e2"
    if pct >= PCT_YELLOW_MIN:
        return "\U0001f7e1"
    return "\U0001f534"


def excel_fill_for(total: int | None, max_total: int | None = MAX_TOTAL) -> str:
    """Excel katakchasi uchun fon rangi."""
    pct = score_pct(total, _eff_max(max_total))
    if pct is None:
        return XL_GREY
    if pct >= PCT_GREEN_MIN:
        return XL_GREEN
    if pct >= PCT_YELLOW_MIN:
        return XL_YELLOW
    return XL_RED


def level_name(total: int | None, max_total: int | None = MAX_TOTAL) -> str:
    pct = score_pct(total, _eff_max(max_total))
    if pct is None:
        return "Baholanmaydi"
    if pct >= PCT_GREEN_MIN:
        return "Yuqori"
    if pct >= PCT_YELLOW_MIN:
        return "O'rta"
    return "Past"
