from rest_framework.permissions import BasePermission

class IsAdminPermission(BasePermission):
    """
    Разрешение только для пользователей с флагом is_staff == True.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
