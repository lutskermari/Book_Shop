from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse

# Create your views here.
 
def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('index'))
    else:
        form = UserCreationForm()
        
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('index'))
    else:
        form = AuthenticationForm()
        
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(reverse('index'))