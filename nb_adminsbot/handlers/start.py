from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..keyboards import main_menu


router = Router(name="nb2_start")


WELCOME = (
    "👋 Salom, {name}!\n\n"
    "Bu — <b>Nuriddin Buildings</b> kanal-adminlari uchun post yaratish boti.\n\n"
    "Bot quyidagilarni qila oladi:\n"
    "• 📝 Matn va medialar (rasm, video, hujjat, audio) bilan post yaratish\n"
    "• 🔗 Inline URL-tugmalar qo'shish\n"
    "• 👍 Reaksiya tugmalari qo'shish\n"
    "• 💬 Izoh sozlash (Native Comments)\n"
    "• 🔕 Ovozsiz yuborish\n"
    "• 📌 Postni avtomatik pin qilish\n"
    "• 🗑 Yuborilgan postni o'chirish\n\n"
    "Boshlash uchun «➕ Kanal qo'shish» tugmasini bosing."
)


HELP_TEXT = (
    "<b>Yordam</b>\n\n"
    "<b>1) Kanalingizni qo'shish</b>\n"
    "  • Botni kanalingizga <b>admin</b> qilib qo'shing (post yuborish huquqi bilan).\n"
    "  • So'ngra «➕ Kanal qo'shish» tugmasini bosib, kanalingizdan istalgan postni botga forward qiling.\n\n"
    "<b>2) Post yaratish</b>\n"
    "  • «📝 Yangi post» tugmasini bosing va kanalni tanlang.\n"
    "  • Matn yoki media yuboring.\n"
    "  • Inline tugmalar, reaksiyalar, ovozsiz rejim va boshqa sozlamalarni tanlang.\n"
    "  • «✅ Nashr etish» tugmasi bilan kanalga yuboring.\n\n"
    "<b>URL-tugmalar formati:</b>\n"
    "<code>Saytimiz - https://nuriddinbuildings.uz</code>\n"
    "<code>Instagram - https://instagram.com/x | Telegram - @username</code>\n"
    "(har bir qator — alohida qator, <code>|</code> bilan ajratilgan tugmalar — bitta qatorda)\n\n"
    "🎨 <b>Tugmaga rang:</b> matn boshiga rang kodi qo'ying:\n"
    "<code>[Q] Ariza - URL</code> → 🔴 Ariza\n"
    "<code>[Y!] Manzil - URL</code> → 🟩🟩 Manzil 🟩🟩 (to'liq rang)\n"
    "<code>[app] Ariza - https://...</code> → yashil pill (Mini App, HTTPS shart)\n\n"
    "O'zbekcha: <code>[Q]</code>🔴 <code>[Y]</code>🟢 <code>[S]</code>🟡 "
    "<code>[K]</code>🔵 <code>[B]</code>🟣 <code>[T]</code>🟠 "
    "<code>[QR]</code>⚫ <code>[O]</code>⚪\n"
    "Kod oxiriga <code>!</code> qo'ying — yorqin to'liq rangli tugma."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    name = message.from_user.first_name if message.from_user else "do'st"
    await message.answer(WELCOME.format(name=name), reply_markup=main_menu())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Yordam")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu())


@router.message(F.text == "❌ Bekor qilish")
async def cancel_any(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("✅ Bekor qilindi.", reply_markup=main_menu())
