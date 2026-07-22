# -*- coding: utf-8 -*-
"""
Saralash savollari banki — «NURIDDIN BUILDING» HR-bot.

Har vakansiya uchun: 3 ta test savoli (variant + ball) va 2 ta yozma savol.
Ball qoidasi: eng to'g'ri = 3, qisman = 1, yaroqsiz = 0.
Bu bank admin panelidan vakansiyaga biriktiriladi (vacancy_questions jadvaliga
nusxalanadi). Keyinchalik AI orqali savol tuzish shu formatni ishlatadi.
"""

# Yozma savollar uchun standart baholash mezonlari (kategoriya bo'yicha)
RUBRIC_LOGIC = "Mavzuga aloqadorlik, mantiqiy izchillik va chuqurlik, aniq misol, savodxonlik. (0–3)"
RUBRIC_AI = "Prompt/yechim aniqligi va amaliyligi, AI'dan to'g'ri foydalanish tushunchasi, natijaga yo'naltirilganlik. (0–3)"
RUBRIC_MOTIVATION = "Samimiylik, aniq shaxsiy tajriba/misol, sohaga qiziqish va mas'uliyat hissi. (0–3)"


def _t(text, o3, o1, o0):
    """Test savoli: 3/1/0 balli 3 variant."""
    return {
        "text": text,
        "options": [
            {"text": o3, "score": 3},
            {"text": o1, "score": 1},
            {"text": o0, "score": 0},
        ],
    }


def _w(text, rubric):
    return {"text": text, "rubric": rubric}


QUESTION_BANK = {
    "ceo": {
        "title": "CEO (Bosh direktor)",
        "test": [
            _t("Kompaniyani inqirozdan olib chiqish yoki keskin o'sishga erishishda birinchi strategik qadamingiz qanday bo'ladi?",
               "Moliyaviy oqim va jarayonlarni tahlil qilib, o'sish nuqtalariga resurs yo'naltiraman",
               "Barcha xarajatlarni qisqartirib, xodimlar sonini kamaytiraman",
               "Rahbariyat ko'rsatmasini kutaman va o'zgarish qilmayman"),
            _t("Strategik qarorlar va biznes rejalarni tahlil qilishda sun'iy intellekt (AI) vositalaridan qanday foydalanasiz?",
               "Bozor tahlili, prognozlar va g'oyalar olish uchun AI tizimlaridan faol foydalanaman",
               "Faqat matn tarjima qilish uchun ishlataman",
               "Umuman foydalanmayman, faqat o'z tajribamga tayanaman"),
            _t("Rahbar sifatida jamoada natijadorlik va intizomni saqlashning eng samarali usuli nima?",
               "KPI, aniq vazifalar va shaffof rag'batlantirish tizimini joriy etaman",
               "Qattiq jarima va doimiy nazorat tizimini qo'llayman",
               "Xodimlardan hech qanday talab qo'ymay, erkin qo'yaman"),
        ],
        "written": [
            _w("Uzoq muddatli rejalashtirish va jamoa samaradorligini oshirish bo'yicha eng muvaffaqiyatli amaliyotingiz qanday bo'lgan?", RUBRIC_LOGIC),
            _w("Kompaniyaning yillik strategiyasini tahlil qilish uchun AIga qanday prompt yozgan bo'lardingiz? Namuna keltiring.", RUBRIC_AI),
        ],
    },
    "prorab": {
        "title": "Prorab (Qurilish ishlari boshlig'i)",
        "test": [
            _t("Obyektda ishchilar belgilangan muddatdan kechikayotgan bo'lsa, birinchi bo'lib nima qilasiz?",
               "Sababini o'rganib, jarayonni optimallashtiraman va qo'shimcha resurs jalb qilaman",
               "Ishchilarni jarimaga tortaman",
               "Kechikishni e'tiborsiz qoldiraman"),
            _t("Loyiha hujjatlari va smeta bilan ishlashda zamonaviy dastur/texnologiyalardan foydalanasizmi?",
               "Maxsus dasturlar va raqamli jadvallardan (Excel, AutoCAD va h.k.) foydalanaman",
               "Faqat qog'oz va qo'lda hisoblayman",
               "Texnologiyalardan xabarim yo'q"),
            _t("Obyektda xavfsizlik qoidasi buzilganini ko'rib qoldingiz. Birinchi harakatingiz?",
               "Darhol ishni to'xtatib, qoidalarni tushuntiraman va choralarni ko'raman",
               "Faqat kechki payt tanbeh beraman",
               "Ko'rmaganga olib o'tib ketaman"),
        ],
        "written": [
            _w("Murakkab obyektda ish hajmini o'z vaqtida va sifatli topshirish uchun qanday boshqaruv usullaridan foydalanasiz?", RUBRIC_LOGIC),
            _w("Kompaniyamiz obyektlarida sifatni keskin oshirish bo'yicha qanday aniq taklifingiz bor?", RUBRIC_MOTIVATION),
        ],
    },
    "texnik_nazoratchi": {
        "title": "Texnik nazoratchi",
        "test": [
            _t("Pudratchi ishni tez bajarish uchun sifat standartlarini buzayotganini aniqladingiz. Nima qilasiz?",
               "Ishni qabul qilmayman va standartlarga muvofiq qayta bajarishni talab qilaman",
               "Puldan ushlab qolaman-u, o'tkazib yuboraman",
               "Ko'z yumib yuboraman, tezroq bitirsin"),
            _t("Kamchiliklarni qayd etish va hisobot yuritishda qanday vositalardan foydalanasiz?",
               "Foto/video dalil bilan maxsus elektron jurnal va hisobotlar yuritaman",
               "Qog'ozga eskirgan usulda yozib qo'yaman",
               "Faqat eslab qolaman"),
            _t("Qurilish materialining sifatsizligi aniqlansa, qanday yo'l tutasiz?",
               "Dalolatnoma tuzib, materialni obyekt hududidan chetlatishni talab qilaman",
               "Arzon bo'lsa mayli deyman",
               "Ishlatishga ruxsat beraman"),
        ],
        "written": [
            _w("Texnik nazoratning eng asosiy vazifasi nima va nuqsonlarni o'z vaqtida aniqlash uchun nima qilish kerak?", RUBRIC_LOGIC),
            _w("Texnik nazoratdagi tajribangiz kompaniyamizga qanday aniq foyda keltiradi?", RUBRIC_MOTIVATION),
        ],
    },
    "kran_muhandisi": {
        "title": "Kran muhandisi",
        "test": [
            _t("Kran mexanizmida kichik g'ayritabiiy tovush sezildi, lekin ish davom etishi kerak. Nima qilasiz?",
               "Darhol ishni to'xtatib, to'liq texnik ko'rikdan o'tkazaman",
               "Kun oxirigacha ishlatib, keyin qarayman",
               "E'tibor bermay ishni davom ettiraveraman"),
            _t("Texnik xizmat jadvali va pasport ma'lumotlarini yuritishda qanday usul qo'llaysiz?",
               "Raqamli jadval va maxsus texnik bazada qat'iy nazorat qilaman",
               "Qog'oz daftar tutaman",
               "Xotiramga tayanaman"),
            _t("Xavfsizlik texnikasi qoidalari buzilganda munosabatingiz qanday bo'ladi?",
               "Qoidabuzarlikni darhol bartaraf etib, qat'iy chora ko'raman",
               "Faqat og'zaki ogohlantirib qo'yaman",
               "O'zim ham e'tibor bermayman"),
        ],
        "written": [
            _w("Og'ir yuk ko'taruvchi texnikada favqulodda holatlarning oldini olish uchun qanday profilaktik choralarni ko'rasiz?", RUBRIC_LOGIC),
            _w("Texnik xavfsizlikni ta'minlash bo'yicha o'z tajribangizdan qisqa misol keltiring.", RUBRIC_MOTIVATION),
        ],
    },
    "sotuv_menejeri": {
        "title": "Sotuv menejeri",
        "test": [
            _t("Mijoz 'Sizning mahsulotingiz qimmatroq' desa, nima qilasiz?",
               "Mahsulotning qiymati va beradigan foydasini tushuntiraman",
               "Darhol chegirma taklif qilaman",
               "Raqobatchilarni yomonlayman"),
            _t("Mijoz barcha ma'lumotni olib 'O'ylab ko'raman' desa, qanday yo'l tutasiz?",
               "Aynan qaysi jihatda ikkilanayotganini aniqlashtiruvchi ochiq savol beraman",
               "Har kuni bir necha marta qo'ng'iroq qilaman",
               "'Xo'p, o'ylab ko'ring' deb qo'yaman"),
            _t("Sotuv matnlari va xabarlarini tayyorlashda AIdan foydalanasizmi?",
               "Aniq promptlar yozib, ChatGPT va boshqa AI vositalaridan faol foydalanaman",
               "Faqat tayyor matnni o'qib chiqaman",
               "Yo'q, umuman ishlatmaganman"),
        ],
        "written": [
            _w("Mijoz telefonda qo'pol munosabatda bo'lib ovozini ko'tardi. Uni yo'qotmaslik uchun birinchi nima deysiz?", RUBRIC_LOGIC),
            _w("Mijozga yuboriladigan ta'sirli sotuv xabari uchun ChatGPTga qanday prompt yozgan bo'lardingiz? Namuna keltiring.", RUBRIC_AI),
        ],
    },
    "it_mutaxassisi": {
        "title": "IT mutaxassisi",
        "test": [
            _t("Kompaniya serveri yoki boti to'satdan ishdan chiqdi. Birinchi qadamingiz?",
               "Sababini tezkor aniqlab, zaxira nusxadan tiklash yoki xatoni bartaraf etishni boshlayman",
               "Boshliqlarga yozib, javob kutib turaman",
               "Ertalabgacha tegmayman"),
            _t("Yangi raqamli yechim yoki avtomatlashtirishni joriy etishda qanday yondashasiz?",
               "Zamonaviy texnologiya va AI yordamida jarayonni tez va samarali avtomatlashtiraman",
               "Birovning tayyor kodini tushunmasdan ko'chirib qo'yaman",
               "Faqat eski usulda ishlayveraman"),
            _t("Tarmoq xavfsizligini ta'minlash uchun asosiy choralar?",
               "Kuchli parol siyosati, shifrlash va doimiy zaxiralash (backup) tizimini o'rnataman",
               "Faqat antivirus ishlataman",
               "Hech qanday chora ko'rmayman"),
        ],
        "written": [
            _w("Kutilmagan texnik nosozlik yuz berganda uni bartaraf etish uchun qanday algoritm bo'yicha ishlaysiz?", RUBRIC_LOGIC),
            _w("Kompaniya samaradorligini oshirish uchun qanday IT yechim yoki avtomatlashtirishni taklif qilasiz?", RUBRIC_AI),
        ],
    },
    "mobilograf": {
        "title": "Mobilograf (Video operator)",
        "test": [
            _t("Obyektdan tezkor va e'tiborni tortadigan Reels/video olish kerak. Qanday yondashasiz?",
               "Dinamik kadr, sifatli ovoz va zamonaviy trendga mos montaj ssenariysi bilan tasvirga olaman",
               "Oddiygina videoga olib qo'yaman",
               "Faqat rasmga olaman"),
            _t("Video g'oyalari va ssenariy topishda AI yoki trend tahlilidan foydalanasizmi?",
               "AI va ijtimoiy tarmoq trendlarini tahlil qilib, kreativ ssenariylar tayyorlayman",
               "Faqat o'zim o'ylab topaman",
               "Boshqalardan ko'chiraman"),
            _t("Topshirish muddati qisqa, lekin sifat talab darajasida bo'lishi kerak. Nima qilasiz?",
               "Tezkor montaj qilib, e'tiborni eng zo'r kadrlarga qarataman",
               "Muddatni o'zgartirishni so'rayman",
               "Sifatini tushirib yuboraman"),
        ],
        "written": [
            _w("Kompaniya faoliyatini (qurilish va xizmatlar) ijtimoiy tarmoqlarda ommalashtirish uchun qanday video formatlarni taklif qilasiz?", RUBRIC_LOGIC),
            _w("Reels ssenariysi yaratish uchun AIga qanday prompt berardingiz? Bitta namuna yozing.", RUBRIC_AI),
        ],
    },
    "hr_menejer": {
        "title": "HR menejer",
        "test": [
            _t("Bo'sh vakansiyaga tezkor va malakali nomzod topish kerak. Qanday strategiya qo'llaysiz?",
               "Telegram botlar, maqsadli e'lonlar va faol sourcing usullaridan foydalanaman",
               "Faqat tanish-bilish orqali izlayman",
               "Bitta joyga e'lon berib kutaman"),
            _t("Dastlabki saralash va test tuzishda AIdan foydalanasizmi?",
               "AI yordamida testlar, savollar va baholash mezonlarini avtomatlashtiraman",
               "Internetdan tayyor ko'chirib olaman",
               "Hammasini qo'lda qilaman"),
            _t("Xodimlar orasida kelishmovchilik chiqqanda birinchi qadamingiz?",
               "Vaziyatni o'rganib, xolis muloqot orqali murosaga keltiraman",
               "Ikkalasini darhol ishdan bo'shataman",
               "Aralashmayman"),
        ],
        "written": [
            _w("Kadrlar oqimini (xodimlar ketishini) kamaytirish uchun qanday motivatsiya tizimini taklif qilasiz?", RUBRIC_LOGIC),
            _w("Nomzodning professional darajasi va shaxsiy sifatlarini 1 daqiqalik video orqali aniqlashda e'tibor beradigan 3 ta asosiy mezoningiz nima?", RUBRIC_LOGIC),
        ],
    },
    "rop": {
        "title": "ROP (Sotuv bo'limi rahbari)",
        "test": [
            _t("Sotuv bo'limi oylik rejadan ortda qolmoqda. Birinchi harakatingiz?",
               "Analitika qilib, oqsayotgan bosqichni aniqlayman va jamoaga amaliy yordam beraman",
               "Rejani o'zim bajarishga urinaman",
               "Xodimlarni qattiq jarimaga tortaman"),
            _t("Sotuv skriptlari va avtomatizatsiyada AIdan qanday foydalanasiz?",
               "AI yordamida skriptlarni mukammallashtiraman va CRM tahlilini tezlashtiraman",
               "Faqat xodimlar o'zlari yozadi",
               "Foydalanmayman, eskicha ishlaymiz"),
            _t("Yangi menejerni jamoaga tez moslashtirish uchun qanday tizim qo'llaysiz?",
               "Mentorlik tizimi, tayyor baza va kunlik tahlil orqali tezkor o'qitaman",
               "Faqat kitob o'qishni aytaman",
               "O'z holiga tashlab qo'yaman"),
        ],
        "written": [
            _w("Sotuv bo'limida konversiyani oshirish va menejerlar mas'uliyatini kuchaytirish uchun qanday KPI tizimini qo'llaysiz?", RUBRIC_LOGIC),
            _w("Sotuv bo'limini boshqarishdagi eng yaxshi natijaviy tajribangiz haqida qisqacha yozing.", RUBRIC_MOTIVATION),
        ],
    },
    "buxgalter": {
        "title": "Buxgalter",
        "test": [
            _t("Soliq hisoboti muddati yaqin, lekin hujjatlarda yetishmovchilik bor. Nima qilasiz?",
               "Zudlik bilan mas'ullar bilan bog'lanib, hujjatlarni tiklayman va o'z vaqtida topshiraman",
               "Hisobotni kechiktiraman",
               "Kutib turaman"),
            _t("Moliyaviy hisobot va soliq hisob-kitobida qanday dasturlardan foydalanasiz?",
               "1C, Soliq va raqamli buxgalteriya dasturlaridan to'liq foydalanaman",
               "Faqat oddiy Excel ishlataman",
               "Faqat qog'ozda yuritaman"),
            _t("Xarajatlarni optimallashtirish uchun qanday moliyaviy nazorat o'rnatasiz?",
               "Birlamchi hujjatlarni qat'iy nazorat qilib, xarajatlar smetasini yuritaman",
               "Hamma xarajatni taqiqlayman",
               "Nazorat qilmayman"),
        ],
        "written": [
            _w("Moliyaviy xatarlarning oldini olish va soliq qonunchiligiga rioya bo'yicha qanday nazorat usullarini qo'llaysiz?", RUBRIC_LOGIC),
            _w("Buxgalteriya jarayonini avtomatlashtirish bo'yicha qanday tajribangiz yoki taklifingiz bor?", RUBRIC_AI),
        ],
    },
    "kassir": {
        "title": "Kassir",
        "test": [
            _t("Kassa hisob-kitobida kamomad (minus) chiqdi. Birinchi ishingiz?",
               "Hujjat va o'tgan operatsiyalarni sinchiklab tekshirib, sababini aniqlayman va rahbariyatga bildiraman",
               "O'z cho'ntagimdan to'lab, indamayman",
               "Boshqaga to'nkab qo'yaman"),
            _t("Kassa dasturlari va terminal tizimlari bilan ishlash tajribangiz qanday?",
               "Maxsus kassa dasturi, terminal va raqamli tizimlarda mukammal ishlayman",
               "Hozircha yangi o'rganaman",
               "Faqat qo'lda daftarga yozaman"),
            _t("Mijoz pulni sanab berayotganda shoshtirsa yoki xato qilsa, qanday yo'l tutasiz?",
               "Xotirjam mablag'ni qayta va aniq sanab, keyin qabul qilaman",
               "Shoshilib qabul qilib yuboraman",
               "Jahlim chiqadi"),
        ],
        "written": [
            _w("Pul bilan ishlashda xavfsizlik va xatoga yo'l qo'ymaslik uchun qanday shaxsiy qoidalarga amal qilasiz?", RUBRIC_LOGIC),
            _w("Kassir ishida halollik va intizom nega eng muhim fazilat deb o'ylaysiz?", RUBRIC_MOTIVATION),
        ],
    },
    "targetolog": {
        "title": "Targetolog",
        "test": [
            _t("Reklama byudjeti sarflanyapti, lekin kutilgan lidlar kelmayapti. Nima qilasiz?",
               "Auditoriya, kreativ va offerni tahlil qilib, A/B testlar orqali o'zgartirish kiritaman",
               "Byudjetni shunchaki oshiraman",
               "Reklamani butunlay o'chiraman"),
            _t("Reklama matni va banner g'oyalarini tayyorlashda AIdan foydalanasizmi?",
               "AI yordamida konversiyaga yo'naltirilgan turli matn va g'oyalar generatsiya qilaman",
               "Faqat o'zim o'ylayman",
               "Boshqalardan ko'chiraman"),
            _t("Facebook Ads qoidalari bo'yicha reklama bloklansa, qanday yo'l tutasiz?",
               "Qoidabuzarlikni aniqlab tuzataman va apellyatsiya yo'llayman",
               "Reklamani butunlay to'xtataman",
               "Boshqa profil ochib, aylanib o'taman"),
        ],
        "written": [
            _w("Kompaniyamiz uchun target reklamada eng yuqori ROI olish uchun qanday strategiya qo'llaysiz?", RUBRIC_LOGIC),
            _w("Oxirgi muvaffaqiyatli reklama kampaniyangiz va uning natijalari (raqamlar bilan) haqida yozing.", RUBRIC_MOTIVATION),
        ],
    },
    "yuridik_maslahatchi": {
        "title": "Yuridik maslahatchi",
        "test": [
            _t("Tuzilayotgan shartnomada kompaniya uchun yashirin yuridik xatar sezdingiz. Nima qilasiz?",
               "Xatarni batafsil bayon qilib, bandlarni kompaniya manfaatiga moslab o'zgartiraman",
               "Shartnomani rad etaman, lekin sababini tushuntirmayman",
               "E'tibor bermay imzo qo'yaveraman"),
            _t("Normativ hujjatlar va o'zgarishlarni kuzatishda raqamli bazalardan foydalanasizmi?",
               "Lex.uz va zamonaviy yuridik tahlil vositalaridan faol foydalanaman",
               "Faqat qog'oz kodekslarni o'qiyman",
               "Kuzatib bormayman"),
            _t("Kompaniyaga nisbatan da'vo kelib tushdi. Birinchi harakatingiz?",
               "Da'voni huquqiy o'rganib, muddatida asosli e'tiroz yoki javob tayyorlayman",
               "Boshliqlarga tashlab qo'yaman",
               "Javob bermay yashirib qo'yaman"),
        ],
        "written": [
            _w("Shartnomalarni tuzishda huquqiy xatarlarni minimallashtirish uchun qanday tekshiruv tizimini qo'llaysiz?", RUBRIC_LOGIC),
            _w("Yuridik amaliyotingizda hal qilgan eng murakkab muammo va uning yechimi haqida yozing.", RUBRIC_MOTIVATION),
        ],
    },
    "pto_muhandisi": {
        "title": "PTO muhandisi (Loyiha-smeta bo'limi)",
        "test": [
            _t("Narxlar oshgani sababli smeta oshib ketish xavfi paydo bo'ldi. Nima qilasiz?",
               "Zudlik bilan optimallashtirish variantlarini topib, rahbariyatga hisobot beraman",
               "Ishni to'xtatib qo'yaman",
               "Indamay xarajatni oshirib yuboraman"),
            _t("Smeta va hajmlarni hisoblashda qanday dasturiy ta'minotdan foydalanasiz?",
               "Smeta dasturlari va ilg'or Excel jadvallaridan foydalanib tez va aniq hisoblayman",
               "Faqat qo'lda kalkulyatorda hisoblayman",
               "Taxminan yozaman"),
            _t("Loyiha hujjatida xatolik aniqlansa, qanday yo'l tutasiz?",
               "Loyiha muallifi va buyurtmachi bilan kelishib, rasmiy o'zgartirish kiritaman",
               "O'z bilganimcha to'g'rilab qo'yaman",
               "E'tibor bermayman"),
        ],
        "written": [
            _w("Smeta tuzishda va xarajatlarni qat'iy nazorat qilishda qanday usullarni qo'llaysiz?", RUBRIC_LOGIC),
            _w("PTO sohasida ish jarayonini tezlashtirish bo'yicha o'z tajribangizdan misol keltiring.", RUBRIC_MOTIVATION),
        ],
    },
    "buxgalter_yordamchisi": {
        "title": "Buxgalter yordamchisi",
        "test": [
            _t("Birlamchi hujjatda (faktura, nakladnoy) imzo yoki sana yetishmayapti. Nima qilasiz?",
               "Mas'ul shaxs bilan bog'lanib, hujjatni to'g'rilattirib, keyin kiritaman",
               "Shundoq o'tkazib yuboraman",
               "Yirtib tashlayman"),
            _t("1C va Excelda ishlash darajangiz qanday?",
               "Birlamchi hujjatlarni tez va xatosiz kirita olaman",
               "Faqat o'rganishni boshlayapman",
               "Umuman ishlamaganman"),
            _t("Ko'p hujjat kiritishda charchoq tufayli xato xavfi bo'lsa, nima qilasiz?",
               "Diqqat bilan tekshirib, qisqa tanaffuslar bilan xatosiz ishlashni ta'minlayman",
               "Ishni tashlab ketaman",
               "Xato bo'lsa farqi yo'q"),
        ],
        "written": [
            _w("Birlamchi hujjatlar bilan ishlashda xatoga yo'l qo'ymaslik uchun qanday tartibga amal qilasiz?", RUBRIC_LOGIC),
            _w("Nega buxgalteriya sohasida karyerangizni davom ettirmoqchisiz va qanday maqsadlaringiz bor?", RUBRIC_MOTIVATION),
        ],
    },
    "yordamchi_xodim": {
        "title": "Yordamchi xodim",
        "test": [
            _t("Sizga bir vaqtda ikkita turli topshiriq berildi. Qanday yo'l tutasiz?",
               "Muhimligi va shoshilinchligiga qarab navbat bilan ikkalasini ham bajaraman",
               "Faqat bittasini qilib, ikkinchisini unutaman",
               "Ikkalasini ham qilmayman"),
            _t("Berilgan topshiriqda mas'uliyatni qanday tushunasiz?",
               "Topshiriqni sifatli, o'z vaqtida va oxirigacha yetkazib bajaraman",
               "Aytgandek qilib qo'ysam bo'ldi",
               "Faqat nazorat bo'lsa bajaraman"),
            _t("Jamoada tartib va tozalikni saqlashga yondashuvingiz qanday?",
               "Doimo tartib va ozodalikka o'zim rioya qilib, boshqalarga yordam beraman",
               "Faqat buyursalar qilaman",
               "Boshqalarning ishi deb o'ylayman"),
        ],
        "written": [
            _w("Kutilmagan yordamchi yumushlarni bajarishda sizni qaysi xususiyatingiz ajratib turadi?", RUBRIC_LOGIC),
            _w("Ishga munosabatingiz va intizomingiz haqida qisqacha yozing.", RUBRIC_MOTIVATION),
        ],
    },
    "kran_mashinisti": {
        "title": "Kran mashinisti",
        "test": [
            _t("Noqulay ob-havoda (kuchli shamol) yuk ko'tarish talab qilindi. Nima qilasiz?",
               "Xavfsizlik qoidasiga ko'ra ishni rad etib, ob-havo yaxshilanishini kutaman",
               "Tavakkal qilib ko'taraman",
               "Buyruq bo'lsa ko'taraveraman"),
            _t("Kranni har kuni ishga tushirishdan oldin texnik tekshiruvdan o'tkazasizmi?",
               "Har safar to'liq texnik ko'rikdan o'tkazib, so'ng ishni boshlayman",
               "Faqat haftada bir marta",
               "Yo'q, shunchaki o'tirib ishlayveraman"),
            _t("Yuk ko'tarishda xavfli zonada odam yurganini ko'rdingiz. Birinchi harakatingiz?",
               "Zudlik bilan kran harakatini to'xtatib, odamlarni xavfsiz hududga chiqaraman",
               "Signal berib davom etaveraman",
               "E'tibor bermayman"),
        ],
        "written": [
            _w("Kran boshqarishda favqulodda vaziyatlarning oldini olish uchun qanday qoidalarga qat'iy amal qilasiz?", RUBRIC_LOGIC),
            _w("Og'ir yuklar bilan ishlash tajribangiz va xavfsizlik mas'uliyatingiz haqida yozing.", RUBRIC_MOTIVATION),
        ],
    },
    "sotuv_operatori": {
        "title": "Sotuv operatori",
        "test": [
            _t("Mijoz telefonda asabiy gapirib, shikoyat qilyapti. Nima qilasiz?",
               "Xotirjam tinglab, tushunish bildiraman va muammosini hal qilishga yordam beraman",
               "Boshqasiga ulab yuboraman",
               "Men ham ovozimni ko'taraman yoki go'shakni qo'yaman"),
            _t("Muloqot paytida ma'lumotni CRMga tezkor va xatosiz kirita olasizmi?",
               "Suhbat davomida bir vaqtda CRMga tezkor va aniq yozib boraman",
               "Sekin yozaman",
               "Faqat qog'ozga yozaman"),
            _t("Kun davomida ko'p qo'ng'iroqda xushmuomalalikni saqlash uchun nima qilasiz?",
               "Har bir mijozga birinchi mijozdek e'tibor va iliqlik bilan munosabatda bo'laman",
               "Ohangsiz, quruq javob beraman",
               "Asabiylashaman"),
        ],
        "written": [
            _w("Mijozning shubhali savollariga ishonchli javob berishda qanday usuldan foydalanasiz?", RUBRIC_LOGIC),
            _w("Sotuv operatori sifatida mijozni jalb qilishdagi asosiy qurolingiz nima?", RUBRIC_MOTIVATION),
        ],
    },
    "brand_face": {
        "title": "Brand Face (Kompaniya qiyofasi)",
        "test": [
            _t("Prodyuser matnni qo'lingizga bermay, mavzuni aytib, improvizatsiya so'radi. Nima qilasiz?",
               "Mavzuni tez tushunib, erkin va ishonchli tarzda tabiiy chiqish qilaman",
               "Faqat yozib berilsa o'qiyman",
               "Juda hayajonlanaman va gapira olmayman"),
            _t("Brend videosi ssenariysiga o'zingizdan kreativlik qo'sha olasizmi?",
               "Kreativ g'oyalar qo'shib, videoni jonli va qiziqarli chiqishini ta'minlayman",
               "Faqat aytilganini qilaman",
               "Fikr bildirmayman"),
            _t("Ijtimoiy tarmoqdagi negativ izohlarga qanday munosabatda bo'lasiz?",
               "Professional yondashib, xotirjam va odob bilan javob beraman",
               "E'tibor bermay o'tkazib yuboraman",
               "Jahl bilan javob qaytaraman"),
        ],
        "written": [
            _w("Kompaniyaning ommaviy imidjini ko'tarish va ishonch uyg'otishda Brand Face sifatida qanday rol o'ynaysiz?", RUBRIC_LOGIC),
            _w("Kamera oldidagi erkinligingiz va xarizmangizni ko'rsatish uchun 1 daqiqalik video-vizitkada nima haqida gapirasiz?", RUBRIC_MOTIVATION),
        ],
    },
    "sayhun_sotuvchi": {
        "title": "Sayhun bozorda sotuvchi",
        "test": [
            _t("Mijoz mahsulot tanlashda ikkilanmoqda. Unga qanday yordam berasiz?",
               "Ehtiyojini so'rab, mos eng yaxshi mahsulotni tavsiya qilaman va afzalligini tushuntiraman",
               "Majburan sotishga urinaman",
               "O'z holiga qo'yib qo'yaman"),
            _t("Savdo nuqtasida mahsulot qoldig'i va tartibini qanday saqlaysiz?",
               "Doimo mahsulotni ko'rinadigan joyda, toza va tartibli saqlayman",
               "Vaqti-vaqti bilan qarayman",
               "Tartibga e'tibor bermayman"),
            _t("Pul hisob-kitobida adashmaslik uchun nima qilasiz?",
               "Har xaridda pulni diqqat bilan sanab, qaytimni aniq beraman",
               "Shoshilib beraman",
               "Tavakkal sanayman"),
        ],
        "written": [
            _w("Bozor ichidagi raqobat muhitida mijozni aynan bizning savdo nuqtamizdan xarid qilishga qanday undaysiz?", RUBRIC_LOGIC),
            _w("Savdo sohasida erishgan eng yaxshi natijangiz yoki mijoz bilan qiziqarli voqeani yozing.", RUBRIC_MOTIVATION),
        ],
    },
    "taminotchi": {
        "title": "Ta'minotchi",
        "test": [
            _t("Zudlik kerak material bozorda qolmagan yoki juda qimmat. Nima qilasiz?",
               "Muqobil yetkazib beruvchi va ulgurji bazalar orqali tezkor topib, eng maqbul narxda keltiraman",
               "Qimmat bo'lsa ham darrov sotib olaveraman",
               "'Topolmadim' deb qo'l siltayman"),
            _t("Yetkazib beruvchilar bilan narx va sifat muzokarasida qanday usul qo'llaysiz?",
               "Uzoq muddatli hamkorlik va hajm evaziga eng yaxshi chegirma va shartlarga erishaman",
               "Faqat aytgan narxini berib olib kelaman",
               "Tortishishni yoqtirmayman"),
            _t("Olib kelingan material sifati talabga javob bermasa, nima qilasiz?",
               "Darhol tovarni qaytarib, sifatlisiga almashtirishni talab qilaman",
               "Rahbariyatga aytmasdan ishlataveraman",
               "Shundoq qabul qilibaveraman"),
        ],
        "written": [
            _w("Ta'minotda tezkorlik va tejamkorlikni bir vaqtda qanday ta'minlaysiz?", RUBRIC_LOGIC),
            _w("Ta'minotdagi aloqalaringiz va eng murakkab buyurtmani muvaffaqiyatli bajarganingiz haqida yozing.", RUBRIC_MOTIVATION),
        ],
    },
}


# Reyting rang chegaralari (jami 19 balldan). Sozlamada o'zgartirilishi mumkin.
COLOR_GREEN_MIN = 14   # 🟢 >= 14
COLOR_YELLOW_MIN = 9   # 🟡 9–13, 🔴 <= 8

MAX_TEST = 9
MAX_WRITTEN = 6
MAX_VIDEO = 4
MAX_TOTAL = 19


def color_for(total: int | None) -> str:
    if total is None:
        return "⚪️"
    if total >= COLOR_GREEN_MIN:
        return "🟢"
    if total >= COLOR_YELLOW_MIN:
        return "🟡"
    return "🔴"
