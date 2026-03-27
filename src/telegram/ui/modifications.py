from __future__ import annotations

from typing import TYPE_CHECKING

from funpayhub.lib.telegram.ui import Menu, MenuModification
from funpayhub.lib.base_app.telegram.app.ui.callbacks import OpenMenu

from . import MenuIds


if TYPE_CHECKING:
    from funpayhub.lib.telegram.ui import MenuContext

    from funpayhub.app.main import FunPayHub as FPH

    from ...properties import DeleteLotsProperties


class AddDeleteLotsButtonModification(
    MenuModification,
    modification_id='fph:delete_lots_plugin:tg:add_delete_lots_button',
):
    async def filter(self, *_, hub: FPH) -> bool:
        try:
            pr: DeleteLotsProperties = hub.properties.plugin_properties.get_properties(
                ['delete_lots'],
            )
        except LookupError:
            return False

        return pr.show_delete_lots_button_in_menu

    async def modify(self, ctx: MenuContext, menu: Menu) -> Menu:
        menu.main_keyboard.add_callback_button(
            button_id='delete_lots_plugin',
            text='🗑️ Удалить лоты',
            callback_data=OpenMenu(
                menu_id=MenuIds.delete_lots_list,
                ui_history=ctx.as_ui_history(),
            ).pack(),
        )
        return menu
