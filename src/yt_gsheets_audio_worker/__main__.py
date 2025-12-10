import logging
import sys
import time

from orc import Orchestrator
from yt_audio_dl import Config, Downloader

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

config = Config(
    audio_format='flac',
    overwrite_existing_files=False,
    sample_rate=48000,
    channels=1,
    filename_is_video_title=False,
    create_video_subdirectory=True
)

downloader = Downloader(config=config)
orc = Orchestrator() 

def download(url: str) -> None:
    logging.info(f"Iniciando download: {url}")
    
    # O downloader captura exceções internamente e retorna um objeto result
    result = downloader.download(url)

    # 1. Tratamento de FALHA
    if result.failed:
        raise RuntimeError(f"Falha no yt_audio_dl: {result.error_message}")

    # 2. Tratamento de SKIPPED
    if result.skipped:
        logging.warning(f"Pulado: {result.error_message}")
        # Retornamos normalmente, mas não deve acontecer, pois o Orchestrator não deve enviar tarefas que já foram baixadas
        return

    # 3. Sucesso
    if result.success:
        logging.info(f"Sucesso: {result.audio_file_path}")

def main():
    logging.info("Worker iniciado. Aguardando tarefas...")
    
    # Loop principal
    i = 0
    while True:
        # Tenta processar uma task
        has_task = orc.process_next_task(download)
        
        # Manda heartbeat 
        # Isso garante que o worker mostre que está vivo e buscando trabalho.
        orc.send_heartbeat() 
        
        if has_task:
            i = 0  # Reseta o backoff se trabalhou
        else:
            # Se não trabalhou, incrementa a espera
            i += 1
            wait = min(60, 2 ** i)
            logging.info(f"Fila vazia. Aguardando {wait}s...")
            time.sleep(wait)

if __name__ == "__main__":
    main()