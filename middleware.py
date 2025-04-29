import logging, re
from typing import Callable, Dict, Any, Awaitable, Set
from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.enums import ChatType

logger = logging.getLogger(__name__)


class ProfanityMiddleware(BaseMiddleware):
    def __init__(self, banned_words: Set[str]):
        self.banned_words = banned_words
        super().__init__()
        logger.info(f"Initialized ProfanityMiddleware with {len(banned_words)} banned words")

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        try:
            message = event.message or event.edited_message
            if not message:
                return await handler(event, data)

            if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
                return await handler(event, data)

            text = message.text or message.caption
            if not text:
                return await handler(event, data)

            found_banned_words = self._find_banned_words(text)
            if not found_banned_words:
                return await handler(event, data)

            try:
                await message.delete()
                logger.info(f"Deleted message with banned words in chat {message.chat.id}")
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")
                return await handler(event, data)

            # Сохраняем информацию о reply_to_message
            reply_to_message_id = None
            if message.reply_to_message:
                reply_to_message_id = message.reply_to_message.message_id

            filtered_text = self._replace_banned_words(text)
            user_mention = message.from_user.mention_html() if message.from_user else "Аноним"

            # Отправляем сообщение с сохранением reply_to_message
            await message.answer(
                f"{user_mention} отправил (цензура):\n{filtered_text}",
                parse_mode="HTML",
                reply_to_message_id=reply_to_message_id
            )
            logger.info(f"Replaced banned message in chat {message.chat.id}")

            return None

        except Exception as e:
            logger.exception(f"Error in ProfanityMiddleware: {e}")
            return await handler(event, data)

    def _find_banned_words(self, text: str) -> Set[str]:
        words = re.findall(r'\b\w+\b', text.lower())
        found_words = {word for word in words if word in self.banned_words}

        # Добавляем проверку на вульгарные приставки
        for word in words:
            if self._contains_vulgar_prefix(word):
                found_words.add(word)

        return found_words

    def _replace_banned_words(self, text: str) -> str:
        words = text.split()
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.banned_words or self._contains_vulgar_prefix(clean_word):
                words[i] = '*' * len(word)
        return ' '.join(words)

    def _contains_vulgar_prefix(self, word: str) -> bool:
        # Приставки для проверки
        prefixes = [
            "хуе", "хуё", "хуй", "хую", "хуя",
            "пизда", "пиздо"
        ]

        return any(word.startswith(prefix) for prefix in prefixes)