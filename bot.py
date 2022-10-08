import time
from email import message
from telegram import Location, ParseMode, Update, ChatAction
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, \
    PrefixHandler, ConversationHandler

from config import Config


NAME, EMAIL = range(2)

EMAIL_REGEX = r"^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"


class Bot:
    """ Very simple temegram bot
    """

    def __init__(self):
        self._chat_id = Config.CHAT_ID

        self._updater = Updater(token=Config.BOT_TOKEN, use_context=True)
        # manages handlers
        self._dispatcher = self._updater.dispatcher

        # handlers: general
        self._dispatcher.add_handler(MessageHandler(
            Filters.text & ~Filters.command & ~Filters.update.edited_message, self._echo))
        self._dispatcher.add_handler(CommandHandler('start', self._start))
        self._dispatcher.add_handler(CommandHandler('botphoto', self._bot_photo))
        self._dispatcher.add_handler(CommandHandler('location', self._location))
        self._dispatcher.add_handler(CommandHandler('date', self._date))
        self._dispatcher.add_handler(CommandHandler('poll', self._poll))

        self._dispatcher.add_handler(CommandHandler('add', self._add))
        self._dispatcher.add_handler(PrefixHandler('!', 'notify', self._notify))

        # handlers: groups
        self._dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, self._new_member))

        # handlers: conversation
        entry_points = [
            CommandHandler("conversation", self._conversation_mode_start)
        ]

        states = {
            NAME: [
                MessageHandler(filters=Filters.text, callback=self._conversation_mode_state_name)
            ],
            EMAIL: [
                MessageHandler(
                    filters=Filters.regex(EMAIL_REGEX),
                    callback=self._conversation_mode_state_email)
            ],
        }

        fallbacks = [
            MessageHandler(filters=Filters.all, callback=self._conversation_mode_fallback)
        ]

        # comments handlers below to start using conversation mode
        # self._dispatcher.add_handler(
        #     ConversationHandler(
        #         entry_points=entry_points,
        #         states=states,
        #         fallbacks=fallbacks,
        #         allow_reentry=True,
        #         # per_chat=False,
        #         # per_user=False
        #     )
        # )

    def _welcome_message(self):
        # welcome message (proactive protocol)
        self._updater.bot.send_message(self._chat_id, "Welcome to this amazing bot!")

    def _echo(self, update: Update, context: CallbackContext) -> None:
        """ Echo the user message

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        update.message.reply_text(f"<b>Echo mode:</b> {update.message.text}",
                                  reply_to_message_id=update.message.message_id,
                                  parse_mode=ParseMode.HTML)

    def _start(self, update: Update, context: CallbackContext) -> None:
        """ Handle start command

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        if self._chat_id != update.message.chat_id:
            self._chat_id = update.message.chat_id
        self._welcome_message()

    def _bot_photo(self, update: Update, context: CallbackContext) -> None:
        """ Send a bot image

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        try:
            image = open('./assets/bot.gif', 'rb')
        except Exception:
            image = "https://www.publicdomainpictures.net/pictures/280000/nahled/not-found-image-15383864787lu.jpg"

        update.message.reply_chat_action(action=ChatAction.UPLOAD_PHOTO)
        update.message.reply_animation(
            image, reply_to_message_id=update.message.message_id, caption="Am I handsome?")

    def _location(self, update: Update, context: CallbackContext) -> None:
        """ Send a location

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        chat_location = Location(
            latitude=42.8778753,
            longitude=-8.549466
        )
        location_message = update.message.reply_location(
            location=chat_location,
            reply_to_message_id=update.message.message_id,
            live_period=60
        )

        # simulates movement
        for i in range(10):
            time.sleep(5)
            chat_location.latitude += .00005
            chat_location.longitude += 0.00005
            location_message.edit_live_location(
                location=chat_location
            )

    def _date(self, update: Update, context: CallbackContext) -> None:
        """ Send a date event

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        latitude = 42.8778753
        longitude = -8.549466
        place_id = "ChIJ-a-URxj-Lg0Ruonht89TrGc"
        address = "My heart, Nº 1 A, Santiago, Spain"
        place_type = "zoo"

        update.message.reply_venue(
            latitude=latitude,
            longitude=longitude,
            title="Mistery date",
            address=address,
            google_place_id=place_id,
            google_place_type=place_type
        )

    def _poll(self, update: Update, context: CallbackContext) -> None:
        """ Send a simple poll event

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        question = "Am I 'special'?"
        options = ["yes", "no", "maybe"]

        update.message.reply_poll(
            question=question,
            options=options,
            is_anonymous=False
        )

    def _new_member(self, update: Update, context: CallbackContext) -> None:
        """ Handler new member callback

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        user = update.message.new_chat_members[0]
        username = f"@{user.username}" if user.username is not None else user.full_name

        update.message.reply_text(
            f"Welcome to this amazing chat <b>{username}</b>!",
            reply_to_message_id=update.message.message_id,
            parse_mode=ParseMode.HTML
        )

    def _add(self, update: Update, context: CallbackContext) -> None:
        """ Sum elements

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        result = sum(list(map(float, context.args)))

        update.message.reply_text(
            f"Result (add) <b>{result}</b>",
            reply_to_message_id=update.message.message_id,
            parse_mode=ParseMode.HTML
        )

    def _notify(self, update: Update, context: CallbackContext) -> None:
        """ Notify message to user

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        context.job_queue.run_repeating(
            self._say_hi,
            int(context.args[0]),
            context=update.message.chat_id,
        )

        update.message.reply_text("Starting notifications ...")

    def _say_hi(self, context: CallbackContext):
        """ Send hi mesage

        Args:
            context (CallbackContext): _description_
        """
        context.bot.send_message(
            chat_id=context.job.context,
            text="This is a hi message. Sorry!! :-P"
        )

    def _conversation_mode_start(self, update: Update, context: CallbackContext):
        """ Conversation mode: start

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        update.message.reply_text(
            text="What is your name my friend?"
        )

        return NAME

    def _conversation_mode_state_name(self, update: Update, context: CallbackContext):
        """ Conversation mode: get email

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        update.message.reply_text(
            text=f"Hello {update.message.text}, my friend! Please write your email."
        )

        return EMAIL

    def _conversation_mode_state_email(self, update: Update, context: CallbackContext):
        """ Conversation mode: send email

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        update.message.reply_text(
            text="Email received!"
        )

        return ConversationHandler.END

    def _conversation_mode_fallback(self, update: Update, context: CallbackContext):
        """ Conversation mode: fallback

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        update.message.reply_text(
            text="I cannot understand you! Please, take this seriously!!"
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
