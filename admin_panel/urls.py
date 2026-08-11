from django.urls import path
from .views import *
from .views import LoginAPIView, LogoutAPIView
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [

    # ===========================
    # Cycle CRUD
    # ===========================
    path(
        "cycles/",
        CycleAPIView.as_view(),
        name="cycle-list-create",
    ),
    path(
        "cycles/<int:pk>/",
        CycleAPIView.as_view(),
        name="cycle-detail",
    ),

    # ===========================
    # Participant CRUD
    # ===========================
    path(
        "participants/",
        ParticipentAPIView.as_view(),
        name="participant-list-create",
    ),
    path(
        "cycles/available/",
        Available_Cycle.as_view(),
        # name="participant-list-create",
    ),
    path(
        "participants/available/",
        AvailableParticipant.as_view(),
        # name="participant-list-create",
    ),
    path(
        "participants/<int:pk>/",
        ParticipentAPIView.as_view(),
        name="participant-detail",
    ),

    # ===========================
    # Participant Cycle Allocation CRUD
    # ===========================
    path(
        "participant-cycles/",
        ParticipentCycleAPIView.as_view(),
        name="participant-cycle-list-create",
    ),
    path(
        "participant-cycles/<int:pk>/",
        ParticipentCycleAPIView.as_view(),
        name="participant-cycle-detail",
    ),

    # ===========================
    # Screen CRUD
    # ===========================
    path(
        "screens/",
        ScreenAPIView.as_view(),
        name="screen-list-create",
    ),
    path(
        "screens/<int:pk>/",
        ScreenAPIView.as_view(),
        name="screen-detail",
    ),
    path(
        "login/",
        LoginAPIView.as_view(),
        name="login",
    ),

    path(
        "logout/",
        LogoutAPIView.as_view(),
        name="logout",
    ),

    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="refresh",
    ),
    path(
        "free-text/",
        LastFreeTextApiView.as_view(),
        name="free-text",
    ),
    path(
        "app-theme/",
        AppThemeAPIView.as_view(),
        name="app-theme",
    )
]