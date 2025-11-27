## 3. messages.py

MESSAGES = {
    'ru': {
        'welcome': """👋 **Добро пожаловать в Garant Bot!**


🔸 Автоматические сделки
🔸 Вывод в любой валюте
🔸 Поддержка 24/7
🔸 Удобный интерфейс

*Выберите нужный раздел ниже:*""",
        'main_menu': "🏠 Главное меню:",
        'create_deal': "🛡 Создать сделку",
        'payment_not_found': "❌ Оплата сделки #{deal_id} не найдена, повторите попытку через 10 секунд или обратитесь в поддержку",
        'profile': "👤 Профиль",
        'requisites': "💳 Реквизиты",
        'support': "🆘 Поддержка",
        'language': "🌐 Change Language",
        'choose_deal_type': "Выберите тип сделки:",
        'gifts': "🎁 Подарки",
        'usertag': "🔖 Юзертейг",
        'channel': "📢 Канал/Чат",
        'enter_gift_links': "Введите ссылку(-и) на подарок(-и) в одном из форматов:\n\nПримеры:\n• https://t.me/nft/CandyCane-147484\n• https://t.me/gift/123456",
        'choose_currency': "Выберите валюту для создания сделки:",
        'choose_fiat': "Выберите фиатную валюту для создания сделки:",
        'enter_amount': "Введите сумму сделки в {currency}\n\nПример: 2000.5",
        'warning_message': '''⚠️ Обязательно к прочтению!

Проверка получение подарка происходит автоматически — только если вы отправляете подарок на аккаунт @tresuresafe_support

Если же вы отправите подарок напрямую покупателю, то проверка НЕ СРАБОТАЕТ, и
• Подарок будет потерян
• Вывести средства станет невозможно
• Сделка будет считаться несостоявшейся и вы потеряете свой подарок и деньги

👉 Чтобы успешно завершить сделку и получить средства — всегда отправляйте подарок только на аккаунт @tresuresafe_support''',
        'i_read': "✅ Я прочитал(-а)",
        'deal_created': '''🛡 Сделка #{deal_id}

💰 Сумма сделки: {amount} {currency} ({total_amount} {currency})
📜 Описание:
{description}''',
        'deal_share': '''🛡 Сделка #{deal_id}

💰 Сумма сделки: {amount} {currency} ({total_amount} {currency})
📜 Описание:
{description}

🔗 Ссылка для покупателя: {buyer_link}''',
        'back': "⬅️ Назад",
        'cancel': "❌ Отменить",
        'share_deal': "📤 Поделиться сделкой",
        'exit_deal': "🚪 Выйти из сделки",
        'my_deals': "📋 Мои сделки",
        'buyer_joined': "👤 Пользователь {username} присоединился к сделке\n\n✅ Успешные сделки: {successful_deals}\n\n⚠️ Проверьте, что это тот же пользователь, с которым вы вели диалог ранее!\n\n❗️После того как покупатель оплатит сделку, в этом чате вы получите уведомление с инструкциями о дальнейших действиях.",
        
        'buyer_deal_info': '''📋 Информация о сделке #{deal_id}

👤 Вы покупатель в сделке.
📌 Продавец: {seller_username}
╰  Успешные сделки: {successful_deals}

💰 Сумма сделки: {amount} {currency} ({total_amount} {currency})
📜 Вы покупаете:
{description}

🏦 Адрес для оплаты:
{payment_address}

💎 Сумма к оплате в TON: {ton_amount} TON
💵 Сумма к оплате в USDT(TON): {usdt_amount} USDT
📝 Комментарий к платежу (мемо): {deal_id}

⚠️ Пожалуйста, убедитесь в правильности данных перед оплатой. Комментарий(мемо) обязателен!''',
        
        'confirm_payment': "✅ Подтвердить оплату",
        'payment_confirmed': '''✅ Оплата по сделке #{deal_id} подтверждена.

👤 Продавец: {seller_name}
💰 Сумма сделки: {amount} {currency} ({total_amount} {currency})
📜 Описание:
{description}

Ожидайте, пока продавец отправит подарок на @tresuresafe_support

⚙️ Подтверждение получения товара - автоматически.''',
        
        'seller_payment_notification': '''✅ Оплата по сделке #{deal_id} подтверждена.

📜 Описание: Подарок
👤 Отправьте подарок администратору @tresuresafe_support

⚠️ Отправляйте подарок только администратору. Обязательно записывайте момент передачи на видео.''',
        
        'gift_sent': "🎁 Я отправил подарок",
        'contact_support': "🆘 Связаться с поддержкой",
        'waiting_admin_confirmation': "✅ Ожидайте подтверждения от администратора",
        'deal_completed': "🎉 Сделка успешно завершена! Средства переведены продавцу.",
        
        'deal_status_created': "📝 Создана",
        'deal_status_waiting_payment': "⏳ Ожидание оплаты",
        'deal_status_paid': "✅ Оплачено",
        'deal_status_gift_sent': "🎁 Подарок отправлен",
        'deal_status_completed': "✅ Завершена"
    },
    'en': {
        'welcome': "👋 Welcome to the guarantee bot!",
        'main_menu': "🏠 Main menu:",
        'create_deal': "🛡 Create deal",
        'profile': "👤 Profile",
        'requisites': "💳 Requisites",
        'support': "🆘 Support",
        'language': "🌐 Change Language",
        'choose_deal_type': "Choose deal type:",
        'gifts': "🎁 Gifts",
        'usertag': "🔖 Usertag",
        'channel': "📢 Channel/Chat",
        'enter_gift_links': "Enter gift link(s) in one of the formats:\n\nExamples:\n• https://t.me/nft/CandyCane-147484\n• https://t.me/gift/123456",
        'choose_currency': "Choose currency for deal creation:",
        'choose_fiat': "Choose fiat currency for deal creation:",
        'enter_amount': "Enter deal amount in {currency}\n\nExample: 2000.5",
        'warning_message': '''⚠️ Must read!
Gift receipt verification happens automatically — only if you send the gift to @tresuresafe_support

If you send the gift directly to the buyer, verification WILL NOT WORK, and
• The gift will be lost
• Withdrawal of funds will become impossible
• The deal will be considered failed and you will lose your gift and money

👉 To successfully complete the deal and receive funds — always send the gift only to @tresuresafe_support account''',
        'i_read': "✅ I have read",
        'deal_created': '''🛡 Deal #{deal_id}

💰 Deal amount: {amount} {currency} ({total_amount} {currency})
📜 Description:
{description}''',
        'deal_share': '''🛡 Deal #{deal_id}

💰 Deal amount: {amount} {currency} ({total_amount} {currency})
📜 Description:
{description}

🔗 Buyer link: {buyer_link}''',
        'back': "⬅️ Back",
        'cancel': "❌ Cancel",
        'share_deal': "📤 Share deal",
        'exit_deal': "🚪 Exit deal",
        'my_deals': "📋 My deals",
        'buyer_joined': "👤 User {username} joined the deal\n\n✅ Successful deals: {successful_deals}\n\n⚠️ Make sure this is the same user you were chatting with before!\n\n❗️After the buyer pays for the deal, you will receive a notification in this chat with further instructions.",
        
        'buyer_deal_info': '''📋 Deal information #{deal_id}

👤 You are the buyer in this deal.
📌 Seller: {seller_username}
╰  Successful deals: {successful_deals}

💰 Deal amount: {amount} {currency} ({total_amount} {currency})
📜 You are buying:
{description}

🏦 Payment address:
{payment_address}

💎 Amount to pay in TON: {ton_amount} TON
💵 Amount to pay in USDT(TON): {usdt_amount} USDT
📝 Payment comment (memo): {deal_id}

⚠️ Please verify the data before payment. Comment(memo) is mandatory!''',
        
        'confirm_payment': "✅ Confirm payment",
        'payment_confirmed': '''✅ Payment for deal #{deal_id} confirmed.

👤 Seller: {seller_name}
💰 Deal amount: {amount} {currency} ({total_amount} {currency})
📜 Description:
{description}

Wait for the seller to send the gift to @tresuresafe_support

⚙️ Product receipt confirmation - automatic.''',
        
        'seller_payment_notification': '''✅ Payment for deal #{deal_id} confirmed.

📜 Description: Gift
👤 Send the gift to administrator @tresuresafe_support

⚠️ Send the gift only to the administrator. Be sure to record the transfer moment on video.''',
        
        'gift_sent': "🎁 I sent the gift",
        'contact_support': "🆘 Contact support",
        'waiting_admin_confirmation': "✅ Wait for administrator confirmation",
        'deal_completed': "🎉 Deal successfully completed! Funds transferred to seller.",
        
        'deal_status_created': "📝 Created",
        'deal_status_waiting_payment': "⏳ Waiting for payment",
        'deal_status_paid': "✅ Paid",
        'deal_status_gift_sent': "🎁 Gift sent",
        'deal_status_completed': "✅ Completed"
    },
    'kz': {
        'welcome': "👋 Кепіл ботына қош келдіңіз!",
        'main_menu': "🏠 Басты мәзір:",
        'create_deal': "🛡 Мәміле жасау",
        'profile': "👤 Профиль",
        'requisites': "📋 Реквизиттер",
        'support': "🆘 Қолдау",
        'language': "🌐 Change Language",
        'choose_deal_type': "Мәміле түрін таңдаңыз:",
        'gifts': "🎁 Сыйлықтар",
        'usertag': "🔖 Юзертейг",
        'channel': "📢 Арна/Чат",
        'enter_gift_links': "Сыйлық сілтемесін (-дерін) форматтардың бірінде енгізіңіз:\n\nМысалдар:\n• https://t.me/nft/CandyCane-147484\n• https://t.me/gift/123456",
        'choose_currency': "Мәміле жасау валютасын таңдаңыз:",
        'choose_fiat': "Мәміле жасауға арналған ақшалай валютаны таңдаңыз:",
        'enter_amount': "{currency} мәміле сомасын енгізіңіз\n\nМысалы: 2000.5",
        'warning_message': '''⚠️ Міндетті түрде оқыңыз!

Сыйлықты тексеру автоматты түрде жүреді — тек сіз сыйлықты @tresuresafe_support аккаунтына жіберсеңіз

Егер сіз сыйлықты тікелей сатып алушыға жіберсеңіз, тексеру ЖҮМЕЙДІ, және
• Сыйлық жоғалады
• Қаражатты алу мүмкін болмайды
• Мәміле сәтсіз болып саналады және сіз сыйлығыңызбен ақшаңызды жоғаласыз

👉 Мәмілені сәтті аяқтау және қаражат алу үшін — әрқашан сыйлықты тек @tresuresafe_support аккаунтына жіберіңіз''',
        'i_read': "✅ Мен оқыдым",
        'deal_created': '''🛡 Мәміле #{deal_id}

💰 Мәміле сомасы: {amount} {currency} ({total_amount} {currency})
📜 Сипаттама:
{description}''',
        'deal_share': '''🛡 Мәміле #{deal_id}

💰 Мәміле сомасы: {amount} {currency} ({total_amount} {currency})
📜 Сипаттама:
{description}

🔗 Сатып алушы сілтемесі: {buyer_link}''',
        'back': "⬅️ Артқа",
        'cancel': "❌ Бас тарту",
        'share_deal': "📤 Мәмілені бөлісу",
        'exit_deal': "🚪 Мәміледен шығу",
        'my_deals': "📋 Менің мәмілелерім",
        'buyer_joined': "👤 {username} пайдаланушысы мәмілеге қосылды\n\n✅ Сәтті мәмілелер: {successful_deals}\n\n⚠️ Бұл сіз бұрын сөйлескен пайдаланушы екеніне көз жеткізіңіз!\n\n❗️Сатып алушы мәміле үшін төлем жасағаннан кейін, сіз осы чатта әрі қарайғы әрекеттер туралы нұсқаулармен хабарлама аласыз.",
        
        'buyer_deal_info': '''📋 Мәміле ақпараты #{deal_id}

👤 Сіз бұл мәміледе сатып алушысыз.
📌 Сатушы: {seller_username}
╰  Сәтті мәмілелер: {successful_deals}

💰 Мәміле сомасы: {amount} {currency} ({total_amount} {currency})
📜 Сіз сатып аласыз:
{description}

🏦 Төлем мекенжайы:
{payment_address}

💎 TON-да төлем сомасы: {ton_amount} TON
💵 USDT(TON)-да төлем сомасы: {usdt_amount} USDT
📝 Төлем түсініктемесі (мемо): {deal_id}

⚠️ Төлемді жасас бұрын деректердің дұрыстығын тексеріңіз. Түсініктеме (мемо) міндетті!''',
        
        'confirm_payment': "✅ Төлемді растау",
        'payment_confirmed': '''✅ #{deal_id} мәмілесі үшін төлем расталды.

👤 Сатушы: {seller_name}
💰 Мәміле сомасы: {amount} {currency} ({total_amount} {currency})
📜 Сипаттама:
{description}

Сатушының @tresuresafe_support-ге сыйлық жіберуін күтіңіз

⚙️ Тауарды алуды растау - автоматты түрде.''',
        
        'seller_payment_notification': '''✅ #{deal_id} мәмілесі үшін төлем расталды.

📜 Сипаттама: Сыйлық
👤 Сыйлықты әкімшіге @tresuresafe_support жіберіңіз

⚠️ Сыйлықты тек әкімшіге жіберіңіз. Беру сәтінің бейнесін міндетті түрде түсіріңіз.''',
        
        'gift_sent': "🎁 Мен сыйлықты жібердім",
        'contact_support': "🆘 Қолдау қызметіне хабарласыңыз",
        'waiting_admin_confirmation': "✅ Әкімшінің растауын күтіңіз",
        'deal_completed': "🎉 Мәміле сәтті аяқталды! Қаражат сатушыға аударылды.",
        
        'deal_status_created': "📝 Жасалған",
        'deal_status_waiting_payment': "⏳ Төлем күтілуде",
        'deal_status_paid': "✅ Төленген",
        'deal_status_gift_sent': "🎁 Сыйлық жіберілген",
        'deal_status_completed': "✅ Аяқталған"
    }
}
