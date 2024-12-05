from utilz.utils import discord_logger
import os 
import logging


logging.basicConfig(level=logging.INFO)


discord_logger(os.getenv('discord_hook'), "ETL pipeline event triggered")
logging.info("ETL pipeline event triggered")


