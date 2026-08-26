from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    photo_url = models.URLField(blank=True)

class Expense(models.Model):

    class Category(models.TextChoices):

        FOOD = "food", "🍔 Food"
        TRANSPORT = "transport", "🚕 Transport"
        HOUSING = "housing", "🏠 Housing"
        UTILITIES = "utilities", "💡 Utilities"
        SHOPPING = "shopping", "🛒 Shopping"
        HEALTH = "health", "💊 Health"
        EDUCATION = "education", "🎓 Education"
        ENTERTAINMENT = "entertainment", "🎉 Entertainment"
        OTHER = "other", "📦 Other"


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    description = models.CharField(
        max_length=255
    )

    expense_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )

    def __str__(self):
        return f"{self.description} - {self.amount}"

