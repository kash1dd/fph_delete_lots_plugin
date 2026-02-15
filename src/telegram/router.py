from __future__ import annotations

import asyncio
from typing import Any, Mapping
from contextlib import suppress

from aiogram import Router, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from funpayparsers.types import SubcategoryType
from funpaybotengine.types import OfferFields, OfferPreview
from funpaybotengine.storage import InMemoryStorage

from funpayhub.lib.telegram.ui import UIRegistry, MenuContext

from funpayhub.app.main import FunPayHub

from .ui import (
    MenuIds,
    DeleteLotsCD,
    AddCategoryCD,
    RemoveCategoryCD,
    ChooseCategoriesCD,
    ConfirmDeleteLotsCD,
    ChooseAllCategoriesCD,
)
from .middleware import ExceptRecordNotFoundMiddleware
from ..properties import DeleteLotsProperties
from ..state_storage import StateStorage


router = Router()
router.callback_query.middleware(ExceptRecordNotFoundMiddleware())


async def get_categories(
    offers: Mapping[SubcategoryType, Mapping[int, list[OfferPreview]]],
    hub: FunPayHub,
) -> dict[int, str]:
    categories = {}
    for subcategory_type, subcategories in offers.items():
        for subcategory_id, offers in subcategories.items():
            storage: InMemoryStorage = hub.funpay.bot.storage  # type: ignore
            category = storage._subcategories[subcategory_type][subcategory_id][1]  # type: ignore
            subcategory = await hub.funpay.bot.storage.get_subcategory(
                subcategory_type=subcategory_type,
                subcategory_id=subcategory_id,
            )

            if subcategory is not None:
                categories[subcategory_id] = f'{subcategory.name} {category.name}'

    return categories


async def get_offers_by_category(
    offers: Mapping[SubcategoryType, Mapping[int, list[OfferPreview]]],
) -> dict[int, list[OfferPreview]]:
    offers_by_category = {}
    for subcategory_type, subcategories in offers.items():
        for subcategory_id, offers in subcategories.items():
            offers_by_category[subcategory_id] = offers_by_category.get(subcategory_id, []) + list(
                offers,
            )

    return offers_by_category


async def create_new_record(
    msg: Message,
    hub: FunPayHub,
    delete_lots_state_storage: StateStorage,
    show_back: bool = True,
) -> int | None:
    bot = hub.funpay.bot

    try:
        profile_page = await bot.get_profile_page(id=bot.userid)
    except Exception:
        txt = '❌ <b>Произошла ошибка при получении страницы профиля :/</b>'
        if msg.from_user.is_bot:
            await msg.edit_text(txt)
        else:
            await msg.reply(txt)
        return None

    categories = await get_categories(profile_page.offers or {}, hub)

    if not categories:
        txt = '❌ <b>У тебя нет активных лотов, которые можно удалить</b>'
        if msg.from_user.is_bot:
            await msg.edit_text(txt)
        else:
            await msg.reply(txt)
        return None

    return delete_lots_state_storage.add_record(
        categories=categories,
        chosen_categories=[],
        show_back=show_back,
    )


async def delete_lots_open_menu(
    record_id: int,
    msg: Message,
    tg_ui: UIRegistry,
    delete_lots_state_storage: StateStorage,
    data: dict[str, Any] | None = None,
    callback_data: ChooseCategoriesCD | None = None,
    edit: bool = False,
) -> None:
    record = delete_lots_state_storage.get_record(record_id)
    data = (data or {}) | {'message': msg}
    if callback_data is None:
        callback_data = ChooseCategoriesCD(history=[], data={})
    menu_ctx = MenuContext(
        menu_id=MenuIds.delete_lots_list,
        data={
            'categories': record.categories,
            'chosen_categories': record.chosen_categories,
            'record_id': record_id,
            'show_back': record.show_back,
        },
        trigger=msg,
        callback_override=callback_data,
    )
    if edit:
        await (await tg_ui.build_menu(menu_ctx, data)).apply_to(msg)
    else:
        await (await tg_ui.build_menu(menu_ctx, data)).answer_to(msg)


@router.message(Command('del_lots'))
async def del_lots_cmd(
    msg: Message,
    data: dict[str, Any],
    delete_lots_state_storage: StateStorage,
    hub: FunPayHub,
    tg_ui: UIRegistry,
) -> None:
    record_id = await create_new_record(
        msg=msg,
        hub=hub,
        delete_lots_state_storage=delete_lots_state_storage,
        show_back=False,
    )

    if record_id is not None:
        await delete_lots_open_menu(
            record_id=record_id,
            msg=msg,
            tg_ui=tg_ui,
            delete_lots_state_storage=delete_lots_state_storage,
            data=data,
        )


@router.callback_query(ChooseCategoriesCD.filter())
async def del_lots_menu(
    call: CallbackQuery,
    callback_data: ChooseCategoriesCD,
    data: dict[str, Any],
    delete_lots_state_storage: StateStorage,
    hub: FunPayHub,
    tg_ui: UIRegistry,
) -> None:
    record_id = await create_new_record(
        msg=call.message,
        hub=hub,
        delete_lots_state_storage=delete_lots_state_storage,
    )

    if record_id is not None:
        await delete_lots_open_menu(
            record_id=record_id,
            msg=call.message,
            tg_ui=tg_ui,
            delete_lots_state_storage=delete_lots_state_storage,
            data=data,
            callback_data=callback_data,
            edit=True,
        )


@router.callback_query(AddCategoryCD.filter())
async def add_offer_to_state(
    call: CallbackQuery,
    callback_data: AddCategoryCD,
    data: dict[str, Any],
    delete_lots_state_storage: StateStorage,
    tg_ui: UIRegistry,
) -> None:
    delete_lots_state_storage.add_category_to_chosen(
        record_id=callback_data.record_id,
        category_id=callback_data.category_id,
    )
    await delete_lots_open_menu(
        record_id=callback_data.record_id,
        msg=call.message,
        tg_ui=tg_ui,
        delete_lots_state_storage=delete_lots_state_storage,
        data=data,
        callback_data=callback_data,
        edit=True,
    )
    await call.answer()


@router.callback_query(RemoveCategoryCD.filter())
async def remove_offer_from_state(
    call: CallbackQuery,
    callback_data: RemoveCategoryCD,
    data: dict[str, Any],
    delete_lots_state_storage: StateStorage,
    tg_ui: UIRegistry,
) -> None:
    delete_lots_state_storage.remove_category_from_chosen(
        record_id=callback_data.record_id,
        category_id=callback_data.category_id,
    )
    await delete_lots_open_menu(
        record_id=callback_data.record_id,
        msg=call.message,
        tg_ui=tg_ui,
        delete_lots_state_storage=delete_lots_state_storage,
        data=data,
        callback_data=callback_data,
        edit=True,
    )
    await call.answer()


@router.callback_query(ChooseAllCategoriesCD.filter())
async def choose_all_categories(
    call: CallbackQuery,
    callback_data: ChooseAllCategoriesCD,
    data: dict[str, Any],
    delete_lots_state_storage: StateStorage,
    tg_ui: UIRegistry,
) -> None:
    record = delete_lots_state_storage.get_record(callback_data.record_id)
    for category_id in record.categories.keys():
        delete_lots_state_storage.add_category_to_chosen(
            record_id=callback_data.record_id,
            category_id=category_id,
        )

    await delete_lots_open_menu(
        record_id=callback_data.record_id,
        msg=call.message,
        tg_ui=tg_ui,
        delete_lots_state_storage=delete_lots_state_storage,
        data=data,
        callback_data=callback_data,
        edit=True,
    )
    await call.answer()


@router.callback_query(DeleteLotsCD.filter())
async def delete_lots(
    call: CallbackQuery,
    callback_data: DeleteLotsCD,
    data: dict[str, Any],
    delete_lots_state_storage: StateStorage,
    tg_ui: UIRegistry,
) -> None:
    record = delete_lots_state_storage.get_record(callback_data.record_id)
    if not record.chosen_categories:
        await call.answer('❌ Ты не выбрал ни одной категории', show_alert=True)
        return

    menu_ctx = MenuContext(
        menu_id=MenuIds.confirm_delete,
        data={
            'record_id': callback_data.record_id,
        },
        trigger=call.message,
        callback_override=callback_data,
    )
    await (await tg_ui.build_menu(menu_ctx, data)).apply_to(call.message)
    await call.answer()


@router.callback_query(ConfirmDeleteLotsCD.filter())
async def confirm_delete_lots(
    call: CallbackQuery,
    callback_data: ConfirmDeleteLotsCD,
    delete_lots_state_storage: StateStorage,
    hub: FunPayHub,
    plugin_properties: DeleteLotsProperties,
) -> None:
    status_msg = await call.message.edit_text(
        '<tg-emoji emoji-id="5454074580010295588">⏳</tg-emoji>',
    )

    record = delete_lots_state_storage.get_record(callback_data.record_id)
    success_count = 0
    error_count = 0

    for category_id in record.chosen_categories:
        offers = await hub.funpay.bot.get_my_offers_page(
            subcategory_id=category_id,
        )

        for offer in offers.offers.values():
            if not plugin_properties.delete_active_lots.value and not offer.disabled:
                continue

            if not plugin_properties.delete_not_active_lots.value and offer.disabled:
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
                    await call.message.reply(
                        f'❌ <b>Ошибка при удалении лота {html.link(value=str(offer.id), link=f"https://funpay.com/lots/offer?id={offer.id}")}:</b> <code>{str(e)}</code>',
                    )

        await asyncio.sleep(1.5)

    delete_lots_state_storage.delete_record(callback_data.record_id)
    if error_count == 0:
        await status_msg.edit_text('<tg-emoji emoji-id="5472060472821818559">🌹</tg-emoji>')
    else:
        await status_msg.edit_text(
            f'🤩 <b>Готово!</b>\n\n'
            f'• Удалено лотов: <code>{success_count} шт.</code>\n'
            f'• Ошибок при удалении: <code>{error_count} шт.</code>',
        )
