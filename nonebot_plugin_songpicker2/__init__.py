from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot import on_command

from .data_source import DataGet, DataProcess

songpicker = on_command("点歌")

dataGet = DataGet()


@songpicker.handle()
async def _(args: Message = CommandArg(), state: T_State):
    args = str(args).split(" ")
    if len(args) > 0:
        state["song_name"] = args[0]
        # TODO: add config option for default choice
    if len(args) > 1:
        state["choice"] = args[1]


@songpicker.got("song_name", prompt="歌名是？")
async def _(state: T_State):
    song_name = state["song_name"]
    song_ids = await dataGet.song_ids(song_name=song_name)
    if not song_ids:
        await songpicker.reject("没有找到这首歌，请发送其它歌名！")
    song_infos = list()
    for song_id in song_ids:
        song_info = await dataGet.song_info(song_id=song_id)
        song_infos.append(song_info)

    song_infos = await DataProcess.mergeSongInfo(song_infos=song_infos)
    if not "choice" in state:
        await songpicker.send(song_infos)
    state["song_ids"] = song_ids


@songpicker.got("choice")
async def _(state: T_State):
    song_ids = state["song_ids"]
    choice = state["choice"]
    try:
        choice = int(str(choice))
    except ValueError:
        await songpicker.reject("选项只能是数字，请重选")
    if choice >= len(song_ids):
        await songpicker.reject("选项超出可选范围，请重选")

    selected_song_id = song_ids[choice]
    await songpicker.send(MessageSegment.music("163", int(selected_song_id)))

    song_comments = await dataGet.song_comments(song_id=selected_song_id)
    song_comments = await DataProcess.mergeSongComments(song_comments=song_comments)
    song_comments = "下面为您播送热评：\n" + song_comments

    await songpicker.finish(song_comments)
