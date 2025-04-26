from django.db import models
from api.models import CustomUser


class SupportRequest(models.Model):
    """
    Модель обращения в техническую поддержку.

    Атрибуты:
        user (ForeignKey): Пользователь, создавший обращение;
        subject (CharField): Тема обращения (краткое описание проблемы);
        message (TextField): Подробное сообщение от пользователя;
        status (CharField): Текущий статус обращения (открыто, в работе, закрыто);
        created_at (DateTimeField): Дата и время создания обращения.
    """
    STATUS_CHOICES = [
        ('open', 'Открыто'),
        ('in_progress', 'В работе'),
        ('closed', 'Закрыто'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='support_requests')
    subject = models.CharField(max_length=255)
    message = models.TextField(verbose_name="Сообщение")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)


class SupportReply(models.Model):
    """
    Модель ответа администратора на обращение в поддержку.

    Атрибуты:
        support_request (ForeignKey): Обращение, на которое дан ответ;
        admin (ForeignKey): Администратор, написавший ответ;
        message (TextField): Текст ответа администратора;
        created_at (DateTimeField): Дата и время отправки ответа.
    """
    support_request = models.ForeignKey(SupportRequest, on_delete=models.CASCADE, related_name='replies')
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
