# API de Gestão de Matrículas

API REST para gerenciamento de estudantes, cursos e matrículas, desenvolvida com Django 5 e Django REST Framework.

O projeto utiliza PostgreSQL (via Docker), autenticação via JWT (Bearer Token) e fornece documentação automatizada (Swagger/OpenAPI 3.0).

## Requisitos

- Python 3.10 ou superior
- [uv](https://docs.astral.sh/uv/) (gerenciador de dependências ultra-rápido)
- Docker e Docker Compose (para o banco de dados)
- Git, caso o projeto ainda não esteja disponível localmente

As dependências do projeto estão centralizadas no arquivo [pyproject.toml](pyproject.toml).

## Como executar localmente com UV

Execute os passos a seguir a partir da pasta raiz do projeto:

### 1. Inicializar o ambiente virtual e sincronizar dependências

```bash
uv sync
```
> O `uv` gerencia o ambiente virtual automaticamente e instala as dependências em milissegundos.

### 2. Subir o banco de dados PostgreSQL

Utilize o Docker Compose para iniciar o banco de dados:

```bash
docker compose up -d
```

### 3. Aplicar as migrações do banco de dados

*Nota: Exporte a variável `DB_PORT=5433` no seu terminal antes de rodar os comandos do Django, para apontar para o container do Docker.*

```bash
DB_PORT=5433 uv run python manage.py makemigrations
DB_PORT=5433 uv run python manage.py migrate
```

### 4. Criar um usuário administrador

Crie um usuário para conseguir se autenticar na API:

```bash
DB_PORT=5433 uv run python manage.py createsuperuser
```

### 5. Iniciar o servidor de desenvolvimento

```bash
DB_PORT=5433 uv run python manage.py runserver
```

Por padrão, a API estará disponível em: http://127.0.0.1:8000/

---

## Documentação da API (Swagger / OpenAPI)

Com o servidor rodando, você pode acessar a documentação interativa gerada automaticamente pelo `drf-spectacular`.

Através da interface do Swagger, você pode testar todos os endpoints, ver os esquemas de dados e até mesmo se autenticar:

- **Swagger UI (Recomendado para testar):** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc (Visualização elegante):** [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **Schema Bruto (YAML/JSON):** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

**Como testar a API no Swagger:**
1. Acesse o **Swagger UI**.
2. Vá até o endpoint `POST /api/token/` e execute com seu `username` e `password`.
3. Copie o valor de `access` gerado.
4. Clique no botão verde **"Authorize"** (no topo da página) e cole o token.
5. Pronto! Agora você pode testar todos os outros endpoints protegidos pela interface.

---

## Endpoints disponíveis

As rotas são protegidas e exigem um **JWT Bearer Token** válido no cabeçalho `Authorization`.

| Método | Endpoint | Objetivo |
| --- | --- | --- |
| POST | `/api/token/` | Gerar tokens JWT de acesso e refresh |
| POST | `/api/token/refresh/` | Renovar o token de acesso |
| GET, POST | `/estudantes/` | Listar ou criar estudantes |
| GET, PUT, PATCH, DELETE | `/estudantes/<id>/` | Consultar, alterar ou remover um estudante |
| GET, POST | `/cursos/` | Listar ou criar cursos |
| GET, PUT, PATCH, DELETE | `/cursos/<id>/` | Consultar, alterar ou remover um curso |
| GET, POST | `/matriculas/` | Listar ou criar matrículas |
| GET, PUT, PATCH, DELETE | `/matriculas/<id>/` | Consultar, alterar ou remover uma matrícula |
| GET | `/estudantes/<id>/matriculas/` | Listar cursos de um estudante |
| GET | `/cursos/<id>/matriculas/` | Listar estudantes de um curso |


## Autenticação via CLI (Curl)

Se preferir testar via linha de comando, primeiro obtenha seu token:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seu_usuario", "password": "sua_senha"}'
```

Copie o valor de `access` e envie no cabeçalho das próximas requisições:

```bash
curl -H "Authorization: Bearer <seu_token_access>" http://127.0.0.1:8000/estudantes/
```

## Testes

Com o ambiente virtual ativado e o banco de dados rodando:

```bash
DB_PORT=5433 uv run python manage.py test -v 2
```

## Solução de problemas

### `401 Unauthorized`
O token JWT pode estar expirado ou ausente. Gere um novo token em `/api/token/` ou use o refresh em `/api/token/refresh/`.

### Erro de Conexão com o Banco / PostgreSQL
Certifique-se de que o container do Docker está rodando (`docker compose ps`) e que a variável `DB_PORT=5433` foi passada antes do comando Django.

### `No module named 'django'`
Sincronize as dependências com o uv:
```bash
uv sync
```
