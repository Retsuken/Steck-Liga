from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from api import views

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]), name="swagger-ui"),
    path("health/", views.health),
    path("me/", views.me),
    path("candidates/", views.CandidateBankView.as_view()),
    path("needs/", views.NeedList.as_view()),
    path("needs/<int:pk>/matches/", views.match_api),
    path("invitations/", views.InvitationListCreate.as_view()),
    path("invitations/<int:pk>/decide/", views.invitation_decide),
    path("vacancies/", views.VacancyList.as_view()),
    path("applications/", views.ApplicationCreate.as_view()),
]
