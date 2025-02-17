from datetime import datetime
from logging import getLogger

from aiohttp import ClientSession
from discord import Client, Object, app_commands

from classes.config import Config

log = getLogger(__name__)


class FAQ_Client(Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = datetime.utcnow()
        self.tree = app_commands.CommandTree(self)
        self.config = Config().load()
        self.modmail_support = Object(self.config.guild)
        self.version = self.config.version

    @property
    def uptime(self):
        return datetime.utcnow() - self.start_time

    async def setup_hook(self) -> None:
        log.info("Setting up hook...")
        log.info(f"Client user; {self.user} ({self.user.id})")
        log.info(f"Client version; {self.version}")
        log.info(f"Client Start Time; {self.start_time}")
        self.tree.copy_global_to(guild=self.modmail_support)
        await self.tree.sync(guild=self.modmail_support)

    async def main(self):
        async with ClientSession() as session:
            async with self:
                self.session = session
                await self.start(self.config.token)
