"""
Servidor HTTP para recibir datos del Listener/Router
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import List, Dict, Any
from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Queue para almacenar eventos recibidos
# En producción, esto debería ser una cola más robusta (Redis, RabbitMQ, etc.)
events_queue: List[Dict[str, Any]] = []

@app.route(Config.HTTP_ENDPOINT, methods=['POST'])
def receive_event():
    """Recibe un evento individual del listener"""
    try:
        event = request.get_json()
        if not event:
            return jsonify({"error": "No se recibió ningún evento"}), 400
        
        events_queue.append(event)
        logger.debug(f"Evento recibido: {event.get('sensor_id', 'unknown')}")
        
        return jsonify({
            "status": "ok",
            "message": "Evento recibido",
            "queue_size": len(events_queue)
        }), 200
        
    except Exception as e:
        logger.error(f"Error al recibir evento: {e}")
        return jsonify({"error": str(e)}), 500

@app.route(f"{Config.HTTP_ENDPOINT}/batch", methods=['POST'])
def receive_batch():
    """Recibe un batch de eventos del listener"""
    try:
        data = request.get_json()
        if not data or 'events' not in data:
            return jsonify({"error": "No se recibió batch válido"}), 400
        
        events = data['events']
        events_queue.extend(events)
        
        logger.info(f"Batch recibido: {len(events)} eventos, queue_size: {len(events_queue)}")
        
        return jsonify({
            "status": "ok",
            "message": f"Batch de {len(events)} eventos recibido",
            "queue_size": len(events_queue)
        }), 200
        
    except Exception as e:
        logger.error(f"Error al recibir batch: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "queue_size": len(events_queue)
    }), 200

@app.route('/stats', methods=['GET'])
def stats():
    """Estadísticas del servidor"""
    return jsonify({
        "queue_size": len(events_queue),
        "endpoint": Config.HTTP_ENDPOINT,
        "port": Config.HTTP_PORT
    }), 200

def get_events_batch(size: int = None) -> List[Dict[str, Any]]:
    """Obtiene un batch de eventos de la cola"""
    if size is None:
        size = len(events_queue)
    
    batch = events_queue[:size]
    events_queue[:size] = []
    return batch

def start_server():
    """Inicia el servidor HTTP"""
    import socket
    import subprocess
    import platform
    
    def is_port_available(host, port):
        """Verifica si un puerto está disponible"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, port))
            sock.close()
            return True
        except:
            return False
    
    def get_port_process(port):
        """Obtiene el PID del proceso que usa el puerto"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['netstat', '-ano'], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            return parts[-1]
            return None
        except:
            return None
    
    port = Config.HTTP_PORT
    
    # Verificar si el puerto está disponible
    if not is_port_available(Config.HTTP_HOST, port):
        pid = get_port_process(port)
        logger.error(f"❌ ERROR: El puerto {port} está OCUPADO")
        if pid:
            logger.error(f"   Proceso usando el puerto: PID {pid}")
            logger.error(f"   Para detenerlo, ejecuta: Stop-Process -Id {pid} -Force")
        else:
            logger.error(f"   No se pudo identificar el proceso")
        logger.error(f"   O cambia HTTP_PORT en el archivo .env o variables de entorno")
        logger.error(f"   Comando para verificar: netstat -ano | findstr :{port}")
        raise OSError(f"Puerto {port} no disponible")
    
    logger.info(f"✓ Iniciando servidor HTTP en {Config.HTTP_HOST}:{port}")
    logger.info(f"  Endpoint: {Config.HTTP_ENDPOINT}")
    logger.info(f"  Endpoint batch: {Config.HTTP_ENDPOINT}/batch")
    logger.info(f"  Health check: http://localhost:{port}/health")
    
    try:
        app.run(host=Config.HTTP_HOST, port=port, debug=False, threaded=True, use_reloader=False)
    except OSError as e:
        error_msg = str(e).lower()
        if "permission denied" in error_msg or "acceso" in error_msg:
            logger.error(f"❌ ERROR: Permisos insuficientes para usar el puerto {port}")
            logger.error(f"   Solución: Ejecuta como administrador o cambia HTTP_PORT")
        else:
            logger.error(f"❌ ERROR: No se pudo iniciar el servidor en puerto {port}: {e}")
        raise

if __name__ == '__main__':
    start_server()

