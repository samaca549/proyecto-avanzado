# handlers/pedido_handler.py
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler
)
from services.firebase_service import guardar_pedido_completo

# Definición de los estados/pasos de la conversación
(DIRECCION, TELEFONO, PAGO, CONFIRMACION) = range(4)

async def iniciar_finalizar_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia el proceso de finalización del pedido pidiendo la dirección."""
    query = update.callback_query
    await query.answer()

    carrito = context.user_data.get('carrito', [])
    if not carrito:
        await query.edit_message_text("Tu carrito está vacío. Añade productos con /menu primero.")
        return ConversationHandler.END

    await query.edit_message_text("Para completar tu pedido, por favor, escribe tu dirección de entrega:")
    return DIRECCION

async def get_direccion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Almacena la dirección y pide el teléfono."""
    context.user_data['direccion'] = update.message.text
    await update.message.reply_text("Gracias. Ahora, por favor, escribe tu número de teléfono de contacto:")
    return TELEFONO

async def get_telefono(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Almacena el teléfono y pide el método de pago."""
    context.user_data['telefono'] = update.message.text
    await update.message.reply_text("Perfecto. ¿Cómo deseas pagar? (Ej: Nequi, Daviplata, Efectivo)")
    return PAGO

async def get_pago_y_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Almacena el método de pago, muestra el resumen y pide confirmación."""
    context.user_data['metodo_pago'] = update.message.text
    
    # Construir el resumen del pedido
    user = update.effective_user
    carrito = context.user_data['carrito']
    total = sum(item['precio'] for item in carrito)
    
    resumen_items = "\n".join([f"- {item['producto']} (${item['precio']:,}) " for item in carrito])
    
    resumen_texto = (
        f"📝 === RESUMEN DE TU PEDIDO === 📝\n\n"
        f"👤 Cliente: {user.full_name}\n"
        f"🏠 Dirección: {context.user_data['direccion']}\n"
        f"📱 Teléfono: {context.user_data['telefono']}\n"
        f"💳 Método de Pago: {context.user_data['metodo_pago']}\n\n"
        f"🛒 Productos:\n{resumen_items}\n\n"
        f"💰 TOTAL A PAGAR: ${total:,.0f}\n\n"
        f"Por favor, escribe 'si' para confirmar tu pedido."
    )
    
    await update.message.reply_text(resumen_texto)
    return CONFIRMACION

async def procesar_confirmacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el pedido en Firebase si el usuario confirma."""
    confirmacion = update.message.text.lower()
    
    if confirmacion == 'si':
        # Guardar todo en Firebase
        user_info = update.effective_user
        pedido_data = {
            'cliente_id': user_info.id,
            'cliente_nombre': user_info.full_name,
            'direccion': context.user_data['direccion'],
            'telefono': context.user_data['telefono'],
            'pago': context.user_data['metodo_pago'],
            'carrito': context.user_data['carrito'],
            'total': sum(item['precio'] for item in context.user_data['carrito'])
        }
        
        guardar_pedido_completo(pedido_data)
        
        await update.message.reply_text("✅ ¡Tu pedido ha sido confirmado y enviado a la cocina! Gracias por tu compra.")
        
        # Limpiar el carrito
        context.user_data['carrito'] = []
    else:
        await update.message.reply_text("❌ Pedido no confirmado. Puedes empezar de nuevo con /menu.")

    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la conversación."""
    await update.message.reply_text("Pedido cancelado. Puedes volver a empezar con /menu.")
    return ConversationHandler.END