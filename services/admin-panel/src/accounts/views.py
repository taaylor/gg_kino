# from pprint import pprint as pp

from accounts.models import User
from django.http import HttpResponse


def experiment_view(request):
    user = User.objects.first()
    if user:
        return HttpResponse(f"{user.username} {user.user_cred.email}")
    return HttpResponse("Empty result")
