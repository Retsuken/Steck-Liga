from rest_framework import serializers
from candidates.models import CandidateProfile, FspAchievement
from employers.models import Company, HiringNeed
from matching.models import Invitation
from vacancies.models import Application, Vacancy


class FspSerializer(serializers.ModelSerializer):
    class Meta:
        model = FspAchievement
        fields = ("event_name", "year", "place", "rating_points", "discipline")


class CandidatePublicSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category_label")
    fsp_points = serializers.IntegerField()
    has_fsp = serializers.BooleanField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()

    class Meta:
        model = CandidateProfile
        fields = (
            "id",
            "full_name",
            "city",
            "category",
            "specialization",
            "confirmed_grade",
            "last_test_score",
            "stack",
            "soft_skills",
            "years_experience",
            "about",
            "fsp_points",
            "has_fsp",
            "email",
            "phone",
            "achievements",
        )

    def _visible(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.is_employer:
            return False
        from matching.engine import contacts_visible

        return contacts_visible(request.user.company, obj)

    def get_email(self, obj):
        return obj.user.email if self._visible(obj) else None

    def get_phone(self, obj):
        return obj.phone if self._visible(obj) else None

    def get_achievements(self, obj):
        if not obj.show_fsp:
            return []
        return FspSerializer(obj.achievements.all(), many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not instance.show_about:
            data["about"] = None
        if not instance.show_stack:
            data["stack"] = []
        return data


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name", "description", "industry", "city", "site")


class NeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringNeed
        fields = (
            "id",
            "title",
            "team_about",
            "description",
            "specialization",
            "grade",
            "stack",
            "salary_from",
            "salary_to",
        )


class InvitationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Invitation
        fields = (
            "id",
            "candidate",
            "need",
            "vacancy",
            "offer_text",
            "salary_from",
            "salary_to",
            "contact_method",
            "status",
            "company_name",
            "created_at",
        )
        read_only_fields = ("status", "created_at", "company_name")


class VacancySerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Vacancy
        fields = (
            "id",
            "title",
            "description",
            "specialization",
            "grade",
            "stack",
            "salary_from",
            "salary_to",
            "city",
            "remote",
            "company",
        )


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ("id", "vacancy", "cover_letter", "status", "created_at")
        read_only_fields = ("status", "created_at")
