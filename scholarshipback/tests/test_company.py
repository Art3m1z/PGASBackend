from rest_framework.test import APITestCase
from ..models import *
from datetime import datetime, date, timedelta
from uuid import uuid4


class CompanyTestCase(APITestCase):

    def setUp(self):
        self.student = Student.objects.create(
            login='TestStudent',
            password='TestStudent',
            token=uuid4(),

            lastname='Иванов',
            firstname='Иван',
            patronymic='Иванович',
            birthday=date(2000, 7, 19),
            learningPlan='Матан | ИВТ',

            phone='8 800 555 35 35',
            institut='Инженерный',
            profile='Автоматизации производства',
            form='Очная',
            source_finance='Бюджет',
            level='Бакалавр',
            course=3,

            date_create_profile=datetime.now(),

            avatar='',
        )
        self.admin = Admin.objects.create(
            login='TestAdmin',
            password='TestAdmin',

            lastname='Андреев',
            firstname='Андрей',
            patronymic='Андреевич',

            avatar='',
        )

    def tearDown(self):
        self.client.credentials(HTTP_AUTHORIZATION='')

    def get_student_tokens_by_login(self):
        resp = self.client.post('/api/auth/student/login/', {
            'login': self.student.login,
            'password': self.student.password,
        })
        return resp.data['access_token'], resp.data['refresh_token']

    def get_admin_tokens_by_login(self):
        resp = self.client.post('/api/auth/admin/login/', {
            'login': self.admin.login,
            'password': self.admin.password,
        })
        return resp.data['access_token'], resp.data['refresh_token']

    def test_create_company_by_admin_with_credentials(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_admin_tokens_by_login()[0]}')
        resp = self.client.post('/api/companies/create/', {
            'name': 'TestCompany',
            'date_start': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'date_end': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        })
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/companies/get/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], 'TestCompany')

    def test_create_company_by_admin_without_credentials(self):
        resp = self.client.post('/api/companies/create/', {
            'name': 'TestCompany',
            'date_start': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'date_end': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        })
        self.assertEqual(resp.status_code, 400)

        resp = self.client.get('/api/companies/get/')
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(hasattr(resp, 'content'))

    def test_create_company_by_student_with_credentials(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_student_tokens_by_login()[0]}')
        resp = self.client.post('/api/companies/create/', {
            'name': 'TestCompany',
            'date_start': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'date_end': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        })
        self.assertEqual(resp.status_code, 403)

        resp = self.client.get('/api/companies/get/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(hasattr(resp, 'content'))
