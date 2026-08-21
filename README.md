**README.md**

# API de Gestão de Matrículas

API REST para gerenciamento de estudantes, cursos e matrículas, desenvolvida com Django 5 e Django REST Framework.

O projeto usa SQLite por padrão, autenticação HTTP Basic e exige um usuário autenticado para acessar os endpoints da API.

## Requisitos

- Python 3.10 ou superior
- `pip`
- Git, caso o projeto ainda não esteja disponível localmente

As versões das bibliotecas utilizadas estão fixadas em [requirements.txt](requirements.txt).

## Estrutura principal

```text
manage.py                 # comandos administrativos do Django
setup/                    # configurações, URLs e servidores ASGI/WSGI
escola/                   # modelos, serializers, views e migrações
db.sqlite3                # banco local, criado após a migração
```

## Como executar localmente

Execute os passos a seguir a partir da pasta raiz do projeto, isto é, a pasta que contém o arquivo `manage.py`.

### 1. Acesse o projeto

Se ainda não tiver o código, clone o repositório e entre na pasta:

```bash
git clone <URL_DO_REPOSITORIO>
cd escola-api-gestao-matriculas
```

Se o projeto já estiver no computador:

```bash
cd caminho/para/escola-api-gestao-matriculas
```

Confirme que está no diretório correto:

```bash
ls manage.py       # Linux/macOS
dir manage.py      # Windows PowerShell
```

### 2. Crie o ambiente virtual

```bash
python -m venv venv
```

No Linux/macOS, se `python` não estiver disponível, use `python3`:

```bash
python3 -m venv venv
```

### 3. Ative o ambiente virtual

Linux/macOS:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Windows Prompt de Comando (cmd):

```bat
venv\Scripts\activate.bat
```

Quando a ativação funcionar, o nome `(venv)` aparecerá no início da linha do terminal.

### 4. Instale as dependências

Com o ambiente virtual ativado:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Verifique a configuração

```bash
python manage.py check
```

O resultado esperado é `System check identified no issues`.

### 6. Crie o banco de dados

Aplique as migrações existentes:

```bash
python manage.py migrate
```

Esse comando cria o arquivo `db.sqlite3` e as tabelas do Django, incluindo `Estudante`, `Curso` e `Matricula`. Não é necessário executar `makemigrations` na primeira execução, pois as migrações já estão versionadas no projeto.

### 7. Crie um usuário para acessar a API

Como a API exige autenticação, crie um usuário administrador:

```bash
python manage.py createsuperuser
```

Informe nome de usuário, e-mail e senha quando solicitado. Esse usuário poderá ser usado nas requisições com autenticação Basic e no painel administrativo.

### 8. Inicie o servidor

```bash
python manage.py runserver
```

Por padrão, a aplicação ficará disponível em:

- API: http://127.0.0.1:8000/
- Administração: http://127.0.0.1:8000/admin/

Para usar outra porta:

```bash
python manage.py runserver 8080
```

Para interromper o servidor, pressione `Ctrl+C`.

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

## Testes

Com o ambiente virtual ativado, execute:

```bash
python manage.py test
```

## Desenvolvimento

Depois de alterar modelos, gere uma nova migração e aplique-a:

```bash
python manage.py makemigrations
python manage.py migrate
```

Antes de abrir uma alteração, verifique a configuração e execute os testes:

```bash
python manage.py check
python manage.py test
```

## Solução de problemas

### `No module named 'django'`

Ative o ambiente virtual e instale as dependências novamente:

```bash
source venv/bin/activate       # Linux/macOS
python -m pip install -r requirements.txt
```

No Windows, use `venv\Scripts\Activate.ps1` para ativar o ambiente.

### `401 Unauthorized`

A API exige autenticação. Confira se a requisição usa `-u usuario:senha` ou informe as credenciais na interface navegável do DRF.

### `no such table`

As migrações ainda não foram aplicadas:

```bash
python manage.py migrate
```

## Links

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Documentação do Django](https://docs.djangoproject.com/)
