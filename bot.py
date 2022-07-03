import os
from dotenv import load_dotenv
import hikari
import lightbulb
import quoth
import ogs
import ipdb

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = lightbulb.BotApp(token=TOKEN, prefix='!')

gamenumber = "0"
movenumber = '0'
gamelink = "https://online-go.com/game/66666"
image = "https://online-go.com/api/v1/games/40424920/apng/40424920-1-1-1500.png?from=0&to=1&frame_delay=1500"

@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return
    
    if event.content.startswith("https://online-go.com/game/"):
        global gamenumber
        global gamelink
        gamelink = event.content
        gamenumber = ogs.getID(gamelink)
        game = ogs.Game(gamenumber)
        game.draw_kifu()
        await event.message.respond(attachment=game.kifu)
    
    if event.content.startswith("..user"):
        #ipdb.set_trace()
        await event.message.respond(f"event.message.author:```{event.message.author}```")
        await event.message.respond(f"event.author.id:```{event.author.id}```")

@bot.command
@lightbulb.command("link", "gets link to current game")
@lightbulb.implements(lightbulb.PrefixCommand)
async def link(ctx: lightbulb.Context) -> None:
    global gamelink
    print(ctx.options.text)
    gameid = ogs.getID(gamelink)
    await ctx.respond(ogs.verses(gameid))

    await ctx.respond(gamelink)
    
@bot.command
@lightbulb.option("size", "width of image in pixels")
@lightbulb.option("playerID", "input OGS player ID")
@lightbulb.command("player", "test function for player data")
@lightbulb.implements(lightbulb.PrefixCommand)
async def player(ctx: lightbulb.Context) -> None:
    print(ctx.options.playerID)
    print(ctx.options.size)
    player = ogs.Player(ctx.options.playerID)
    size = ctx.options.size
    
    await ctx.respond(attachment=player.get_icon(size))
    
@bot.command
@lightbulb.option("gameID", "OGS game ID")
@lightbulb.command("gamelike", "test function for game data")
@lightbulb.implements(lightbulb.PrefixCommand)
async def gamelike(ctx: lightbulb.Context) -> None:
    print(ctx.options.gameID)
    game = ogs.Game(ctx.options.gameID)
    print(game.link)
    print(game.totalmoves)
    await ctx.respond(attachment=game.gif())
    
    
@bot.command
@lightbulb.command("coords", "shows game with coordinates")
@lightbulb.implements(lightbulb.PrefixCommand)
async def link(ctx: lightbulb.Context) -> None:
    global image
    coordinates = ogs.add_coordinates(image)
    await ctx.respond(attachment=coordinates)
    
@bot.command
@lightbulb.command("cat", "shows a cat that does not exist")
@lightbulb.implements(lightbulb.PrefixCommand)
async def cat(ctx):
    await ctx.respond(attachment=ogs.cat())
    
@bot.command
@lightbulb.command("human", "shows a human that does not exist")
@lightbulb.implements(lightbulb.PrefixCommand)
async def human(ctx):
    await ctx.respond(attachment=ogs.human())
    
@bot.command
@lightbulb.command("anime", "shows an anime that does not exist")
@lightbulb.implements(lightbulb.PrefixCommand)
async def anime(ctx):
    attachment, seed, creativity = ogs.anime()
    await ctx.respond(attachment)
    await ctx.respond(f"Seed = {seed}, creativity = {creativity}")

@bot.command
@lightbulb.command("ping", "checks the bot is alive")
@lightbulb.implements(lightbulb.PrefixCommand)
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond("Poong!")
    await ctx.respond("POoOOOOOOooooong")

@bot.command
@lightbulb.option("text", "input OGS game ID")
@lightbulb.command("game", "sets the OGS game ID")
@lightbulb.implements(lightbulb.PrefixCommand)
async def game(ctx: lightbulb.Context) -> None:
    global gamenumber
    print(ctx.options.text)
    gamenumber = ctx.options.text
    image = "https://online-go.com/api/v1/games/" + gamenumber + "/png/" + gamenumber + ".png"
    print(image)
    await ctx.respond(image)

@bot.command
@lightbulb.option("text", "input move number")
@lightbulb.command("move", "sets the move number to display")
@lightbulb.implements(lightbulb.PrefixCommand)
async def move(ctx: lightbulb.Context) -> None:
    global image
    movenumber = ctx.options.text
    image = "https://online-go.com/api/v1/games/" + gamenumber + "/apng/" + gamenumber + "-0-0-1500.png?from=" + movenumber + "&to=" + str(int(movenumber) + 1) + "&frame_delay=1500"
    print(image)
    await ctx.respond(image)

@bot.command
@lightbulb.option("text", "get quote command")
@lightbulb.command("!", "will respond with a goofy message given the right input")
@lightbulb.implements(lightbulb.PrefixCommand)
async def goofy(ctx: lightbulb.Context) -> None:
    word = ctx.options.text
    if word == "esc":
        await ctx.respond("hop outta here!")
        
@bot.command
@lightbulb.command("quote", "quotes Hamlet")
@lightbulb.implements(lightbulb.PrefixCommand)
async def quote(ctx: lightbulb.Context) -> None:
    await ctx.respond(quoth.quotation())

bot.run()

