from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import UserRegisterForm, AuthenticationForm
from django.views import View
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView as ApiView
from rest_framework import status

# Models
from .models import User

# Serializers
from .serializers import UserSearchSerializer

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
    

class UserSearchView(ApiView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query_params = request.query_params
        search_query = query_params.get('q', '')
        if search_query:
            users = User.objects.filter(
                username__icontains=search_query
            ).exclude(
                id=request.user.id
            )
        else:
            users = User.objects.none()

        serializer = UserSearchSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        