from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from escola.views import (
    CursoViewSet,
    EstudanteViewSet,
    ListaMatriculaCurso,
    ListaMatriculaEstudante,
    MatriculaViewSet,
)

router = routers.DefaultRouter()
router.register("estudantes", EstudanteViewSet, basename="Estudantes")
router.register("cursos", CursoViewSet, basename="Cursos")
router.register("matriculas", MatriculaViewSet, basename="Matriculas")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("estudantes/<int:pk>/matriculas/", ListaMatriculaEstudante.as_view()),
    path("cursos/<int:pk>/matriculas/", ListaMatriculaCurso.as_view()),
    # JWT Authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # OpenAPI 3 Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
