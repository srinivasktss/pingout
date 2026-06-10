from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import UserRegisterForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("users:register")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})
