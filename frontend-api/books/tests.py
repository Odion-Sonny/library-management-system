from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Book, Publisher, Category, BorrowedBook
from datetime import date, timedelta
from django.utils import timezone

User = get_user_model()

class BookAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test data
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.category = Category.objects.create(name='Fiction')
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            publisher=self.publisher,
            category=self.category,
            published_date=date.today(),
            description='Test description'
        )
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)
    
    def test_list_available_books(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Book')
    
    def test_get_single_book(self):
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')
    
    def test_filter_books_by_publisher(self):
        response = self.client.get('/api/books/', {'publisher_name': 'Test Publisher'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_books_by_category(self):
        response = self.client.get('/api/books/', {'category_name': 'Fiction'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_borrow_book(self):
        data = {
            'book_id': self.book.id,
            'days': 7
        }
        response = self.client.post('/api/books/borrow/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check book is no longer available
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)
        
        # Check borrowed book record
        borrowed = BorrowedBook.objects.get(book=self.book, user=self.user)
        self.assertIsNotNone(borrowed)
        expected_return = timezone.now() + timedelta(days=7)
        self.assertAlmostEqual(
            borrowed.return_date.timestamp(),
            expected_return.timestamp(),
            delta=60  # 1 minute tolerance
        )
    
    def test_cannot_borrow_unavailable_book(self):
        # Make book unavailable
        self.book.is_available = False
        self.book.save()
        
        data = {
            'book_id': self.book.id,
            'days': 7
        }
        response = self.client.post('/api/books/borrow/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_my_borrowed_books(self):
        # Borrow a book
        BorrowedBook.objects.create(
            user=self.user,
            book=self.book,
            return_date=timezone.now() + timedelta(days=7)
        )
        
        response = self.client.get('/api/books/my-borrowed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['book'], self.book.id)

class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_user_registration(self):
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Check user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
    
    def test_registration_password_mismatch(self):
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'securepass123',
            'password_confirm': 'differentpass123'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)