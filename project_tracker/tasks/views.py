from django.shortcuts import render, get_object_or_404
from datetime import date
from .models import CashbackService, CashbackOrder, CashbackOrderService

def all_cashback_services(request):
    # Количество карточек в заявке
    transaction_count = CashbackOrderService.objects.filter(order__creator=request.user).count()

    # Обработка запроса поиска
    search_query = request.GET.get('cashback_categories', '')
    if search_query:
        filtered_services = CashbackService.objects.filter(category__icontains=search_query, status='active')
    else:
        filtered_services = CashbackService.objects.filter(status='active')

    current_report_id = 1  # Задайте нужный отчет

    return render(request, 'index.html', {
        'data': {
            'current_date': date.today(),
            'services': filtered_services,
            'cart_item_count': transaction_count,
            'current_report_id': current_report_id,
            'search_query': search_query
        }
    })

def cashback_details(request, id):
    service = get_object_or_404(CashbackService, id=id)
    return render(request, 'cashback_details.html', {'data': service})

def monthly_cashbacks_view(request, report_id):
    transactions_with_titles = []
    selected_report = get_object_or_404(CashbackOrder, id=report_id)

    for transaction in CashbackOrderService.objects.filter(order=selected_report):
        transactions_with_titles.append({
            'category': transaction.service.category,
            'spent_amount': transaction.total_spent,
            'cashback_earned': extract_cashback_percentage(transaction.service.cashback_percentage_text) * transaction.total_spent,
            'image_url': transaction.service.image_url,
            'cashback_percentage_text': transaction.service.cashback_percentage_text,
            'report_id': selected_report.id  
        })

    return render(request, 'monthly_cashbacks.html', {
        'data': {
            'transactions': transactions_with_titles,
            'current_month': selected_report.month
        }
    })

def extract_cashback_percentage(cashback_percentage_text):
    match = re.search(r'(\d+)%', cashback_percentage_text)
    if match:
        return int(match.group(1)) / 100
    return 0

# from django.shortcuts import render
# from datetime import date
# import re  # Для извлечения процентов

# # Вынесенная коллекция заказов
# cashbacks = [
#     {
#         'id': 1,
#         'title': 'Образование',
#         'image_url': 'http://127.0.0.1:9000/web/free-icon-books-4645290.png',
#         'details_text': 'Вы получите 7% кешбэка',
#         'full_description': 'Оплата образовательных программ и курсов.',
#         'price': 'Кешбэк за оплату обучения в аккредитованных учебных заведениях, онлайн-курсах и платформах для повышения квалификации.',
#     },
#     {
#         'id': 2,
#         'title': 'Кафе и рестораны',
#         'image_url': 'http://127.0.0.1:9000/web/free-icon-restaurant-1689246.png',
#         'details_text': 'Вы получите 5% кешбэка',
#         'full_description': 'Оплата в заведениях общественного питания.',
#         'price': 'Кешбэк за покупки в ресторанах, кафе, барах и сетях быстрого питания, включая доставку еды.',
#     },
#     {
#         'id': 3,
#         'title': 'Спортивные товары',
#         'image_url': 'http://127.0.0.1:9000/web/free-icon-basketball-4645268.png',
#         'details_text': 'Вы получите 5% кешбэка',
#         'full_description': 'Покупки спортивного инвентаря и экипировки.',
#         'price': 'Кешбэк за приобретение спортивных товаров, одежды, инвентаря и оборудования в специализированных магазинах и онлайн-платформах.',
#     },
#     {
#         'id': 4,
#         'title': 'Аптеки',
#         'image_url': 'http://127.0.0.1:9000/web/free-icon-online-pharmacy-4435601.png',
#         'details_text': 'Вы получите 10% кешбэка',
#         'full_description': 'Покупка медикаментов и товаров для здоровья.',
#         'price': 'Кешбэк за оплату в аптеках, профильных магазинах товаров для здоровья и онлайн-аптеках.',
#     },
#     {
#         'id': 5,
#         'title': 'Туризм',
#         'image_url': 'http://127.0.0.1:9000/web/free-icon-hiking-1974052.png',
#         'details_text': 'Вы получите 7% кешбэка',
#         'full_description': 'Оплата туристических услуг, включая бронирование отелей и билетов.',
#         'price': 'Кешбэк за услуги в туристических агентствах, онлайн-сервисах для путешествий и при бронировании экскурсионных туров.',
#     },
#     {
#         'id': 6,
#         'title': 'Электроника',
#         'image_url': 'http://127.0.0.1:9000/web/free-icon-electronics-1692714.png',
#         'details_text': 'Вы получите 5% кешбэка',
#         'full_description': 'Покупка техники и электроники.',
#         'price': 'Кешбэк за приобретение смартфонов, компьютеров, телевизоров и других гаджетов в магазинах и онлайн-платформах.',
#     },
# ]

# # Мои кешбэки за месяц с ID заявки
# categories_cashbacks = [
#     {
#         'order_id': 1,
#         'month': 'Сентябрь',
#         'items': [
#             {'cashback_id': 1, 'spent': 33213},
#             {'cashback_id': 2, 'spent': 12132},
#             {'cashback_id': 3, 'spent': 53123},
#         ]
#     },
# ]

# # Вспомогательная функция для извлечения процента кешбэка из текста
# def extract_cashback_percentage(details_text):
#     match = re.search(r'(\d+)%', details_text)
#     if match:
#         return int(match.group(1)) / 100
#     return 0

# def cashback_services(request):
#     # Количество карточек в корзине
#     item_count = sum(len(category['items']) for category in categories_cashbacks)

#     # Обработка запроса поиска
#     search_query = request.GET.get('cashback_categories', '')
#     if search_query:
#         filtered_cashbacks = [cashback for cashback in cashbacks if search_query.lower() in cashback['title'].lower()]
#     else:
#         filtered_cashbacks = cashbacks

#     current_month_id = 1  # Задайте нужный месяц

#     return render(request, 'index.html', {
#         'data': {
#             'current_date': date.today(),
#             'cashbacks': filtered_cashbacks,
#             'cart_item_count': item_count,
#             'current_month_id': current_month_id,
#             'search_query': search_query  # Добавлено для сохранения значения поиска
#         }
#     })

# def GetOrder(request, id):
#     item = next((cashback for cashback in cashbacks if cashback['id'] == id), None)
#     if item is None:
#         return render(request, '404.html')

#     return render(request, 'order.html', {'data': item})

# def categories_cashbacks_view(request, order_id):
#     cart_items_with_titles = []

#     # Находим категории по идентификатору заявки (order_id)
#     selected_order = next((order for order in categories_cashbacks if order['order_id'] == order_id), None)
    
#     if selected_order:
#         for item in selected_order['items']:
#             cashback = next((cashback for cashback in cashbacks if cashback['id'] == item['cashback_id']), None)
#             if cashback:
#                 # Извлекаем процент кешбэка
#                 cashback_percentage = extract_cashback_percentage(cashback['details_text'])
#                 # Рассчитываем полученный кешбэк и округляем до целого числа
#                 cashback_received = int(item['spent'] * cashback_percentage)
                
#                 cart_items_with_titles.append({
#                     'title': cashback['title'],
#                     'spent': item['spent'],
#                     'cashback_received': cashback_received,  # Добавляем округленный полученный кешбэк
#                     'image_url': cashback['image_url'],
#                     'details_text': cashback['details_text'],
#                     'order_id': selected_order['order_id']  # Поле ID заявки
#                 })

#     return render(request, 'cashbacks.html', {
#         'data': {
#             'categories_cashbacks': cart_items_with_titles,
#             'current_month': selected_order['month'] if selected_order else 'Неизвестный месяц'
#         }
#     })






