import logging
import os
# lib url: https://pypi.org/project/python-telegram-bot/
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from datetime import datetime
from pprint import pprint  

logger = logging.getLogger('vilavelha.bot.vacina')

BASE_URL = 'https://vacina.vilavelha.es.gov.br/api'

#region API

def get_all_vacines_vacancies():
    response = requests.get(f'{BASE_URL}/categorias')
    categories_payload = response.json()    
    services = []; 
    append_services = services.append
    for i, category in enumerate(categories_payload): 
        response = requests.get(f'{BASE_URL}/categorias/{category["id"]}/servicos')
        categories_payload[i]['servicos'] = response.json()
    pprint(categories_payload)
    

#endregion

#region Bot Commands

def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Olá! User o comando /vagas vacina para consultar ')

def format_msg_vacines_vacancies(vagas) -> str:
    msg = ''
    for vaga in vagas:
        inicio = datetime.fromisoformat(vaga['inicio']).strftime("%d/%m/%Y")
        fim = datetime.fromisoformat(vaga['fim']).strftime("%d/%m/%Y")
        
        msg += f'*{vaga["nome"].replace(" - "," no ")}*\n' \
               f'`{vaga["vagasDisponiveis"]}` vagas disponíves\n' \
               f'entre `{inicio}` e `{fim}`\n\n'
    return msg


def cmd_vagas(update: Update, context: CallbackContext)-> None:
    update.message.reply_text(f'💉 *Vacinas para COVID19*\n\n'
                              f'{format_msg_vacancies(payload)}',
                              parse_mode=ParseMode.MARKDOWN)

#endregion

#region Bot

#endregion

def main():
    """
    python3 main.py
    """
    updater = Updater(os.environ['BOT__TOKEN'])
    dp = updater.dispatcher
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    # /vagas
    dispatcher.add_handler(CommandHandler("vagas", cmd_vagas))
    # dispatcher.add_handler(CommandHandler("help", start))
    # dispatcher.add_handler(CommandHandler("set", set_timer))
    # dispatcher.add_handler(CommandHandler("unset", unset))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

# Todo
# Retornar número de vacinas por serviço
# Formatar o dado para exibição no bot