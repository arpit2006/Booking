from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Hotel


class HotelModelTest(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            location="Test City",
            rooms=50,
            price_per_night=99.99
        )
    
    def test_hotel_creation(self):
        self.assertEqual(self.hotel.name, "Test Hotel")
        self.assertEqual(self.hotel.location, "Test City")
        self.assertEqual(self.hotel.rooms, 50)
        self.assertEqual(self.hotel.price_per_night, 99.99)
    
    def test_hotel_str_method(self):
        self.assertEqual(str(self.hotel), "Test Hotel")


class HotelAPITest(APITestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="API Test Hotel",
            location="API Test City",
            rooms=25,
            price_per_night=149.99
        )
    
    def test_get_hotel_list(self):
        url = reverse('hotel-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_hotel(self):
        url = reverse('hotel-list')
        data = {
            'name': 'New Hotel',
            'location': 'New City',
            'rooms': 30,
            'price_per_night': 199.99
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Hotel.objects.count(), 2)


class HotelTemplateTest(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Template Test Hotel",
            location="Template Test City",
            rooms=40,
            price_per_night=129.99
        )
    
    def test_hotel_list_view(self):
        url = reverse('hotel_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Template Test Hotel")
        self.assertContains(response, "Template Test City")