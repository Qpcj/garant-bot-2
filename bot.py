# bot.py (полная версия - сделки только в оперативке)
import logging
import os
import re
import time
from uuid import uuid4

from telegram import (
    Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup,
    InlineQueryResultArticle, InputTextMessageContent
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    InlineQueryHandler, ContextTypes, filters
)

from config import BOT_TOKEN, TON_RATE, USDT_RATE, FEE_PERCENT
from database import Database
from messages import MESSAGES
from keyboards import (
    get_welcome_inline_keyboard,
    get_deal_type_keyboard,
    get_currency_keyboard,
    get_fiat_currency_keyboard,
    get_warning_keyboard,
    get_buyer_payment_keyboard,
    get_seller_gift_sent_keyboard,
    get_language_keyboard,
    get_payment_retry_keyboard,
    get_requisites_main_keyboard,
    get_requisites_add_type_keyboard,
    get_requisites_view_type_keyboard,
    get_card_currency_keyboard,
    get_back_to_requisites_keyboard
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных только для пользователей и админов
db = Database("guarantee_bot.db")

# =====================
# Временное хранение в оперативной памяти
# =====================
class UserState:
    def __init__(self):
        self.states = {}
        self.active_deals = {}  # Активные сделки в оперативке
        self.deal_counter = 0

    def set_state(self, user_id, state, data=None):
        if data is None:
            data = {}
        self.states[user_id] = {'state': state, 'data': data}

    def get_state(self, user_id):
        return self.states.get(user_id, {'state': None, 'data': {}})

    def clear_state(self, user_id):
        if user_id in self.states:
            del self.states[user_id]

    def create_deal(self, deal_data):
        """Создает сделку в оперативной памяти"""
        self.deal_counter += 1
        deal_id = f"deal_{int(time.time())}_{self.deal_counter}"
        deal_data['deal_id'] = deal_id
        deal_data['status'] = 'waiting_buyer'
        self.active_deals[deal_id] = deal_data
        logger.info(f"Created deal {deal_id} in memory")
        return deal_id

    def get_deal(self, deal_id):
        """Получает сделку из оперативной памяти"""
        return self.active_deals.get(deal_id)

    def update_deal(self, deal_id, updates):
        """Обновляет сделку в оперативной памяти"""
        if deal_id in self.active_deals:
            self.active_deals[deal_id].update(updates)
            return True
        return False

    def delete_deal(self, deal_id):
        """Удаляет сделку из оперативной памяти"""
        if deal_id in self.active_deals:
            del self.active_deals[deal_id]
            return True
        return False

    def get_user_deals(self, user_id):
        """Получает все сделки пользователя из оперативной памяти"""
        user_deals = []
        for deal_id, deal in self.active_deals.items():
            if deal.get('seller_id') == user_id or deal.get('buyer_id') == user_id:
                user_deals.append({
                    'deal_id': deal_id,
                    'amount': deal.get('amount', 0),
                    'fiat_currency': deal.get('fiat_currency', 'RUB'),
                    'status': deal.get('status', 'unknown'),
                    'seller_id': deal.get('seller_id'),
                    'buyer_id': deal.get('buyer_id')
                })
        return user_deals

    def get_waiting_payment_deals(self):
        """Получает все сделки, ожидающие оплаты"""
        waiting_deals = []
        for deal_id, deal in self.active_deals.items():
            if deal.get('status') == 'waiting_payment':
                waiting_deals.append(deal)
        return waiting_deals

# Глобальная переменная для хранения состояния
user_states = UserState()

# =====================
# Helpers / validation
# =====================
def is_valid_ton_wallet(wallet):
    pattern = r'^[A-Za-z0-9_-]{48}$'
    return re.match(pattern, wallet) is not None

def is_valid_card_number(card_number):
    card_number = card_number.replace(' ', '')
    return len(card_number) == 16 and card_number.isdigit()

# =====================
# Improved send/edit photo
# =====================
REQUISITES_IMAGE = 'images/requisites.jpg'

async def send_photo_message(update, photo_path, text, reply_markup=None, parse_mode=None):
    """Улучшенная смена фото/текста без падений"""
    query_attr = getattr(update, "callback_query", None)
    message_attr = getattr(update, "message", None)

    if query_attr:
        try:
            await query_attr.answer()
        except:
            pass
        try:
            with open(photo_path, "rb") as f:
                media = InputMediaPhoto(media=f, caption=text, parse_mode=parse_mode)
                await query_attr.edit_message_media(media=media, reply_markup=reply_markup)
            return
        except Exception as e:
            logger.info(f"Не удалось изменить медиа: {e}, пробуем изменить только подпись...")
            try:
                await query_attr.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
                return
            except Exception as e2:
                logger.info(f"Не удалось изменить подпись: {e2}, отправляем новое сообщение...")
                try:
                    await query_attr.message.delete()
                except:
                    pass
                with open(photo_path, "rb") as f:
                    await query_attr.message.chat.send_photo(
                        photo=f, caption=text, reply_markup=reply_markup, parse_mode=parse_mode
                    )
                return

    if message_attr:
        with open(photo_path, "rb") as f:
            await message_attr.reply_photo(
                photo=f, caption=text, reply_markup=reply_markup, parse_mode=parse_mode
            )
        return

# =====================
# Start and deal join
# =====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    user_language = db.get_user_language(user.id)

    command_arguments = context.args
    if command_arguments and command_arguments[0].startswith('deal_'):
        await handle_deal_join(update, context, command_arguments[0])
        return

    await send_photo_message(
        update,
        'images/najalo.jpg',
        MESSAGES[user_language]['welcome'],
        reply_markup=get_welcome_inline_keyboard(user_language),
        parse_mode='Markdown'
    )

async def handle_deal_join(update: Update, context: ContextTypes.DEFAULT_TYPE, deal_parameter):
    user = update.effective_user
    user_language = db.get_user_language(user.id)

    deal_identifier = deal_parameter
    deal_info = user_states.get_deal(deal_identifier)
    
    if not deal_info:
        await send_photo_message(update, 'images/najalo.jpg', "❌ Сделка не найдена",
                                 reply_markup=get_welcome_inline_keyboard(user_language))
        return

    # Проверка: пользователь не может присоединиться к своей сделке
    if deal_info['seller_id'] == user.id:
        await send_photo_message(update, 'images/najalo.jpg', "❌ Вы не можете присоединиться к своей собственной сделке",
                                 reply_markup=get_welcome_inline_keyboard(user_language))
        return

    # Обновляем сделку
    user_states.update_deal(deal_identifier, {
        'buyer_id': user.id,
        'status': 'waiting_payment'
    })

    seller_username = f"@{deal_info.get('seller_username', 'Unknown')}"

    gift_links_list = deal_info['gift_links']
    if isinstance(gift_links_list, list):
        deal_description = "\n".join(gift_links_list)
    else:
        deal_description = str(gift_links_list)

    deal_info_text = f"""🛡 **Сделка #{deal_identifier}**

🤵 **Продавец:** {seller_username}
💰 **Сумма сделки:** {deal_info['amount']} {deal_info['fiat_currency']}
💸 **Итоговая сумма:** {deal_info['total_amount']} {deal_info['fiat_currency']}

📋 **Описание:**
{deal_description}

💎 **TON кошелек для оплаты:** `{deal_info.get('payment_address', '—')}`
⚡ **Сумма в TON:** {deal_info.get('ton_amount', '—')}
💵 **Сумма в USDT:** {deal_info.get('usdt_amount', '—')}

Выберите способ оплаты:"""

    await send_photo_message(update, 'images/najalo.jpg', deal_info_text,
                             reply_markup=get_buyer_payment_keyboard(user_language))

    # Уведомление продавца
    try:
        seller_language = db.get_user_language(deal_info['seller_id'])
        await context.bot.send_message(
            chat_id=deal_info['seller_id'],
            text=f"🎉 Покупатель присоединился к вашей сделке!\n\n👤 Имя: {update.effective_user.first_name}\n📞 Юзернейм: @{update.effective_user.username if update.effective_user.username else 'не указан'}"
        )
    except Exception as e:
        logger.error(f"Notify seller failed: {e}")

# =====================
# REQUISITES block
# =====================
async def show_requisites_main_menu(query, user_language):
    requisites_text = "💳 **Реквизиты**\n\nВыберите действие:"
    try:
        await query.edit_message_caption(caption=requisites_text, reply_markup=get_requisites_main_keyboard(user_language), parse_mode='Markdown')
    except Exception:
        await send_photo_message(query, REQUISITES_IMAGE, requisites_text, get_requisites_main_keyboard(user_language), 'Markdown')

async def show_requisites_add_menu(query, user_language):
    add_text = "💳 **Добавить реквизиты**\n\nВыберите тип реквизита:"
    try:
        await query.edit_message_caption(caption=add_text, reply_markup=get_requisites_add_type_keyboard(user_language), parse_mode='Markdown')
    except Exception:
        await send_photo_message(query, REQUISITES_IMAGE, add_text, get_requisites_add_type_keyboard(user_language), 'Markdown')

async def show_requisites_view_menu(query, user_language):
    view_text = "💳 **Посмотреть реквизиты**\n\nВыберите тип реквизита:"
    try:
        await query.edit_message_caption(caption=view_text, reply_markup=get_requisites_view_type_keyboard(user_language), parse_mode='Markdown')
    except Exception:
        await send_photo_message(query, REQUISITES_IMAGE, view_text, get_requisites_view_type_keyboard(user_language), 'Markdown')

async def show_ton_wallet_info(query, user_id, user_language):
    ton_wallet = db.get_user_requisites(user_id)
    if db.has_custom_ton_wallet(user_id):
        wallet_text = f"💎 **Ваш TON кошелёк**\n\n`{ton_wallet}`"
        try:
            await query.edit_message_caption(caption=wallet_text, reply_markup=get_back_to_requisites_keyboard(user_language), parse_mode='Markdown')
        except Exception:
            await send_photo_message(query, REQUISITES_IMAGE, wallet_text, get_back_to_requisites_keyboard(user_language), 'Markdown')
    else:
        await query.answer("❌ TON кошелек не добавлен", show_alert=True)

async def show_bank_cards_list(query, user_id, user_language):
    bank_cards = db.get_user_bank_cards(user_id)
    if bank_cards:
        cards_text = "💳 **Ваши банковские карты**\n\nВыберите реквизит для управления:"
        keyboard = []
        for card in bank_cards:
            masked = f"{card['card_number'][:4]} **** **** {card['card_number'][-4:]}"
            keyboard.append([InlineKeyboardButton(f"{masked} ({card['currency']})", callback_data=f"select_card_{card['id']}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_requisites")])
        markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_caption(caption=cards_text, reply_markup=markup, parse_mode='Markdown')
        except Exception:
            await send_photo_message(query, REQUISITES_IMAGE, cards_text, markup, 'Markdown')
    else:
        await query.answer("❌ Банковские карты не добавлены", show_alert=True)

# =====================
# Message handler (text)
# =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_language = db.get_user_language(user.id)
    state_data = user_states.get_state(user.id)
    state = state_data['state']
    data = state_data.get('data', {})

    if text == '/start':
        await start_command(update, context)
        return

    if text == MESSAGES[user_language]['create_deal']:
        await send_photo_message(update, 'images/create_deal.jpg', MESSAGES[user_language]['choose_deal_type'],
                                 reply_markup=get_deal_type_keyboard(user_language))
        return

    if text == MESSAGES[user_language]['language']:
        language_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
        ])
        await send_photo_message(update, 'images/language.jpg', "🌐 Выберите язык / Choose language:",
                                 reply_markup=language_keyboard)
        return

    if text == MESSAGES[user_language]['requisites']:
        await send_photo_message(update, REQUISITES_IMAGE, "💳 **Реквизиты**\n\nВыберите действие:",
                                 reply_markup=get_requisites_main_keyboard(user_language), parse_mode='Markdown')
        return

    if text == MESSAGES[user_language]['support']:
        support_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Написать в поддержку", url="https://t.me/tresure_support")]
        ])
        await update.message.reply_text("🆘 Нажмите кнопку ниже, чтобы написать в поддержку:", reply_markup=support_keyboard)
        return

    if text == MESSAGES[user_language]['profile']:
        profile_text = "👤 **Профиль**\n\n📊 Успешных сделок: 0"
        profile_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Мои сделки", callback_data="my_deals")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
        ])
        await send_photo_message(update, 'images/profile.jpg', profile_text, reply_markup=profile_keyboard, parse_mode='Markdown')
        return

    # Обработка состояний создания сделки
    if state == 'waiting_gift_links':
        gift_links = [link.strip() for link in text.split('\n') if link.strip()]
        if gift_links:
            data['gift_links'] = gift_links
            user_states.set_state(user.id, 'waiting_currency', data)
            await send_photo_message(update, 'images/create_deal.jpg', 
                                   MESSAGES[user_language]['choose_currency'],
                                   reply_markup=get_currency_keyboard(user_language))
        else:
            await update.message.reply_text("❌ Пожалуйста, введите хотя бы одну ссылку")
        return

    if state == 'waiting_amount':
        try:
            amount_value = float(text)
            if amount_value <= 0:
                await update.message.reply_text("❌ Сумма должна быть больше 0")
                return
            data['amount'] = amount_value
            await send_photo_message(update, 'images/create_deal.jpg', MESSAGES[user_language]['warning_message'],
                                     reply_markup=get_warning_keyboard(user_language))
            user_states.set_state(user.id, 'waiting_warning', data)
        except ValueError:
            await update.message.reply_text("❌ Пожалуйста, введите корректную сумму (например: 2000.5)")
        return

    # Requisites: add TON
    if state == 'waiting_ton_wallet':
        if is_valid_ton_wallet(text):
            ok = db.update_user_requisites(user.id, text)
            if ok:
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("👀 Посмотреть реквизиты", callback_data="view_requisites")]])
                await update.message.reply_text(f"✅ TON кошелек успешно добавлен!\nРеквизит: {text}", reply_markup=keyboard)
            else:
                await update.message.reply_text("❌ Ошибка при сохранении TON кошелька", reply_markup=get_back_to_requisites_keyboard(user_language))
            user_states.clear_state(user.id)
        else:
            await update.message.reply_text("❌ Неверный формат TON кошелька. Попробуйте еще раз:", reply_markup=get_back_to_requisites_keyboard(user_language))
        return

    # Default fallback
    await update.message.reply_text("Используйте кнопки меню для навигации. Для начала нажмите /start", reply_markup=get_welcome_inline_keyboard(user_language))

# =====================
# Callback handler
# =====================
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    callback_data = query.data
    user_language = db.get_user_language(user.id)
    state_data = user_states.get_state(user.id)

    logger.info(f"[CALLBACK] {user.id} -> {callback_data}")

    try:
        # MAIN
        if callback_data == 'create_deal':
            await send_photo_message(update, 'images/create_deal.jpg', MESSAGES[user_language]['choose_deal_type'],
                                     reply_markup=get_deal_type_keyboard(user_language))
            return

        if callback_data == 'profile':
            profile_text = "👤 **Профиль**\n\n📊 Успешных сделок: 0"
            profile_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Мои сделки", callback_data="my_deals")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
            ])
            await send_photo_message(update, 'images/profile.jpg', profile_text, reply_markup=profile_keyboard, parse_mode='Markdown')
            return

        if callback_data == 'requisites':
            await show_requisites_main_menu(query, user_language)
            return

        if callback_data == 'support':
            support_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Написать в поддержку", url="https://t.me/tresure_support")]
            ])
            await query.message.reply_text("🆘 Нажмите кнопку ниже, чтобы написать в поддержку:", reply_markup=support_keyboard)
            return

        if callback_data == 'change_language':
            language_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
                [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
            ])
            await send_photo_message(update, 'images/language.jpg', "🌐 Выберите язык / Choose language:",
                                     reply_markup=language_keyboard)
            return

        # Информация о конкретной сделке
        if callback_data.startswith('deal_info_'):
            deal_id = callback_data.split('_', 2)[2]
            deal_info = user_states.get_deal(deal_id)
            if not deal_info:
                await query.answer("❌ Сделка не найдена", show_alert=True)
                return

            gift_links = deal_info.get('gift_links', [])
            if isinstance(gift_links, list):
                deal_description = "\n".join(gift_links)
            else:
                deal_description = str(gift_links)

            if deal_info['seller_id'] == user.id:
                role_text = "👤 Вы продавец в сделке."
                if deal_info.get('buyer_id'):
                    buyer_info = db.get_user(deal_info['buyer_id'])
                    if buyer_info:
                        buyer_username = f"@{buyer_info[1]}" if buyer_info[1] else str(buyer_info[0])
                        counterpart_info = f"📌 Покупатель: {buyer_username}"
                    else:
                        counterpart_info = f"📌 Покупатель: {deal_info['buyer_id']}"
                else:
                    counterpart_info = "📌 Покупатель: ожидание присоединения"
            else:
                role_text = "👥 Вы покупатель в сделке."
                seller_info = db.get_user(deal_info['seller_id'])
                if seller_info:
                    seller_username = f"@{seller_info[1]}" if seller_info[1] else seller_info[2]
                    counterpart_info = f"📌 Продавец: {seller_username}"
                else:
                    counterpart_info = f"📌 Продавец: {deal_info['seller_id']}"

            deal_info_text = (
                f"📋 Информация о сделке #{deal_id}\n\n"
                f"{role_text}\n{counterpart_info}\n\n"
                f"💰 Сумма сделки: {deal_info['amount']} {deal_info['fiat_currency']} "
                f"({deal_info['total_amount']} {deal_info['fiat_currency']})\n"
                f"📜 Вы {'продаете' if deal_info['seller_id'] == user.id else 'покупаете'}:\n{deal_description}"
            )

            info_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="my_deals")]])
            await send_photo_message(update, 'images/profile.jpg', deal_info_text, reply_markup=info_keyboard)
            return

        if callback_data.startswith('lang_'):
            new_lang = callback_data.split('_', 1)[1]
            db.update_user_language(user.id, new_lang)
            await send_photo_message(update, 'images/language.jpg', MESSAGES[new_lang]['welcome'], reply_markup=get_welcome_inline_keyboard(new_lang))
            return

        # Deal creation flow
        if callback_data.startswith('deal_'):
            deal_type = callback_data.split('_', 1)[1]
            user_states.set_state(user.id, 'waiting_gift_links', {'deal_type': deal_type})
            
            deal_messages = {
                'gift': 'enter_gift_links',
                'channel': 'enter_channel_links', 
                'username': 'enter_username_links',
                'premium': 'enter_premium_links'
            }
            
            message_key = deal_messages.get(deal_type, 'enter_gift_links')
            message_text = MESSAGES[user_language][message_key]
            
            await send_photo_message(update, 'images/create_deal.jpg', message_text, reply_markup=None)
            return

        if callback_data.startswith('currency_'):
            currency = callback_data.split('_', 1)[1]
            data = state_data.get('data', {})
            data['currency'] = currency
            if currency == 'card':
                await send_photo_message(update, 'images/create_deal.jpg', MESSAGES[user_language]['choose_fiat'], reply_markup=get_fiat_currency_keyboard(user_language))
                user_states.set_state(user.id, 'waiting_fiat', data)
            else:
                await send_photo_message(update, 'images/create_deal.jpg', MESSAGES[user_language]['enter_amount'].format(currency=currency.upper()), reply_markup=None)
                user_states.set_state(user.id, 'waiting_amount', data)
            return

        if callback_data.startswith('fiat_'):
            fiat = callback_data.split('_', 1)[1]
            data = state_data.get('data', {})
            data['fiat_currency'] = fiat
            await send_photo_message(update, 'images/create_deal.jpg', MESSAGES[user_language]['enter_amount'].format(currency=fiat), reply_markup=None)
            user_states.set_state(user.id, 'waiting_amount', data)
            return

        if callback_data == 'warning_read':
            deal_info_data = state_data.get('data', {})
            
            if 'amount' not in deal_info_data:
                await query.answer("❌ Ошибка: сумма сделки не определена", show_alert=True)
                return
                
            if 'currency' not in deal_info_data and 'fiat_currency' not in deal_info_data:
                await query.answer("❌ Ошибка: валюта не определена", show_alert=True)
                return

            currency = deal_info_data.get('fiat_currency') or deal_info_data.get('currency', 'RUB')
            amount = deal_info_data['amount']
            total_amount = round(amount * (1 + FEE_PERCENT / 100), 2)
            
            # Создаем сделку в оперативной памяти
            deal_data = {
                'seller_id': user.id,
                'seller_username': user.username,
                'deal_type': deal_info_data.get('deal_type', 'gift'),
                'gift_links': deal_info_data.get('gift_links', []),
                'currency': currency,
                'fiat_currency': currency,
                'amount': amount,
                'total_amount': total_amount,
                'fee_percent': FEE_PERCENT,
                'ton_rate': TON_RATE,
                'usdt_rate': USDT_RATE,
                'payment_address': 'UQC6xSiO2wZ3GTGFnrdxoLY5iNqzwzZftbduHxznEHe6wC5M',  # Пример кошелька
                'ton_amount': round(total_amount / TON_RATE, 4),
                'usdt_amount': round(total_amount / USDT_RATE, 2)
            }

            deal_id = user_states.create_deal(deal_data)
            
            if not deal_id:
                await query.answer("❌ Ошибка при создании сделки", show_alert=True)
                return

            share_url = f"https://t.me/share/url?url=https://t.me/TreasureSaveBot?start={deal_id}"

            share_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Поделиться сделкой", url=share_url)],
                [InlineKeyboardButton("❌ Выйти из сделки", callback_data="exit_deal")],
                [InlineKeyboardButton("📋 Мои сделки", callback_data="my_deals")]
            ]) 

            gift_links = deal_info_data.get('gift_links', [])
            desc = "\n".join(gift_links) if isinstance(gift_links, list) else str(gift_links)

            deal_created_text = (
                f"🛡 Сделка #{deal_id}\n\n"
                f"💰 Сумма сделки: {amount} {currency} "
                f"({total_amount} {currency})\n"
                f"📜 Описание:\n{desc}\n"
                f"🔗 Ссылка для пересылки: {share_url}"
            )

            await send_photo_message(update, 'images/create_deal.jpg', deal_created_text, reply_markup=share_keyboard)
            user_states.clear_state(user.id)
            return

        # Requisites navigation/actions
        if callback_data == 'add_requisites':
            await show_requisites_add_menu(query, user_language)
            return

        if callback_data == 'view_requisites':
            await show_requisites_view_menu(query, user_language)
            return

        if callback_data == 'add_ton_wallet':
            user_states.set_state(user.id, 'waiting_ton_wallet')
            try:
                await query.edit_message_caption(
                    caption=("💎 **Добавление TON кошелька**\n\nВведите TON кошелек:\n\n"
                             "Пример: UQC6xSiO2wZ3GTGFnrdxoLY5iNqzwzZftbduHxznEHe6wC5M"),
                    reply_markup=get_back_to_requisites_keyboard(user_language),
                    parse_mode='Markdown'
                )
            except Exception:
                await send_photo_message(
                    query, REQUISITES_IMAGE,
                    "💎 **Добавление TON кошелька**\n\nВведите TON кошелек:\n\nПример: UQC6xSiO2wZ3GTGFnrdxoLY5iNqzwzZftbduHxznEHe6wC5M",
                    get_back_to_requisites_keyboard(user_language), 'Markdown'
                )
            return

        # ====== ПОДТВЕРЖДЕНИЕ ОПЛАТЫ (только для админов) ======
        if callback_data == 'confirm_payment':
            user_id = user.id
            is_admin = db.is_admin(user_id)
            
            if not is_admin:
                await query.answer("❌ Оплата не найдена. Если вы уверены в оплате, повторите попытку через 10 секунд", show_alert=True)
                return

            waiting_deals = user_states.get_waiting_payment_deals()
            
            if waiting_deals:
                deal = waiting_deals[0]
                user_states.update_deal(deal['deal_id'], {'status': 'paid'})
                
                try:
                    await query.edit_message_caption(caption="✅ Оплата подтверждена! Ожидайте отправки подарка продавцом.")
                except Exception:
                    try:
                        await query.edit_message_text(text="✅ Оплата подтверждена! Ожидайте отправки подарка продавцом.")
                    except:
                        pass
                
                # Уведомляем продавца
                try:
                    seller_language = db.get_user_language(deal['seller_id'])
                    await context.bot.send_message(
                        chat_id=deal['seller_id'],
                        text=f"💰 Оплата по сделке #{deal['deal_id']} подтверждена!\n\n👤 Отправьте подарок администратору @tresure_support\n\n⚠️ Отправляйте подарок только администратору. Обязательно записывайте момент передачи на видео.",
                        reply_markup=get_seller_gift_sent_keyboard(seller_language)
                    )
                except Exception as e:
                    logger.error(f"Notify seller error after admin confirm: {e}")
            else:
                await query.answer("❌ Нет сделок для подтверждения", show_alert=True)
            return

        # Navigation
        if callback_data == 'back_main':
            await send_photo_message(update, 'images/najalo.jpg', MESSAGES[user_language]['welcome'], reply_markup=get_welcome_inline_keyboard(user_language))
            return

        if callback_data == 'back_requisites':
            await show_requisites_main_menu(query, user_language)
            return

        # Мои сделки - список сделок
        if callback_data == 'my_deals':
            user_deals_list = user_states.get_user_deals(user.id)
            if not user_deals_list:
                deals_text = "🛡 Мои сделки\n\n📋 У вас пока нет сделок"
                deals_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад в профиль", callback_data="profile")]])
                await send_photo_message(update, 'images/profile.jpg', deals_text, reply_markup=deals_keyboard)
                return

            deals_text = "🛡 Мои сделки\n\nВыберите сделку для управления:"
            keyboard = []
            for deal in user_deals_list[:10]:
                deal_button_text = f"💰 {deal['amount']} {deal['fiat_currency']} | #{deal['deal_id']}"
                keyboard.append([InlineKeyboardButton(deal_button_text, callback_data=f"deal_info_{deal['deal_id']}")])
            keyboard.append([InlineKeyboardButton("⬅️ Назад в профиль", callback_data="profile")])
            deals_keyboard = InlineKeyboardMarkup(keyboard)
            await send_photo_message(update, 'images/profile.jpg', deals_text, reply_markup=deals_keyboard)
            return

        if callback_data == 'gift_sent':
            user_deals_list = user_states.get_user_deals(user.id)
            current_deal_info = next((d for d in user_deals_list if d.get('status') == 'paid' and d.get('seller_id') == user.id), None)
            if current_deal_info:
                user_states.update_deal(current_deal_info['deal_id'], {'status': 'completed'})
                try:
                    await query.edit_message_caption(caption="✅ Сделка завершена! Спасибо за использование нашего сервиса.")
                except Exception:
                    try:
                        await query.edit_message_text(text="✅ Сделка завершена! Спасибо за использование нашего сервиса.")
                    except:
                        pass
                try:
                    await context.bot.send_message(chat_id=current_deal_info['buyer_id'], text="✅ Продавец отправил подарок! Сделка завершена.")
                except Exception as e:
                    logger.error(f"Notify buyer after gift_sent error: {e}")
            else:
                await query.answer("У вас нет сделок, ожидающих отправки подарка")
            return

        if callback_data == 'exit_deal':
            user_states.clear_state(user.id)
            await send_photo_message(update, 'images/create_deal.jpg', MESSAGES[user_language]['welcome'], reply_markup=get_welcome_inline_keyboard(user_language))
            return

    except Exception as e:
        logger.error(f"Callback handler error: {e}")
        try:
            await query.edit_message_caption(caption="❌ Произошла ошибка. Пожалуйста, попробуйте еще раз.")
        except Exception:
            try:
                await query.edit_message_text(text="❌ Произошла ошибка. Пожалуйста, попробуйте еще раз.")
            except Exception:
                try:
                    await query.message.reply_text("❌ Произошла ошибка. Пожалуйста, попробуйте еще раз.")
                except:
                    pass

# =====================
# Global error handler
# =====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

# =====================
# Admin command
# =====================
async def sculpture_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /sculpture для добавления админа"""
    user = update.effective_user
    
    try:
        db.add_user(user.id, user.username, user.first_name)
        success = db.add_admin(user.id, user.username)
        
        if success:
            await update.message.reply_text(
                "🔧 **Режим администратора активирован!**\n\n"
                "Теперь вы можете подтверждать оплаты сделок.", 
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ **Не удалось активировать режим администратора.**", 
                parse_mode='Markdown'
            )
                
    except Exception as e:
        logger.error(f"Add admin error: {e}")
        await update.message.reply_text(f"❌ **Ошибка:** {e}")

# =====================
# Main / run
# =====================
def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Укажите токен в config.BOT_TOKEN")
        return

    os.makedirs('images', exist_ok=True)

    try:
        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("sculpture", sculpture_command))
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(CallbackQueryHandler(handle_callback_query))

        print("✅ Бот запускается...")
        print("🔄 Бот работает. Для остановки нажмите Ctrl+C")

        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        logger.error(f"Bot startup error: {e}")
    except KeyboardInterrupt:
        print("⏹️ Бот остановлен пользователем")
    finally:
        print("👋 Бот завершил работу")

if __name__ == "__main__":
    main()
