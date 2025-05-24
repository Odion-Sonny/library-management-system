from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

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

class BorrowedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    borrowed_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-borrowed_date']
        unique_together = ['user', 'book', 'actual_return_date']

    def __str__(self):
        return f"{self.user.email} - {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.pk:  # New borrowing
            self.book.is_available = False
            self.book.save()
        super().save(*args, **kwargs)

    def return_book(self):
        self.actual_return_date = timezone.now()
        self.book.is_available = True
        self.book.save()
        self.save()