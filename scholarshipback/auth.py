import jwt
from datetime import datetime, timezone, timedelta

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError
from .models import Student, Admin
from django.conf import settings


def authenticate(user) -> dict:
    access_token = jwt.encode(
        {
            'id': user.id,
            'role': 'student' if type(user) == Student else 'admin',
            'type': 'access',
            'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=720),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    refresh_token = jwt.encode(
        {
            'id': user.id,
            'role': 'student' if type(user) == Student else 'admin',
            'type': 'refresh',
            'exp': datetime.now(tz=timezone.utc) + timedelta(weeks=1)
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


class CustomAuthMiddleware(View):

    def dispatch(self, request: WSGIRequest, *args, **kwargs):
        if 'Authorization' not in request.headers:
            return JsonResponse({'detail': 'No auth credentials!'}, status=400)

        try:
            str_access_token = request.headers['Authorization'].split('Bearer ')[1]
        except IndexError:
            return JsonResponse({'detail': 'No auth credentials!'}, status=400)

        try:
            data = jwt.decode(str_access_token, settings.SECRET_KEY, [settings.ALGORITHM], {'verify_exp': True, 'verify_signature': True})

            if data['role'] == 'student':
                get_object_or_404(Student, id=data['id'])
            else:
                get_object_or_404(Admin, id=data['id'])

        except ExpiredSignatureError:
            return JsonResponse({'detail': 'Access token expired, refresh it!'}, status=401)
        except InvalidSignatureError:
            return JsonResponse({'detail': 'Invalid signature of token!'}, status=401)
        except DecodeError:
            return JsonResponse({'detail': 'Can not decode token!'}, status=401)

        response = super(CustomAuthMiddleware, self).dispatch(request, *args, **kwargs)
        return response
