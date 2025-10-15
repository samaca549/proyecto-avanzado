# main.py
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_TOKEN
from services.firebase_service import inicializar_firebase
from handlers.menu_handler import start_command, menu_command, boton_menu_callback, agregar_al_carrito_callback
from handlers.pedido_handler import (
    iniciar_finalizar_pedido, get_direccion, get_telefono, get_pago_y_confirmar,
    procesar_confirmacion, cancelar,
    DIRECCION, TELEFONO, PAGO, CONFIRMACION
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    inicializar_firebase()
    
    if not TELEGRAM_TOKEN:
        logger.error("Error: No se encontró el TELEGRAM_TOKEN.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # --- Manejador de la Conversación de Pedido ---
    pedido_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(iniciar_finalizar_pedido, pattern='^finalizar_pedido$')],
        states={
            DIRECCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_direccion)],
            TELEFONO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telefono)],
            PAGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pago_y_confirmar)],
            CONFIRMACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_confirmacion)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    )

    # Añadir manejadores al bot
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Manejador para los botones de categoría (Desayunos, Almuerzos)
    application.add_handler(CallbackQueryHandler(boton_menu_callback, pattern='^menu_'))
    
    # Manejador para los botones de añadir producto
    application.add_handler(CallbackQueryHandler(agregar_al_carrito_callback, pattern='^add_'))

    # Añadir la conversación de pedido
    application.add_handler(pedido_conv_handler)
    
    print("🚀 Bot completamente funcional iniciado. ¡Listo para tomar pedidos!")
    application.run_polling()

if __name__ == "__main__":
    main()