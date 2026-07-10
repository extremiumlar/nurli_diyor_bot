"""Umumiy yordamchi funksiyalar: guruhga ishonchli yuborish va foydalanuvchilarga broadcast."""
import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter


async def send_to_group(bot: Bot, group_id: int, text: str | None = None,
                        photo_id: str | None = None) -> tuple[bool, str | None]:
    """Guruhga xabar (yoki rasm+caption) yuboradi.

    Superguruhga migratsiya bo'lsa (chat ID o'zgargan bo'lsa) yangi ID ga
    avtomatik qayta yuboradi va sozlamani yangilaydi.
    Qaytaradi: (True, None) muvaffaqiyatli; (False, "xato matni") aks holda.
    """
    from app.database.crud import set_setting

    async def _do(gid: int):
        if photo_id:
            await bot.send_photo(gid, photo=photo_id, caption=text, parse_mode="HTML")
        else:
            await bot.send_message(gid, text, parse_mode="HTML")

    try:
        await _do(group_id)
        return True, None
    except Exception as e:
        # Superguruh migratsiyasi — yangi chat ID ga o'tish
        new_id = getattr(e, "migrate_to_chat_id", None)
        if new_id is not None:
            try:
                await set_setting("apps_group_id", str(new_id))
                await _do(new_id)
                return True, None
            except Exception as e2:
                return False, str(e2)
        return False, str(e)


async def broadcast_to_users(bot: Bot, user_ids, text: str,
                             reply_markup=None, delay: float = 0.05) -> tuple[int, int]:
    """Foydalanuvchilar ro'yxatiga xabar yuboradi.

    Bloklagan foydalanuvchilar obunadan chiqariladi (is_subscribed=False).
    Qaytaradi: (yuborilgan, yuborilmagan) soni.
    """
    from app.database.crud import set_user_unsubscribed

    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, text, parse_mode="HTML", reply_markup=reply_markup)
            sent += 1
            await asyncio.sleep(delay)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
            try:
                await bot.send_message(uid, text, parse_mode="HTML", reply_markup=reply_markup)
                sent += 1
            except Exception:
                failed += 1
        except TelegramForbiddenError:
            # Foydalanuvchi botni bloklagan
            failed += 1
            try:
                await set_user_unsubscribed(uid)
            except Exception:
                pass
        except Exception:
            failed += 1
    return sent, failed
