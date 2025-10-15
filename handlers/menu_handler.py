# handlers/menu_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.firebase_service import guardar_usuario

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Guarda al usuario en Firebase y le da la bienvenida."""
    user = update.effective_user
    guardar_usuario(user)
    await update.message.reply_html(
        rf"¡Hola, {user.mention_html()}! 👋 Soy tu asistente de pedidos. Usa /menu para ver las opciones."
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el menú principal con botones."""
    keyboard = [
        [InlineKeyboardButton("🍳 Desayunos", callback_data='menu_desayunos')],
        [InlineKeyboardButton("🍝 Almuerzos", callback_data='menu_almuerzos')],
        [InlineKeyboardButton("Finalizar y Pagar", callback_data='finalizar_pedido')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Inicializa el carrito de compras si no existe
    if 'carrito' not in context.user_data:
        context.user_data['carrito'] = []

    await update.message.reply_text("👇 Por favor, elige una categoría:", reply_markup=reply_markup)

async def boton_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja las pulsaciones de los botones del menú."""
    query = update.callback_query
    await query.answer() # Responde al callback para que el botón deje de cargar

    opcion = query.data

    # Aquí definimos los productos de cada categoría
    productos = {
        'menu_desayunos': [
            ("Calentado Paisa", 15000),
            ("Huevos al Gusto", 12000),
            ("Arepa con Queso", 8000),
        ],
        'menu_almuerzos': [
            ("Bandeja Paisa", 25000),
            ("Ajiaco Santafereño", 22000),
            ("Sancocho de Gallina", 20000),
        ]
    }

    if opcion in productos:
        keyboard = []
        for producto, precio in productos[opcion]:
            # El callback_data será 'add_PRODUCTONOMBRE_PRECIO'
            callback_str = f"add_{producto.replace(' ', '')}_{precio}"
            keyboard.append([InlineKeyboardButton(f"{producto} - ${precio:,.0f}", callback_data=callback_str)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Selecciona un producto para añadir al carrito:", reply_markup=reply_markup)

async def agregar_al_carrito_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Añade un producto al carrito de compras."""
    query = update.callback_query
    await query.answer()

    # Extraemos el nombre y precio del callback_data
    _, nombre_producto, precio_str = query.data.split('_')
    precio = int(precio_str)

    # Añadimos al carrito en context.user_data
    if 'carrito' not in context.user_data:
        context.user_data['carrito'] = []
    
    context.user_data['carrito'].append({'producto': nombre_producto, 'precio': precio})

    # Mostramos una confirmación
    carrito_actual = context.user_data['carrito']
    total = sum(item['precio'] for item in carrito_actual)
    
    await query.edit_message_text(
        text=f"✅ Añadido: {nombre_producto}.\n\nTu carrito actual tiene {len(carrito_actual)} productos.\nTotal: ${total:,.0f}\n\nUsa /menu para añadir más o finalizar."
    )