from django.http import HttpRequest
from rest_framework.permissions import BasePermission


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request: HttpRequest, _):
        return bool(
            request.method == 'GET' or
            request.user and
            request.user.is_superuser
        )


class IsSuperUser(BasePermission):
    def has_permission(self, request: HttpRequest, _):
        return bool(
            request.user and
            request.user.is_superuser
        )
