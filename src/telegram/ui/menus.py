from __future__ import annotations

from aiogram.types import InlineKeyboardButton

from funpayhub.lib.telegram.ui import Menu, Button, MenuBuilder, MenuContext, KeyboardBuilder
from funpayhub.lib.base_app.telegram.app.ui.ui_finalizers import StripAndNavigationFinalizer

from .ids import MenuIds
from .callbacks import AddCategoryCD, RemoveCategoryCD, ConfirmDeleteLotsCD


class OffersListMenuBuilder(
    MenuBuilder,
    menu_id=MenuIds.delete_lots_list,
    context_type=MenuContext,
):
    async def build(self, ctx: MenuContext) -> Menu:
        categories: dict[int, str] = ctx.data['categories']
        chosen_categories: list[int] = ctx.data['chosen_categories']

        kb = KeyboardBuilder()

        for category_id, category_name in categories.items():
            kwargs = {
                'record_id': ctx.data['record_id'],
                'history': ctx.callback_data.as_history() if ctx.callback_data is not None else [],
                'category_id': category_id,
                'data': {
                    **(ctx.callback_data.data if ctx.callback_data is not None else {}),
                    'menu_page': ctx.menu_page,
                },
            }
            emoji = '✅ ' if category_id in chosen_categories else ' '

            kb.add_callback_button(
                button_id=f'delete_lots_category_{category_id}',
                text=f'{emoji}{category_name}',
                callback_data=AddCategoryCD(**kwargs).pack()
                if category_id not in chosen_categories
                else RemoveCategoryCD(**kwargs).pack(),
                style='success' if category_id in chosen_categories else None,
            )

        return Menu(
            main_keyboard=kb,
            header_text='🗑️ <b><u>Удаление лотов</u></b>',
            footer_text='<i>Выбери категории, лоты которых ты хочешь удалить</i>',
            finalizer=StripAndNavigationFinalizer(back_button=ctx.data['show_back']),
        )


class ConfirmDeleteMenuBuilder(
    MenuBuilder,
    menu_id=MenuIds.confirm_delete,
    context_type=MenuContext,
):
    async def build(self, ctx: MenuContext) -> Menu:
        kb = KeyboardBuilder()

        kb.add_row(
            Button(
                button_id='delete_lots_confirm_delete',
                obj=InlineKeyboardButton(
                    text='✅ Да, удалить',
                    callback_data=ConfirmDeleteLotsCD(
                        history=ctx.callback_data.as_history()
                        if ctx.callback_data is not None
                        else [],
                        record_id=ctx.data['record_id'],
                        data={
                            **(ctx.callback_data.data if ctx.callback_data is not None else {}),
                            'menu_page': ctx.menu_page,
                        },
                    ).pack(),
                ),
            ),
            Button(
                button_id='back',
                obj=InlineKeyboardButton(
                    text='❌ Нет, отменить',
                    callback_data=ctx.callback_data.pack_history()
                    if ctx.callback_data is not None
                    else None,
                ),
            ),
        )

        return Menu(
            main_keyboard=kb,
            finalizer=StripAndNavigationFinalizer(),
            header_text='❗ <b><u>Подтверждение удаления</u></b>',
            footer_text='❓ <i>Ты уверен, что хочешь удалить лоты в выбранных категориях?</i>',
        )
