from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ExpenseForm
from .models import Expense
from datetime import date
from django.db.models import Sum

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user)
            return redirect("dashboard")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user, date__month=date.today().month)
    total = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
    by_category = expenses.values("category").annotate(total=Sum("amount"))
    return render(request, "dashboard.html", {"expenses": expenses, "total": total, "by_category": by_category})

@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            return redirect("dashboard")
    else:
        form = ExpenseForm()
    return render(request, "expense_form.html", {"form": form})

@login_required
def edit_expense(request, pk):
    exp = Expense.objects.get(id=pk, user=request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ExpenseForm(instance=exp)
    return render(request, "expense_form.html", {"form": form})

@login_required
def delete_expense(request, pk):
    Expense.objects.filter(id=pk, user=request.user).delete()
    return redirect("dashboard")