from django.test import TestCase, Client
from django.urls import reverse
from myapp.models import User , AbstractUser 


class CreateUserViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('createUser')  
        self.admin_user = User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')

    def test_create_user_get_request(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'createUser.html')

    def test_create_user_post_request_valid(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(self.url, {
            'username': 'newuser',
            'password': 'newpassword',
            'name': 'New',
            'lastname': 'User',
            'email': 'newuser@example.com',
            'Tipo': 'Mesero'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'createUser.html')
        self.assertContains(response, 'success')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_create_user_post_request_invalid(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(self.url, {
            'username': '',
            'password': '',
            'name': '',
            'lastname': '',
            'email': '',
            'Tipo': 'Mesero'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'createUser.html')
        self.assertContains(response, 'error')
        self.assertFalse(User.objects.filter(username='').exists())