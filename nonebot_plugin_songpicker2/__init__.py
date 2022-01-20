# import nonebot
from .data_source import dataGet, dataProcess
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.params import State
from nonebot import on_command


dataget = dataGet()

songpicker = on_command("点歌")


@songpicker.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State = State()):
    args = str(event.get_message()).strip()
    if args:
        state["songName"] = args


@songpicker.got("songName", prompt="歌名是？")
async def handle_songName(bot: Bot, event: Event, state: T_State = State()):
    songName = state["songName"]
    songIdList = await dataget.songIds(songName=songName)
    if songIdList is None:
        await songpicker.reject("没有找到这首歌，请发送其它歌名！")
    songInfoList = list()
    for songId in songIdList:
        songInfoDict = await dataget.songInfo(songId)
        songInfoList.append(songInfoDict)
    songInfoMessage = await dataProcess.mergeSongInfo(songInfoList)
    await songpicker.send(songInfoMessage)
    state["songIdList"] = songIdList


@songpicker.got("songNum")
async def handle_songNum(bot: Bot, event: Event, state: T_State = State()):
    songIdList = state["songIdList"]
    songNum = int(state["songNum"])

    if songNum >= len(songIdList):
        await songpicker.reject("数字序号错误，请重选")

    selectedSongId = songIdList[int(songNum)]

    await songpicker.send(MessageSegment.music("163", selectedSongId))

    songCommentsDict = await dataget.songComments(songId=selectedSongId)
    state["songCommentsDict"] = songCommentsDict
    songCommentsMessage = await dataProcess.mergeSongComments(songCommentsDict)
    commentContent = "下面为您播送热评：\n" + songCommentsMessage
    await songpicker.send(commentContent)


