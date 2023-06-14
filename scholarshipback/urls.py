from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('auth/student/login/', views.StudentSignInView.as_view()),
    path('auth/student/detail/', views.GetStudentDataView.as_view()),
    path('auth/admin/login/', views.AdminSignInView.as_view()),
    path('auth/admin/detail/', views.GetAdminDataView.as_view()),
    path('auth/refresh/', views.UpdateAccessTokenView.as_view()),

    path('auth/redirect-to-admin-panel/<int:id>/', views.RedirectToAdminPanelView.as_view()),

    path('auth/save-student-email/', views.SaveStudentEmail.as_view()),

    path('companies/get/', views.CompaingViewList.as_view()),
    path('companies/create/', views.CompaningViewCreate.as_view()),
    path('companies/detail/', views.CompaingViewDetail.as_view()),
    path('companies/check-show-student-points/', views.CheckShowStudentPointsView.as_view()),

    path('requests/get/', views.RequestViewList.as_view()),
    path('requests/set-admin-row-point/', views.SetAdminPointForRow.as_view()),
    path('requests/save/', views.SaveRequestView.as_view()),
    path('requests/learning/save/', views.SaveLearingRequestView.as_view()),
    path('requests/create/', views.CreateRequestView.as_view()),
    path('requests/remove-data/', views.RemoveDataRowView.as_view()),
    path('requests/add-row/', views.AddRowView.as_view()),
    path('notifications/get/', views.NotificationListView.as_view()),
    path('notifications/detail/', views.NotificationDetailView.as_view()),
    path('comments/create/', views.AddCommentView.as_view()),

    path('set-image/', views.SetImageView.as_view()),

    path('nominations/get/', views.dictTypeMiracleView.as_view()),
    path('progress/get/', views.dictProgressView.as_view()),
    path('view-progress/get/', views.dictViewProgressView.as_view()),
    path('status-progress/get/', views.dictStatusProgressView.as_view()),
    path('level-progress/get/', views.dictLevelProgressView.as_view()),
    path('table/get/', views.GetDictView.as_view()),

    path('statistic/', views.GetWordView.as_view()),
    path('get-csv/', views.GetCSVView.as_view()),
    path('bb/', views.GetBigBoysView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
