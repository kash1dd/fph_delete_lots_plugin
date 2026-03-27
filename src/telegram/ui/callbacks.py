from __future__ import annotations

from funpayhub.lib.telegram.callback_data import CallbackData


class DeleteLotsCD(CallbackData, identifier='delete_lots_delete_lots'):
    chosen_subcategories: list[int]

