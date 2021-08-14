from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.utils import get_yandex_data


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def update_now(request):
    get_yandex_data()
    return Response()
