import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, admin
import keyboard as kb
import functions as func
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Throttled

storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
connection = sqlite3.connect('data.db') # подключение к бд
q = connection.cursor()

class st(StatesGroup):
	item = State()
	item2 = State()
	item3 = State()
	item4 = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    func.join(chat_id=message.chat.id)
    q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
    user_name = message.from_user.username if message.from_user.username else "неизвестно"
    result = q.fetchone()
    if result[0] == 0:
        if message.chat.id in admin:
            await message.answer(f"🤝 Добро пожаловать, @{user_name}!", reply_markup=kb.menu)
        else:
            # Инлайн-кнопки "О нас", "Правила" и "Сайт""Сайт"
            inline_buttons = [
                types.InlineKeyboardButton("О нас", callback_data="about"),
                #types.InlineKeyboardButton("Правила", callback_data="rules"),
                types.InlineKeyboardButton("Сайт", url="https://tsarsmm.com/")
            ]
            inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
            inline_keyboard.add(*inline_buttons)
            
            # Сообщение с кнопками
            await message.answer(
                f"👋 Приветствую тебя,\n@{user_name}!\n\n✍️ Напиши мне свой вопрос/предложение/просьбу и я отправлю его администрации.\n\n❗️ За спам/флуд - вы можете получить как временный, так и вечный ЧС!\n\n🚀 ПОЕХАЛИ!",
                reply_markup=inline_keyboard
            )
    else:
        await message.answer('❌ Вы были заблокированны!')

@dp.message_handler(content_types=['text'], text='👑 Админ-панель')
async def handfler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			await message.answer('🤝 Добро пожаловать в админ-панель!', reply_markup=kb.adm)

@dp.message_handler(content_types=['text'], text='⏪ Назад')
async def handledr(message: types.Message, state: FSMContext):
	await message.answer('Добро пожаловать!', reply_markup=kb.menu)

@dp.message_handler(content_types=['text'], text='👿 ЧС')
async def handlaer(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			q.execute(f"SELECT * FROM users WHERE block == 1")
			result = q.fetchall()
			sl = []
			for index in result:
				i = index[0]
				sl.append(i)

			ids = '\n'.join(map(str, sl))
			await message.answer(f'‼️ ID пользователей находящихся в ЧС:\n{ids}')

@dp.message_handler(content_types=['text'], text='✅ Добавить в ЧС')
async def hanadler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			await message.answer('🆔 Введите id пользователя, которого нужно заблокировать.\n\n⚠️ Для отмены нажмите кнопку ниже', reply_markup=kb.back)
			await st.item3.set()

@dp.message_handler(content_types=['text'], text='❎ Убрать из ЧС')
async def hfandler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			await message.answer('🆔 Введите id пользователя, которого нужно разблокировать.\n\n⚠️ Для отмены нажмите кнопку ниже', reply_markup=kb.back)
			await st.item4.set()

@dp.message_handler(content_types=['text'], text='💬 Рассылка')
async def hangdler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			await message.answer('📩 Введите текст для рассылки.\n\n⚠️ Для отмены нажмите на кнопку ниже', reply_markup=kb.back)
			await st.item.set()


@dp.message_handler(content_types=['text'])
@dp.throttled(func.antiflood, rate=60) # 120 - секунды после каждого сообщения пользователя, анти-флуд система.
async def h(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			pass
		else:
			await message.answer('✅ Сообщение успешно отправленно!')
			for admin_id in admin:
				await bot.send_message(admin_id, f"<b>⭐️ Получен новый вопрос!</b>\n<b>От:</b> {message.from_user.mention}\nID: {message.chat.id}\n<b>Сообщение:</b> {message.text}", reply_markup=kb.fun(message.chat.id), parse_mode='HTML')
	else:
		await message.answer('❌ Вы заблокированны в боте.')

@dp.callback_query_handler(lambda call: call.data in ['about'], state=None)
async def inline_button_handler(call: types.CallbackQuery):
    if call.data == 'about':
        await call.message.edit_text(f"Команда разработчиков TSARSMM приветствует Вас!\n\n"
									f"⭐ Вас ждет\n\n"
									f"💯 Большой выбор!\n\n"
									f"— Более 800 услуг в каталоге!\n\n"
									f"🌍 Полная автоматизация!\n\n"
									f"— Все происходит в реальном времени!\n\n"
									f"🔔 Отзывчивая поддержка!\n\n"
									f"— Наши агенты всегда помогут вам!\n\n"
									f"🎁 Что вы можете получить с помощью нашем панели?\n\n"
									f"1. 👆 Продвижение!\n\n"
										f"💯 Становитесь популярными с помощью нашей панели!\n\n"
									f"2. 💰 Заработок!\n\n"
										f"🔥 Вы можете продавать лайки и подписчиков дальнейшим клиентам!\n\n"
									f"✅ Преимущества\n\n"
										f"1️⃣   Высокое качество - мы постоянно следим за качеством наших услуг;\n"
										f"2️⃣   Удобная панель - наша панель использует все современные технологии;\n"
										f"3️⃣   Лучшие цены - покупайте услуги  с первых рук.\n\n"
									f"⭐️ НАШ САЙТ - https://tsarsmm.com/")

@dp.callback_query_handler(lambda call: True) # Inline часть
async def cal(call, state: FSMContext):
	if 'ans' in call.data:
		a = call.data.index('-ans')
		ids = call.data[:a]
		await call.message.answer('✍️ Введите ответ:', reply_markup=kb.back)
		await st.item2.set() # администратор отвечает пользователю
		await state.update_data(uid=ids)
	elif 'ignor' in call.data:
		await call.answer('🚮 Удалено')
		await bot.delete_message(call.message.chat.id, call.message.message_id)
		await state.finish()

@dp.message_handler(state=st.item2)
async def proc(message: types.Message, state: FSMContext):
	if message.text == '⏪ Отмена':
		await message.answer('Отмена! Возвращаю назад.', reply_markup=kb.menu)
		await state.finish()
	else:
		await message.answer('✅ Сообщение отправлено.', reply_markup=kb.menu)
		data = await state.get_data()
		id = data.get("uid")
		await state.finish()
		await bot.send_message(id, '📣 Вам поступил ответ от администратора:\n\nТекст: {}'.format(message.text))

@dp.message_handler(state=st.item)
async def process_name(message: types.Message, state: FSMContext):
	q.execute(f'SELECT user_id FROM users')
	row = q.fetchall()
	connection.commit()
	text = message.text
	if message.text == '⏪ Отмена':
		await message.answer('⏪ Отмена! Возвращаю назад.', reply_markup=kb.adm)
		await state.finish()
	else:
		info = row
		await message.answer('📤 Рассылка начата!', reply_markup=kb.adm)
		for i in range(len(info)):
			try:
				await bot.send_message(info[i][0], str(text))
			except:
				pass
		await message.answer('✅ Рассылка завершена!', reply_markup=kb.adm)
		await state.finish()


@dp.message_handler(state=st.item3)
async def proce(message: types.Message, state: FSMContext):
	if message.text == '⏪ Отмена':
		await message.answer('⏪ Отмена! Возвращаю назад.', reply_markup=kb.adm)
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await message.answer('🤷‍♂️ Такой пользователь не найден в базе данных.', reply_markup=kb.adm)
				await state.finish()
			else:
				a = result[0]
				id = a[0]
				if id == 0:
					q.execute(f"UPDATE users SET block = 1 WHERE user_id = {message.text}")
					connection.commit()
					await message.answer('✅ Пользователь успешно заблокирован.', reply_markup=kb.adm)
					await state.finish()
					await bot.send_message(message.text, 'Вы были заблокированны администрацией!')
				else:
					await message.answer('🚫 Данный пользователь уже заблокирован!', reply_markup=kb.adm)
					await state.finish()
		else:
			await message.answer('⚠️ Не вводите буквы, нужен ID.\nВведите ID')

@dp.message_handler(state=st.item4)
async def proc(message: types.Message, state: FSMContext):
	if message.text == '⏪ Отмена':
		await message.answer('⏪ Отмена! Возвращаю назад.', reply_markup=kb.adm)
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await message.answer('🤷‍♂️ Такой пользователь не найден в базе данных.', reply_markup=kb.adm)
				await state.finish()
			else:
				a = result[0]
				id = a[0]
				if id == 1:
					q.execute(f"UPDATE users SET block = 0 WHERE user_id = {message.text}")
					connection.commit()
					await message.answer('✅ Пользователь успешно разбанен.', reply_markup=kb.adm)
					await state.finish()
					await bot.send_message(message.text, 'Вы были разблокированы администрацией.')
				else:
					await message.answer('⚠️ Данный пользователь не заблокирован.', reply_markup=kb.adm)
					await state.finish()
		else:
			await message.answer('⚠️ Не вводите буквы, нужен ID.\nВведи ID')

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)