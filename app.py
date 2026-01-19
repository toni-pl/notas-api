import os
import logging
from flask import Flask, request, jsonify

import mysql.connector

# Configuración de logs en formato JSON
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración desde variables de entorno
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'secret')
DB_NAME = os.getenv('DB_NAME', 'notasdb')

def get_db_connection():
    """Crea una conexión a la base de datos"""
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def init_db():
    """Crea la tabla si no existe"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            contenido TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Base de datos inicializada")

# ============== INTERFAZ WEB ==============

@app.route('/')
def index():
    """Página principal con interfaz web"""
    return '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📝 Notas API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        h1 {
            color: #fff;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input[type="text"], textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.2);
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102,126,234,0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .notas-list {
            list-style: none;
        }
        
        .nota-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid #667eea;
        }
        
        .nota-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .nota-content {
            flex: 1;
        }
        
        .nota-title {
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        
        .nota-text {
            color: #666;
            font-size: 0.95em;
            margin-bottom: 8px;
        }
        
        .nota-date {
            color: #999;
            font-size: 0.8em;
        }
        
        .delete-btn {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 18px;
            transition: transform 0.2s;
            flex-shrink: 0;
            margin-left: 15px;
        }
        
        .delete-btn:hover {
            transform: scale(1.1);
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .empty-state span {
            font-size: 4em;
            display: block;
            margin-bottom: 15px;
        }
        
        .stats {
            text-align: center;
            color: rgba(255,255,255,0.7);
            margin-bottom: 20px;
            font-size: 0.9em;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .nota-item {
            animation: fadeIn 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Notas API</h1>
        <p class="stats">Aplicación desplegada con Docker Compose</p>
        
        <div class="card">
            <h2 style="margin-bottom: 20px; color: #333;">Nueva Nota</h2>
            <form id="notaForm">
                <div class="form-group">
                    <label for="titulo">Título</label>
                    <input type="text" id="titulo" placeholder="Escribe el título..." required>
                </div>
                <div class="form-group">
                    <label for="contenido">Contenido</label>
                    <textarea id="contenido" placeholder="Escribe el contenido..."></textarea>
                </div>
                <button type="submit">✨ Crear Nota</button>
            </form>
        </div>
        
        <div class="card">
            <h2 style="margin-bottom: 20px; color: #333;">Mis Notas</h2>
            <div id="notasContainer">
                <div class="loading">Cargando notas...</div>
            </div>
        </div>
    </div>
    
    <script>
        const API_URL = '/notas';
        
        async function cargarNotas() {
            try {
                const response = await fetch(API_URL);
                const notas = await response.json();
                renderNotas(notas);
            } catch (error) {
                console.error('Error cargando notas:', error);
                document.getElementById('notasContainer').innerHTML = 
                    '<div class="empty-state"><span>❌</span>Error al cargar las notas</div>';
            }
        }
        
        function renderNotas(notas) {
            const container = document.getElementById('notasContainer');
            
            if (notas.length === 0) {
                container.innerHTML = '<div class="empty-state"><span>📭</span>No hay notas todavía.<br>¡Crea tu primera nota!</div>';
                return;
            }
            
            container.innerHTML = '<ul class="notas-list">' + notas.map(nota => `
                <li class="nota-item">
                    <div class="nota-content">
                        <div class="nota-title">${escapeHtml(nota.titulo)}</div>
                        <div class="nota-text">${escapeHtml(nota.contenido || 'Sin contenido')}</div>
                        <div class="nota-date">🕐 ${new Date(nota.creado_en).toLocaleString('es-ES')}</div>
                    </div>
                    <button class="delete-btn" onclick="borrarNota(${nota.id})" title="Borrar nota">🗑️</button>
                </li>
            `).join('') + '</ul>';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function crearNota(titulo, contenido) {
            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ titulo, contenido })
                });
                
                if (response.ok) {
                    cargarNotas();
                    return true;
                }
            } catch (error) {
                console.error('Error creando nota:', error);
            }
            return false;
        }
        
        async function borrarNota(id) {
            if (!confirm('¿Seguro que quieres borrar esta nota?')) return;
            
            try {
                const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    cargarNotas();
                }
            } catch (error) {
                console.error('Error borrando nota:', error);
            }
        }
        
        document.getElementById('notaForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const titulo = document.getElementById('titulo').value.trim();
            const contenido = document.getElementById('contenido').value.trim();
            
            if (titulo) {
                const success = await crearNota(titulo, contenido);
                if (success) {
                    document.getElementById('titulo').value = '';
                    document.getElementById('contenido').value = '';
                }
            }
        });
        
        // Cargar notas al iniciar
        cargarNotas();
    </script>
</body>
</html>
    '''

# ============== API ENDPOINTS ==============

@app.route('/notas', methods=['GET'])
def listar_notas():
    """Lista todas las notas"""
    logger.info("Listando notas")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM notas ORDER BY creado_en DESC')
    notas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convertir datetime a string para JSON
    for nota in notas:
        nota['creado_en'] = nota['creado_en'].isoformat()
    
    return jsonify(notas)

@app.route('/notas', methods=['POST'])
def crear_nota():
    """Crea una nueva nota"""
    datos = request.get_json()
    titulo = datos.get('titulo', '')
    contenido = datos.get('contenido', '')
    
    if not titulo:
        logger.warning("Intento de crear nota sin título")
        return jsonify({'error': 'El título es obligatorio'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO notas (titulo, contenido) VALUES (%s, %s)',
        (titulo, contenido)
    )
    conn.commit()
    nota_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    logger.info(f"Nota creada con ID: {nota_id}")
    return jsonify({'id': nota_id, 'mensaje': 'Nota creada'}), 201

@app.route('/notas/<int:id>', methods=['DELETE'])
def borrar_nota(id):
    """Borra una nota por su ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notas WHERE id = %s', (id,))
    conn.commit()
    filas_afectadas = cursor.rowcount
    cursor.close()
    conn.close()
    
    if filas_afectadas == 0:
        logger.warning(f"Intento de borrar nota inexistente: {id}")
        return jsonify({'error': 'Nota no encontrada'}), 404
    
    logger.info(f"Nota borrada con ID: {id}")
    return jsonify({'mensaje': 'Nota borrada'})

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
