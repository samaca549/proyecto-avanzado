# services/telegram_service.py
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import Update
from config import TELEGRAM_TOKEN

from handlers.menu_handler import MenuHandler
from handlers.pedido_handler import PedidoHandler


class TelegramService:
    """Clase principal del bot que conecta los handlers con Telegram y Firebase."""

    def __init__(self):
        # Inicialización del bot
        self.app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Handlers de menús y pedidos
        self.menu_handler = MenuHandler()
        self.pedido_handler = PedidoHandler()

        # Registro de comandos
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("ver_pedidos", self.ver_pedidos))
        self.app.add_handler(CallbackQueryHandler(self.menu_callback))

    # =====================
    # COMANDOS PRINCIPALES
    # =====================

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start: muestra el menú principal."""
        await self.menu_handler.mostrar_menu_principal(update)

    async def ver_pedidos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ver_pedidos: muestra los pedidos guardados en Firebase."""
        pedidos = self.pedido_handler.firebase.listar_pedidos()
        if not pedidos:
            await update.message.reply_text("📭 No hay pedidos registrados todavía.")
            return

        mensaje = "📋 *Pedidos registrados:*\n"
        for clave, data in pedidos.items():
            mensaje += f"\n🧾 {data.get('pedido', {}).get('plato', 'Desconocido')} — {data.get('pedido', {}).get('estado', 'N/A')}"
        await update.message.reply_text(mensaje, parse_mode="Markdown")

    # =====================
    # CALLBACKS DE BOTONES
    # =====================

    async def menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja las respuestas del menú (cuando el usuario elige una opción)."""
        query = update.callback_query
        await self.menu_handler.manejar_opcion(update)

        # 🔥 Guardar el pedido en Firebase
        opcion = query.data
        user_id = query.from_user.id
        self.pedido_handler.registrar_pedido(user_id, opcion)

        # Confirmar al usuario
        await query.answer("✅ Pedido registrado en el sistema")

    # =====================
    # EJECUCIÓN DEL BOT
    # =====================

    def run(self):
        print("🤖 Bot del restaurante corriendo...")
        self.app.run_polling()
