from core.template import Template

_name = 'BaseCube'
_author = 'Karako'
_description = """
This is base cube,you can add some base functions hear.
1.Do not delete this.
2.This cube cannot be reinstalled and uninstalled.
"""

from core.application.message.parser.kanata import Kanata
from core.application.message.parser.signature import (
    FullMatch,
    RequireParam,
)

from core.application import (
    MessageChain,
    Friend,
    KarakoMiraiApplication,
)
from cube import Cube
from . import feature
from utils.context import get_var
from utils import get_config

bot = get_var('bot')
app: KarakoMiraiApplication = bot.app


@feature(
    'FriendMessage',
    dispatchers=[Kanata([FullMatch("!root"), RequireParam('param')])]
)
async def friend_base(message: MessageChain, friend: Friend,
                      param: MessageChain):
    if friend.id == get_config('master'):
        cmd = param.asDisplay.strip() if param is not None else None

        if cmd == 'on':
            result = Cube.install_all_cube()

        if cmd == 're':
            try:
                Cube.reinstall_all_cube()
            except Exception as e:
                app.logger.exception(f'Cubes reinstall error:{e}')

        if cmd == 'off':
            try:
                Cube.uninstall_all_cube()
            except Exception as e:
                app.logger.exception(f'Cubes uninstall error:{e}')
                await app.sendFriendMessage(friend, Template(f"{e}"))
