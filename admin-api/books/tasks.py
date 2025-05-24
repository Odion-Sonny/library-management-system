from celery import shared_task
import requests
from django.conf import settings
from .models import Book, Publisher, Category

@shared_task
def sync_book_to_frontend(book_id):
    try:
        book = Book.objects.get(id=book_id)
        
        # Prepare data for frontend API
        data = {
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'publisher_name': book.publisher.name,
            'category_name': book.category.name,
            'published_date': str(book.published_date),
            'description': book.description,
            'is_available': book.is_available
        }
        
        # Send to frontend API
        headers = {
            'Authorization': f'Token {settings.INTER_SERVICE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{settings.FRONTEND_API_URL}/api/internal/sync-book/",
            json=data,
            headers=headers
        )
        
        return response.status_code == 201
    except Exception as e:
        print(f"Error syncing book: {e}")
        return False

@shared_task
def sync_book_deletion_to_frontend(isbn):
    try:
        headers = {
            'Authorization': f'Token {settings.INTER_SERVICE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.delete(
            f"{settings.FRONTEND_API_URL}/api/internal/sync-book/{isbn}/",
            headers=headers
        )
        
        return response.status_code == 204
    except Exception as e:
        print(f"Error syncing book deletion: {e}")
        return False