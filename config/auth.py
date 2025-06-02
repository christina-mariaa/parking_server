from django.http import JsonResponse


def lockout_response(request, credentials, *args, **kwargs):
    return JsonResponse(
        {'error': 'Аккаунт временно заблокирован из-за слишком большого количества неудачных попыток входа. Повторите позже.'},
        status=403
    )
