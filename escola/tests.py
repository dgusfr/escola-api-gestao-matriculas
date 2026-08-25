from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from escola.models import Curso, Estudante, Matricula


class AutenticacaoTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        self.estudante = Estudante.objects.create(
            nome="Carlos Silva",
            email="carlos@test.com",
            cpf="11122233344",
            data_nascimento="2000-01-15",
            celular="11988887777",
        )

    def test_requisicao_sem_autenticacao_retorna_401(self):
        """Verifica se requisição não autenticada é bloqueada com status 401"""
        self.client.force_authenticate(user=None)
        response = self.client.get("/estudantes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_requisicao_com_autenticacao_retorna_200(self):
        """Verifica se requisição autenticada tem acesso permitido"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/estudantes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EstudantesTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        self.client.force_authenticate(user=self.user)
        self.estudante_1 = Estudante.objects.create(
            nome="Ana Paula",
            email="ana@test.com",
            cpf="12345678901",
            data_nascimento="2001-05-10",
            celular="11999990001",
        )
        self.estudante_2 = Estudante.objects.create(
            nome="Bruno Lima",
            email="bruno@test.com",
            cpf="98765432100",
            data_nascimento="1999-10-20",
            celular="11999990002",
        )

    def test_listar_estudantes_com_paginacao(self):
        """Verifica listagem de estudantes e formato paginado"""
        response = self.client.get("/estudantes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)

    def test_criar_estudante_sucesso(self):
        """Verifica criação de um novo estudante via POST"""
        dados = {
            "nome": "Carla Mendes",
            "email": "carla@test.com",
            "cpf": "55566677788",
            "data_nascimento": "2002-03-12",
            "celular": "11987654321",
        }
        response = self.client.post("/estudantes/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nome"], "Carla Mendes")
        self.assertEqual(Estudante.objects.count(), 3)

    def test_detalhar_estudante(self):
        """Verifica consulta de detalhes de um estudante específico via GET"""
        response = self.client.get(f"/estudantes/{self.estudante_1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], self.estudante_1.nome)

    def test_atualizar_estudante(self):
        """Verifica atualização de estudante via PATCH"""
        dados_atualizacao = {"celular": "11977776666"}
        response = self.client.patch(
            f"/estudantes/{self.estudante_1.id}/", dados_atualizacao, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.estudante_1.refresh_from_db()
        self.assertEqual(self.estudante_1.celular, "11977776666")

    def test_excluir_estudante(self):
        """Verifica exclusão de estudante via DELETE"""
        response = self.client.delete(f"/estudantes/{self.estudante_1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Estudante.objects.count(), 1)

    def test_buscar_estudante_por_nome(self):
        """Verifica busca textual por nome (?search=)"""
        response = self.client.get("/estudantes/?search=Ana")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["nome"], "Ana Paula")

    def test_ordenar_estudantes(self):
        """Verifica ordenação alfabética decrescente (?ordering=-nome)"""
        response = self.client.get("/estudantes/?ordering=-nome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["nome"], "Bruno Lima")


class CursosTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        self.client.force_authenticate(user=self.user)
        self.curso_1 = Curso.objects.create(codigo="PY01", descricao="Python Básico", nivel="B")
        self.curso_2 = Curso.objects.create(
            codigo="DJ01", descricao="Django Intermediário", nivel="I"
        )
        self.curso_3 = Curso.objects.create(
            codigo="JS01", descricao="JavaScript Avançado", nivel="A"
        )

    def test_listar_cursos(self):
        """Verifica listagem de cursos"""
        response = self.client.get("/cursos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_criar_curso_sucesso(self):
        """Verifica criação de um novo curso via POST"""
        dados = {"codigo": "REACT01", "descricao": "React para Iniciantes", "nivel": "B"}
        response = self.client.post("/cursos/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Curso.objects.count(), 4)

    def test_detalhar_curso(self):
        """Verifica consulta de detalhes de um curso"""
        response = self.client.get(f"/cursos/{self.curso_1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["codigo"], "PY01")

    def test_atualizar_curso(self):
        """Verifica atualização de curso via PATCH"""
        dados = {"descricao": "Python para Data Science"}
        response = self.client.patch(f"/cursos/{self.curso_1.id}/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.curso_1.refresh_from_db()
        self.assertEqual(self.curso_1.descricao, "Python para Data Science")

    def test_excluir_curso(self):
        """Verifica exclusão de curso via DELETE"""
        response = self.client.delete(f"/cursos/{self.curso_1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Curso.objects.count(), 2)

    def test_filtrar_cursos_por_nivel(self):
        """Verifica filtro por nível (?nivel=B)"""
        response = self.client.get("/cursos/?nivel=B")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["codigo"], "PY01")

    def test_buscar_curso_por_descricao(self):
        """Verifica busca textual por descrição do curso (?search=Django)"""
        response = self.client.get("/cursos/?search=Django")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["codigo"], "DJ01")


class MatriculasTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        self.client.force_authenticate(user=self.user)
        self.estudante = Estudante.objects.create(
            nome="Lucas Rocha",
            email="lucas@test.com",
            cpf="33344455566",
            data_nascimento="1998-07-22",
            celular="11966665555",
        )
        self.curso = Curso.objects.create(codigo="DOCKER01", descricao="Docker Básico", nivel="B")
        self.matricula = Matricula.objects.create(
            estudante=self.estudante, curso=self.curso, periodo="M"
        )

    def test_listar_matriculas(self):
        """Verifica listagem paginada de matrículas"""
        response = self.client.get("/matriculas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_criar_matricula_sucesso(self):
        """Verifica criação de nova matrícula via POST"""
        novo_curso = Curso.objects.create(codigo="K8S01", descricao="Kubernetes", nivel="A")
        dados = {"estudante": self.estudante.id, "curso": novo_curso.id, "periodo": "N"}
        response = self.client.post("/matriculas/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Matricula.objects.count(), 2)

    def test_detalhar_matricula(self):
        """Verifica consulta de detalhes de matrícula via GET"""
        response = self.client.get(f"/matriculas/{self.matricula.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["estudante"], self.estudante.id)
        self.assertEqual(response.data["periodo"], "M")

    def test_atualizar_periodo_matricula(self):
        """Verifica alteração de período da matrícula via PATCH"""
        dados = {"periodo": "V"}
        response = self.client.patch(f"/matriculas/{self.matricula.id}/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.matricula.refresh_from_db()
        self.assertEqual(self.matricula.periodo, "V")

    def test_excluir_matricula(self):
        """Verifica cancelamento/exclusão de matrícula via DELETE"""
        response = self.client.delete(f"/matriculas/{self.matricula.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Matricula.objects.count(), 0)

    def test_filtrar_matriculas_por_periodo(self):
        """Verifica filtro por período (?periodo=M)"""
        response = self.client.get("/matriculas/?periodo=M")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_buscar_matricula_por_nome_estudante(self):
        """Verifica busca textual de matrícula por nome do estudante (?search=Lucas)"""
        response = self.client.get("/matriculas/?search=Lucas")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class MatriculasRelacionadasTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        self.client.force_authenticate(user=self.user)
        self.estudante = Estudante.objects.create(
            nome="Mariana Dias",
            email="mariana@test.com",
            cpf="44455566677",
            data_nascimento="2003-11-05",
            celular="11944443333",
        )
        self.curso_1 = Curso.objects.create(codigo="JAVA01", descricao="Java Completo", nivel="I")
        self.curso_2 = Curso.objects.create(
            codigo="SQL01", descricao="SQL para Iniciantes", nivel="B"
        )
        Matricula.objects.create(estudante=self.estudante, curso=self.curso_1, periodo="M")
        Matricula.objects.create(estudante=self.estudante, curso=self.curso_2, periodo="N")

    def test_listar_cursos_de_um_estudante(self):
        """Verifica endpoint /estudantes/<id>/matriculas/ listando os cursos matriculados"""
        response = self.client.get(f"/estudantes/{self.estudante.id}/matriculas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        # Verifica se traz o nome do curso e o período por extenso
        cursos_nomes = [item["curso"] for item in response.data["results"]]
        self.assertIn("Java Completo", cursos_nomes)
        self.assertIn("SQL para Iniciantes", cursos_nomes)

    def test_listar_estudantes_de_um_curso(self):
        """Verifica endpoint /cursos/<id>/matriculas/ listando os estudantes matriculados"""
        response = self.client.get(f"/cursos/{self.curso_1.id}/matriculas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["estudante_nome"], "Mariana Dias")
