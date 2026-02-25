from django.urls import path, include
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard_alt'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Add animal URLs - support both patterns for compatibility
    path('animal/add/', views.AddAnimalView.as_view(), name='add_animal'),
    path('add-animal/', lambda request: redirect('add_animal'), name='add_animal_redirect'),
    
    path('animals/', views.AnimalListView.as_view(), name='animal_list'),
    path('animal/<int:pk>/checkup/', views.UpdateCheckupStatusView.as_view(), name='update_checkup'),
    
    path('milk/add/', views.AddMilkRecordView.as_view(), name='add_milk_record'),
    path('milk/', views.MilkRecordsView.as_view(), name='milk_records'),
    path('milk-records/', lambda request: redirect('milk_records'), name='milk_records_redirect'),
]
