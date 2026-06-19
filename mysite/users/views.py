from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, CustomUserCreationForm

# Create your views here.
 
def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            regular_group = Group.objects.get(name="Regular Users")
            user.groups.add(regular_group) 

            login(request, user, backend='django.contrib.auth.backends.ModelBackend') 
            return redirect(reverse('index'))
    else:
        form = CustomUserCreationForm()
        
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

@login_required 
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, 'profile.html', {'form': form})