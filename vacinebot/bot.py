import logging
import os
from datetime import datetime
from pprint import pprint  

from addict import Dict
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

from . import utils


BASE_URL = 'https://vacina.vilavelha.es.gov.br/api'
logger = logging.getLogger('vilavelha.bot.vacina')


#region API

@utils.cache(60*5)
def get_all_vacines_vacancies():
    services_vacancies = {}
    
    response = requests.get(f'{BASE_URL}/categorias')
    categories_payload = response.json()

    for i, category in enumerate(categories_payload): 
        category_id = category['id']
        response = requests.get(f'{BASE_URL}/categorias/{category["id"]}/servicos')
        services_payload = response.json()
        
        for i, service in enumerate(services_payload): 
            service_id = service['id']

            response = requests.get(f'{BASE_URL}/servicos/{service_id}/unidades/vagas')
            vacancies_payload = response.json()

            if service_id not in vacancies_payload:
                services_vacancies[service_id] = Dict({
                    'id': service_id,
                    'category': category, 
                    'service': service, 
                    'vacancies': vacancies_payload
                })
            else:
                services_vacancies[service_id].vacancies.append(vacancies_payload)
    
    return services_vacancies.values()


#endregion

#region Bot Utils

def format_msg_vacines_vacancies(svv) -> str:
    msg = f'*# Vagas para Vacinação: * 💉\n\n' \
          f'*## {svv.category.nome}*\n\n' \
          f'*### {svv.service.nome}*\n'

    for vc in svv.vacancies: 
        inicio = datetime.fromisoformat(vc.inicio).strftime("%d/%m/%Y")
        fim = datetime.fromisoformat(vc.fim).strftime("%d/%m/%Y")
        msg += f'📍 *{vc.nome}*\n' \
               f'`{vc.vagasDisponiveis}` vagas disponíves\n' \
               f'entre `{inicio}` e `{fim}`\n'
    return msg

#endregion

#region Bot Commands

def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Olá! User o comando /vagas para consultar todas as vagas disponíveis')

def cmd_vagas(update: Update, context: CallbackContext)-> None:
    logger.info('command=vacines event=start')
    update.message.reply_text(f'🤖 `Buscando vagas de vacinação!`\n'
                              f'`Isso pode levar alguns segundos.`',
                              parse_mode=ParseMode.MARKDOWN)
    services_vacancies = get_all_vacines_vacancies()
    for svv in services_vacancies:
        vv_msg = format_msg_vacines_vacancies(svv)
        update.message.reply_text(vv_msg,
                                  parse_mode=ParseMode.MARKDOWN)
    logger.info('command=vacines event=end')

#endregion

#region Bot

def start():
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

#endregion
