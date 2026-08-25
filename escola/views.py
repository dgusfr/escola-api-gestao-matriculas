from rest_framework import filters, generics, viewsets

from escola.models import Curso, Estudante, Matricula
from escola.serializers import (
    CursoSerializer,
    EstudanteSerializer,
    ListaMatriculasCursoSerializer,
    ListaMatriculasEstudanteSerializer,
    MatriculaSerializer,
)


class EstudanteViewSet(viewsets.ModelViewSet):
    """Exibindo todos os estudantes com suporte a busca e ordenação"""

    queryset = Estudante.objects.all().order_by("nome")
    serializer_class = EstudanteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nome", "cpf", "email"]
    ordering_fields = ["nome", "id", "data_nascimento"]
    ordering = ["nome"]


class CursoViewSet(viewsets.ModelViewSet):
    """Exibindo todos os cursos com suporte a busca, filtros e ordenação"""

    serializer_class = CursoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["codigo", "descricao"]
    ordering_fields = ["codigo", "descricao", "nivel"]
    ordering = ["codigo"]

    def get_queryset(self):
        queryset = Curso.objects.all().order_by("codigo")
        nivel = self.request.query_params.get("nivel")
        if nivel:
            queryset = queryset.filter(nivel=nivel.upper())
        return queryset


class MatriculaViewSet(viewsets.ModelViewSet):
    """Exibindo todas as matrículas com suporte a busca, filtros e ordenação"""

    serializer_class = MatriculaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["estudante__nome", "curso__codigo", "curso__descricao"]
    ordering_fields = ["id", "periodo", "estudante__nome"]
    ordering = ["id"]

    def get_queryset(self):
        queryset = Matricula.objects.all().order_by("id")
        periodo = self.request.query_params.get("periodo")
        if periodo:
            queryset = queryset.filter(periodo=periodo.upper())
        return queryset


class ListaMatriculaEstudante(generics.ListAPIView):
    """Listando as matrículas de um estudante"""

    serializer_class = ListaMatriculasEstudanteSerializer

    def get_queryset(self):
        return Matricula.objects.filter(estudante_id=self.kwargs["pk"]).order_by("id")


class ListaMatriculaCurso(generics.ListAPIView):
    """Listando os estudantes matriculados em um curso"""

    serializer_class = ListaMatriculasCursoSerializer

    def get_queryset(self):
        return Matricula.objects.filter(curso_id=self.kwargs["pk"]).order_by("id")
