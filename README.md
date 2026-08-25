**README.md**

# API de Gestão de Matrículas

API REST para gerenciamento de estudantes, cursos e matrículas, desenvolvida com Django 5 e Django REST Framework.

O projeto usa SQLite por padrão, autenticação HTTP Basic e exige um usuário autenticado para acessar os endpoints da API.

## Requisitos

- Python 3.10 ou superior
- [uv](https://docs.astral.sh/uv/) (gerenciador de dependências ultra-rápido)
- Git, caso o projeto ainda não esteja disponível localmente

As dependências do projeto estão centralizadas no arquivo [pyproject.toml](pyproject.toml).

## Estrutura principal

```text
pyproject.toml            # dependências e configurações do projeto (UV / PEP 621)
manage.py                 # comandos administrativos do Django
setup/                    # configurações, URLs e servidores ASGI/WSGI
escola/                   # modelos, serializers, views e migrações
db.sqlite3                # banco local, criado após a migração
```

## Como executar localmente com UV

Execute os passos a seguir a partir da pasta raiz do projeto (onde está o arquivo `pyproject.toml`):

### 1. Inicializar o ambiente virtual e sincronizar dependências

O `uv` gerencia o ambiente virtual automaticamente através do arquivo `pyproject.toml`:

```bash
uv sync
```

> Esse comando cria a pasta `.venv` e instala todas as dependências do projeto e de desenvolvimento (`pytest`, `ruff`) em milissegundos.

### 2. Ativar o ambiente virtual (Opcional)

Se preferir trabalhar com o ambiente ativado diretamente no terminal:

* **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```
* **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
* **Windows (Prompt de Comando - CMD):**
  ```bat
  .venv\Scripts\activate.bat
  ```

> **Nota:** Com o `uv`, ativar o ambiente é opcional. Você pode executar qualquer comando precedido por `uv run` (ex: `uv run python manage.py runserver`).

### 3. Aplicar as migrações do banco de dados

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### 4. Criar um usuário administrador para acessar a API

Como a API exige autenticação HTTP Basic, crie um superusuário:

```bash
uv run python manage.py createsuperuser
```

### 5. Executar a suíte de testes

```bash
# Executar testes nativos do Django/DRF
uv run python manage.py test -v 2

# Ou executar com pytest
uv run pytest
```

### 6. Iniciar o servidor de desenvolvimento

```bash
uv run python manage.py runserver
```

Por padrão, a aplicação estará disponível em:
- **API:** http://127.0.0.1:8000/
- **Painel Administrativo:** http://127.0.0.1:8000/admin/

Para usar outra porta:
```bash
uv run python manage.py runserver 8080
```


## Endpoints disponíveis

Todas as rotas abaixo aceitam autenticação HTTP Basic e são protegidas por `IsAuthenticated`.

| Método | Endpoint | Objetivo |
| --- | --- | --- |
| GET, POST | `/estudantes/` | Listar ou criar estudantes |
| GET, PUT, PATCH, DELETE | `/estudantes/<id>/` | Consultar, alterar ou remover um estudante |
| GET, POST | `/cursos/` | Listar ou criar cursos |
| GET, PUT, PATCH, DELETE | `/cursos/<id>/` | Consultar, alterar ou remover um curso |
| GET, POST | `/matriculas/` | Listar ou criar matrículas |
| GET, PUT, PATCH, DELETE | `/matriculas/<id>/` | Consultar, alterar ou remover uma matrícula |
| GET | `/estudantes/<id>/matriculas/` | Listar cursos de um estudante |
| GET | `/cursos/<id>/matriculas/` | Listar estudantes de um curso |

Os endpoints de coleção também disponibilizam a interface navegável do Django REST Framework no navegador.

## Exemplos de uso

Com o servidor rodando e substituindo `usuario` e `senha` pelos dados criados:

### Listar estudantes

```bash
curl -u usuario:senha http://127.0.0.1:8000/estudantes/
```

### Criar um estudante

```bash
curl -u usuario:senha \
    -H "Content-Type: application/json" \
    -d '{"nome":"Maria Silva","email":"maria@example.com","cpf":"12345678901","data_nascimento":"2005-04-20","celular":"11999999999"}' \
    http://127.0.0.1:8000/estudantes/
```

### Criar um curso

`nivel` deve ser `B` (Básico), `I` (Intermediário) ou `A` (Avançado):

```bash
curl -u usuario:senha \
    -H "Content-Type: application/json" \
    -d '{"codigo":"PYTHON01","descricao":"Python para iniciantes","nivel":"B"}' \
    http://127.0.0.1:8000/cursos/
```

### Criar uma matrícula

Use os IDs existentes de estudante e curso. `periodo` pode ser `M` (Matutino), `V` (Vespertino) ou `N` (Noturno):

```bash
curl -u usuario:senha \
    -H "Content-Type: application/json" \
    -d '{"estudante":1,"curso":1,"periodo":"M"}' \
    http://127.0.0.1:8000/matriculas/
```

### Consultar matrículas relacionadas

```bash
curl -u usuario:senha http://127.0.0.1:8000/estudantes/1/matriculas/
curl -u usuario:senha http://127.0.0.1:8000/cursos/1/matriculas/
```

### Paginação, Busca, Filtros e Ordenação

* **Paginação**: Por padrão, 10 itens por página. É possível navegar com `page` e customizar a quantidade com `page_size`:
  ```bash
  curl -u usuario:senha "http://127.0.0.1:8000/estudantes/?page=2"
  curl -u usuario:senha "http://127.0.0.1:8000/estudantes/?page=1&page_size=20"
  ```
* **Busca textual (`search`)**:
  ```bash
  curl -u usuario:senha "http://127.0.0.1:8000/estudantes/?search=Maria"
  curl -u usuario:senha "http://127.0.0.1:8000/cursos/?search=PYTHON"
  curl -u usuario:senha "http://127.0.0.1:8000/matriculas/?search=Maria"
  ```
* **Filtros por atributos**:
  ```bash
  curl -u usuario:senha "http://127.0.0.1:8000/cursos/?nivel=B"
  curl -u usuario:senha "http://127.0.0.1:8000/matriculas/?periodo=M"
  ```
* **Ordenação (`ordering`)**:
  ```bash
  curl -u usuario:senha "http://127.0.0.1:8000/estudantes/?ordering=nome"
  curl -u usuario:senha "http://127.0.0.1:8000/estudantes/?ordering=-data_nascimento"
  curl -u usuario:senha "http://127.0.0.1:8000/cursos/?ordering=-codigo"
  ```

## Testes

Com o ambiente virtual ativado, execute:

```bash
python manage.py test
```

## Desenvolvimento

Depois de alterar modelos, gere uma nova migração e aplique-a:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

Antes de abrir uma alteração, execute os testes e linters:

```bash
uv run python manage.py test -v 2
uv run ruff check .
```

## Solução de problemas

### `No module named 'django'`

Sincronize as dependências com o uv novamente:

```bash
uv sync
```

### `401 Unauthorized`

A API exige autenticação. Confira se a requisição usa `-u usuario:senha` ou informe as credenciais na interface navegável do DRF.

### `no such table`

As migrações ainda não foram aplicadas:

```bash
uv run python manage.py migrate
```

## Links

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Documentação do Django](https://docs.djangoproject.com/)
