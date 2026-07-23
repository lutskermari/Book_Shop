from rest_framework import viewsets, permissions, status
from .permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category, Book, Order, OrderItem
from .serializers import CategorySerializer, BookSerializer, OrderSerializer, CartItemSerializer
from .filters import BookFilter

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]   
     
    filterset_class = BookFilter
    search_fields = ['title', 'author', 'description']
    ordering_fields = ['price', 'published_date']


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        order = serializer.save()
        cart = self.request.session.get('cart', {})
        for book_id, item_data in cart.items():
            book = get_object_or_404(Book, id=int(book_id))
            OrderItem.objects.create(
                order=order, book=book, price=book.price, quantity=item_data['quantity']
            )
        self.request.session['cart'] = {}


class CartAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = request.session.get('cart', {})
        output = []
        total_price = 0
        for book_id, item in cart.items():
            book = Book.objects.filter(id=int(book_id)).first()
            if book:
                subtotal = book.price * item['quantity']
                total_price += subtotal
                output.append({
                    'book': BookSerializer(book).data, 
                    'quantity': item['quantity'],
                    'subtotal': subtotal
                })
        return Response({'items': output, 'total_price': total_price})

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            book_id = str(serializer.validated_data['book_id'])
            quantity = serializer.validated_data['quantity']
            book = get_object_or_404(Book, id=int(book_id))
            
            cart = request.session.get('cart', {})
            if book_id in cart:
                cart[book_id]['quantity'] += quantity
            else:
                cart[book_id] = {'quantity': quantity}
                
            request.session['cart'] = cart
            request.session.modified = True
            return Response({"status": "Success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)