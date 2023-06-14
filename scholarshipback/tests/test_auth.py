import jwt
from django.conf import settings
from rest_framework.test import APITestCase
from ..models import *
from datetime import datetime, date, timezone, timedelta
from uuid import uuid4


class AuthTestCase(APITestCase):

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

    def test_student_login(self):
        resp = self.client.post('/api/auth/student/login/', {
            'login': self.student.login,
            'password': self.student.password,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], self.student.id)
        self.assertEqual(resp.data['fio'], self.student.fio())

    def test_admin_login(self):
        resp = self.client.post('/api/auth/admin/login/', {
            'login': self.admin.login,
            'password': self.admin.password,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], self.admin.id)
        self.assertFalse('fio' in resp.data)

    def test_try_login_student_by_fake_credentials(self):
        resp = self.client.post('/api/auth/student/login/', {
            'login': self.student.login,
            'password': 'FakePasss',
        })

        self.assertEqual(resp.status_code, 404)
        self.assertTrue('detail' in resp.data)
        self.assertEqual(resp.data['detail'], 'Неверный логин или пароль!')

    def test_try_login_student_by_admin(self):
        resp = self.client.post('/api/auth/admin/login/', {
            'login': self.student.login,
            'password': self.student.password,
        })

        self.assertEqual(resp.status_code, 404)
        self.assertTrue('detail' in resp.data)
        self.assertEqual(resp.data['detail'], 'Неверный логин или пароль!')

    def test_try_login_admin_by_student(self):
        resp = self.client.post('/api/auth/student/login/', {
            'login': self.admin.login,
            'password': self.admin.password,
        })

        self.assertEqual(resp.status_code, 404)
        self.assertTrue('detail' in resp.data)
        self.assertEqual(resp.data['detail'], 'Неверный логин или пароль!')

    def test_get_student_data_without_access_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='')
        resp = self.client.post('/api/auth/student/detail/', {
            'id': self.student.id
        })
        self.assertEqual(resp.status_code, 400)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer')
        resp = self.client.post('/api/auth/student/detail/', {
            'id': self.student.id
        })
        self.assertEqual(resp.status_code, 400)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer dfgfdg-fdgfdgfdg-dfgdfgfdg')
        resp = self.client.post('/api/auth/student/detail/', {
            'id': self.student.id
        })
        self.assertEqual(resp.status_code, 401)

    def test_get_student_data_with_access_token(self):
        access_token, _ = self.get_student_tokens_by_login()
        self.assertNotEqual(len(access_token), 0)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        resp = self.client.post('/api/auth/student/detail/', {
            'id': self.student.id
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['fio'], self.student.fio())
        self.assertEqual(' | '.join(resp.data['learningPlans']), self.student.learningPlan)

    def test_update_access_token(self):
        _, refresh_token = self.get_student_tokens_by_login()

        resp = self.client.post('/api/auth/refresh/', {
            'refresh_token': refresh_token
        })

        self.assertEqual(resp.status_code, 200)
        self.assertTrue('access_token' in resp.data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["access_token"]}')
        resp = self.client.post('/api/auth/student/detail/', {
            'id': self.student.id
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['fio'], self.student.fio())
        self.assertEqual(' | '.join(resp.data['learningPlans']), self.student.learningPlan)

    def test_try_update_access_token_by_expired_refresh_token(self):
        refresh_token = jwt.encode(
            {
                'id': self.student.id,
                'role': 'student',
                'type': 'refresh',
                'exp': datetime.now(tz=timezone.utc) - timedelta(weeks=1)
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        resp = self.client.post('/api/auth/refresh/', {
            'refresh_token': refresh_token
        })

        self.assertEqual(resp.status_code, 401)
        self.assertFalse('access_token' in resp.data)
        self.assertTrue('detail' in resp.data)
        self.assertEqual(resp.data['detail'], 'Refresh token expired, login required!')

    def test_try_update_access_token_by_invalid_refresh_token(self):
        refresh_token = 'khfgkhfdhg.gfd4khjhgkfdh.324gfddfg4'
        resp = self.client.post('/api/auth/refresh/', {
            'refresh_token': refresh_token
        })

        self.assertEqual(resp.status_code, 401)
        self.assertFalse('access_token' in resp.data)
        self.assertTrue('detail' in resp.data)
        self.assertEqual(resp.data['detail'], 'Can not decode token!')

        refresh_token = jwt.encode(
            {
                'id': self.student.id,
                'role': 'student',
                'type': 'refresh',
                'exp': datetime.now(tz=timezone.utc) - timedelta(weeks=1)
            },
            'FAKE_SIGNATURE',
            algorithm=settings.ALGORITHM
        )
        resp = self.client.post('/api/auth/refresh/', {
            'refresh_token': refresh_token
        })

        self.assertEqual(resp.status_code, 401)
        self.assertFalse('access_token' in resp.data)
        self.assertTrue('detail' in resp.data)
        self.assertEqual(resp.data['detail'], 'Invalid signature of token!')
