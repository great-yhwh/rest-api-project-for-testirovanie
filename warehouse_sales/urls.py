from django.urls import path
from . import views

app_name = 'warehouse_sales'

urlpatterns = [
    path('', views.contractor_list, name='contractor_list'),
    path('contractors/create/', views.contractor_create, name='contractor_create'),
    path('contractors/update/<str:ref_key>/', views.contractor_update, name='contractor_update'),
    path('contractors/delete/<str:ref_key>/', views.contractor_delete, name='contractor_delete'),
    path('stock/', views.stock_list, name='stock_list'),
]