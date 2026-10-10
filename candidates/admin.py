from django.contrib import admin
from candidates.models import CandidateProfile, Experience, FspAchievement, GradeHistory

admin.site.register(CandidateProfile)
admin.site.register(Experience)
admin.site.register(FspAchievement)
admin.site.register(GradeHistory)
