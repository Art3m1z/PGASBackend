import datetime
import json

import jwt
import pandas
from django.conf import settings
from django.contrib.auth import login, authenticate as django_authenticate
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from docxtpl import DocxTemplate
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request as APIRequest
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import CustomAuthMiddleware, authenticate
from .serializers import *


class StudentSignInView(APIView):
    '''
    Вход студента
    todo Дополнить проверкой через LDAP, если пользователь есть в системе старой, скопировать его данные в БД и далее проверяем по логину и паролю
    '''

    def post(self, request):
        login = request.data.get('login')
        password = request.data.get('password')

        try:
            s = Student.objects.get(login=login, password=password)
        except Student.DoesNotExist:
            return Response({'detail': 'Неверный логин или пароль!'}, 404)

        return Response({
            **authenticate(s),
            'id': s.id,
            'fio': s.fio(),
            'email': s.email,
            'avatarUrl': s.avatar,
            'financingSource': s.source_finance,
            'learningPlans': [s.learningPlan]
        })


class AdminSignInView(APIView):
    '''
    Вход админа
    '''

    def post(self, request):
        login = request.data.get('login')
        password = request.data.get('password')

        try:
            s = Admin.objects.get(login=login, password=password)
        except Admin.DoesNotExist:
            return Response({'detail': 'Неверный логин или пароль!'}, 404)

        return Response({**authenticate(s), 'id': s.id, 'avatarUrl': s.avatar, 'email': s.email})


class UpdateAccessTokenView(APIView):

    def post(self, request):
        refresh = request.data.get('refresh_token')

        try:
            data = jwt.decode(refresh, settings.SECRET_KEY, [settings.ALGORITHM],
                              {'verify_exp': True, 'verify_signature': True})

            if data['role'] == 'student':
                u = get_object_or_404(Student, id=data['id'])
            else:
                u = get_object_or_404(Admin, id=data['id'])

            return Response({**authenticate(u), 'refresh_token': refresh})

        except ExpiredSignatureError:
            return Response({'detail': 'Refresh token expired, login required!'}, 401)
        except InvalidSignatureError:
            return Response({'detail': 'Invalid signature of token!'}, 401)
        except DecodeError:
            return Response({'detail': 'Can not decode token!'}, 401)


class GetStudentDataView(CustomAuthMiddleware, APIView):

    def post(self, request):
        s = get_object_or_404(Student, id=request.data['id'])
        token = request.headers['Authorization'].split('Bearer ')[1]

        data = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM],
                          {'verify_exp': True, 'verify_signature': True})

        if data['role'] != 'student':
            return Response({'detail': 'No credentials!'}, 403)

        return Response({
            'id': s.id,
            'fio': s.fio(),
            'email': s.email,
            'avatarUrl': s.avatar,
            'learningPlans': [s.learningPlan]
        })


class GetAdminDataView(CustomAuthMiddleware, APIView):

    def post(self, request):
        a = get_object_or_404(Admin, id=request.data['id'])
        token = request.headers['Authorization'].split('Bearer ')[1]

        data = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM],
                          {'verify_exp': True, 'verify_signature': True})

        if data['role'] != 'admin':
            return Response({'detail': 'No credentials!'}, 403)

        return Response({
            'id': a.id,
            'fio': a.fio(),
            'email': a.email,
            'avatarUrl': a.avatar,
        })


class CompaingViewList(CustomAuthMiddleware, ListAPIView):
    '''Работа с компаниями'''

    serializer_class = CompaingSerializer
    queryset = Compaing.objects.filter(isDeleted=False)


class CompaingViewDetail(CustomAuthMiddleware, APIView):
    def get(self, request: APIRequest):
        company = get_object_or_404(Compaing, id=request.data['id'])
        serializer = CompaingSerializer(company, many=False)
        return Response(serializer.data)

    def post(self, request):
        data = {
            'name': request.data.get('name'),
            'startDate': datetime.datetime(
                get_date(request.data['date_start']).year,
                get_date(request.data['date_start']).month,
                get_date(request.data['date_start']).day,
                0,
                0,
                0,
                0
            ),
            'endDate': datetime.datetime(
                get_date(request.data['date_end']).year,
                get_date(request.data['date_end']).month,
                get_date(request.data['date_end']).day,
                23,
                59,
                59,
                0
            ),
        }

        c: Compaing = get_object_or_404(Compaing, id=request.data['id'])

        c.name = data['name']
        c.date_start = data['startDate']
        c.date_end = data['endDate']

        c.save()

        return Response(status=204)

    def delete(self, request):
        c: Compaing = get_object_or_404(Compaing, id=request.data['id'])
        c.isDeleted = True
        c.save()

        return Response(status=204)


class CompaningViewCreate(CustomAuthMiddleware, APIView):

    def post(self, request):
        token = request.headers['Authorization'].split('Bearer ')[1]
        data = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM],
                          {'verify_exp': True, 'verify_signature': True})

        if data['role'] == 'student':
            return Response({'detail': 'No credentials!'}, 403)

        data = {
            'name': request.data.get('name'),
            'startDate': datetime.datetime(
                get_date(request.data['date_start']).year,
                get_date(request.data['date_start']).month,
                get_date(request.data['date_start']).day,
                0,
                0,
                0,
                0
            ),
            'endDate': datetime.datetime(
                get_date(request.data['date_end']).year,
                get_date(request.data['date_end']).month,
                get_date(request.data['date_end']).day,
                23,
                59,
                59,
                0
            ),
        }

        serializer = CompaingSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'id': serializer.data['id']})

        return Response({"detail": serializer.errors}, 400)


class CheckShowStudentPointsView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        token = request.headers['Authorization'].split('Bearer ')[1]

        data = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM],
                          {'verify_exp': True, 'verify_signature': True})

        get_object_or_404(Admin, id=data['id'])

        if data['role'] != 'admin':
            return Response({'detail': 'No credentials!'}, 403)

        company = get_object_or_404(Compaing, id=request.data['id'])

        company.show_student_points = not company.show_student_points
        company.save()

        return Response(status=204)


class RequestViewList(CustomAuthMiddleware, APIView, PageNumberPagination):
    page_size = 20

    def get(self, request: APIRequest):

        token = request.headers['Authorization'].split('Bearer ')[1]
        data = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM],
                          {'verify_exp': True, 'verify_signature': True})
        # student requests

        if data['role'] == "student":
            requests = Request.objects.exclude(isDeleted=True).filter(student__id=data['id'])
            serializer = RequestSerializer(requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:

            # all requests for admin

            requests = Request.objects.exclude(isDeleted=True).exclude(last_status="Черновик")
            page = self.paginate_queryset(requests, request)
            serializer = RequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def post(self, request: APIRequest):
        # устанавливает оценку, которую дал админ за аттестат
        req: Request = get_object_or_404(Request, id=request.data['id'])

        req.admin_exam_point = request.data['point']

        req.save()

        return Response(status=204)

    def put(self, request):
        # этим запросом устанавливают статус заявки
        req: Request = get_object_or_404(Request, id=request.data['id'])

        req.last_status = request.data['status']

        req.save()

        return Response(status=204)


class NotificationListView(CustomAuthMiddleware, ListAPIView):
    serializer_class = ListNotificationSerializer
    queryset = Notification.objects.all()


class NotificationDetailView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        serializer = CreateNotificationSerializer(data=request.data)

        if serializer.is_valid():
            n = serializer.save()

            return Response({'id': n.id}, 201)

        return Response({"detail": serializer.errors}, 400)

    def delete(self, request: APIRequest):
        n: Notification = get_object_or_404(Notification, id=request.data['id'])

        n.delete()

        return Response(status=204)


class SetAdminPointForRow(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        req: Request = get_object_or_404(Request, id=request.data['id'])
        token = request.headers['Authorization'].split('Bearer ')[1]

        data = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM],
                          {'verify_exp': True, 'verify_signature': True})

        get_object_or_404(Admin, id=data['id'])

        if data['role'] != 'admin':
            return Response({'detail': 'No credentials!'}, 403)

        for d, p in zip(req.data.all(), request.data['data']):
            d.point = int(p)
            d.save()

        return Response(status=204)


class CreateRequestView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):

        token = request.headers['Authorization'].split('Bearer ')[1]
        data = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM],
                          {'verify_exp': True, 'verify_signature': True})
        student = get_object_or_404(Student, id=data['id'])

        if data['role'] != 'student':
            return Response({'detail': 'No credentials!'}, 403)

        company = get_object_or_404(Compaing, id=request.data['company_id'])

        if now().timestamp() > company.date_end.timestamp():
            return Response({'detail': 'Время работы кампании истекло!'}, 400)

        type_miracle = get_object_or_404(DictTypeMiracle, id=int(request.data['nomination']))

        if type_miracle.name == 'Учебная деятельность':
            learning_nomination_data = LearningNominationData.objects.create()

            Request.objects.create(
                compaing=company,
                student=student,
                typeMiracle=type_miracle,
                learningPlan=student.learningPlan,
                last_status='Черновик',
                learning_nomination_data=learning_nomination_data
            )
        else:
            Request.objects.create(
                compaing=company,
                student=student,
                typeMiracle=type_miracle,
                learningPlan=student.learningPlan,
                last_status='Черновик',
            )

        return Response(status=status.HTTP_201_CREATED)


class AddCommentView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        print(request.data)
        req: Request = get_object_or_404(Request, id=request.data['id'])

        if request.data['text'].strip() == '':
            return Response({'detail': 'Комментрий не должен быть пустым!'}, 400)

        if request.data['role'] == 'student':
            req.comments.create(text=request.data['text'], student_id=request.data['user_id'])
        elif request.data['role'] == 'admin':
            req.comments.create(text=request.data['text'], admin_id=request.data['user_id'])

        send_mail(
            'Новый комментарий!',
            '',
            settings.EMAIL_HOST_USER,
            [req.student.email],
            fail_silently=True,
            html_message=f'Сотрудник БФУ имени Канта оставил комментарий под Вашей заявкой на получение '
                         f'повышенной стипендии для номинации <b>{req.typeMiracle.name}'
                         f'</b>:<br/><i>{request.data["text"]}</i>',
        )
        print('sent')

        return Response(status=201)


class SetImageView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        print(request.FILES)
        img: InMemoryUploadedFile = request.FILES['image']

        print(img)

        if img.size > 10485760:
            return Response({'detail': 'Файл должен быть до 10 МБ!'}, 400)

        path = './media/uploads/{}'.format(img.name.replace('.', f'.{now().timestamp()}.'))

        with open(path, 'wb') as writer:
            writer.write(img.read())

        return Response({'url': path.split('.', maxsplit=1)[1]})


class SaveRequestView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        req: Request = get_object_or_404(Request, id=request.data['id'])
        achivement_id = request.data['achivementId']
        achivement_file_link = request.data['achivementFileLink']

        for index, item in enumerate(request.data['componentInfo']):
            print(index)
            try:
                data_info_miracle = DataInfoMiracle.objects.get(id=achivement_id[index])
                print(data_info_miracle)
                data_info_miracle.name = item['achivement']
                data_info_miracle.progress = item['miracle']
                data_info_miracle.view_progress = item['typeMiracle']
                data_info_miracle.status_progress = item['stateMiracle']
                data_info_miracle.level_progress = item['levelMiracle']
                data_info_miracle.date_event = item['dateAchivement']
                data_info_miracle.number_of_docs = item['documentNumber']
                data_info_miracle.linkDocs = achivement_file_link[index]
                data_info_miracle.save()
                req.LastUpdate = now()
                req.save()

                HistoryChangeRequest.objects.create(
                    student=req.student,
                    json=json.dumps(_from_models_to_json([req]))
                )

            except Exception as err:
                print(err)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)
        # for d, t in zip(req.data.all(), request.data['data']):
        #     if t['data'][0].strip() == '':
        #         return Response({'detail': 'Поля "Название" и "Документ" обязательные!'}, 400)
        #
        #     d.name = t['data'][0]
        #     d.progress = t['data'][1]
        #     d.view_progress = t['data'][2]
        #     d.status_progress = t['data'][3]
        #     d.level_progress = t['data'][4]
        #     d.date_event = t['data'][5]
        #     d.number_of_docs = t['data'][6]
        #     d.linkDocs = t['data'][7]
        #
        #     d.save()
        #
        # req.LastUpdate = now()
        # req.save()

        # HistoryChangeRequest.objects.create(
        #     student=req.student,
        #     json=json.dumps(_from_models_to_json([req]))
        # )

        # return Response(status=status.HTTP_200_OK)


class AddRowView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        req: Request = get_object_or_404(Request, id=request.data['id'])
        t = request.data

        d = DataInfoMiracle()
        d.save()

        req.data.add(d)
        req.LastUpdate = now()
        req.save()

        HistoryChangeRequest.objects.create(
            student=req.student,
            json=json.dumps(_from_models_to_json([req]))
        )

        return Response({'id': d.id}, 201)


class SaveLearingRequestView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        req: Request = get_object_or_404(Request, id=request.data['id'])
        print(request.data['linkToGradebook'])
        req.learning_nomination_data.linkgradebook = request.data['linkToGradebook']
        req.learning_nomination_data.excellent_mark_pecent = request.data['percent']
        req.learning_nomination_data.admin_exam_point = request.data['point']

        req.learning_nomination_data.save()
        req.save()

        return Response(status=204)


# class dictTypeEventView(CustomAuthMiddleware, APIView):
#
#     def post(self, request):
#         name_type_Miracle = request.data["nomination"]
#         qs = dictTypeEvent.objects.filter(type_miracle__name=name_type_Miracle)
#
#         resp = []
#         for t in qs:
#             resp.append(t.name)
#
#         return Response(resp)
#
#
# class dictTypeWorkView(CustomAuthMiddleware, APIView):
#
#     def post(self, request):
#         name_type_Miracle = request.data["nomination"]
#         qs = dictTypeWork.objects.filter(type_miracle__name=name_type_Miracle)
#
#         resp = []
#         for t in qs:
#             resp.append(t.name)
#
#         return Response(resp)
#
#
# class dictRoleStudentToWorkView(CustomAuthMiddleware, APIView):
#
#     def post(self, request):
#         name_type_Miracle = request.data["nomination"]
#         qs = dictRoleStudentToWork.objects.filter(type_miracle__name=name_type_Miracle)
#
#         resp = []
#         for t in qs:
#             resp.append(t.name)
#
#         return Response(resp)
#
#
# class dictWinnerPlaceView(CustomAuthMiddleware, APIView):
#
#     def post(self, request):
#         name_type_Miracle = request.data["nomination"]
#         qs = dictWinnerPlace.objects.filter(type_miracle__name=name_type_Miracle)
#
#         resp = []
#         for t in qs:
#             resp.append(t.name)
#
#         return Response(resp)


class dictTypeMiracleView(CustomAuthMiddleware, APIView):

    def get(self, request):
        nominations = DictTypeMiracle.objects.exclude(isDeleted=True)
        serializer = NominationsSerializers(nominations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class dictProgressView(CustomAuthMiddleware, APIView):
    def post(self, request):
        name_type_Miracle = request.data.get('nomination')
        qs = DictProgress.objects.filter(typemiracle__name=name_type_Miracle).filter(isDeleted=False)
        resp = []
        for t in qs:
            resp.append(t.name)

        return Response(resp)


class dictViewProgressView(CustomAuthMiddleware, APIView):
    def post(self, request):
        name_type_Miracle = request.data.get('nomination')
        dictprogress = request.data.get('progress')

        qs = dictViewProgress.objects.filter(typemiracle__name=name_type_Miracle).filter(
            dictprogress__name=dictprogress).filter(isDeleted=False)
        resp = []
        for t in qs:
            resp.append(t.name)
        return Response(resp)


class dictStatusProgressView(CustomAuthMiddleware, APIView):
    def post(self, request):
        name_type_Miracle = request.data.get('nomination')
        dictprogress = request.data.get('progress')
        dictviewprogress = request.data.get('viewprogress')
        qs = dictStatusProgress.objects.filter(typemiracle__name=name_type_Miracle).filter(
            dictprogress__name=dictprogress).filter(dictviewprogress__name=dictviewprogress).filter(isDeleted=False)
        resp = []
        for t in qs:
            resp.append(t.name)
        return Response(resp)


class dictLevelProgressView(CustomAuthMiddleware, APIView):
    def post(self, request):
        name_type_Miracle = request.data.get('nomination')
        dictprogress = request.data.get('progress')
        dictviewprogress = request.data.get('viewprogress')
        dictstatusprogress = request.data.get('statusprogress')

        qs = dictLevelProgress.objects.filter(typemiracle__name=name_type_Miracle).filter(
            dictprogress__name=dictprogress).filter(dictviewprogress__name=dictviewprogress).filter(
            dictstatusprogress__name=dictstatusprogress).filter(isDeleted=False)
        resp = []
        for t in qs:
            resp.append(t.name)
        return Response(resp)


class GetDictView(CustomAuthMiddleware, APIView):

    def get(self, request: APIRequest):
        resp = []

        for n in DictTypeMiracle.objects.all():

            nomination = {
                'name': n.name,
                'progress': []
            }

            for p in DictProgress.objects.filter(typemiracle__name=n.name):

                progress = {
                    'name': p.name,
                    'viewprogress': []
                }

                for v in dictViewProgress.objects.filter(typemiracle__name=n.name,
                                                         dictprogress__name=p.name):
                    view = {
                        'name': v.name,
                        'statusprogress': []
                    }

                    for s in dictStatusProgress.objects.filter(typemiracle__name=n.name,
                                                               dictprogress__name=p.name,
                                                               dictviewprogress__name=v.name):
                        status = {
                            'name': s.name,
                            'levelprogress': []
                        }

                        for l in dictLevelProgress.objects.filter(typemiracle__name=n.name,
                                                                  dictprogress__name=p.name,
                                                                  dictviewprogress__name=v.name,
                                                                  dictstatusprogress__name=s.name):
                            status['levelprogress'].append(l.name)

                        view['statusprogress'].append(status)

                    progress['viewprogress'].append(view)

                nomination['progress'].append(progress)

            resp.append(nomination)

        return Response(resp)


class GetCSVView(CustomAuthMiddleware, APIView):

    def post(self, request):
        name = f'requests.{now().timestamp()}.csv'
        json = []
        requests = []

        for r in request.data['requests']:
            requests.extend(r)

        qs = Request.objects.all()

        for r in qs:
            if r.id in requests:
                for datareq in r.data.all():
                    data = {
                        'Студент': r.student.fio(),
                        'Дата рождения': r.student.birthday,
                        'Институт': r.student.institut,
                        'Направление обучения': r.student.institut,
                        'Форма обучения': r.student.form,
                        'Источник финансирования': r.student.source_finance,
                        'Уровень обучения': r.student.level,
                        'Курс': r.student.course,

                        'Кампания': r.compaing.name,
                        'Направление заявки': r.typeMiracle.name,
                        'Учебный план': r.learningPlan,
                        'Дата создания': r.CreatedOn,
                        'Статус': r.last_status,

                        "Название мероприятия": datareq.name,
                        "Вид мероприятия": datareq.view_progress,
                        "Статус мероприятия": datareq.status_progress,
                        "Балл за мероприятие": datareq.point
                    }

                    if r.typeMiracle.name == 'Учебная деятельность':
                        data['Баллы за зачётную книжку'] = r.learning_nomination_data.admin_exam_point
                    else:
                        data['Баллы за зачётную книжку'] = 0

                    data['Сумма баллы за мероприятия'] = sum(map(lambda el: el.point, r.data.all()))
                    data['Сумма баллы за мероприятия и зачётную книжку'] = sum(
                        map(lambda el: el.point, r.data.all())) + data['Баллы за зачётную книжку']

                    json.append(data)

        pandas.DataFrame(json).to_csv('./media/' + name, index=False, encoding='utf16', sep='\t')

        return Response({'url': f'/media/{name}'}, 201)
        # return redirect(f'/media/{name}')
        # return FileResponse(open(path, 'rb'), filename='requests.csv')


class GetWordView(CustomAuthMiddleware, APIView):

    def post(self, request):
        data = []
        context = {
            'faces': request.data['big_boys']
        }

        for r in Request.objects.filter(
                compaing_id=request.data['compaing_id'],
                typeMiracle=DictTypeMiracle.objects.get(name=request.data['typeMiracle_id'])
        ):
            datainfo = r.data.all()
            info = []
            sum_points = 0
            last_i = 0

            for i, d in enumerate(datainfo):
                s = f"{i + 1}: {d.name}; {d.progress}; {d.view_progress}; {d.status_progress};{d.level_progress}; {str(d.point)}"
                info.append(s)
                sum_points += d.point
                last_i += 1

            if r.typeMiracle.name == 'Учебная деятельность':  # учебная номинация
                s = f'{last_i + 2}: Балл за оценки: {r.learning_nomination_data.admin_exam_point}'
                info.append(s)
                sum_points += r.learning_nomination_data.admin_exam_point

            data.append({
                'fio': r.student.fio(),
                'profile': r.student.profile,
                'course': r.student.course,
                'status': r.last_status,
                'data': "\n".join(info),
                'ball': sum_points
            })

            qr = r.typeMiracle
            name_nom = qr.name
            context = {
                'nomination': name_nom,
                'data_info': data
            }

        p = create_word_file(context)
        return Response({'url': p}, 201)


class GetBigBoysView(CustomAuthMiddleware, ListAPIView):
    serializer_class = BigBoysSerializer
    queryset = BigBoys.objects.all()


class RemoveDataRowView(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        req: Request = get_object_or_404(Request, id=request.data['id'])

        req.data.filter(id=request.data['bodyId'])[0].delete()

        return Response(status=204)


class RedirectToAdminPanelView(APIView):

    def get(self, request: APIRequest, id: int):
        admin = get_object_or_404(Admin, id=id)

        user = django_authenticate(request, username=admin.login, password=admin.password)
        login(request, user)

        return redirect('/django-admin/')


class SaveStudentEmail(CustomAuthMiddleware, APIView):

    def post(self, request: APIRequest):
        s = get_object_or_404(Student, id=request.data['id'])

        s.email = request.data['email']
        s.save()

        return Response(status=204)


def get_date(fdate):
    return datetime.datetime.strptime(fdate, "%Y-%m-%dT%H:%M:%S.%fZ")


def from_models_to_json(request_qs):
    resp = []
    requests = {}

    for r in request_qs:
        if f'{r.student.id}{r.compaing.id}' in requests:
            requests[f'{r.student.id}{r.compaing.id}'].append(r)
        else:
            requests[f'{r.student.id}{r.compaing.id}'] = [r]

    for key, r_list in requests.items():
        resp.append({})

        for idx, r in enumerate(r_list):
            r: Request
            comments = []
            s = get_object_or_404(Student, id=r.student.id)

            for c in r.comments.all():
                if c.admin is None:
                    user = c.student
                else:
                    user = c.admin

                comments.append({
                    'name': user.fio(),
                    'sendedDate': c.created_at,
                    'imageUrl': user.avatar,
                    'text': c.text,
                })

            if idx == 0:
                resp[-1] = {
                    'id': r.id,
                    'companyId': r.compaing.id,
                    'studentId': r.student.id,
                    'company': r.compaing.name,
                    'fio': r.student.fio(),
                    'subRequests': []
                }

            resp[-1]['subRequests'].append({
                'id': r.id,

                'nomination': r.typeMiracle.name,
                'status': r.last_status,
                'learningPlan': s.learningPlan,
                'createdDate': r.CreatedOn,
                'changedDate': r.LastUpdate,

                'educationForm': r.student.form,
                'phone': r.student.phone,
                'financingSource': r.student.source_finance,
                'institute': r.student.institut,
                'level': r.student.level,
                'direction': r.student.profile,
                'course': r.student.course,

                'percent': str(r.learning_nomination_data.excellent_mark_pecent) if r.learning_nomination_data else '',
                'point': r.learning_nomination_data.admin_exam_point if r.learning_nomination_data else 0,
                'linkToGradebook': r.learning_nomination_data.linkgradebook if r.learning_nomination_data and r.learning_nomination_data.linkgradebook else '',

                'tables': {
                    'header': [
                        'Наименование достижения',
                        'Достижение',
                        'Вид достижения',
                        'Уровень достижения',
                        'Статус достижения',
                        'Дата мероприятия',
                        'Номер документа',
                        'Документ',
                    ],
                    'body': [
                        {
                            'data': [
                                v for k, v in
                                DataInfoMiracleSerializer(row).data.items()
                            ],
                            'points': row.point,
                            'id': row.id
                        } for row in r.data.all()
                    ]
                },
                'comments': comments,
            })

    return resp


def _from_models_to_json(request_qs):
    resp = []
    requests = {}

    for r in request_qs:
        if f'{r.student.id}{r.compaing.id}' in requests:
            requests[f'{r.student.id}{r.compaing.id}'].append(r)
        else:
            requests[f'{r.student.id}{r.compaing.id}'] = [r]

    for key, r_list in requests.items():
        resp.append({})

        for idx, r in enumerate(r_list):
            r: Request
            comments = []
            s = get_object_or_404(Student, id=r.student.id)

            for c in r.comments.all():
                if c.admin is None:
                    user = c.student
                else:
                    user = c.admin

                comments.append({
                    'name': user.fio(),
                    'sendedDate': str(c.created_at),
                    'imageUrl': user.avatar,
                    'text': c.text,
                })

            if idx == 0:
                resp[-1] = {
                    'id': r.id,
                    'companyId': r.compaing.id,
                    'studentId': r.student.id,
                    'company': r.compaing.name,
                    'fio': r.student.fio(),
                    'subRequests': []
                }

            resp[-1]['subRequests'].append({
                'id': r.id,

                'nomination': r.typeMiracle.name,
                'status': r.last_status,
                'learningPlan': s.learningPlan,
                'createdDate': str(r.CreatedOn),
                'changedDate': str(r.LastUpdate),

                'educationForm': r.student.form,
                'phone': r.student.phone,
                'financingSource': r.student.source_finance,
                'institute': r.student.institut,
                'level': r.student.level,
                'direction': r.student.profile,
                'course': r.student.course,

                'percent': str(r.learning_nomination_data.excellent_mark_pecent) if r.learning_nomination_data else '',
                'point': r.learning_nomination_data.admin_exam_point if r.learning_nomination_data else 0,
                'linkToGradebook': r.learning_nomination_data.linkgradebook if r.learning_nomination_data and r.learning_nomination_data.linkgradebook else '',

                'tables': {
                    'header': [
                        'Наименование достижения',
                        'Достижение',
                        'Вид достижения',
                        'Уровень достижения',
                        'Статус достижения',
                        'Дата мероприятия',
                        'Номер документа',
                        'Документ',
                    ],
                    'body': [
                        {
                            'data': [
                                v for k, v in
                                DataInfoMiracleSerializer(row).data.items()
                            ],
                            'points': row.point,
                            'id': row.id
                        } for row in r.data.all()
                    ]
                },
                'comments': comments,
            })

    return resp


def create_word_file(content):
    # doc = DocxTemplate('./media/uploads/template_doc/MiracleProtocol.docx')
    doc = DocxTemplate('/home/adanilin/MiracleMaterial/media/template_doc/MiracleProtocol.docx')
    doc.render(content)
    doc.save('./media/loadDocs/MiracleProtocol_all_q.docx')
    return '/media/loadDocs/MiracleProtocol_all_q.docx'


def create_word_file111(content):
    doc = DocxTemplate('./media/uploads/template_doc/MiracleProtocol.docx')
    doc.render(content)
    doc.save('./media/uploads/loadDocs/MiracleProtocol_all.docx')
    return '/media/uploads/loadDocs/MiracleProtocol_all.docx'
