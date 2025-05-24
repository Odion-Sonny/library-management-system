from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    published_date = models.DateField()
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class LibraryUser(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    enrollment_date = models.DateTimeField()
    
    def __str__(self):
        return self.email

class BorrowedBook(models.Model):
    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name='borrowed_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    borrowed_date = models.DateTimeField()
    return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-borrowed_date']

    def __str__(self):
        return f"{self.user.email} - {self.book.title}"