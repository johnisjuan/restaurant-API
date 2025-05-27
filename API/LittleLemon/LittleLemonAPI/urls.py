from  django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items/',views.allmenu_items.as_view()),
    path('menu-items/<str:menuItem>',views.singlemenu_item.as_view()),
    path('api-token-auth/',obtain_auth_token),
    path('groups/<str:group_name>/users/',views.getuserinfo.as_view()),
    path('groups/<str:group_name>/users/<str:userID>',views.deluserinfo.as_view()),
    path('cart/menu-items',views.cartinfo.as_view()),
    path('orders/',views.orderinfo.as_view()),
    path('orders/<int:orderID>',views.singleorderinfo.as_view()),
]