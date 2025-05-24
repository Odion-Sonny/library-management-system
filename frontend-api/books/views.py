from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, BorrowedBook
from .serializers import BookSerializer, BorrowBookSerializer, BorrowedBookSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from .authentication import InterServiceAuthentication


class BookListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['publisher', 'category']
    search_fields = ['title', 'author', 'isbn']
    
    def get_queryset(self):
        queryset = Book.objects.filter(is_available=True)
        
        # Filter by publisher name
        publisher_name = self.request.query_params.get('publisher_name', None)
        if publisher_name:
            queryset = queryset.filter(publisher__name__icontains=publisher_name)
        
        # Filter by category name
        category_name = self.request.query_params.get('category_name', None)
        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)
        
        return queryset

class BookDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def borrow_book(request):
    serializer = BorrowBookSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        borrowed_book = serializer.save()
        response_serializer = BorrowedBookSerializer(borrowed_book)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_borrowed_books(request):
    borrowed_books = BorrowedBook.objects.filter(
        user=request.user,
        actual_return_date__isnull=True
    )
    serializer = BorrowedBookSerializer(borrowed_books, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([InterServiceAuthentication])
@permission_classes([])
def sync_book_create(request):
    # Get or create publisher and category
    publisher, _ = Publisher.objects.get_or_create(
        name=request.data['publisher_name']
    )
    category, _ = Category.objects.get_or_create(
        name=request.data['category_name']
    )
    
    # Create or update book
    book_data = {
        'title': request.data['title'],
        'author': request.data['author'],
        'isbn': request.data['isbn'],
        'publisher': publisher,
        'category': category,
        'published_date': request.data['published_date'],
        'description': request.data.get('description', ''),
        'is_available': request.data.get('is_available', True)
    }
    
    book, created = Book.objects.update_or_create(
        isbn=book_data['isbn'],
        defaults=book_data
    )
    
    return Response(BookSerializer(book).data, 
                   status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([InterServiceAuthentication])
@permission_classes([])
def sync_book_delete(request, isbn):
    try:
        book = Book.objects.get(isbn=isbn)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)