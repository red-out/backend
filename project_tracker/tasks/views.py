from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import date
from .models import CashbackService, CashbackOrder, CashbackOrderService
import random
import re
from django.db import connection


def all_cashback_services(request):
    # Получаем активную заявку (черновик или завершённую)
    active_order = CashbackOrder.objects.filter(creator=request.user).order_by('-id').first()
    
    # Если текущая заявка завершена или удалена, не показываем её
    if active_order and active_order.status in ['completed', 'deleted']:
        active_order = None  # Сбрасываем активную заявку

    # Если активной заявки нет, создаем новую
    if not active_order:
        active_order = CashbackOrder.objects.create(
            creator=request.user,
            status='draft',
            month=date.today().strftime("%B")
        )

    # Количество карточек в текущей заявке
    transaction_count = CashbackOrderService.objects.filter(order=active_order).count() if active_order else 0

    # Обработка запроса поиска
    search_query = request.GET.get('cashback_categories', '')
    if search_query:
        filtered_services = CashbackService.objects.filter(category__icontains=search_query, status='active')
    else:
        filtered_services = CashbackService.objects.filter(status='active')

    current_report_id = active_order.id if active_order else None  # Получаем ID активной заявки, если она существует

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

    # Получаем черновик для текущего пользователя или создаем новый, если его нет
    order = CashbackOrder.objects.filter(
        creator=request.user,
        status='draft'
    ).first()

    if not order:
        order = CashbackOrder.objects.create(
            creator=request.user,
            status='draft',
            month=date.today().strftime("%B")  # Пример месяца
        )

    return render(request, 'cashback_details.html', {'data': service})


def add_cashback(request, id):
    if request.method == 'POST':
        # Получаем активную заявку (черновик)
        active_order = CashbackOrder.objects.filter(creator=request.user, status='draft').first()
        
        if not active_order:
            return HttpResponseRedirect(reverse('home'))  # Не добавляем кешбэк, если активной заявки нет

        # Получаем кешбэк по ID
        cashback_service = get_object_or_404(CashbackService, id=id)

        # Проверяем, существует ли уже услуга в текущем заказе
        if CashbackOrderService.objects.filter(order=active_order, service=cashback_service).exists():
            return HttpResponseRedirect(reverse('home'))  # Возвращаем редирект, если кешбэк уже добавлен

        # Добавляем кешбэк в заявку
        CashbackOrderService.objects.create(
            order=active_order,
            service=cashback_service,
            total_spent=77777  # Здесь можно установить реальную сумму, если она известна
        )

    return HttpResponseRedirect(reverse('home'))


def monthly_cashbacks_view(request, report_id):
    # Пытаемся получить заявку по ID
    selected_report = get_object_or_404(CashbackOrder, id=report_id, creator=request.user)

    # Проверяем статус заявки
    if selected_report.status == 'deleted':
        return HttpResponse("Кешбэки за этот месяц были удалены")  # Возвращаем сообщение, если заявка удалена

    transactions_with_titles = []
    
    for transaction in CashbackOrderService.objects.filter(order=selected_report):
        cashback_received = extract_cashback_percentage(transaction.service.cashback_percentage_text) * transaction.total_spent
        
        transactions_with_titles.append({
            'title': transaction.service.category,
            'category': transaction.service.category,
            'spent': transaction.total_spent,
            'cashback_received': round(cashback_received),  # Округляем до целого числа
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
            'current_order_id': report_id,  # Передаем ID заявки для удаления
            'total_spent_month': total_spent_month  # Добавляем в контекст общую сумму
        }
    })


def delete_cashback_order(request, report_id):
    if request.method == 'POST':
        # Удаляем заявку и её услуги
        with connection.cursor() as cursor:
            cursor.execute("UPDATE tasks_cashbackorder SET status = 'deleted' WHERE id = %s AND creator_id = %s", [report_id, request.user.id])
        
        # Удаляем все услуги, связанные с данной заявкой
        CashbackOrderService.objects.filter(order_id=report_id).delete()

        return HttpResponseRedirect(reverse('home'))   # Перенаправление на главную страницу


def extract_cashback_percentage(cashback_percentage_text):
    match = re.search(r'(\d+)%', cashback_percentage_text)
    if match:
        return int(match.group(1)) / 100
    return 0

