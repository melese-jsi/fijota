

from django.urls import path
from . import views

from myExpense import views

urlpatterns = [
   
    path(
        "",
        views.telegram_auth_page,
        name="telegram_auth"
    ),
    # path ("expenses/", views.home, name="expense"),
    path("telegram_login/", views.telegram_login, name="telegram_login"),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),
       path(
        "profile/",
        views.profile,
        name="profile"
    ),
     # Expenses

    path(
        "expenses/",
        views.expenses,
        name="expenses"
    ),

    path(
        "expenses/add/",
        views.add_expense,
        name="add_expense"
    ),

    path(
        "expenses/<int:expense_id>/edit/",
        views.edit_expense,
        name="edit_expense"
    ),

    path(
        "expenses/<int:expense_id>/delete/",
        views.delete_expense,
        name="delete_expense"
    ),

    path(
    "daily-summary/",
    views.daily_summary,
    name="daily_summary"
    ),
    path(
    "monthly-summary/", views.monthly_summary, name="monthly_summary"
    ),
     path(
        "reports/",
        views.reports,
        name="reports"
    ),

]