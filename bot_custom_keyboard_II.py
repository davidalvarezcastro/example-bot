
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Updater)

from config import Config

QUESTION, NO = range(2)


class Bot:
    """ Very simple telegram bot
    """

    def __init__(self):
        self._chat_id = Config.CHAT_ID

        self._updater = Updater(token=Config.BOT_TOKEN, use_context=True)
        # manages handlers
        self._dispatcher = self._updater.dispatcher

        entry_points = [CommandHandler('conversation', self._keyboard)]
        states = {
            QUESTION: [
                CallbackQueryHandler(self._yes, pattern=r'^yes$'),
                CallbackQueryHandler(self._no, pattern=r'^no$')
            ],
            NO: [
                CallbackQueryHandler(self._reason)
            ]
        }
        fallbacks = []

        # handlers: general
        self._dispatcher.add_handler(
            ConversationHandler(entry_points=entry_points, states=states, fallbacks=fallbacks)
        )

    def _keyboard(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard (convertation in line)

        Args:
            update (Update)
            context (CallbackContext)
        """
        buttons = [
            [InlineKeyboardButton("Yes", callback_data="yes")],
            [InlineKeyboardButton("No", callback_data="no")],
        ]

        keyboardMarkup = InlineKeyboardMarkup(buttons)

        update.message.reply_text(
            "¿Do you like it?",
            reply_markup=keyboardMarkup,
        )
        return QUESTION

    def _yes(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard response yes

        Args:
            update (Update)
            context (CallbackContext)
        """
        query = update.callback_query
        query.answer()
        query.edit_message_text("Thanks!")

        return ConversationHandler.END

    def _no(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard response no

        Args:
            update (Update)
            context (CallbackContext)
        """
        query = update.callback_query
        query.answer()

        buttons = [
            [
                InlineKeyboardButton("Bad explanation", callback_data="bad"),
                InlineKeyboardButton("Not much content", callback_data="not_much")
            ],
            [
                InlineKeyboardButton("Other", callback_data="other")
            ]
        ]

        keyboardMarkup = InlineKeyboardMarkup(buttons)
        query.edit_message_text("Oh!!!. ¿Reason?", reply_markup=keyboardMarkup)

        return NO

    def _reason(self, update: Update, context: CallbackContext) -> None:
        """ Handle custom keyboard handler reason

        Args:
            update (Update)
            context (CallbackContext)
        """
        query = update.callback_query
        query.answer()
        query.edit_message_text("Thanks for your feadback!")

        return ConversationHandler.END

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
