from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from funpayhub.lib.translater import translater
from funpayhub.lib.telegram.ui import Menu, MenuBuilder, MenuContext
from funpayhub.lib.base_app.telegram.app.ui.callbacks import OpenMenu
from funpayhub.lib.base_app.telegram.app.ui.ui_finalizers import StripAndNavigationFinalizer

from funpayhub.app.telegram.ui.premade import confirmable_button

from .ids import MenuIds
from .callbacks import DeleteLotsCD


if TYPE_CHECKING:
    from funpaybotengine.storage import InMemoryStorage

    from funpayhub.app.main import FunPayHub as FPH


ru = translater.translate


class OffersListMenuContext(MenuContext):
    chosen_subcategories: list[int] = Field(default_factory=list)


class OffersListMenuBuilder(
    MenuBuilder,
    menu_id=MenuIds.delete_lots_list,
    context_type=OffersListMenuContext,
):
    async def build(self, ctx: OffersListMenuContext, hub: FPH) -> Menu:
        menu = Menu(
            header_text=ru('🗑️ <b><u>Удаление лотов</u></b>'),
            footer_text=ru('<i>Выбери категории, лоты которых ты хочешь удалить</i>'),
            finalizer=StripAndNavigationFinalizer(),
        )

        subcategories = await self.get_subcategories(hub)
        chosen_subcategories = [i for i in ctx.chosen_subcategories if i in subcategories]
        for id, name in subcategories.items():
            selected = id in chosen_subcategories
            if selected:
                new_chosen_subcategories = [i for i in chosen_subcategories if i != id]
            else:
                new_chosen_subcategories = chosen_subcategories + [id]

            menu.main_keyboard.add_callback_button(
                button_id=f'toggle_lots_category:{id}',
                text=f'{"✅ " if id in ctx.chosen_subcategories else ""}{name}',
                callback_data=OpenMenu.from_menu_context(
                    context=ctx,
                    context_data_update={'chosen_subcategories': new_chosen_subcategories},
                    ui_history=ctx.ui_history,
                ).pack(),
                style='success' if selected else None,
            )

        menu.footer_keyboard.add_callback_button(
            button_id='select_all_subcategories',
            text='✅ Выбрать все лоты',
            callback_data=OpenMenu.from_menu_context(
                context=ctx,
                context_data_update={'chosen_subcategories': list(subcategories.keys())},
                ui_history=ctx.ui_history,
            ).pack(),
        )

        menu.footer_keyboard.add_row(
            *confirmable_button(
                ctx,
                button_id='delete_lots',
                text='🗑️ Удалить лоты',
                callback_data=DeleteLotsCD(
                    ui_history=ctx.as_ui_history(),
                    chosen_subcategories=chosen_subcategories,
                ).pack(),
            ),
        )

        return menu

    async def get_subcategories(self, hub: FPH) -> dict[int, str]:
        offers = (await hub.funpay.profile()).offers or {}
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
