from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts import views as av
from candidates import views as cv
from employers import views as ev

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", av.home, name="home"),
    path("pitch/", av.pitch, name="pitch"),
    path("register/", av.register, name="register"),
    path("login/", av.login_view, name="login"),
    path("logout/", av.logout_view, name="logout"),
    path("confirm/", av.confirm_pending, name="confirm_pending"),
    path("confirm/<uuid:token>/", av.confirm_email, name="confirm_email"),
    path("dashboard/", av.dashboard, name="dashboard"),
    path("c/", cv.dashboard, name="candidate_dashboard"),
    path("c/profile/", cv.profile_edit, name="candidate_profile"),
    path("c/resume/", cv.resume_upload, name="candidate_resume"),
    path("c/profile.pdf", cv.profile_pdf, name="candidate_pdf"),
    path("c/survey/", cv.survey, name="candidate_survey"),
    path("c/test/", cv.test_start, name="candidate_test_start"),
    path("c/test/<int:pk>/", cv.test_take, name="candidate_test_take"),
    path("c/test/<int:pk>/result/", cv.test_result, name="candidate_test_result"),
    path("c/category/", cv.category, name="candidate_category"),
    path("c/invitations/", cv.invitations, name="candidate_invitations"),
    path("c/invitations/<int:pk>/", cv.invitation_detail, name="candidate_invitation"),
    path("c/vacancies/", cv.vacancy_list, name="candidate_vacancies"),
    path("c/vacancies/<int:pk>/", cv.vacancy_detail, name="candidate_vacancy"),
    path("c/applications/", cv.applications, name="candidate_applications"),
    path("c/assignments/", cv.assignments_view, name="candidate_assignments"),
    path("c/assignments/<int:pk>/", cv.assignment_submit, name="candidate_assignment"),
    path("c/settings/", cv.settings_view, name="candidate_settings"),
    path("e/", ev.dashboard, name="employer_dashboard"),
    path("e/company/", ev.company_edit, name="employer_company"),
    path("e/needs/", ev.need_list, name="employer_needs"),
    path("e/needs/new/", ev.need_edit, name="employer_need_new"),
    path("e/needs/<int:pk>/edit/", ev.need_edit, name="employer_need_edit"),
    path("e/needs/<int:pk>/matches/", ev.matches, name="employer_matches"),
    path("e/shortlists/", ev.shortlists, name="employer_shortlists"),
    path("e/bank/", ev.bank, name="employer_bank"),
    path("e/candidates/<int:pk>/", ev.candidate_card, name="employer_candidate"),
    path("e/candidates/<int:pk>/invite/", ev.invite_create, name="employer_invite"),
    path("e/invitations/", ev.invitations, name="employer_invitations"),
    path("e/vacancies/", ev.vacancy_list, name="employer_vacancies"),
    path("e/vacancies/new/", ev.vacancy_edit, name="employer_vacancy_new"),
    path("e/vacancies/<int:pk>/edit/", ev.vacancy_edit, name="employer_vacancy_edit"),
    path("e/vacancies/<int:pk>/apps/", ev.vacancy_apps, name="employer_vacancy_apps"),
    path("e/challenges/new/", ev.challenge_create, name="employer_challenge_new"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
