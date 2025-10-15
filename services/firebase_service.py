import firebase_admin
from firebase_admin import credentials, db
from config import FIREBASE_CONFIG
import datetime # <-- IMPORTANTE: Añadimos la librería de fecha y hora

# Variable para evitar inicializar la app múltiples veces
app_inicializada = False

def inicializar_firebase():
    """Inicializa la app de Firebase si no ha sido inicializada antes."""
    global app_inicializada
    if not app_inicializada:
        try:
            pk_formateada = FIREBASE_CONFIG["private_key"].replace('\\n', '\n')
            
            cred_config = {
                "type": FIREBASE_CONFIG["type"],
                "project_id": FIREBASE_CONFIG["project_id"],
                "private_key_id": FIREBASE_CONFIG["private_key_id"],
                "private_key": pk_formateada,
                "client_email": FIREBASE_CONFIG["client_email"],
                "client_id": FIREBASE_CONFIG["client_id"],
                "auth_uri": FIREBASE_CONFIG["auth_uri"],
                "token_uri": FIREBASE_CONFIG["token_uri"],
                "auth_provider_x509_cert_url": FIREBASE_CONFIG["auth_provider_x509_cert_url"],
                "client_x509_cert_url": FIREBASE_CONFIG["client_x509_cert_url"],
            }

            cred = credentials.Certificate(cred_config)
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': f'https://{FIREBASE_CONFIG["project_id"]}-default-rtdb.firebaseio.com/'
            })
            
            app_inicializada = True
            print("✅ Conexión con Firebase exitosa.")

        except Exception as e:
            print(f"❌ Error al conectar con Firebase: {e}")

def guardar_usuario(user):
    """Guarda o actualiza la información de un usuario en la Realtime Database."""
    if not app_inicializada:
        return
        
    try:
        ref = db.reference(f'users/{user.id}')
        ref.update({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
        })
        print(f"Usuario {user.id} guardado/actualizado en Firebase.")
    except Exception as e:
        print(f"❌ Error al guardar usuario en Firebase: {e}")

def guardar_pedido_completo(pedido_data):
    """Guarda un pedido completo bajo un nuevo ID único en la base de datos."""
    if not app_inicializada:
        print("Advertencia: Firebase no está inicializado.")
        return
        
    try:
        ref = db.reference('pedidos').push()
        
        # === CAMBIO CLAVE ===
        # Reemplazamos la línea que falla por la fecha y hora actual del sistema.
        pedido_data['fecha_pedido'] = datetime.datetime.now().isoformat()
        pedido_data['estado'] = 'recibido'
        
        ref.set(pedido_data)
        print(f"✅ Pedido {ref.key} guardado exitosamente en Firebase.")
        
    except Exception as e:
        print(f"❌ Error al guardar el pedido en Firebase: {e}")