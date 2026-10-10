from django.contrib import admin
from testing.models import Assignment, AttemptItem, EmployerChallenge, Question, TestAttempt

admin.site.register(Question)
admin.site.register(TestAttempt)
admin.site.register(AttemptItem)
admin.site.register(EmployerChallenge)
admin.site.register(Assignment)
