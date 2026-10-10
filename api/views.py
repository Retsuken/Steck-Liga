from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.serializers import (
    ApplicationSerializer,
    CandidatePublicSerializer,
    InvitationSerializer,
    NeedSerializer,
    VacancySerializer,
)
from candidates.models import CandidateProfile
from matching.engine import bank_candidates, match_candidates
from matching.models import Invitation
from vacancies.models import Application, Vacancy


class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_employer


class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_candidate


@api_view(["GET"])
def me(request):
    u = request.user
    return Response({"id": u.id, "email": u.email, "role": u.role, "email_confirmed": u.email_confirmed})


class CandidateBankView(generics.ListAPIView):
    permission_classes = [IsEmployer]
    serializer_class = CandidatePublicSerializer

    def get_queryset(self):
        ranked = bank_candidates(self.request.query_params)
        return [x["profile"] for x in ranked]


@api_view(["GET"])
@permission_classes([IsEmployer])
def match_api(request, pk):
    need = request.user.company.needs.get(pk=pk)
    ranked = match_candidates(need, request.query_params)
    data = []
    for row in ranked:
        item = CandidatePublicSerializer(row["profile"], context={"request": request}).data
        item["match_score"] = row["score"]
        item["reasons"] = row["reasons"]
        data.append(item)
    return Response(data)


class InvitationListCreate(generics.ListCreateAPIView):
    serializer_class = InvitationSerializer

    def get_queryset(self):
        u = self.request.user
        if u.is_employer:
            return u.company.invitations.all()
        return u.candidate.invitations.all()

    def perform_create(self, serializer):
        if not self.request.user.is_employer:
            raise permissions.PermissionDenied
        salary_from = serializer.validated_data.get("salary_from")
        salary_to = serializer.validated_data.get("salary_to")
        if not salary_from or not salary_to:
            raise permissions.PermissionDenied
        serializer.save(company=self.request.user.company)

    def get_permissions(self):
        return [permissions.IsAuthenticated()]


@api_view(["POST"])
@permission_classes([IsCandidate])
def invitation_decide(request, pk):
    inv = request.user.candidate.invitations.get(pk=pk)
    action = request.data.get("action")
    if action not in ("accept", "decline"):
        return Response({"detail": "action=accept|decline"}, status=400)
    inv.status = "accepted" if action == "accept" else "declined"
    inv.save()
    return Response(InvitationSerializer(inv).data)


class VacancyList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VacancySerializer
    queryset = Vacancy.objects.filter(is_published=True).select_related("company")


class ApplicationCreate(generics.CreateAPIView):
    permission_classes = [IsCandidate]
    serializer_class = ApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.candidate)


class NeedList(generics.ListCreateAPIView):
    permission_classes = [IsEmployer]
    serializer_class = NeedSerializer

    def get_queryset(self):
        return self.request.user.company.needs.all()

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    return Response({"status": "ok", "service": "stekliga"})
