from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import json
import datetime


class UsersApi:
    @staticmethod
    def get(request):
        # my user works here, should get it from db
        user_data = {
            "profile_fields": {
                "useGravatar": True,
                "notify": True
            },
            "id": 153565,
            "username": "5299729",
            "first": "Christopher",
            "last": "Solanilla",
            "email": "ch862076@ucf.edu",
            "group": 1,
            "last_login": 1733146261,
            "created_at": 1717441736,
            "updated_at": 1717441736,
            "avatar": "https://secure.gravatar.com/avatar/36ad3cc772e5967214841b49ee6b57f8?s=256&d=retro",
            "is_student": False,
            "is_support_user": False
        }
        return JsonResponse(user_data)
        # try:
        #     user = User.objects.get(id=user_id)
        #     settings = user.settings.profile_fields
        #     user_data = {
        #         "id": user.id,
        #         "username": user.username,
        #         "first": user.first_name,
        #         "last": user.last_name,
        #         "email": user.email,
        #         "profile_fields": settings,
        #     }
        #     return JsonResponse(user_data)
        # except User.DoesNotExist:
        #     return JsonResponse({"error": "User not found"}, status=404)

    @staticmethod
    def activity(request):
        # some dummy data, should get it from db somehow.
        activity_data = {
            "activity": [
                {
                    "play_id": 12345,
                    "created_at": int(datetime.datetime.now().timestamp()),
                    "score": "100.0",
                    "percent": 100,
                    "is_complete": "1",
                    "inst_id": 6789,
                    "widget_name": "Associations",
                    "inst_name": "Associations is the best widget",
                },
            ],
            "more": False,
        }
        return JsonResponse(activity_data)


    def service_user_login(request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                username = data.get("username")
                password = data.get("password")

                user = authenticate(username=username, password=password)
                if user is not None:
                    return JsonResponse({"isAuthenticated": True}, status=200)
                else:
                    return JsonResponse({"isAuthenticated": False}, status=401)

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

            return JsonResponse({"error": "Invalid request method"}, status=405)
