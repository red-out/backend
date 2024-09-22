from django.shortcuts import render
from datetime import date
import re  # Для извлечения процентов

# Коллекция кешбэк-услуг
cashback_services = [
    {
        'id': 1,
        'category': 'Образование',
        'image_url': 'http://127.0.0.1:9000/web/free-icon-books-4645290.png',
        'cashback_percentage_text': 'Вы получите 7% кешбэка',
        'full_description': 'Оплата образовательных программ и курсов.',
        'details': 'Кешбэк за оплату обучения в аккредитованных учебных заведениях, онлайн-курсах и платформах для повышения квалификации.',
    },
    {
        'id': 2,
        'category': 'Кафе и рестораны',
        'image_url': 'http://127.0.0.1:9000/web/free-icon-restaurant-1689246.png',
        'cashback_percentage_text': 'Вы получите 5% кешбэка',
        'full_description': 'Оплата в заведениях общественного питания.',
        'details': 'Кешбэк за покупки в ресторанах, кафе, барах и сетях быстрого питания, включая доставку еды.',
    },
    {
        'id': 3,
        'category': 'Спортивные товары',
        'image_url': 'http://127.0.0.1:9000/web/free-icon-basketball-4645268.png',
        'cashback_percentage_text': 'Вы получите 5% кешбэка',
        'full_description': 'Покупки спортивного инвентаря и экипировки.',
        'details': 'Кешбэк за приобретение спортивных товаров, одежды, инвентаря и оборудования в специализированных магазинах и онлайн-платформах.',
    },
    {
        'id': 4,
        'category': 'Аптеки',
        'image_url': 'http://127.0.0.1:9000/web/free-icon-online-pharmacy-4435601.png',
        'cashback_percentage_text': 'Вы получите 10% кешбэка',
        'full_description': 'Покупка медикаментов и товаров для здоровья.',
        'details': 'Кешбэк за оплату в аптеках, профильных магазинах товаров для здоровья и онлайн-аптеках.',
    },
    {
        'id': 5,
        'category': 'Туризм',
        'image_url': 'http://127.0.0.1:9000/web/free-icon-hiking-1974052.png',
        'cashback_percentage_text': 'Вы получите 7% кешбэка',
        'full_description': 'Оплата туристических услуг, включая бронирование отелей и билетов.',
        'details': 'Кешбэк за услуги в туристических агентствах, онлайн-сервисах для путешествий и при бронировании экскурсионных туров.',
    },
    {
        'id': 6,
        'category': 'Электроника',
        'image_url': 'http://127.0.0.1:9000/web/free-icon-electronics-1692714.png',
        'cashback_percentage_text': 'Вы получите 5% кешбэка',
        'full_description': 'Покупка техники и электроники.',
        'details': 'Кешбэк за приобретение смартфонов, компьютеров, телевизоров и других гаджетов в магазинах и онлайн-платформах.',
    },
]

# Мои кешбэки за месяц
monthly_cashbacks = [
    {
        'report_id': 1,
        'month': 'Сентябрь',
        'transactions': [
            {'service_id': 1, 'spent_amount': 33213},
            {'service_id': 2, 'spent_amount': 12132},
            {'service_id': 3, 'spent_amount': 53123},
        ]
    },
]

# Функция для извлечения процента кешбэка
def extract_cashback_percentage(cashback_percentage_text):
    match = re.search(r'(\d+)%', cashback_percentage_text)
    if match:
        return int(match.group(1)) / 100
    return 0

def all_cashback_services(request):
    # Количество карточек в заявке
    transaction_count = sum(len(report['transactions']) for report in monthly_cashbacks)

    # Обработка запроса поиска
    search_query = request.GET.get('cashback_categories', '')
    if search_query:
        filtered_services = [service for service in cashback_services if search_query.lower() in service['category'].lower()]
    else:
        filtered_services = cashback_services

    current_report_id = 1  # Задайте нужный отчет

    return render(request, 'index.html', {
        'data': {
            'current_date': date.today(),
            'services': filtered_services,
            'cart_item_count': transaction_count,
            'current_report_id': current_report_id,
            'search_query': search_query  # Добавлено для сохранения значения поиска
        }
    })

def cashback_details(request, id):
    service = next((service for service in cashback_services if service['id'] == id), None)
    if service is None:
        return render(request, '404.html')

    return render(request, 'cashback_details.html', {'data': service})

def monthly_cashbacks_view(request, report_id):
    transactions_with_titles = []

    # Находим отчет по идентификатору заявки
    selected_report = next((report for report in monthly_cashbacks if report['report_id'] == report_id), None)
    
    if selected_report:
        for transaction in selected_report['transactions']:
            service = next((service for service in cashback_services if service['id'] == transaction['service_id']), None)
            if service:
                cashback_percentage = extract_cashback_percentage(service['cashback_percentage_text'])
                cashback_earned = int(transaction['spent_amount'] * cashback_percentage)
                
                transactions_with_titles.append({
                    'category': service['category'],
                    'spent_amount': transaction['spent_amount'],
                    'cashback_earned': cashback_earned,
                    'image_url': service['image_url'],
                    'cashback_percentage_text': service['cashback_percentage_text'],
                    'report_id': selected_report['report_id']  
                })

    return render(request, 'monthly_cashbacks.html', {
        'data': {
            'transactions': transactions_with_titles,
            'current_month': selected_report['month'] if selected_report else 'Неизвестный месяц'
        }
    })

