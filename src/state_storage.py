from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StateRecord:
    categories: dict[int, str]
    """All categories in format {category_id: category_name}"""

    chosen_categories: list[int]
    """Chosen categories"""

    show_back: bool
    """Whether to show back button in menu"""


class RecordNotFoundError(Exception): ...


class StateStorage:
    def __init__(self) -> None:
        self._storage: dict[int, StateRecord] = {}

    def _get_max_id(self) -> int:
        return max(self._storage.keys(), default=0)

    def add_record(
        self,
        categories: dict[int, str],
        chosen_categories: list[int],
        show_back: bool = True,
    ) -> int:
        new_id = self._get_max_id() + 1
        self._storage[new_id] = StateRecord(
            categories,
            chosen_categories,
            show_back,
        )
        return new_id

    def get_record(self, record_id: int) -> StateRecord | None:
        return self._storage.get(record_id)

    def add_category_to_chosen(self, record_id: int, category_id: int) -> None:
        if record_id in self._storage:
            record = self._storage[record_id]
            if category_id not in record.chosen_categories:
                new_chosen = record.chosen_categories + [category_id]
                self._storage[record_id] = StateRecord(
                    record.categories,
                    new_chosen,
                    record.show_back,
                )
        else:
            raise RecordNotFoundError

    def remove_category_from_chosen(self, record_id: int, category_id: int) -> None:
        if record_id in self._storage:
            record = self._storage[record_id]
            if category_id in record.chosen_categories:
                new_chosen = [cat for cat in record.chosen_categories if cat != category_id]
                self._storage[record_id] = StateRecord(
                    record.categories,
                    new_chosen,
                    record.show_back,
                )
        else:
            raise RecordNotFoundError

    def delete_record(self, record_id: int) -> None:
        if record_id in self._storage:
            del self._storage[record_id]
