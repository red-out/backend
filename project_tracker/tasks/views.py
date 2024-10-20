from django.db import connection  # Добавляем импорт connection
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import date
from .models import CashbackService, CashbackOrder, CashbackOrderService
import re

def all_cashback_services(request):
    if request.user.is_authenticated:
        # Получаем активную заявку (черновик) сразу через фильтрацию
        active_order = CashbackOrder.objects.filter(creator=request.user, status='draft').order_by('-id').first()

        # Если активной заявки нет, создаем новую
        if not active_order:
            active_order = CashbackOrder.objects.create(
                creator=request.user,
                status='draft',
                month=date.today().strftime("%B")
            )
            print(f'Создана новая активная заявка: {active_order.id}')

        transaction_count = CashbackOrderService.objects.filter(order=active_order).count() if active_order else 0
        current_report_id = active_order.id if active_order else None
    else:
        transaction_count = 0
        current_report_id = None

    search_query = request.GET.get('cashback_categories', '')
    if search_query:
        filtered_services = CashbackService.objects.filter(category__icontains=search_query, status='active')
    else:
        filtered_services = CashbackService.objects.filter(status='active')

    return render(request, 'index.html', {
        'data': {
            'current_date': date.today(),
            'services': filtered_services,
            'cart_item_count': transaction_count,
            'current_report_id': current_report_id,
            'search_query': search_query
        },
        'user_authenticated': request.user.is_authenticated
    })

def cashback_details(request, id):
    service = get_object_or_404(CashbackService, id=id)

    if request.user.is_authenticated:
        # Получаем активную заявку (черновик) сразу через фильтрацию
        order = CashbackOrder.objects.filter(creator=request.user, status='draft').first()

        # Если активной заявки нет, создаем новую
        if not order:
            order = CashbackOrder.objects.create(
                creator=request.user,
                status='draft',
                month=date.today().strftime("%B")
            )

    return render(request, 'cashback_details.html', {'data': service})

def add_cashback(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))  # Перенаправляем неавторизованного пользователя на главную

    if request.method == 'POST':
        # Получаем активную заявку (черновик) сразу через фильтрацию
        active_order = CashbackOrder.objects.filter(creator=request.user, status='draft').first()

        # Если активной заявки нет, создаем новую
        if not active_order:
            active_order = CashbackOrder.objects.create(
                creator=request.user,
                status='draft',
                month=date.today().strftime("%B")
            )
            print(f'Создана новая активная заявка: {active_order.id}')

        print(f'Текущая активная заявка: {active_order.id}')

        # Получаем кешбэк по ID
        cashback_service = get_object_or_404(CashbackService, id=id)
        print(f'Пытаемся добавить кешбэк: {cashback_service.category} (ID: {cashback_service.id})')

        # Проверяем, существует ли уже услуга в текущем заказе
        if CashbackOrderService.objects.filter(order=active_order, service=cashback_service).exists():
            print(f'Эта услуга уже добавлена в заявку: {cashback_service.category} (ID: {cashback_service.id})')
            return HttpResponseRedirect(reverse('home'))

        # Добавляем кешбэк в заявку
        cashback_order_service = CashbackOrderService.objects.create(
            order=active_order,
            service=cashback_service,
            total_spent=77777  # Здесь можно установить реальную сумму, если она известна
        )
        print(f'Кешбэк добавлен: {cashback_order_service.service.category} в заказ: {active_order.id}')

    return HttpResponseRedirect(reverse('home'))

def monthly_cashbacks_view(request, report_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    selected_report = get_object_or_404(CashbackOrder, id=report_id, creator=request.user)

    if selected_report.status == 'deleted':
        return HttpResponse("Кешбэки за этот месяц были удалены")

    transactions_with_titles = []
    
    for transaction in CashbackOrderService.objects.filter(order=selected_report):
        cashback_received = extract_cashback_percentage(transaction.service.cashback_percentage_text) * transaction.total_spent
        
        transactions_with_titles.append({
            'title': transaction.service.category,
            'category': transaction.service.category,
            'spent': transaction.total_spent,
            'cashback_received': round(cashback_received),
            'image_url': transaction.service.image_url,
            'details_text': transaction.service.cashback_percentage_text,
            'cashback_percentage_text': transaction.service.cashback_percentage_text,
            'report_id': selected_report.id  
        })

    total_spent_month = selected_report.total_spent_month if selected_report.status == 'completed' else None

    return render(request, 'monthly_cashbacks.html', {
        'data': {
            'categories_cashbacks': transactions_with_titles,
            'current_month': selected_report.month,
            'current_order_id': report_id,
            'total_spent_month': total_spent_month
        }
    })

def delete_cashback_order(request, report_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        # Используем курсор для обновления статуса заявки
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE tasks_cashbackorder SET status = 'deleted' WHERE id = %s AND creator_id = %s",
                [report_id, request.user.id]
            )

        return HttpResponseRedirect(reverse('home'))

def extract_cashback_percentage(cashback_percentage_text):
    match = re.search(r'(\d+)%', cashback_percentage_text)
    if match:
        return int(match.group(1)) / 100
    return 0

# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponseRedirect, HttpResponse
# from django.urls import reverse
# from datetime import date
# from .models import CashbackService, CashbackOrder, CashbackOrderService
# import re

# def all_cashback_services(request):
#     if request.user.is_authenticated:
#         # Получаем активную заявку (черновик)
#         active_order = CashbackOrder.objects.filter(creator=request.user).order_by('-id').first()

#         # Если текущая заявка завершена или удалена, сбрасываем активную заявку
#         if active_order and active_order.status in ['completed', 'deleted']:
#             active_order = None

#         # Если активной заявки нет, создаем новую
#         if not active_order:
#             active_order = CashbackOrder.objects.create(
#                 creator=request.user,
#                 status='draft',
#                 month=date.today().strftime("%B")
#             )
#             print(f'Создана новая активная заявка: {active_order.id}')

#         transaction_count = CashbackOrderService.objects.filter(order=active_order).count() if active_order else 0
#         current_report_id = active_order.id if active_order else None
#     else:
#         transaction_count = 0
#         current_report_id = None

#     search_query = request.GET.get('cashback_categories', '')
#     if search_query:
#         filtered_services = CashbackService.objects.filter(category__icontains=search_query, status='active')
#     else:
#         filtered_services = CashbackService.objects.filter(status='active')

#     return render(request, 'index.html', {
#         'data': {
#             'current_date': date.today(),
#             'services': filtered_services,
#             'cart_item_count': transaction_count,
#             'current_report_id': current_report_id,
#             'search_query': search_query
#         },
#         'user_authenticated': request.user.is_authenticated
#     })

# def cashback_details(request, id):
#     service = get_object_or_404(CashbackService, id=id)

#     if request.user.is_authenticated:
#         order = CashbackOrder.objects.filter(
#             creator=request.user,
#             status='draft'
#         ).first()

#         if not order:
#             order = CashbackOrder.objects.create(
#                 creator=request.user,
#                 status='draft',
#                 month=date.today().strftime("%B")
#             )

#     return render(request, 'cashback_details.html', {'data': service})

# def add_cashback(request, id):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse('home'))  # Перенаправляем неавторизованного пользователя на главную

#     if request.method == 'POST':
#         # Получаем активную заявку (черновик)
#         active_order = CashbackOrder.objects.filter(creator=request.user, status='draft').first()

#         # Если активной заявки нет, создаем новую
#         if not active_order:
#             active_order = CashbackOrder.objects.create(
#                 creator=request.user,
#                 status='draft',
#                 month=date.today().strftime("%B")
#             )
#             print(f'Создана новая активная заявка: {active_order.id}')

#         print(f'Текущая активная заявка: {active_order.id}')

#         # Получаем кешбэк по ID
#         cashback_service = get_object_or_404(CashbackService, id=id)
#         print(f'Пытаемся добавить кешбэк: {cashback_service.category} (ID: {cashback_service.id})')

#         # Проверяем, существует ли уже услуга в текущем заказе
#         if CashbackOrderService.objects.filter(order=active_order, service=cashback_service).exists():
#             print(f'Эта услуга уже добавлена в заявку: {cashback_service.category} (ID: {cashback_service.id})')
#             return HttpResponseRedirect(reverse('home'))

#         # Добавляем кешбэк в заявку
#         cashback_order_service = CashbackOrderService.objects.create(
#             order=active_order,
#             service=cashback_service,
#             total_spent=77777  # Здесь можно установить реальную сумму, если она известна
#         )
#         print(f'Кешбэк добавлен: {cashback_order_service.service.category} в заказ: {active_order.id}')

#     return HttpResponseRedirect(reverse('home'))

# def monthly_cashbacks_view(request, report_id):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse('home'))

#     selected_report = get_object_or_404(CashbackOrder, id=report_id, creator=request.user)

#     if selected_report.status == 'deleted':
#         return HttpResponse("Кешбэки за этот месяц были удалены")

#     transactions_with_titles = []
    
#     for transaction in CashbackOrderService.objects.filter(order=selected_report):
#         cashback_received = extract_cashback_percentage(transaction.service.cashback_percentage_text) * transaction.total_spent
        
#         transactions_with_titles.append({
#             'title': transaction.service.category,
#             'category': transaction.service.category,
#             'spent': transaction.total_spent,
#             'cashback_received': round(cashback_received),
#             'image_url': transaction.service.image_url,
#             'details_text': transaction.service.cashback_percentage_text,
#             'cashback_percentage_text': transaction.service.cashback_percentage_text,
#             'report_id': selected_report.id  
#         })

#     total_spent_month = selected_report.total_spent_month if selected_report.status == 'completed' else None

#     return render(request, 'monthly_cashbacks.html', {
#         'data': {
#             'categories_cashbacks': transactions_with_titles,
#             'current_month': selected_report.month,
#             'current_order_id': report_id,
#             'total_spent_month': total_spent_month
#         }
#     })

# def delete_cashback_order(request, report_id):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse('home'))

#     if request.method == 'POST':
#         CashbackOrder.objects.filter(id=report_id, creator=request.user).update(status='deleted')
#         CashbackOrderService.objects.filter(order_id=report_id).delete()

#         return HttpResponseRedirect(reverse('home'))

# def extract_cashback_percentage(cashback_percentage_text):
#     match = re.search(r'(\d+)%', cashback_percentage_text)
#     if match:
#         return int(match.group(1)) / 100
#     return 0

