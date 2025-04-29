# ProfanityMiddleware | Автоматическая цензура в Telegram чатах
Этот middleware обеспечивает чистоту общения в чатах, автоматически фильтруя нецензурную лексику. Давайте разберём его функционал детально. <br>
[Разработка Телеграм ботов](https://else.com.ru "Разработка Телеграм ботов") -> https://else.com.ru/

## Назначение класса
`ProfanityMiddleware` выполняет важные функции модерации:

<ol> 
    <li>Обнаружение запрещённых слов в сообщениях</li> 
    <li>Автоматическое удаление сообщений с ненормативной лексикой</li> 
    <li>Публикация цензурированной версии сообщения</li> 
    <li>Сохранение контекста общения (ответы на сообщения)</li> 
</ol>
    
## Инициализация
```
  def __init__(self, banned_words: Set[str]):
    self.banned_words = banned_words
    super().__init__()
    logger.info(f"Initialized ProfanityMiddleware with {len(banned_words)} banned words")
```

+ `banned_words` - множество запрещённых слов</li>
+ Логирование количества запрещённых слов при инициализации</li>

## Основная логика работы
1. Проверка сообщения
```
  message = event.message or event.edited_message
  if not message:
    return await handler(event, data)

  if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
    return await handler(event, data)

  text = message.text or message.caption
  if not text:
    return await handler(event, data)
```
+ Работает с обычными и отредактированными сообщениями
+ Активируется только в групповых чатах
+ Проверяет текст сообщений и подписи к медиа

2. Поиск запрещённых слов
```
  found_banned_words = self._find_banned_words(text)
  if not found_banned_words:
    return await handler(event, data)
```
Использует продвинутый алгоритм поиска:

+ Точное совпадение слов
+ Проверка вульгарных приставок
+ Независимость от регистра

3. Обработка нарушений
```
  try:
    await message.delete()
    logger.info(f"Deleted message with banned words in chat {message.chat.id}")
  except Exception as e:
    logger.error(f"Failed to delete message: {e}")
    return await handler(event, data)

  # Сохраняем контекст ответа
  reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None

  # Подготавливаем цензурированную версию
  filtered_text = self._replace_banned_words(text)
  user_mention = message.from_user.mention_html() if message.from_user else "Аноним"

  # Отправляем уведомление
  await message.answer(
    f"{user_mention} отправил (цензура):\n{filtered_text}",
    parse_mode="HTML",
    reply_to_message_id=reply_to_message_id
  )
```
+ Удаляет оригинальное сообщение
+ Сохраняет цепочку обсуждения
+ Публикует очищенную версию
+ Использует HTML-разметку для упоминания пользователя

## Алгоритмы фильтрации
Поиск запрещённых слов
```
  def _find_banned_words(self, text: str) -> Set[str]:
    words = re.findall(r'\b\w+\b', text.lower())
    found_words = {word for word in words if word in self.banned_words}

    # Проверка вульгарных приставок
    for word in words:
        if self._contains_vulgar_prefix(word):
            found_words.add(word)

    return found_words
```
+ Разбивает текст на отдельные слова
+ Проверяет точные совпадения
+ Анализирует приставки слов

Замена нецензурных слов
```
  def _replace_banned_words(self, text: str) -> str:
    words = text.split()
    for i, word in enumerate(words):
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if clean_word in self.banned_words or self._contains_vulgar_prefix(clean_word):
            words[i] = '*' * len(word)
    return ' '.join(words)
```
+ Сохраняет оригинальную длину слов
+ Заменяет на символы *
+ Сохраняет пунктуацию

Детектор вульгарных приставок
```
  def _contains_vulgar_prefix(self, word: str) -> bool:
    prefixes = [
        "хуе", "хуё", "хуй", "хую", "хуя",
        "пизда", "пиздо"
    ]
    return any(word.startswith(prefix) for prefix in prefixes)
```
+ Проверяет начало слов
+ Обнаруживает замаскированную брань

## Практическое применение
Middleware особенно полезен для:

+ Публичных сообществ
+ Корпоративных чатов
+ Образовательных проектов
+ Чатов с детской аудиторией
+ Любых групп, где важна культура общения

## Кастомизация
Вы можете расширить функционал:

<ol>
    <li>Добавить собственные списки запрещённых слов</li>
    <li>Настроить белые списки пользователей</li>
    <li>Реализовать систему предупреждений</li>
    <li>Добавить анализ стикеров и медиа</li>
</ol>

```
  # Пример расширения словаря
  banned_words = {"мат", "брань", "оскорбление"}
  middleware = ProfanityMiddleware(banned_words)
```

## Заключение
ProfanityMiddleware обеспечивает автоматическую цензуру в Telegram-чатах, поддерживая чистоту общения без участия модераторов.
<br>
<blockquote>
<b>Хотите чистый и культурный чат без мата?</b>

Команда ELSE (https://else.com.ru/) разрабатывает комплексные системы модерации:<br>

✅ Интеллектуальные фильтры нецензурной лексики<br>
✅ Кастомизированные словари запрещённых слов<br>
✅ Системы предупреждений и банов<br>
✅ Решения для соответствия возрастным ограничениям<br>

Закажите модерацию чата на else.com.ru и поддерживайте культуру общения!<br>
[Создание Телеграм ботов](https://else.com.ru "Разработка Телеграм ботов") -> https://else.com.ru/
</blockquote>
    

    
