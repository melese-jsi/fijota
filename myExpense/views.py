from datetime import date, timedelta
import json
from urllib.parse import parse_qsl
from django.db.models.aggregates import Avg, Count, Sum
from django.http import JsonResponse, request
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from myExpense.models import Expense, User
from myExpense.forms import ExpenseForm

# Create your views here.

def telegram_auth_page(request):

    # If the user is already authenticated,
    # don't authenticate again.

    if request.user.is_authenticated:

        return redirect("dashboard")


    return render(
        request,
        "telegram_login.html"
    )

def home(request):
    return render(request, "home.html")
@csrf_exempt
def telegram_login(request):
    
    if request.method != "POST":
        # dont Handle the login logic here
        return JsonResponse({"success": False, "error": "post request required"}, status=405)
    try:
        print("INIT DATA:", request.body)
        body = json.loads(request.body)
        print ("BODY:", body)
        init_data = body.get("init_data")
        print("INIT DATA:", init_data)
        if not init_data:
            return JsonResponse({"success": False, "error": "init_data is required"}, status=400)

        data = dict(parse_qsl(init_data))
        telegram_user = json.loads(data['user'])
        print("data:", data)
        # Process the Telegram user data as needed
        
        telegram_id = telegram_user.get("id") if telegram_user else None
        # Do something with the Telegram user data, e.g., create or update a user in your database

        user, created = User.objects.get_or_create(telegram_id=telegram_id, 
                                   defaults={"username": telegram_user.get("username"),
                                                "first_name": telegram_user.get("first_name"),
                                                "last_name": telegram_user.get("last_name"),
                                             },
                                   )
        # update user details if they already exist
        print(created)
        if not created:
            user.username = telegram_user.get("username")
            user.first_name = telegram_user.get("first_name")
            user.last_name = telegram_user.get("last_name")
            user.save()

        # create django session for the user
        login(request, user)
        return JsonResponse({"success": True, 
                             "created": created, "user": {
                                 "id": user.id, "telegram_id": user.telegram_id, "first_name": user.first_name, "last_name": user.last_name, "username": user.username
                             }})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    
@login_required
def dashboard(request):

    today = date.today()

    daily_total = Expense.objects.filter(
        user=request.user,
        expense_date=today
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    monthly_total = Expense.objects.filter(
        user=request.user,
        expense_date__year=today.year,
        expense_date__month=today.month
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    recent_expenses = Expense.objects.filter(
        user=request.user
    ).order_by("-expense_date", "-created_at")[:5]

    return render(
        request,
        "dashboard.html",
        {
            "daily_total": daily_total,
            "monthly_total": monthly_total,
            "recent_expenses": recent_expenses,
        }
    )

@login_required
def profile(request):
    print("User:", request.user)

    return render(
        request,
        "profile.html"
    )

@login_required
def expenses(request):
    print("User:", request.user)

    expenses = Expense.objects.filter(
        user=request.user
    ).order_by("-expense_date", "-created_at")

    return render(
        request,
        "expenses.html",
        {
            "expenses": expenses
        }
    )

@login_required
def add_expense(request):

    if request.method == "POST":

        form = ExpenseForm(request.POST)

        if form.is_valid():

            expense = form.save(commit=False)

            expense.user = request.user

            expense.save()

            return redirect("expenses")

    else:

        form = ExpenseForm()

    return render(
        request,
        "expense_form.html",
        {
            "form": form,
            "title": "Add Expense",
        }
    )

@login_required
def edit_expense(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user
    )

    if request.method == "POST":

        form = ExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            form.save()

            return redirect("expenses")

    else:

        form = ExpenseForm(
            instance=expense
        )

    return render(
        request,
        "expense_form.html",
        {
            "form": form,
            "title": "Edit Expense",
        }
    )

@login_required
def delete_expense(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user
    )

    if request.method == "POST":

        expense.delete()

        return redirect("expenses")

    return render(
        request,
        "expense_confirm_delete.html",
        {
            "expense": expense
        }
    )

@login_required
def daily_summary(request):

    slected_date = request.GET.get("date")
    if slected_date:
        try:
            selected_date = date.fromisoformat(slected_date)
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()


    

    daily_expenses = Expense.objects.filter(
        expense_date=selected_date,
        user=request.user
    ).order_by("-created_at")

    daily_total = daily_expenses.aggregate( 
        
        total=Sum("amount")
    )["total"] or 0

    category_totals = daily_expenses.values("category").annotate(
        total=Sum("amount")
    ).order_by("-total")

    for category_total in category_totals:
        category_total["percentage"] = (category_total['total']/daily_total) * 100 if daily_total > 0 else 0

    return render(
        request,
        "daily_summary.html",
        {
            "daily_expenses": daily_expenses,
            "selected_date": selected_date,
            "daily_total": daily_total,
            "category_totals": category_totals,
        }
    )
def monthly_summary(request):
    selected_month = request.GET.get("month")
    if selected_month:
        try:
            year, month = map(int, selected_month.split("-"))
        except (ValueError, TypeError):
            today = date.today()
            year = today.year
            month = today.month
    else:
        today = date.today()
        year = today.year
        month = today.month

    expenses = Expense.objects.filter(
        expense_date__year=year,
        expense_date__month=month,
        user=request.user
    ).order_by("-expense_date", "-created_at")

    total = expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    category_totals = expenses.values("category").annotate(
        total=Sum("amount")
    ).order_by("-total")

    return render(
        request,
        "monthly_summary.html",
        {
            "expenses": expenses,
            "year": year,
            "month": month,
            "total": total,
            "category_totals": category_totals,
            "selected_month": selected_month if selected_month else f"{year}-{month:02d}"
        }
        
    )

@login_required
def reports(request):

    user = request.user

    today = date.today()

    period = request.GET.get(
        "period",
        "month"
    )


    # --------------------------------------------------
    # DETERMINE DATE RANGE
    # --------------------------------------------------

    if period == "today":

        start_date = today
        end_date = today


    elif period == "week":

        # Monday = beginning of week
        start_date = (
            today - timedelta(
                days=today.weekday()
            )
        )

        end_date = today


    elif period == "month":

        start_date = today.replace(
            day=1
        )

        end_date = today


    elif period == "custom":

        start_date_string = request.GET.get(
            "start_date"
        )

        end_date_string = request.GET.get(
            "end_date"
        )


        try:

            start_date = date.fromisoformat(
                start_date_string
            )

            end_date = date.fromisoformat(
                end_date_string
            )

        except (
            ValueError,
            TypeError
        ):

            # Fall back to current month

            period = "month"

            start_date = today.replace(
                day=1
            )

            end_date = today


    else:

        period = "month"

        start_date = today.replace(
            day=1
        )

        end_date = today


    # --------------------------------------------------
    # CURRENT USER'S EXPENSES
    # --------------------------------------------------

    expenses = Expense.objects.filter(

        user=request.user,

        expense_date__range=(
            start_date,
            end_date
        )

    )


    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    summary = expenses.aggregate(

        total=Sum("amount"),

        count=Count("id"),

        average=Avg("amount")

    )


    total = summary["total"] or 0

    transaction_count = (
        summary["count"] or 0
    )

    average_expense = (
        summary["average"] or 0
    )


    # --------------------------------------------------
    # DAILY SPENDING
    # --------------------------------------------------

    daily_spending = (

        expenses

        .values("expense_date")

        .annotate(
            total=Sum("amount")
        )

        .order_by("expense_date")

    )


    daily_labels = []

    daily_values = []


    for item in daily_spending:

        daily_labels.append(
            item["expense_date"].strftime(
                "%b %d"
            )
        )

        daily_values.append(
            float(item["total"])
        )


    # --------------------------------------------------
    # CATEGORY SPENDING
    # --------------------------------------------------

    category_spending = (

        expenses

        .values("category")

        .annotate(

            total=Sum("amount"),

            count=Count("id")

        )

        .order_by("-total")

    )


    category_choices = dict(
        Expense.Category.choices
    )


    for item in category_spending:

        item["category_name"] = (
            category_choices.get(
                item["category"],
                item["category"]
            )
        )


    # --------------------------------------------------
    # CONTEXT
    # --------------------------------------------------

    context = {

        "period": period,

        "start_date": start_date,

        "end_date": end_date,

        "total": total,

        "transaction_count":
            transaction_count,

        "average_expense":
            average_expense,

        "daily_labels":
            daily_labels,

        "daily_values":
            daily_values,

        "category_spending":
            category_spending,

    }


    return render(
        request,
        "reports.html",
        context
    )