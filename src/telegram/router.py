from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio
from contextlib import suppress

from aiogram import Router, html
from aiogram.types import Message
from aiogram.filters import Command
from funpaybotengine.types import OfferFields

from .ui import (
    MenuIds,
    DeleteLotsCD,
    OffersListMenuContext
)
from ..properties import DeleteLotsProperties

if TYPE_CHECKING:
    from aiogram.types import Message, CallbackQuery as Query
    from funpayhub.app.main import FunPayHub as FPH


router = Router()


@router.message(Command('del_lots'))
async def del_lots_cmd(msg: Message) -> None:
    await OffersListMenuContext(menu_id=MenuIds.delete_lots_list, trigger=msg).answer_to()


@router.callback_query(DeleteLotsCD.filter())
async def delete_lots(
    q: Query, cbd: DeleteLotsCD, hub: FPH, plugin_properties: DeleteLotsProperties
) -> None:
    if not cbd.chosen_subcategories:
        await q.answer('❌ Ты не выбрал ни одной категории', show_alert=True)
        return

    status_msg = await q.message.edit_text(
        '<tg-emoji emoji-id="5454074580010295588">⏳</tg-emoji>',
    )

    success_count = 0
    error_count = 0

    for category_id in cbd.chosen_subcategories:
        offers = await hub.funpay.bot.get_my_offers_page(subcategory_id=category_id)

        for offer in offers.offers.values():
            if not plugin_properties.delete_active_lots and not offer.disabled:
                continue

            if not plugin_properties.delete_not_active_lots and offer.disabled:
                continue

            try:
                await hub.funpay.bot.save_offer_fields(
                    OfferFields(
                        fields_dict={'offer_id': str(offer.id), 'deleted': '1'},
                        raw_source='',
                    ),
                )
                success_count += 1
                await asyncio.sleep(0.7)
            except Exception as e:
                error_count += 1
                with suppress(Exception):
                    await q.message.reply(
                        f'❌ <b>Ошибка при удалении лота '
                        f'{html.link(value=str(offer.id), link=f"https://funpay.com/lots/offer?id={offer.id}")}:</b> '
                        f'<code>{str(e)}</code>',
                    )

        await asyncio.sleep(1.5)

    if error_count == 0:
        await status_msg.edit_text('<tg-emoji emoji-id="5472060472821818559">🌹</tg-emoji>')
    else:
        await status_msg.edit_text(
            f'🤩 <b>Готово!</b>\n\n'
            f'• Удалено лотов: <code>{success_count} шт.</code>\n'
            f'• Ошибок при удалении: <code>{error_count} шт.</code>',
        )
