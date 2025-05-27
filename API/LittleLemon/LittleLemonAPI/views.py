from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import serializers
from .models import Category,MenuItem,Cart,Order,OrderItem
from rest_framework.views import  APIView
from .serializers import MenuItemSerializer,UserSerializer,CartSerializer,OrderSerializer,OrderItemSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import  permission_classes
from django.contrib.auth.models import User,Group
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle
from rest_framework import filters
from django.core.paginator import Paginator,EmptyPage

# Create your views here.


class allmenu_items(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    # filterset_fields = ['category']  
    # ordering_fields = ['price', 'title']         
    # search_fields = ['title']

    def get(self,request):
        items = MenuItem.objects.all()

        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage',default=2)
        page = request.query_params.get('page',default=1)

        if category_name:
            items = items.filter(category__title = category_name)
        if to_price:
            items = items.filter(price__lte = to_price)
        if search:
            items = items.filter(title__icontains = search)
        if ordering:
            items = items.order_by(ordering)

        paginator = Paginator(items,per_page=perpage)

        try:
            items = paginator.page(number=page)
        except:
            items=[]

        serializer = MenuItemSerializer(items,many=True)
        return Response(serializer.data)


    def post(self,request):

        if not request.user.groups.filter(name = 'manager').exists():
            return Response({"Detail" : "Only Managers can add menu items"},status=status.HTTP_403_FORBIDDEN)

        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer._errors,status=status.HTTP_400_BAD_REQUEST)
    

class singlemenu_item(APIView):


    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]

    def get(self,request,menuItem):
        try:
            item = MenuItem.objects.get(title__iexact = menuItem)
        except:
            return Response({"Error" : f"Menu Item '{menuItem}' not found!"},status=status.HTTP_404_NOT_FOUND)

        serializer = MenuItemSerializer(item)
        return Response(serializer.data)
    
    def put(self,request,menuItem):

        if not request.user.groups.filter(name = 'manager').exists():
            return Response({"Detail" : "Only Managers can add menu items"},status=status.HTTP_403_FORBIDDEN)
        
        item = MenuItem.objects.get(title__iexact = menuItem)
        if not item:
            return Response({"Error" : f"Menu item '{menuItem}' not found!"},status=status.HTTP_404_NOT_FOUND)
        serializer = MenuItemSerializer(item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,request,menuItem):

        if not request.user.groups.filter(name = 'manager').exists():
            return Response({"Detail" : "Only Managers can add menu items"},status=status.HTTP_403_FORBIDDEN)
        
        item = MenuItem.objects.get(title__iexact = menuItem)
        if not item:
            return Response({"Error" : f"Menu item '{menuItem}' not found!"},status=status.HTTP_404_NOT_FOUND)
        serializer = MenuItemSerializer(item,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,menuItem):

        if not request.user.groups.filter(name = 'manager').exists():
            return Response({"Detail" : "Only Managers can add menu items"},status=status.HTTP_403_FORBIDDEN)
        
        item = MenuItem.objects.get(title__iexact = menuItem)
        if not item:
            return Response({"Error" : f"Menu item '{menuItem}' not found!"},status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"Message" : f"{menuItem} deleted"},status=status.HTTP_204_NO_CONTENT)


class getuserinfo(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self,request,group_name):

        if not request.user.groups.filter(name = 'manager').exists():
            return Response({"Detail" : "Only Managers can view user details"},status=status.HTTP_403_FORBIDDEN)
        
        try:
            group = Group.objects.get(name = group_name)
        except:
            return Response({"Error" : f"{group_name} does not exist"},status=status.HTTP_404_NOT_FOUND)
        
        users = group.user_set.all()
        serializer = UserSerializer(users,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request,group_name):

        if not request.user.groups.filter(name = 'manager').exists():
            return Response({"Detail" : "Only Managers can view user details"},status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            try:
                group = Group.objects.get(name = group_name)
                user.groups.add(group)
            except:
                return Response({"Error" :f"{group_name} does not exist."},status=status.HTTP_404_NOT_FOUND)
            
            return Response({"Message" : "User added to group"},status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class deluserinfo(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self,request,group_name,userID):

        if not request.user.groups.filter(name = 'manager').exists():
            return Response({"Detail" : "Only Managers can view user details"},status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=userID)
        except User.DoesNotExist:
            return Response({"Error" : f"{group_name} does not exist."},status=status.HTTP_404_NOT_FOUND)
        
        if not user.groups.filter(name=group_name).exists():
            return Response({"Error" : f"User with {userID} does not exist as {group_name}"},status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response({"Message" : "User Deleted."},status=status.HTTP_200_OK)
    

class cartinfo(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self,request):
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items,many=True)
        return Response(serializer.data)

    def post(self,request):
        user = request.user
        menuitem_id = request.data.get("menuitem")
        quantity = request.data.get("quantity")

        try:
            menuitem = MenuItem.objects.get(pk=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({"Error" : "Menu Item not found"},status=status.HTTP_404_NOT_FOUND)
        
        single = menuitem.price
        total = single * int(quantity)

        item,created = Cart.objects.update_or_create(
            user=user,
            menuitem=menuitem,
            defaults={
                "quantity" : quantity,
                "unit_price" : single,
                "price" : total
            }
        )

        serializer = CartSerializer(item)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request):
        user = request.user
        Cart.objects.filter(user=user).delete()
        return Response({"Message" : "Cart Deleted"},status=status.HTTP_204_NO_CONTENT)


class orderinfo(APIView):
    
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self,request):

        items = Order.objects.filter(user=request.user)

        total = request.query_params.get('total')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage',default=2)
        page = request.query_params.get('page',default=1)

        if total:
            items = items.filter(total__lte = total)
        if search:
            items = items.filter(title__icontains = search)
        if ordering:
            items = items.order_by(ordering)

        paginator = Paginator(items,per_page=perpage)

        try:
            items = paginator.page(number=page)
        except:
            items=[]

        if request.user.groups.filter(name = 'manager').exists():
            items = Order.objects.all()

            total = request.query_params.get('total')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            perpage = request.query_params.get('perpage',default=2)
            page = request.query_params.get('page',default=1)

            if total:
                items = items.filter(total__lte = total)
            if search:
                items = items.filter(title__icontains = search)
            if ordering:
                items = items.order_by(ordering)

            paginator = Paginator(items,per_page=perpage)

            try:
                items = paginator.page(number=page)
            except:
                items=[]

            serializer = OrderSerializer(items,many=True)
            return Response(serializer.data)
        
        if request.user.groups.filter(name = 'delivery-crew').exists():
            items = Order.objects.filter(delivery_crew=request.user)

            total = request.query_params.get('total')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            perpage = request.query_params.get('perpage',default=2)
            page = request.query_params.get('page',default=1)

            if total:
                items = items.filter(total__lte = total)
            if search:
                items = items.filter(title__icontains = search)
            if ordering:
                items = items.order_by(ordering)

            paginator = Paginator(items,per_page=perpage)

            try:
                items = paginator.page(number=page)
            except:
                items=[]

            serializer = OrderSerializer(items,many=True)
            return Response(serializer.data)

        serializer = OrderSerializer(items,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        user = request.user
        items = Cart.objects.filter(user=user)

        if not items.exists():
            return Response({"Message" : "Cart is empty"},status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(item.price for item in items)

        order = Order.objects.create(
            user=user,
            total=total,
            date=now().date()
        )

        orderitems = [
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            for item in items
        ]
        OrderItem.objects.bulk_create(orderitems)

        items.delete()

        return Response({"Message" : "Order created successfully"},status=status.HTTP_201_CREATED)


class singleorderinfo(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self,request,orderID):
        order = get_object_or_404(Order,id=orderID)

        try:
            order = Order.objects.get(id=orderID)
        except Order.DoesNotExist:
            return Response({"error": f"Order with ID {orderID} not found."},status=status.HTTP_404_NOT_FOUND)

        if request.user == order.user or request.user.groups.filter(name='manager').exists() or request.user.groups.filter(name='delivery-crew').exists():
            order_items = OrderItem.objects.filter(order=order)
            serializer  = OrderItemSerializer(order_items,many=True)
            return Response(serializer.data)
    
        return Response({"Message" : "No Permission"},status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, orderID):
        try:
            order=Order.objects.get(id=orderID)
        except Order.DoesNotExist:
            return Response({"Error": f"Order with ID {orderID} not found."},status=status.HTTP_404_NOT_FOUND)
        
        if request.user.groups.filter(name='manager').exists():
            serializer = OrderSerializer(order,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        elif request.user.groups.filter(name='deliver-crew').exists():
            if order.delivery_crew != request.user:
                return Response({"Error" : "No Permission"},status=status.HTTP_403_FORBIDDEN)
            
            if "status" not in request.data:
                return Response({"Error" : "Only Status can be modified"},status=status.HTTP_400_BAD_REQUEST)
            
            order.status=request.data.get("status")
            order.save()
            return Response({"Message" : "Status Updated"})

        return Response({"Error" : "No Permission"},status=status.HTTP_403_FORBIDDEN)



    def delete(self,request,orderID):
        if not request.user.groups.filter(name='manager').exists():
            return Response({"Message" : "Only Managers can delete orders"},status=status.HTTP_403_FORBIDDEN)
        
        try:
            order = Order.objects.get(id = orderID)
        except Order.DoesNotExist:
            return Response({"Error" : f"Order Id {orderID} not found"},status=status.HTTP_404_NOT_FOUND)
        
        order.delete()

        return Response({"Message" : "Order Deleted"},status=status.HTTP_204_NO_CONTENT)



    

