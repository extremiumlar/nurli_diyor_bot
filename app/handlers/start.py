from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.database.crud import create_or_update_user, get_setting
from app.keyboards.reply import main_menu
from app.keyboards.inline import not_subscribed_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    await create_or_update_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    await message.answer(
        "👋 <b>Xush kelibsiz!</b>\nQuyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


@router.message(F.text == "🏢 Biz haqimizda")
async def about_handler(message: Message):
    text = (
        "🏗 <b>Nurli Diyor Qurilish Kompaniyasi</b>\n\n"

        "Biz — Sirdaryo bo'ylab zamonaviy, sifatli va qulay uy-joylar quruvchi "
        "ishonchli qurilish kompaniyasimiz. Har bir loyihamizda mijozlarimizning "
        "ehtiyojlari va qulayligi birinchi o'rinda turadi.\n\n"

        "👷 <b>Bizning jamoamiz</b>\n"
        "Jamoamizda 100+ dan ortiq malakali mutaxassislar: muhandislar, "
        "me'morlar, brigadirlar va ishchilar faoliyat yuritadi. Har bir "
        "xodimimiz o'z sohasining professionali — barchaning umumiy maqsadi "
        "sifatli natija!\n\n"

        "💼 <b>Ish sharoitlari</b>\n"
        "✅ Rasmiy mehnat shartnomasi\n"
        "✅ O'z vaqtida ish haqi to'lovi\n"
        "✅ Ijtimoiy kafolatlar (ta'til, kasallik varag'i)\n"
        "✅ Qulay ish grafigi (5 kun, 8 soat)\n"
        "✅ Jamoaviy korporativ tadbirlar\n"
        "✅ Malaka oshirish va o'sish imkoniyatlari\n\n"

        "💰 <b>Ish haqi</b>\n"
        "Ish haqi lavozim va tajribaga qarab belgilanadi. "
        "To'lov <b>kompaniya hisobidan</b>, har oyning belgilangan sanasida — "
        "hech qanday kechikishsiz!\n\n"

        "🌟 <b>Nega aynan biz?</b>\n"
        "Nurli Diyor — bu nafaqat ish joyi, balki o'zingizni rivojlantira "
        "oladigan, jamoada o'sib, karyerangizni qura oladigan muhit. "
        "Yangi avlod mutaxassislarini qo'llab-quvvatlaymiz va ularga "
        "real imkoniyat yaratamiz!\n\n"

        "📩 Qo'shilishni xohlaysizmi? <b>Ariza Topshirish</b> tugmasini bosing!"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=main_menu())


@router.callback_query(lambda c: c.data == "check_subscribe")
async def check_subscribe_handler(callback: CallbackQuery, bot: Bot):
    channel_id_str = await get_setting("channel_id")
    if not channel_id_str:
        await callback.answer("✅ Botdan foydalanishingiz mumkin!", show_alert=False)
        try:
            await callback.message.delete()
        except Exception:
            pass
        return

    try:
        from aiogram.types import ChatMemberLeft, ChatMemberBanned
        member = await bot.get_chat_member(int(channel_id_str), callback.from_user.id)
        if isinstance(member, (ChatMemberLeft, ChatMemberBanned)):
            await callback.answer("❌ Siz hali kanalga a'zo bo'lmagansiz!", show_alert=True)
            return
    except Exception:
        await callback.answer("✅ Botdan foydalanishingiz mumkin!")
        try:
            await callback.message.delete()
        except Exception:
            pass
        return

    await callback.answer("✅ Rahmat! Botdan foydalanishingiz mumkin.", show_alert=True)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        "👋 <b>Xush kelibsiz!</b>\nQuyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
