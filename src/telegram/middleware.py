from __future__ import annotations

from typing import Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from ..state_storage import RecordNotFoundError


class ExceptRecordNotFoundMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except RecordNotFoundError:
            if isinstance(event, CallbackQuery):
                await event.answer(
                    '📛 Запись не найдена :/\n\n'
                    'Открой меню удаления лотов заново, чтобы обновить данные',
                    show_alert=True,
                )
