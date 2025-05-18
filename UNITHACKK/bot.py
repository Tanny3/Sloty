import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import Database
import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
class NotificationStates(StatesGroup):
    waiting_for_notification_text = State()


# Инициализация бота
TOKEN = "7751476184:AAH9wSjVNpuJXAEiNdA4yLR0_si8JQR-R4k"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация базы данных
db = Database('database.db')

# Логирование
logging.basicConfig(level=logging.INFO)

# Клавиатура с кнопкой "Старт"
def start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Старт")
    return builder.as_markup(resize_keyboard=True)

# Главное меню
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Участник", callback_data="participant")
    builder.button(text="🛠️ Организатор", callback_data="organizer")
    builder.button(text="📞 Контакты", callback_data="contacts")
    builder.button(text="ℹ️ О нас", callback_data="about")
    builder.adjust(2)
    return builder.as_markup()

# Меню участника
def participant_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Запись на мероприятие", callback_data="event_registration")
    builder.button(text="📅 Мое расписание", callback_data="my_schedule")
    builder.button(text="📍 Карта мероприятия", callback_data="event_map")
    builder.button(text="📊 Опросы и голосования", callback_data="polls")
    builder.button(text="💬 Чат участников", callback_data="participants_chat")
    builder.button(text="❓ Задать вопрос", callback_data="ask_question")
    builder.button(text="🔍 FAQ", callback_data="faq")
    builder.button(text="🔔 Уведомления", callback_data="notifications")
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(2)
    return builder.as_markup()

# Меню записи на мероприятия
def events_menu_keyboard():
    events = db.get_all_events()
    builder = InlineKeyboardBuilder()
    for event in events:
        builder.button(text=event[1], callback_data=f"event_{event[0]}")  # event_<ID>
    builder.button(text="Назад", callback_data="back_to_participant")
    builder.adjust(1)
    return builder.as_markup()

# Меню организатора
def organizer_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛠️ Настройка расписания", callback_data="schedule_settings")
    builder.button(text="👀✅ Контроль посещаемости", callback_data="attendance_control")
    builder.button(text="🔔 Уведомления", callback_data="org_notifications")
    builder.button(text="💬 Обратная связь", callback_data="feedback")
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(2)
    return builder.as_markup()

# Меню настроек расписания
def schedule_settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить активность", callback_data="add_activity")
    builder.button(text="➖ Удалить активность", callback_data="remove_activity")
    builder.button(text="🔙 Назад", callback_data="back_to_organizer")
    builder.adjust(1)
    return builder.as_markup()

class NewActivity(StatesGroup):
    waiting_for_data = State()

# Обработчик кнопки "Добавить активность"
@dp.callback_query(lambda c: c.data == "add_activity")
async def add_activity_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите данные активности в формате: Название|Дата|Время\n"
        "Пример: Концерт|2024-05-25|18:00"
    )
    await state.set_state(NewActivity.waiting_for_data)
    await callback.answer()

# Обработчик ввода данных активности
@dp.message(NewActivity.waiting_for_data)
async def process_activity_data(message: Message, state: FSMContext):
    try:
        name, date, time = message.text.split("|")
        db.add_event(name.strip(), date.strip(), time.strip())
        await message.answer(f"✅ Активность «{name}» добавлена!")
    except ValueError:
        await message.answer("❌ Ошибка формата. Используйте: Название|Дата|Время")
    await state.clear()


# Меню контроля посещаемости
def attendance_control_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 Статистика", callback_data="statistics")
    builder.button(text="🔄 Обновить", callback_data="refresh_stats")
    builder.button(text="👥 Список участников", callback_data="participants_list")
    builder.button(text="🔙 Назад", callback_data="back_to_organizer")
    builder.adjust(2)
    return builder.as_markup()

# Меню уведомлений организатора
def org_notifications_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Отправить всем", callback_data="send_to_all")
    builder.button(text="👥 Отправить группе", callback_data="send_to_group")
    builder.button(text="🔙 Назад", callback_data="back_to_organizer")
    builder.adjust(1)
    return builder.as_markup()

# Меню списка мероприятий для организатора
def events_list_keyboard():
    events = db.get_all_events()
    builder = InlineKeyboardBuilder()
    for event in events:
        builder.button(text=event[1], callback_data=f"org_event_{event[0]}")
    builder.button(text="Назад", callback_data="back_to_attendance")
    builder.adjust(1)
    return builder.as_markup()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    db.add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "👋 Добро пожаловать! Нажмите кнопку «Старт», чтобы начать работу с ботом.",
        reply_markup=start_keyboard()  # Отправляем клавиатуру с кнопкой "Старт"
    )
# Обработчик кнопки Старт
@dp.message(lambda message: message.text == "Старт")
async def start_message(message: Message):
    welcome_text = """Привет! 👋 Я — твой надежный помощник на мероприятии!
✨ Что я умею:
📅 Держу тебя в курсе расписания и важных изменений
🎟 Записываю на мастер-классы и уведомляю о свободных местах
💬 Отвечаю на вопросы и помогаю связаться с организаторами
🗳 Провожу опросы и собираю мнения в реальном времени
🔒 Гарантирую безопасный доступ только для участников
Готов помочь сделать твой опыт на мероприятии удобным и ярким! 🚀"""
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())


# Обработчик главного меню (обновлённая версия)
@dp.callback_query(lambda c: c.data in ["participant", "organizer", "contacts", "about"])
async def main_menu_handler(callback: CallbackQuery):
    if callback.data == "participant":
        await callback.message.edit_text(
            "Привет! Ты успешно зарегистрирован как участник. Я помогу тебе следить за обновлениями "
            "и не пропустить ничего важного 🚀",
            reply_markup=participant_menu_keyboard()
        )
    elif callback.data == "organizer":
        if db.is_organizer(callback.from_user.id):
            await callback.message.edit_text(
                "Привет! Ты вошёл как организатор (лектор). Готовы начинать планирование? "
                "Я помогу тебе управлять участниками и деталями мероприятия 📋\n\n"
                "Если ты зашел как лектор, нажми на кнопку ниже",
                reply_markup=organizer_menu_keyboard()
            )
        else:
            await callback.answer("Доступ запрещён. Вы не организатор.", show_alert=True)
    elif callback.data == "about":
        await callback.message.edit_text(
            """<b>Naumen</b> — российский вендор корпоративного ПО и облачных сервисов, технологический партнер в цифровой трансформации для компаний и органов власти, признанный лидер в технологиях:

• Контактных центров
• Клиентского сервиса
• Виртуальных ассистентов (ботов)
• Платформ бизнес-процессов (BPM, low-code)
• Управления знаниями (KMS)
• Управления рабочей силой (WFM)
• Управления ИТ-сервисами (ITSM)

Компания строит внутренние центры компетенций, предоставляет готовые и гибкие решения, а также высокоэффективные low-code инструменты для создания корпоративных приложений силами внутренних команд.

🌍 Сегодня решения Naumen доступны в пяти странах, где находятся офисы и эксклюзивные партнеры компании. Более <b>200 млн пользователей</b> из России, Европы и Азии ежедневно взаимодействуют с решениями Naumen.""",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    elif callback.data == "contacts":
        await callback.message.edit_text(
            "Контакты организаторов:\nТелефон: +7 (XXX) XXX-XX-XX\nEmail: example@example.com", 
            reply_markup=main_menu_keyboard()
        )
    await callback.answer()

# Обработчик кнопки FAQ



# Обработчик кнопки назад

@dp.callback_query(lambda c: c.data == "back_to_participant")
async def back_to_participant_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "Меню участника:",
        reply_markup=participant_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_participant")
async def back_to_participant_handler(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "Меню участника:",
            reply_markup=participant_menu_keyboard()
        )
    except Exception as e:
        await callback.answer("Произошла ошибка, попробуйте еще раз")
        logging.error(f"Back error: {e}")
    finally:
        await callback.answer()

def events_menu_keyboard():
    events = db.get_all_events()
    builder = InlineKeyboardBuilder()
    for event in events:
        builder.button(text=event[1], callback_data=f"event_{event[0]}")
    builder.button(text="Назад", callback_data="back_to_participant")  # Важно!
    builder.adjust(1)
    return builder.as_markup()

# Обработчик меню участника
@dp.callback_query(lambda c: c.data in ["event_registration", "my_schedule", "event_map", "polls", 
                                       "participants_chat", "ask_question", "faq", "notifications", "back_to_main"])
async def participant_menu_handler(callback: CallbackQuery):
    if callback.data == "event_registration":
        await callback.message.edit_text("Выберите мероприятие:", reply_markup=events_menu_keyboard())
    elif callback.data == "my_schedule":
        events = db.get_user_events(callback.from_user.id)
        if events:
            text = "Ваше расписание:\n"
            builder = InlineKeyboardBuilder()
            for event in events:
                text += f"- {event[1]} ({event[2]} в {event[3]})\n"
                builder.button(text=f"❌ Отменить {event[1]}", callback_data=f"unregister_{event[0]}")
            builder.button(text="🔙 Назад", callback_data="back_to_participant")
            builder.adjust(1)
            await callback.message.edit_text(text, reply_markup=builder.as_markup())
        else:
            text = "У вас нет запланированных мероприятий."
            await callback.message.edit_text(text, reply_markup=participant_menu_keyboard())
    elif callback.data == "event_map":
        await callback.message.answer_photo(photo=types.FSInputFile("map.jpg"), caption="Карта мероприятия")
        await callback.answer()
    elif callback.data == "participants_chat":
        await callback.message.edit_text("Чат участников: https://t.me/+9QfxMYoYHBkzNTUy", 
                                        reply_markup=participant_menu_keyboard())
    elif callback.data == "ask_question":
        await callback.message.edit_text(
            "Вы можете задать вопрос в нашем чате: https://t.me/+9QfxMYoYHBkzNTUy\n\n"
            "Или напишите ваш вопрос здесь, и мы ответим вам в личных сообщениях.",
            reply_markup=participant_menu_keyboard()
        )
        # Здесь нужно добавить состояние для ожидания вопроса
    elif callback.data == "notifications":
        notifications = db.get_user_notifications(callback.from_user.id)
        if notifications:
            text = "Ваши уведомления:\n"
            for note in notifications:
                text += f"- {note[1]}\n"
        else:
            text = "У вас нет новых уведомлений."
        await callback.message.edit_text(text, reply_markup=participant_menu_keyboard())
    elif callback.data == "back_to_main":
        await callback.message.edit_text("Главное меню:", reply_markup=main_menu_keyboard())
    await callback.answer()

# Обработчик записи на мероприятие
# Обработчик выбора мероприятия (заменяет старый)
@dp.callback_query(lambda c: c.data.startswith("event_"))
async def select_event(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split("_")[1])
    event = db.get_event(event_id)  # Получаем данные мероприятия
    
    if not event:
        await callback.answer("Мероприятие не найдено!", show_alert=True)
        return

    # Сохраняем event_id в состоянии
    await state.update_data(event_id=event_id)
    
    # Формируем сообщение с деталями
    event_details = (
        f"🏷 Название: {event[1]}\n"
        f"📅 Дата: {event[2]}\n"
        f"⏰ Время: {event[3]}\n"
        f"🔢 Свободных мест: {10 - db.get_event_participants_count(event_id)}"  # Пример: 10 - текущие записи
    )

    # Клавиатура с подтверждением
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить запись", callback_data=f"confirm_{event_id}")
    builder.button(text="❌ Отменить", callback_data="cancel_registration")
    builder.adjust(1)

    await callback.message.edit_text(
        f"Вы выбрали:\n\n{event_details}\n\nПодтвердите запись:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Отмена регистрации


@dp.callback_query(lambda c: c.data.startswith("unregister_"))
async def unregister_from_event(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    if db.unregister_user_from_event(user_id, event_id):
        await callback.message.edit_text(
            "✅ Вы отменили запись на мероприятие.",
            reply_markup=participant_menu_keyboard()
        )
    else:
        await callback.answer("Не удалось отменить запись. Возможно, вы не были записаны.", show_alert=True)
    await callback.answer()

# Старт




# Обработчик подтверждения записи
@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    if db.is_user_registered(user_id, event_id):
        await callback.answer("Вы уже записаны на это мероприятие!", show_alert=True)
        return

    db.register_user_to_event(user_id, event_id)
    count = db.get_event_participants_count(event_id)
    
    await callback.message.edit_text(
        f"✅ Вы успешно записаны!\nТекущее количество участников: {count}",
        reply_markup=events_menu_keyboard()  # Возврат к списку мероприятий
    )
    await state.clear()
    await callback.answer()

# Обработчик отмены
@dp.callback_query(lambda c: c.data == "cancel_registration")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Запись отменена.",
        reply_markup=events_menu_keyboard()  # Возврат к списку мероприятий
    )
    await state.clear()
    await callback.answer()

# Обработчик меню организатора
@dp.callback_query(lambda c: c.data in ["schedule_settings", "attendance_control", "org_notifications", 
                                       "feedback", "back_to_organizer"])
async def organizer_menu_handler(callback: CallbackQuery):
    if callback.data == "schedule_settings":
        await callback.message.edit_text("Настройка расписания:", reply_markup=schedule_settings_keyboard())
    elif callback.data == "attendance_control":
        await callback.message.edit_text("Контроль посещаемости:", reply_markup=attendance_control_keyboard())
    elif callback.data == "org_notifications":
        await callback.message.edit_text("Управление уведомлениями:", reply_markup=org_notifications_keyboard())
    elif callback.data == "feedback":
        await callback.message.edit_text("Обратная связь от участников будет приходить сюда.")
    elif callback.data == "back_to_organizer":
        await callback.message.edit_text("Меню организатора:", reply_markup=organizer_menu_keyboard())
    await callback.answer()

# Обработчик настроек расписания
@dp.callback_query(lambda c: c.data in ["add_activity", "remove_activity", "back_to_organizer"])
async def schedule_settings_handler(callback: CallbackQuery):
    if callback.data == "add_activity":
        await callback.message.edit_text("Введите название новой активности, дату и время в формате:\nНазвание|Дата|Время")
        # Здесь нужно добавить состояние для ожидания ввода новой активности
    elif callback.data == "remove_activity":
        events = db.get_all_events()
        if events:
            await callback.message.edit_text("Выберите активность для удаления:", reply_markup=events_list_keyboard())
        else:
            await callback.answer("Нет активностей для удаления.", show_alert=True)
    elif callback.data == "back_to_organizer":
        await callback.message.edit_text("Меню организатора:", reply_markup=organizer_menu_keyboard())
    await callback.answer()

# Обработчик контроля посещаемости
@dp.callback_query(lambda c: c.data in ["statistics", "refresh_stats", "participants_list", "back_to_attendance"])
async def attendance_control_handler(callback: CallbackQuery):
    if callback.data in ["statistics", "refresh_stats"]:
        stats = db.get_events_stats()
        text = "Статистика посещаемости:\n"
        for stat in stats:
            text += f"- {stat[0]}: {stat[1]} участников\n"
        await callback.message.edit_text(text, reply_markup=attendance_control_keyboard())
    elif callback.data == "participants_list":
        await callback.message.edit_text("Выберите мероприятие для просмотра списка участников:", 
                                       reply_markup=events_list_keyboard())
    elif callback.data == "back_to_attendance":
        await callback.message.edit_text("Контроль посещаемости:", reply_markup=attendance_control_keyboard())
    await callback.answer()

# Обработчик списка участников мероприятия
@dp.callback_query(lambda c: c.data.startswith("org_event_"))
async def event_participants_handler(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[2])
    participants = db.get_event_participants(event_id)
    if participants:
        text = "Участники мероприятия:\n"
        for user in participants:
            text += f"- @{user[1]}\n"
    else:
        text = "На это мероприятие пока никто не записался."
    await callback.message.edit_text(text, reply_markup=events_list_keyboard())
    await callback.answer()

# Обработчик уведомлений организатора
@dp.callback_query(lambda c: c.data in ["send_to_all", "send_to_group", "back_to_organizer"])
async def org_notifications_handler(callback: CallbackQuery):
    if callback.data == "send_to_all":
        await callback.message.edit_text("Введите текст уведомления для всех участников:")
        # Здесь нужно добавить состояние для ожидания ввода уведомления
    elif callback.data == "send_to_group":
        await callback.message.edit_text("Введите текст уведомления для группы:")
        # Здесь нужно добавить состояние для ожидания ввода уведомления
    elif callback.data == "back_to_organizer":
        await callback.message.edit_text("Меню организатора:", reply_markup=organizer_menu_keyboard())
    await callback.answer()




# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())