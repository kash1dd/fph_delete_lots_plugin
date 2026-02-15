from __future__ import annotations

from funpayhub.lib.telegram.callback_data import CallbackData


class ChooseCategoriesCD(CallbackData, identifier='delete_lots_menu'): ...


class AddCategoryCD(ChooseCategoriesCD, identifier='delete_lots_add_category'):
    category_id: int
    record_id: int


class RemoveCategoryCD(
    AddCategoryCD,
    identifier='delete_lots_remove_category',
): ...


class ChooseAllCategoriesCD(ChooseCategoriesCD, identifier='delete_lots_choose_all_categories'):
    record_id: int


class DeleteLotsCD(CallbackData, identifier='delete_lots_delete_lots'):
    record_id: int


class ConfirmDeleteLotsCD(DeleteLotsCD, identifier='delete_lots_confirm_delete_lots'): ...
