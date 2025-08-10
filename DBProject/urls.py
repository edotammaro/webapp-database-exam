from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
path('dashboard/allenatore/', views.dashboard_allenatore, name='dashboard_allenatore'),
    path('dashboard/presidente-squadra/', views.dashboard_pres_squadra, name='dashboard_pres_squadra'),
    path('dashboard/presidente-squadra/rimuovi/<int:membro_id>/<str:tipo_membro>/', views.rimuovi_membro,
         name='rimuovi_membro'),
    path('logout/', views.logout_view, name='logout'),
]