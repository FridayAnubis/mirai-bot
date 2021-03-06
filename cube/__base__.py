_disable = False
_name = 'BaseCube'
_author = 'Karako'
_description = """
This is base cube,you can add some base functions hear.
1.Do not delete this.
2.This cube cannot be reinstalled and uninstalled.
"""

from core.application import (
    MessageChain,
    Friend,
    KarakoMiraiApplication,
)
from core.application.message.parser.kanata import Kanata
from core.application.message.parser.signature import (
    FullMatch,
    RequireParam,
    OptionalParam,
)
from core.template import Template
from cube import Cube
from utils import (
    get_bot_config,
    serial_number,
)
from utils.context import get_var
from . import feature

bot = get_var('bot')
app: KarakoMiraiApplication = bot.application


@feature(
        'FriendMessage',
        dispatchers=Kanata([FullMatch("!cube"), OptionalParam('param')])
)
async def friend_cube(friend: Friend, param: MessageChain):
    if friend.id == get_bot_config('master'):
        cmd = param.asDisplay.strip() if param is not None else None
        content = ''
        if cmd is None or cmd == '':
            for cube in Cube.__cube_list__:
                content += "{} {}-{}\n".format(
                        serial_number(Cube.__cube_list__.index(cube) + 1),
                        cube.name,
                        cube.author
                )
            content = content[:-1]
            await app.sendFriendMessage(friend, Template(content))


@feature(
        'FriendMessage',
        dispatchers=Kanata([FullMatch("!switch"), RequireParam('param')])
)
async def cube_switch(friend: Friend, param: MessageChain):
    result = [_ for _ in param.asDisplay.strip(' ').split(' ') if _ != '']
    if len(result) == 2:
        cmd = result[0]
        name = result[1]
    else:
        name = result[0]
        cmd = 'sw'
    cube = Cube.get_by_name(name)
    if cube is not None:
        try:
            if cmd == 'on':
                cube.turn_on()
            elif cmd == 'off':
                cube.turn_off()
            elif cmd == 're':
                cube.reinstall()
            elif cmd == 'sw':
                cube.switch()
            else:
                await app.sendFriendMessage(friend, Template("????????????????????????"))
                return
            await app.sendFriendMessage(friend, Template(f"??????????????????"))
        except Exception as e:
            await app.sendFriendMessage(friend, Template(f"?????????????????????????????????????????????{e}"))
            app.logger.exception(e)
    else:
        await app.sendFriendMessage(friend, Template(f"???????????????'{name}'???cube"))
