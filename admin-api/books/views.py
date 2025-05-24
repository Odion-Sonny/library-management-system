from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.utils import timezone
from .models import Book, LibraryUser, BorrowedBook
from .serializers import BookSerializer, LibraryUserSerializer, BorrowedBookSerializer
from .tasks import sync_book_to_frontend, sync_book_deletion_to_frontend

class BookCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def perform_create(self, serializer):
        book = serializer.save()
        # Sync to frontend API
        sync_book_to_frontend.delay(book.id)

class BookDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Book.objects.all()
    
    def perform_destroy(self, instance):
        book_id = instance.id
        isbn = instance.isbn
        super().perform_destroy(instance)
        # Sync deletion to frontend API
        sync_book_deletion_to_frontend.delay(isbn)

class LibraryUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = LibraryUser.objects.all()
    serializer_class = LibraryUserSerializer

class UserBorrowedBooksView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = BorrowedBookSerializer
    
    def get_queryset(self):
        return BorrowedBook.objects.filter(actual_return_date__isnull=True)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def unavailable_books(request):
    borrowed_books = BorrowedBook.objects.filter(
        actual_return_date__isnull=True
    ).select_related('book')
    
    unavailable_data = []
    for borrowed in borrowed_books:
        unavailable_data.append({
            'book': BookSerializer(borrowed.book).data,
            'available_date': borrowed.return_date,
            'borrowed_by': borrowed.user.email
        })
    
    return Response(unavailable_data)