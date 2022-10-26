from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      Update)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from config import Config

GENDER = range(1)


class Bot:
    """ Very simple temegram bot
    """

    def __init__(self):
        self._chat_id = Config.CHAT_ID

        self._updater = Updater(token=Config.BOT_TOKEN, use_context=True)
        # manages handlers
        self._dispatcher = self._updater.dispatcher

        entry_points = [CommandHandler('keyboard', self._keyboard)]
        states = {GENDER: [MessageHandler(filters=Filters.regex(
            r"^(Boy)(?!Girls)|(?!Boy)(Girls)$"), callback=self._reponse)]}
        fallbacks = [MessageHandler(filters=Filters.all, callback=self._fallback)]

        # handlers: general
        self._dispatcher.add_handler(ConversationHandler(
            entry_points=entry_points, states=states, fallbacks=fallbacks))
        self._dispatcher.add_handler(CommandHandler('keyboard_inline', self._keyboard_inline))
        self._dispatcher.add_handler(CallbackQueryHandler(self._reponse_inline))

    def _keyboard(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard

        Args:
            update (Update)
            context (CallbackContext)
        """
        buttons = [
            [KeyboardButton("Boy"), KeyboardButton("Girl")],
        ]

        keyboardMarkup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)

        update.message.reply_text(
            "¿Are you a boy or a girl?",
            reply_markup=keyboardMarkup,
        )
        return GENDER

    def _keyboard_inline(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard-inline

        Args:
            update (Update)
            context (CallbackContext)
        """
        buttons = [
            [InlineKeyboardButton("Boy", callback_data="boy")],
            [InlineKeyboardButton("Girl", callback_data="girl")]
        ]

        keyboardMarkup = InlineKeyboardMarkup(buttons)

        update.message.reply_text(
            "¿Are you a boy or a girl?",
            reply_markup=keyboardMarkup,
        )

    def _reponse(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard response

        Args:
            update (Update)
            context (CallbackContext)
        """
        keyboardMarkupRemove = ReplyKeyboardRemove()
        update.message.reply_text(
            f"Oh! you are a {update.message.text}", reply_markup=keyboardMarkupRemove
        )
        return ConversationHandler.END

    def _reponse_inline(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard-inline response

        Args:
            update (Update)
            context (CallbackContext)
        """
        update.callback_query.answer(
            f"Oh! you are a {update.callback_query.data}",
        )
        update.callback_query.edit_message_text(
            "Thank you dude!"
        )

    def _fallback(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard fallback

        Args:
            update (Update)
            context (CallbackContext)
        """
        update.message.reply_text(
            "What are you saying!!",
        )

    def run(self) -> None:
        """ Init bot
        """
        self._updater.start_polling()
        self._updater.idle()


def init_bot_server() -> None:
    """ Start the bot server
    """
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    init_bot_server()
