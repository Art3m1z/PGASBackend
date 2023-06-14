import json

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
        self.company: Compaing = Compaing.objects.create(
            name='TestCompany',
            date_start=date.today(),
            date_end=date.today() + timedelta(days=10),
        )
        DictTypeMiracle.objects.create(
            name='Спортивные достижения',
            CreadedOn=datetime.now()
        )
        DictTypeMiracle.objects.create(
            name='Олимпиады',
            CreadedOn=datetime.now()
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

    def test_create_request_by_student(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_student_tokens_by_login()[0]}')
        resp = self.client.post('/api/requests/create/', {
            'nomination': 'Спортивные достижения | Олимпиады',
            'company_id': self.company.id,
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['id'], 1)
        self.assertEqual(resp.data['requests'][0]['nomination'], 'Спортивные достижения')
        self.assertEqual(resp.data['requests'][1]['nomination'], 'Олимпиады')

        resp = self.client.get('/api/requests/get/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_create_request_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_admin_tokens_by_login()[0]}')
        resp = self.client.post('/api/requests/create/', {
            'nomination': 'Спортивные достижения | Олимпиады',
            'company_id': self.company.id,
        })
        self.assertEqual(resp.status_code, 403)

        resp = self.client.get('/api/requests/get/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_add_comments(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_student_tokens_by_login()[0]}')
        request_id = self.client.post('/api/requests/create/', {
            'nomination': 'Спортивные достижения | Олимпиады',
            'company_id': self.company.id,
        }).data['id']

        resp = self.client.post('/api/comments/create/', {
            'id': request_id,
            'role': 'student',
            'user_id': self.student.id,
            'text': 'Comment from user'
        })
        self.assertEqual(resp.status_code, 201)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_admin_tokens_by_login()[0]}')
        resp = self.client.post('/api/comments/create/', {
            'id': request_id,
            'role': 'admin',
            'user_id': self.student.id,
            'text': 'Comment from admin'
        })
        self.assertEqual(resp.status_code, 201)

