from __future__ import annotations

from aiogram.types import InlineKeyboardButton

from funpayhub.lib.telegram.ui import Menu, Button, MenuContext, MenuModification

from funpayhub.app.main import FunPayHub

from .callbacks import DeleteLotsCD, ChooseCategoriesCD, ChooseAllCategoriesCD
from ...properties import DeleteLotsProperties


class AddDeleteLotsButtonModification(
    MenuModification,
    modification_id='fph:delete_lots_plugin:tg:add_delete_lots_button',
):
    async def filter(self, *_, hub: FunPayHub) -> bool:
        try:
            pr: DeleteLotsProperties = hub.properties.get_properties(  # type: ignore
                ['plugin_properties', 'delete_lots'],
            )
        except LookupError:
            return False

        return pr.show_delete_lots_button_in_menu.value

    async def modify(
        self,
        ctx: MenuContext,
        menu: Menu,
    ) -> Menu:
        menu.main_keyboard.add_callback_button(
            button_id='delete_lots_plugin',
            text='🗑️ Удалить лоты',
            callback_data=ChooseCategoriesCD(history=ctx.callback_data.as_history()).pack(),
        )
        return menu


class AddFooterKeyboardModification(
    MenuModification,
    modification_id='fph:delete_lots_plugin:tg:add_choose_all_categories_button',
):
    async def modify(
        self,
        ctx: MenuContext,
        menu: Menu,
    ) -> Menu:
        menu.footer_keyboard.add_row(
            Button(
                button_id='delete_lots_choose_all_categories',
                obj=InlineKeyboardButton(
                    text='✅ Выбрать все лоты',
                    callback_data=ChooseAllCategoriesCD(
                        history=ctx.callback_data.as_history(),
                        record_id=ctx.data['record_id'],
                        data={
                            **(ctx.callback_data.data if ctx.callback_data is not None else {}),
                            'menu_page': ctx.menu_page,
                        },
                    ).pack(),
                ),
            ),
            Button(
                button_id='delete_lots_del_lots',
                obj=InlineKeyboardButton(
                    text='🗑️ Удалить лоты',
                    callback_data=DeleteLotsCD(
                        history=ctx.callback_data.as_history(),
                        record_id=ctx.data['record_id'],
                        data={
                            **(ctx.callback_data.data if ctx.callback_data is not None else {}),
                            'menu_page': ctx.menu_page,
                        },
                    ).pack(),
                ),
            ),
        )
        return menu
