from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from escola.models import Curso, Estudante, Matricula


def gerar_token_para(user):
    """Helper: gera e retorna o access token JWT de um usuário."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class AutenticacaoJWTTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        self.token_url = "/api/token/"
        self.refresh_url = "/api/token/refresh/"

    def test_obter_token_com_credenciais_validas(self):
        """Verifica que POST /api/token/ com usuário e senha válidos retorna access e refresh token"""
        response = self.client.post(
            self.token_url,
            {"username": "admin_test", "password": "secretpassword123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obter_token_com_credenciais_invalidas_retorna_401(self):
        """Verifica que credenciais erradas retornam 401"""
        response = self.client.post(
            self.token_url,
            {"username": "admin_test", "password": "senhaerrada"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_retorna_novo_access_token(self):
        """Verifica que POST /api/token/refresh/ retorna um novo access token"""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            self.refresh_url,
            {"refresh": str(refresh)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_requisicao_sem_token_retorna_401(self):
        """Verifica que requisições sem token são bloqueadas com 401"""
        response = self.client.get("/estudantes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_requisicao_com_token_invalido_retorna_401(self):
        """Verifica que token malformado é rejeitado com 401"""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer token.invalido.aqui")
        response = self.client.get("/estudantes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_requisicao_com_token_valido_retorna_200(self):
        """Verifica que access token JWT válido permite acesso à API"""
        token = gerar_token_para(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/estudantes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EstudantesTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        token = gerar_token_para(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.estudante_1 = Estudante.objects.create(
            nome="Ana Paula",
            email="ana@test.com",
            cpf="01234567893",
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
        """Verifica criação de um novo estudante com dados válidos"""
        dados = {
            "nome": "Carla Mendes",
            "email": "carla@test.com",
            "cpf": "44455566619",
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

    def test_recusar_estudante_com_cpf_invalido(self):
        """Verifica rejeição (400) ao tentar criar estudante com dígitos de CPF inválidos"""
        dados = {
            "nome": "Marcos Teste",
            "email": "marcos@test.com",
            "cpf": "12345678999",  # Dígitos verificadores incorretos
            "data_nascimento": "2000-01-01",
            "celular": "11999998888",
        }
        response = self.client.post("/estudantes/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", response.data)

    def test_recusar_estudante_com_cpf_digitos_iguais(self):
        """Verifica rejeição (400) para CPF com 11 dígitos repetidos (ex: 11111111111)"""
        dados = {
            "nome": "Jose Repetido",
            "email": "jose@test.com",
            "cpf": "11111111111",
            "data_nascimento": "2000-01-01",
            "celular": "11999998888",
        }
        response = self.client.post("/estudantes/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", response.data)

    def test_recusar_estudante_com_nome_invalido(self):
        """Verifica rejeição (400) ao tentar cadastrar nome com números"""
        dados = {
            "nome": "João 123 Silva",
            "email": "joao@test.com",
            "cpf": "44455566619",
            "data_nascimento": "2000-01-01",
            "celular": "11999998888",
        }
        response = self.client.post("/estudantes/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nome", response.data)

    def test_recusar_estudante_com_celular_invalido(self):
        """Verifica rejeição (400) ao tentar cadastrar celular fora do padrão"""
        dados = {
            "nome": "Lucas Santos",
            "email": "lucas.s@test.com",
            "cpf": "44455566619",
            "data_nascimento": "2000-01-01",
            "celular": "12345",  # Menos dígitos do que o exigido
        }
        response = self.client.post("/estudantes/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("celular", response.data)

    def test_recusar_estudante_com_cpf_duplicado(self):
        """Verifica rejeição (400) ao tentar cadastrar CPF já existente no banco"""
        dados = {
            "nome": "Outro Estudante",
            "email": "outro@test.com",
            "cpf": "01234567893",  # Mesmo CPF de estudante_1
            "data_nascimento": "1995-05-15",
            "celular": "11999997777",
        }
        response = self.client.post("/estudantes/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CursosTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        token = gerar_token_para(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
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

    def test_recusar_curso_codigo_duplicado(self):
        """Verifica rejeição (400) ao tentar criar curso com código já existente"""
        dados = {"codigo": "PY01", "descricao": "Outro Curso Python", "nivel": "A"}
        response = self.client.post("/cursos/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MatriculasTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        token = gerar_token_para(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.estudante = Estudante.objects.create(
            nome="Lucas Rocha",
            email="lucas@test.com",
            cpf="11144477735",
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

    def test_recusar_matricula_duplicada(self):
        """Verifica bloqueio (400) ao tentar matricular o mesmo estudante 2 vezes no mesmo curso"""
        dados = {"estudante": self.estudante.id, "curso": self.curso.id, "periodo": "V"}
        response = self.client.post("/matriculas/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_filtrar_matriculas_por_status(self):
        """Verifica filtro por status (?status=A)"""
        response = self.client.get("/matriculas/?status=A")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        response_inativo = self.client.get("/matriculas/?status=C")
        self.assertEqual(len(response_inativo.data["results"]), 0)

    def test_trancar_matricula_ativa_sucesso(self):
        """Verifica se é possível trancar uma matrícula ativa via action PATCH"""
        response = self.client.patch(f"/matriculas/{self.matricula.id}/trancar/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.matricula.refresh_from_db()
        self.assertEqual(self.matricula.status, "T")

    def test_cancelar_matricula_ativa_sucesso(self):
        """Verifica se é possível cancelar uma matrícula ativa via action PATCH"""
        response = self.client.patch(f"/matriculas/{self.matricula.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.matricula.refresh_from_db()
        self.assertEqual(self.matricula.status, "C")

    def test_finalizar_matricula_ativa_sucesso(self):
        """Verifica se é possível finalizar uma matrícula ativa via action PATCH"""
        response = self.client.patch(f"/matriculas/{self.matricula.id}/finalizar/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.matricula.refresh_from_db()
        self.assertEqual(self.matricula.status, "F")

    def test_trancar_matricula_inativa_retorna_400(self):
        """Verifica que não é possível trancar uma matrícula que não está ativa"""
        self.matricula.status = "C"
        self.matricula.save()
        response = self.client.patch(f"/matriculas/{self.matricula.id}/trancar/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Apenas matrículas ativas", response.data["erro"])


class MatriculasRelacionadasTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin_test", password="secretpassword123")
        token = gerar_token_para(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.estudante = Estudante.objects.create(
            nome="Mariana Dias",
            email="mariana@test.com",
            cpf="22233344405",
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
        cursos_nomes = [item["curso"] for item in response.data["results"]]
        self.assertIn("Java Completo", cursos_nomes)
        self.assertIn("SQL para Iniciantes", cursos_nomes)

    def test_listar_estudantes_de_um_curso(self):
        """Verifica endpoint /cursos/<id>/matriculas/ listando os estudantes matriculados"""
        response = self.client.get(f"/cursos/{self.curso_1.id}/matriculas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["estudante_nome"], "Mariana Dias")
