from rest_framework import serializers
from .models import Book, Publisher, Category, BorrowedBook
from datetime import timedelta
from django.utils import timezone

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'publisher', 'publisher_name', 
                  'category', 'category_name', 'published_date', 'description', 
                  'is_available']

class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    days = serializers.IntegerField(min_value=1, max_value=30)
    
    def validate_book_id(self, value):
        try:
            book = Book.objects.get(id=value)
            if not book.is_available:
                raise serializers.ValidationError("This book is not available for borrowing.")
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book not found.")
        return value
    
    def create(self, validated_data):
        book = Book.objects.get(id=validated_data['book_id'])
        return_date = timezone.now() + timedelta(days=validated_data['days'])
        
        borrowed_book = BorrowedBook.objects.create(
            user=self.context['request'].user,
            book=book,
            return_date=return_date
        )
        return borrowed_book

class BorrowedBookSerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)
    
    class Meta:
        model = BorrowedBook
        fields = ['id', 'book', 'book_details', 'borrowed_date', 
                  'return_date', 'actual_return_date']