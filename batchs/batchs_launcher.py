from application.services import discord_service
from batchs import call_ups_batch
from batchs import registrations_batch
from batchs import notifications_sender_batch
from batchs import update_matches_batch
from infrastructure.database.repositories.setting_repository import SettingRepository

from infrastructure.logger.logger import log, BATCH

setting_repository = SettingRepository()

async def pgw(bot):
    if setting_repository.get_batchs_active() is False:
        return
    log.info(BATCH, "Lancement du batch pgw")
    await discord_service.pgw(bot)
    log.info(BATCH, "Fin du batch pgw")

async def registrations():
    if setting_repository.get_batchs_active() is False:
        return
    log.info(BATCH, "Lancement du batch inscriptions")
    registrations_batch.run(True)
    log.info(BATCH, "Fin du batch inscriptions")

async def call_ups():
    if setting_repository.get_batchs_active() is False:
        return
    log.info(BATCH, "Lancement du batch convocations")
    call_ups_batch.run()
    log.info(BATCH, "Fin du batch convocations")

async def send_notif_loop(bot):
    if setting_repository.get_batchs_active() is False:
        return
    log.info(BATCH, "Lancement du batch sendNotif")
    await notifications_sender_batch.run(bot)
    log.info(BATCH, "Fin du batch sendNotif")

async def update_matches():
    if setting_repository.get_batchs_active() is False:
        return
    log.info(BATCH, "Lancement du batch updateMatch")
    update_matches_batch.run()
    log.info(BATCH, "Fin du batch updateMatch")