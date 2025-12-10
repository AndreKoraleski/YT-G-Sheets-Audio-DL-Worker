FROM python:3.10-slim

# Dependências de sistema:
# - ffmpeg: Conversão de áudio
# - git: Baixar dependências do git
# - nodejs: Necessário para o yt-dlp resolver assinaturas complexas do YouTube
RUN apt-get update && \
    apt-get install -y ffmpeg git nodejs && \
    rm -rf /var/lib/apt/lists/*

# Instala o uv (gerenciador de pacotes rápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copia definição do projeto, README e código fonte
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Instala o pacote no ambiente do sistema (ideal para container)
RUN uv pip install --system .

# Garante que os logs apareçam imediatamente
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "yt_gsheets_audio_worker"]
