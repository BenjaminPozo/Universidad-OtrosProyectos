from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name = 'HomePage'),
    path('registro/', views.register_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='HomePage'), name='logout'),
    path('transactions/', views.transaction, name = 'Transacciones del Usuario'),
    path('add_transactions/',views.addTransaction,name='Agregar Transacciones'),
    path('modificar_transaction/<int:transaction_id>/', views.modificarTransaction, name='Modificar Transaccion'), 
]