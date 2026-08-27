from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
    ordering_fields = ["id", "periodo", "estudante__nome", "status"]
    ordering = ["id"]

    def get_queryset(self):
        queryset = Matricula.objects.all().order_by("id")
        periodo = self.request.query_params.get("periodo")
        status_matricula = self.request.query_params.get("status")

        if periodo:
            queryset = queryset.filter(periodo=periodo.upper())
        if status_matricula:
            queryset = queryset.filter(status=status_matricula.upper())

        return queryset

    @action(detail=True, methods=["patch"])
    def trancar(self, request, pk=None):
        """Tranca uma matrícula ativa."""
        matricula = self.get_object()
        if matricula.status != "A":
            return Response(
                {"erro": "Apenas matrículas ativas podem ser trancadas."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        matricula.status = "T"
        matricula.save()
        return Response({"status": "Matrícula trancada com sucesso."})

    @action(detail=True, methods=["patch"])
    def cancelar(self, request, pk=None):
        """Cancela uma matrícula (ativa ou trancada)."""
        matricula = self.get_object()
        if matricula.status not in ["A", "T"]:
            return Response(
                {"erro": "Apenas matrículas ativas ou trancadas podem ser canceladas."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        matricula.status = "C"
        matricula.save()
        return Response({"status": "Matrícula cancelada com sucesso."})

    @action(detail=True, methods=["patch"])
    def finalizar(self, request, pk=None):
        """Finaliza uma matrícula (conclusão de curso)."""
        matricula = self.get_object()
        if matricula.status != "A":
            return Response(
                {"erro": "Apenas matrículas ativas podem ser finalizadas."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        matricula.status = "F"
        matricula.save()
        return Response({"status": "Matrícula finalizada com sucesso."})


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
