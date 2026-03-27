from __future__ import annotations

from aiogram import Router as TGRouter

from funpayhub.lib.telegram import Command
from funpayhub.lib.telegram.ui import MenuBuilder, MenuModification

from funpayhub.app.plugin import Plugin
from funpayhub.app.telegram.ui.ids import MenuIds

from .properties import DeleteLotsProperties
from .telegram.ui import (
    OffersListMenuBuilder,
    AddDeleteLotsButtonModification,
)
from .telegram.router import router as delete_lots_tg_router


class DeleteLotsPlugin(Plugin):
    async def properties(self) -> DeleteLotsProperties:
        return DeleteLotsProperties()

    async def telegram_routers(self) -> TGRouter | list[TGRouter]:
        return delete_lots_tg_router

    async def menus(self) -> type[MenuBuilder] | list[type[MenuBuilder]]:
        return OffersListMenuBuilder

    async def menu_modifications(
        self,
    ) -> dict[str, type[MenuModification] | list[type[MenuModification]]]:
        return {
            MenuIds.main_menu: AddDeleteLotsButtonModification,
        }

    async def commands(self) -> Command | list[Command] | None:
        return Command(
            command='del_lots',
            description='[Delete Lots] Удалить лоты',
            setup=True,
            source=self.manifest.plugin_id,
        )
