FROM python:3.12-slim

# Evita que o Python grave arquivos .pyc no disco
ENV PYTHONDONTWRITEBYTECODE=1
# Garante que as saídas do stdout e stderr sejam exibidas no terminal em tempo real
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala o uv (gerenciador de dependências ultra-rápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copia os arquivos de dependência
COPY pyproject.toml ./

# Sincroniza as dependências. 
# O uv cria o .venv automaticamente na raiz do projeto dentro do container
RUN uv sync

# Copia todo o resto do projeto
COPY . .

# Expõe a porta que o Django vai rodar
EXPOSE 8000

# Comando para iniciar o servidor (escutando em todas as interfaces)
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

