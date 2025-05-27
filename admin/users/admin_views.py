import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from users.models import UserWallet


@login_required
def update_wallet_stats_view(request, wallet_id):
    if request.method == "POST":
        if not wallet_id:
            return JsonResponse({"error": "Wallet_id is required"}, status=400)

        try:
            return JsonResponse({"status": "ok", "task_id": "123"})
            # Тут был вызов селери-задача \ TODO: изменить на вызов метода с бека
            # return JsonResponse({'status': 'ok', 'task_id': task.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@login_required
def toggle_wallet_status(request, wallet_id):
    if request.method == "POST":
        # Получаем данные из JSON тела запроса
        data = json.loads(request.body)
        action = data.get("action")  # Извлекаем тип действия

        if not action:
            return JsonResponse({"error": "Action is required"}, status=400)

        try:
            # Получаем объект кошелька
            user_wallet, created = UserWallet.objects.get_or_create(
                user=request.user, wallet_id=wallet_id
            )
            # Переключаем статусы в зависимости от действия
            if action == "favorite":
                user_wallet.is_favorite = not user_wallet.is_favorite
                user_wallet.is_blacklisted = False
                user_wallet.is_watch_later = False
            elif action == "blacklist":
                user_wallet.is_blacklisted = not user_wallet.is_blacklisted
                user_wallet.is_favorite = False
                user_wallet.is_watch_later = False
            elif action == "watch_later":
                user_wallet.is_watch_later = not user_wallet.is_watch_later
                user_wallet.is_favorite = False
                user_wallet.is_blacklisted = False
            else:
                return JsonResponse({"error": "Invalid action"}, status=400)

            user_wallet.save()

            # Возвращаем все статусы для обновления UI
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Кошелек обновлен.",
                    "is_favorite": user_wallet.is_favorite,
                    "is_blacklisted": user_wallet.is_blacklisted,
                    "is_watch_later": user_wallet.is_watch_later,
                }
            )

        except UserWallet.DoesNotExist:
            return JsonResponse({"error": "Wallet not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def update_remark(request, wallet_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            remark = data.get("remark")
            user = request.user
            # Здесь предполагаем, что есть модель Wallet, в которой сохраняется описание
            wallet, created = UserWallet.objects.update_or_create(
                user=user,
                wallet_id=wallet_id,
                defaults={"remark": remark},  # Параметры для обновления
            )
            return JsonResponse(
                {"status": "success", "message": "Описание успешно сохранено!"}
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Неверный формат данных"}
            )
