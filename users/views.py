from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import UserRegisterForm, AuthenticationForm
from django.views import View
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

# Models
from .models import User

# Serializers
from .serializers import UserSearchSerializer

class RegisterView(APIView):
    form_class = UserRegisterForm
    initial_data = {}
    template_name = 'users/register.html'

    def get(self, request):
        form = self.form_class(initial=self.initial_data)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        data = request.data
        
        form = self.form_class(data)

        if not form.is_valid():
            first_field = next(iter(form.errors))
            first_error = form.errors[first_field][0]
            return JsonResponse({'details': first_error}, status=status.HTTP_400_BAD_REQUEST)
        
        user = form.save()

        login(request, user)

        return JsonResponse({'detail': 'Registration successful'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):

    form_class = AuthenticationForm
    initial_data = {}
    template_name = 'users/login.html'
    home_template_name = 'users/home.html'

    def get(self, request):
        form = self.form_class(initial=self.initial_data)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        data = request.data
        form = self.form_class(request, data=data)
        if not form.is_valid():
            first_field = next(iter(form.errors))
            first_error = form.errors[first_field][0]
            return JsonResponse({'detail': first_error}, status=status.HTTP_400_BAD_REQUEST)
        
        user = form.get_user()
        login(request, user)
        
        return JsonResponse({'detail': 'Login successful'}, status=status.HTTP_200_OK)
    

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
    

class UserSearchView(APIView):
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
        