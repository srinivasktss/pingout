from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import UserRegisterForm, AuthenticationForm
from django.views import View
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class RegisterView(View):
    form_class = UserRegisterForm
    initial_data = {}
    template_name = 'users/register.html'

    def get(self, request):
        form = self.form_class(initial=self.initial_data)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("users:login")
        return render(request, self.template_name, {'form': form})

class LoginView(View):

    form_class = AuthenticationForm
    initial_data = {}
    template_name = 'users/login.html'
    home_template_name = 'users/home.html'

    def get(self, request):
        form = self.form_class(initial=self.initial_data)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have logged in successfully.")
            return redirect("users:home")
        return render(request, self.template_name, {'form': form})
    

class HomeView(View):
    template_name = 'users/home.html'
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, self.template_name)
    
class LogoutView(View):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        messages.success(request, "You have logged out successfully.")
        return redirect("users:login")