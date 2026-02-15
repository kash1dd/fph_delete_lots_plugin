from __future__ import annotations

from funpayhub.lib.properties import Properties, ToggleParameter


class DeleteLotsProperties(Properties):
    def __init__(self) -> None:
        super().__init__(
            id='delete_lots',
            name='Delete Lots',
            description="Настройки Delete Lots Plugin'а",
            file='config/delete_lots.toml',
        )
        self.delete_active_lots = self.attach_node(
            ToggleParameter(
                id='delete_active_lots',
                name='Удалять активные лоты',
                description='Если включено, плагин будет удалять активные лоты.'
                ' Если выключено, плагин будет удалять только неактивные лоты в'
                ' категории.',
                default_value=False,
            ),
        )
        self.delete_not_active_lots = self.attach_node(
            ToggleParameter(
                id='delete_not_active_lots',
                name='Удалять неактивные лоты',
                description='Если включено, плагин будет удалять неактивные лоты в категории.',
                default_value=True,
            ),
        )
        self.show_delete_lots_button_in_menu = self.attach_node(
            ToggleParameter(
                id='show_delete_lots_button_in_menu',
                name='Показывать кнопку удаления лотов в меню',
                description='Если включено, в главном меню будет отображаться кнопка для '
                'удаления лотов.',
                default_value=True,
            ),
        )
