from django.db import models
from django.utils.timezone import now


# Create your models here.

class Student(models.Model):
    '''Студенты которые подают заявку на стипендию,
    после первой авторизации данные появятся тут'''
    login = models.CharField(unique=True, max_length=256)
    password = models.CharField(unique=True, max_length=256)
    token = models.UUIDField(max_length=256, unique=True)

    lastname = models.CharField("Фамилия", max_length=256)
    firstname = models.CharField("Имя", max_length=256)
    patronymic = models.CharField("Отчество", max_length=256)
    birthday = models.DateField("Дата рождения")
    learningPlan = models.CharField(max_length=255)
    email = models.EmailField(max_length=256, blank=True, null=True)

    phone = models.CharField("Телефон", max_length=256)
    institut = models.CharField("Интститут", max_length=256)
    profile = models.CharField("Направление", max_length=256)
    form = models.CharField("Форма обучения", max_length=256)
    source_finance = models.CharField("Источник финансирования", max_length=256)
    level = models.CharField("Уровень обучения", max_length=256)
    course = models.IntegerField("Курс")

    date_create_profile = models.DateField("Дата создания")
    isDeleted = models.BooleanField(default=False)

    avatar = models.URLField()

    def __str__(self):
        return str(self.lastname + " " + self.firstname + " " + self.patronymic).strip()

    def fio(self):
        return f'{self.lastname} {self.firstname} {self.patronymic}'

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


class Admin(models.Model):
    '''Админы'''
    login = models.CharField(unique=True, max_length=256)
    password = models.CharField(unique=True, max_length=256)

    lastname = models.CharField("Фамилия", max_length=256)
    firstname = models.CharField("Имя", max_length=256)
    patronymic = models.CharField("Отчество", max_length=256)
    email = models.EmailField(max_length=256, blank=True, null=True)

    avatar = models.URLField()

    def __str__(self):
        return str(self.lastname + " " + self.firstname + " " + self.patronymic).strip()

    def fio(self):
        return f'{self.lastname} {self.firstname} {self.patronymic}'

    class Meta:
        verbose_name = 'Админ'
        verbose_name_plural = 'Админы'


class HistoryChangeRequest(models.Model):
    '''История изменения полей в таблицы Студенты, возможно изменение автоматически при проверке авторизации'''
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateTimeField("Дата изменения", default=now)
    json = models.JSONField()


class Compaing(models.Model):
    '''Комапания'''
    date_created = models.DateField("Дата создания", auto_now=True)
    name = models.CharField("Название компании", max_length=256)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    show_student_points = models.BooleanField(default=True)
    isDeleted = models.BooleanField("Удалено", default=False)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'


class LearningNominationData(models.Model):
    linkgradebook = models.TextField(blank=True)
    excellent_mark_pecent = models.IntegerField("Очкнка(отлично),%", default=0)
    admin_exam_point = models.PositiveIntegerField("Балл за оценку за экзамены (выставляет админ)", default=0)


class Comments(models.Model):
    """ Комментарии """
    student = models.ForeignKey(Student, models.CASCADE, null=True, blank=True)
    admin = models.ForeignKey(Admin, models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)


# class dictTypeEvent(models.Model):
#     '''Справочник вида мероприятия, зависит от типа стипендии'''
#     name = models.CharField("Название", max_length=255)
#     type_miracle = models.ForeignKey(dictTypeMiracle, on_delete=models.CASCADE)
#     CreatedOn = models.DateField()
#     isDeleted = models.BooleanField("Удалено", default=False)
#
#     def __str__(self) -> str:
#         return self.name
#
#
# class dictStatusEvent(models.Model):
#     '''Справочник статуса мероприятия '''
#     name = models.CharField("Название", max_length=255)
#     type_miracle = models.ForeignKey(dictTypeMiracle, on_delete=models.CASCADE)
#     CreatedOn = models.DateField()
#     isDeleted = models.BooleanField("Удалено", default=False)
#
#     def __str__(self) -> str:
#         return self.name
#
#
# class dictTypeWork(models.Model):
#     '''Справочник вида работ, зависит от типа стипендии'''
#     name = models.CharField("Название", max_length=255)
#     type_miracle = models.ForeignKey(dictTypeMiracle, on_delete=models.CASCADE)
#     CreatedOn = models.DateField()
#     isDeleted = models.BooleanField("Удалено", default=False)
#
#     def __str__(self) -> str:
#         return self.name
#
#
# class dictRoleStudentToWork(models.Model):
#     ''' Справочник роли студента в мероприятии '''
#     name = models.CharField("Название", max_length=255)
#     type_miracle = models.ForeignKey(dictTypeMiracle, on_delete=models.CASCADE)
#     CreatedOn = models.DateField()
#     isDeleted = models.BooleanField("Удалено", default=False)
#
#     def __str__(self) -> str:
#         return self.name
#
#
# class dictWinnerPlace(models.Model):
#     name = models.CharField("Название", max_length=255)
#     type_miracle = models.ForeignKey(dictTypeMiracle, on_delete=models.CASCADE)
#     CreatedOn = models.DateField()
#     isDeleted = models.BooleanField("Удалено", default=False)
#
#     def __str__(self) -> str:
#         return self.name
#
#
# class DataInfoMiracle(models.Model):
#     "Таблища с данными предоставленные студентом на стипендию"
#     type_micacle = models.CharField(max_length=256)
#     type_event = models.CharField(max_length=256)
#     type_work = models.CharField(max_length=256)
#     date_event = models.CharField(max_length=256)
#     number_of_docs = models.CharField("Номер документа", max_length=256)
#     winner_place = models.CharField(max_length=256)
#     role_student = models.CharField(max_length=256)
#     linkDocs = models.FileField(upload_to='uploads/')
#     point = models.PositiveIntegerField(default=0)
#
#
# class RequestOld(models.Model):
#     '''Заявка пользователя на стипендию'''
#     compaing = models.ForeignKey(Compaing, on_delete=models.CASCADE)
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     typeMiracle = models.ForeignKey(dictTypeMiracle, on_delete=models.CASCADE)
#     learningPlan = models.ForeignKey(dictLearningPlan, on_delete=models.CASCADE)
#     last_status = models.CharField("Текущий статус", max_length=156)
#     CreatedOn = models.DateTimeField("Дата создания", default=datetime.datetime.now())
#     LastUpdate = models.DateTimeField("Последнее изменеиние", default=datetime.datetime.now())
#     isDeleted = models.BooleanField("Удалено", default=False)
#     comments = models.ManyToManyField(Comments, blank=True)
#     #data = models.ManyToManyField(DataInfoMiracle)
#     data = models.OneToOneField(DataInfoMiracle, on_delete=models.CASCADE)
#     learning_nomination_data = models.ForeignKey(LearningNominationData, models.CASCADE, blank=True, null=True)


class Notification(models.Model):
    """ Объявления """
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)


# ----new variant

class DataInfoMiracle(models.Model):
    "Таблища с данными предоставленные студентом на стипендию"
    type_miracle = models.CharField(max_length=256)  # номинация
    name = models.CharField(max_length=512, default="")  # Название мероприятия
    progress = models.CharField(max_length=256)  # Достижение
    view_progress = models.CharField(max_length=256)  # Вид достижения
    status_progress = models.CharField(max_length=512)  # Статус мероприятия(международный, региональный)
    level_progress = models.CharField(max_length=512)  # Уровень достижения
    date_event = models.DateField("Дата мероприятия")  # Дата мероприятия
    number_of_docs = models.CharField("Номер документа", max_length=256)
    linkDocs = models.TextField(blank=True)
    point = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = verbose_name_plural = 'Таблица с данными предоставленные студентом на стипендию'


class DictTypeMiracle(models.Model):
    "Тип повышенной стипендии: Учебная, Научно - исследовательская, общественная, Культурно-творческая, Спортивная"
    name = models.CharField("Название", max_length=256)
    isDeleted = models.BooleanField("Удалено", default=False)
    CreadedOn = models.DateTimeField("Дата создания")

    class Meta:
        verbose_name = verbose_name_plural = 'Тип повышенной стипендии'

    def __str__(self):
        return f'{self.name}'


class Request(models.Model):
    '''Заявка пользователя на стипендию'''
    compaing = models.ForeignKey(Compaing, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    typeMiracle = models.ForeignKey(DictTypeMiracle, on_delete=models.CASCADE)
    learningPlan = models.CharField(max_length=255)
    last_status = models.CharField("Текущий статус", max_length=156)
    CreatedOn = models.DateTimeField("Дата создания", default=now)
    LastUpdate = models.DateTimeField("Последнее изменеиние", default=now)
    isDeleted = models.BooleanField("Удалено", default=False)
    comments = models.ManyToManyField(Comments, blank=True)
    data = models.ManyToManyField(DataInfoMiracle, blank=True)
    learning_nomination_data = models.ForeignKey(LearningNominationData, models.CASCADE, blank=True, null=True)


class DictProgress(models.Model):
    '''Достижения(заголовки таблиц по схеме в ворде)'''
    typemiracle = models.ForeignKey(DictTypeMiracle, related_name="dict_progress", on_delete=models.CASCADE)
    name = models.CharField("Достижение", max_length=255)
    isDeleted = models.BooleanField(default=False)
    CreatedOn = models.DateTimeField(default=now)
    DeletedOn = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Достижения'

    def __str__(self) -> str:
        return f'{self.name} | {self.typemiracle.name}'


class dictViewProgress(models.Model):
    '''Вид достижения '''
    typemiracle = models.ForeignKey(DictTypeMiracle, related_name="dict_view_progress", on_delete=models.CASCADE)
    dictprogress = models.ForeignKey(DictProgress, on_delete=models.CASCADE)
    name = models.CharField("Вид достижения", max_length=255)
    isDeleted = models.BooleanField(default=False)
    CreatedOn = models.DateTimeField(default=now)
    DeletedOn = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Вид достижения'

    def __str__(self) -> str:
        return f'{self.name} | {self.typemiracle.name}'


class dictStatusProgress(models.Model):
    '''Статус мероприятия(международный, региональный)'''
    typemiracle = models.ForeignKey(DictTypeMiracle, related_name="dict_status_progress", on_delete=models.CASCADE)
    dictprogress = models.ForeignKey(DictProgress, on_delete=models.CASCADE)
    dictviewprogress = models.ForeignKey(dictViewProgress, on_delete=models.CASCADE)
    name = models.CharField("Статус достижения", max_length=255)
    isDeleted = models.BooleanField(default=False)
    CreatedOn = models.DateTimeField(default=now)
    DeletedOn = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Статус мероприятия'

    def __str__(self) -> str:
        return f'{self.name} | {self.dictviewprogress.name} | {self.typemiracle.name}'


class dictLevelProgress(models.Model):
    '''Уровень достижения'''
    typemiracle = models.ForeignKey(DictTypeMiracle, related_name="dict_level_progress",on_delete=models.CASCADE)
    dictprogress = models.ForeignKey(DictProgress, on_delete=models.CASCADE)
    dictviewprogress = models.ForeignKey(dictViewProgress, on_delete=models.CASCADE)
    dictstatusprogress = models.ForeignKey(dictStatusProgress, on_delete=models.CASCADE)
    name = models.CharField("Уровень достижения", max_length=255)
    isDeleted = models.BooleanField(default=False)
    CreatedOn = models.DateTimeField(default=now)
    DeletedOn = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Уровень достижения'

    def __str__(self) -> str:
        return f'{self.name} | {self.dictstatusprogress.name} | {self.dictviewprogress.name} | {self.typemiracle.name}'


class BigBoys(models.Model):
    """ Должностные лица для word """
    fio = models.CharField(max_length=150)
