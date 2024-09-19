from django.shortcuts import render
from datetime import date

# Вынесенная коллекция заказов
def get_cashbacks():
    return [
        {
            'id': 1,
            'title': 'Образование',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-books-4645290.png',
            'details_text': 'Вы получите 7% кешбэка',
            'full_description': 'Оплата образовательных программ и курсов.',
            'price': 'Кешбэк за оплату обучения в аккредитованных учебных заведениях, онлайн-курсах и платформах для повышения квалификации.',
        },
        {
            'id': 2,
            'title': 'Кафе и рестораны',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-restaurant-1689246.png',
            'details_text': 'Вы получите 5% кешбэка',
            'full_description': 'Оплата в заведениях общественного питания.',
            'price': 'Кешбэк за покупки в ресторанах, кафе, барах и сетях быстрого питания, включая доставку еды.',
        },
        {
            'id': 3,
            'title': 'Спортивные товары',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-basketball-4645268.png',
            'details_text': 'Вы получите 5% кешбэка',
            'full_description': 'Покупки спортивного инвентаря и экипировки.',
            'price': 'Кешбэк за приобретение спортивных товаров, одежды, инвентаря и оборудования в специализированных магазинах и онлайн-платформах.',
        },
        {
            'id': 4,
            'title': 'Аптеки',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-online-pharmacy-4435601.png',
            'details_text': 'Вы получите 10% кешбэка',
            'full_description': 'Покупка медикаментов и товаров для здоровья.',
            'price': 'Кешбэк за оплату в аптеках, профильных магазинах товаров для здоровья и онлайн-аптеках.',
        },
       {
            'id': 5,
            'title': 'Туризм',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-hiking-1974052.png',
            'details_text': 'Вы получите 7% кешбэка',
            'full_description': 'Оплата туристических услуг, включая бронирование отелей и билетов.',
            'price': 'Кешбэк за услуги в туристических агентствах, онлайн-сервисах для путешествий и при бронировании экскурсионных туров.'
},
{
            'id': 6,
            'title': 'Электроника',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-electronics-1692714.png',
            'details_text': 'Вы получите 5% кешбэка',
            'full_description': 'Покупка техники и электроники.',
            'price': 'Кешбэк за приобретение смартфонов, компьютеров, телевизоров и других гаджетов в магазинах и онлайн-платформах.'
}

    ]

# Пример данных для корзины
categories_cashbacks = [
    {
        'order_id': 1,  # Ссылается на идентификатор заказа
        'spent': {'amount': 35435, 'range': 'Сентябрь'},
        'cashback_received': 2480,
        'image_url': 'http://127.0.0.1:9000/web/free-icon-books-4645290.png',
        'details_text': '7% кешбэка по данной категории'
    },
    {
        'order_id': 2,  # Ссылается на идентификатор заказа
        'spent': {'amount': 17342, 'range': 'Сентябрь'},
        'cashback_received': 867,
        'image_url': 'http://127.0.0.1:9000/web/free-icon-restaurant-1689246.png',
        'details_text': '5% кешбэка по данной категории'
    },
    {
        'order_id': 5,  # Ссылается на идентификатор заказа
        'spent': {'amount': 9983, 'range': 'Сентябрь'},
        'cashback_received': 699,
        'image_url': 'http://127.0.0.1:9000/web/free-icon-hiking-1974052.png',
        'details_text': '7% кешбэка по данной категории'
    },
]

def cashback_services(request):
    cashbacks = get_cashbacks()
    item_count = len(categories_cashbacks)  # Количество карточек в корзине

    # Обработка запроса поиска
    search_query = request.GET.get('search', '')
    if search_query:
        cashbacks = [order for order in cashbacks if search_query.lower() in order['title'].lower()]

    return render(request, 'index.html', {
        'data': {
            'current_date': date.today(),
            'cashbacks': cashbacks,
            'cart_item_count': item_count  # Передаем количество карточек в корзине
        }
    })

def GetOrder(request, id):
    cashbacks = get_cashbacks()

    # Найти товар по id
    item = next((order for order in cashbacks if order['id'] == id), None)
    if item is None:
        return render(request, '404.html')  # Страница 404, если товар не найден

    return render(request, 'order.html', {'data': item})

def categories_cashbacks_view(request):
    cashbacks = get_cashbacks()
    cart_items_with_titles = []

    for item in categories_cashbacks:
        order = next((order for order in cashbacks if order['id'] == item['order_id']), None)
        if order:
            item['title'] = order['title']
        cart_items_with_titles.append(item)

    return render(request, 'cashbacks.html', {
        'data': {
            'categories_cashbacks': cart_items_with_titles,
            'current_month': 'Сентябрь'  # или динамически определяемый месяц
        }
    })



