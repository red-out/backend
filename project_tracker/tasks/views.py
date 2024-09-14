from django.shortcuts import render, redirect
from datetime import date

def hello(request):
   
    orders = [
        {
            'id': 1,
            'title': 'Образование',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-books-4645290.png',
            'alt': 'Образование',
            'details_text': ' Вы получите от 13 до 500 рублей',
        },
        {
            'id': 2,
            'title': 'Кафе и рестораны',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-restaurant-1689246.png',
            'alt': 'Кафе и рестораны',
            'details_text': ' Вы получите от 1,33% до 6,7%',
        },
        {
            'id': 3,
            'title': 'Спортивные товары',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-basketball-4645268.png',
            'alt': 'Спортивные товары',
            'details_text': ' Вы получите от 0,31% до 6,92%',
        },
        {
            'id': 4,
            'title': 'Аптеки',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-online-pharmacy-4435601.png',
            'alt': 'Аптеки',
            'details_text': 'Вы получите от 0,75% до 1,13%',
        },
    ]
    
    # Обработка запроса поиска
    search_query = request.GET.get('search', '')

    if search_query:
        orders = [order for order in orders if search_query.lower() in order['title'].lower()]

    return render(request, 'index.html', {'data': {
        'current_date': date.today(),
        'orders': orders,
    }})


def GetOrder(request, id):
    # Данные для страницы с информацией о товаре
    orders = [
        {
            'id': 1,
            'title': 'Образование',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-books-4645290.png',
            'description': 'Оплата образовательных услуг.',
            'price': 'Подписка на телеграмм.',
            'quantity': '5213 шт.',
        },
        {
            'id': 2,
            'title': 'Кафе и рестораны',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-restaurant-1689246.png',
            'description': 'Популярный бренд одежды.',
            'price': 'Подписка на вконтакте.',
            'quantity': '1230 шт.',
        },
        {
            'id': 3,
            'title': 'Спортивные товары',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-basketball-4645268.png',
            'description': 'Покупки в спортивных магазинах',
            'price': 'Регистрация на сайте Алиэкспресса.',
            'quantity': '7321 шт.',
        },
        {
            'id': 4,
            'title': 'Аптеки',
            'image_url': 'http://127.0.0.1:9000/web/free-icon-online-pharmacy-4435601.png',
            'description': 'Оплата в аптеках и профильных магазинах медикаментов',
            'price': 'Купить 3 товара на Авито.',
            'quantity': '8321 шт.',
        },
    ]
    
    # Найти товар по id
    item = next((order for order in orders if order['id'] == id), None)
    
    if item is None:
        return render(request, '404.html')  # Страница 404, если товар не найден

    return render(request, 'order.html', {'data': item})

def cart(request):
    # Страница корзины с элементами, сохраненными в сессии
    cart_items = request.session.get('cart', [])
    return render(request, 'cart.html', {'data': {
        'cart_items': cart_items
    }})

def add_to_cart(request, id):
    cart = request.session.get('cart', [])
    # Проверьте, чтобы не было дубликатов в корзине
    if not any(item['id'] == id for item in cart):
        cart.append({'id': id, 'title': f'Кэшбэк {id}'})
        request.session['cart'] = cart
    return redirect('cart')

def clear_cart(request):
    # Очистка корзины
    request.session.pop('cart', None)
    return redirect('cart')
