from django.urls import path

from orders import views

app_name = 'orders'
urlpatterns = [
    path('summary/', views.bag_summary, name='summary'),
    path('add/', views.bag_add, name='bag_add'),
    path('update/', views.bag_update, name='bag_update'),
    path('delete/', views.bag_delete, name='bag_delete'),
    path('clear/', views.bag_clear, name='bag_clear'),
    path('orders/',views.view_orders, name="view_orders")
]
