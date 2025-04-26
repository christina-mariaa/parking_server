from rest_framework import serializers
from .models import SupportRequest, SupportReply


class SupportReplySerializer(serializers.ModelSerializer):
    """
    Сериализатор для ответа администратора.
    """
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    admin_last_name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = SupportReply
        fields = ['id', 'admin_email', 'admin_last_name', 'message', 'created_at']
        read_only_fields = ['id', 'admin_email', 'admin_last_name', 'created_at']


class SupportRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения обращения пользователя в техподдержку
    вместе с вложенными ответами администратора, и создания обращения.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    replies = SupportReplySerializer(many=True, read_only=True)

    class Meta:
        model = SupportRequest
        fields = ['id', 'user_email', 'user_first_name', 'user_last_name',
                  'subject', 'message', 'status', 'created_at', 'replies']
        read_only_fields = ['id', 'user_email', 'user_first_name', 'user_last_name',
                            'status' 'created_at', 'replies']
