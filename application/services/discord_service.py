from datetime import datetime as date
from datetime import timedelta
from discord.ui import Button, View
from discord import Embed, ButtonStyle
from batchs.batchs_launcher import setting_repository
from common.constants import constants, messages, settings

from common.constants.messages import YES_OR_NO
from infrastructure.database.repositories.channel_repository import ChannelRepository
from infrastructure.database.repositories.category_repository import CategoryRepository
from infrastructure.database.repositories.match_repository import MatchRepository
from infrastructure.database.repositories.player_categories_repository import PlayerCategoriesRepository
from infrastructure.database.repositories.player_repository import PlayerRepository
from infrastructure.database.repositories.ranking_repository import RankingRepository
from infrastructure.database.repositories.setting_repository import SettingRepository

channel_repository = ChannelRepository()
category_repository = CategoryRepository()
match_repository = MatchRepository()
player_categories_repository = PlayerCategoriesRepository()
player_repository = PlayerRepository()
ranking_repository = RankingRepository()
setting_repository = SettingRepository()

async def check(ctx):
    await ctx.send(messages.CONNECTED)

async def nb(bot, ctx):
    category = channel_repository.get_category_by_channel_id(ctx.channel.id)
    if category is None:
        await ctx.send(generate_total_message())
    else:
        await ctx.send(generate_number_by_category_message(category))
    details = await yes_or_not(bot, ctx, messages.ASK_DETAILS) #TODO
    if details :
        if category is None:
            await ctx.send(embed=get_players_details())
        else:
            await ctx.send(embed=get_players_details_by_category(category))

async def info(ctx, match_label: str = None):
    if match_label is None:
        await ctx.send(messages.INFO_INVALID_PARAM)
        return
    match_label = match_label.upper()
    match = match_repository.get_by_label(match_label)
    if match is None:
        await ctx.send(messages.NO_MATCH.replace("MATCH_LABEL", match_label))
        return
    message = generate_match_info_message(match)
    await ctx.send(message)

async def pgw(bot):
    channel_id = channel_repository.get_log_channel_id("WA")
    channel = await bot.fetch_channel(channel_id)
    date = get_current_date().strftime("%d/%m")
    request_date = get_current_date().strftime("%Y-%m-%d")
    matches = match_repository.get_all_by_date(request_date)
    if matches in (None, []):
        await channel.send(messages.NO_PG.replace("DATE", date))
    else:
        await channel.send(generate_schedule_message(matches, date))

async def auth(ctx, value: int = 0):
    if value == 0 or value == 1:
        setting_repository.set_auth_error(value)
        await ctx.send(constants.AUTH_ERROR_SET.replace("VALUE", str(value)))
        return
    await ctx.send(constants.AUTH_ERROR_INVALID_PARAM)

async def cmd(ctx):
    await ctx.send(messages.COMMANDS_LIST)

async def clear(ctx, nombre: int = 100):
    await ctx.channel.purge(limit=nombre+1, check=lambda msg: not msg.pinned)

# ---------------------- Private methods ------------------------

def generate_total_message():
    categories = category_repository.get_all()
    total = player_repository.get_total_players()
    message = f"Il y a {total} inscrit{'' if total < 2 else 's'} dans le tournoi"
    for category in categories:
        message += f"\n\t\t{generate_number_by_category_message(category)}"
    return message

def generate_number_by_category_message(category):
    players_number = player_categories_repository.get_player_number_by_category(category.id)
    return f"Il y a {players_number} inscrit{'' if players_number < 2 else 's'} dans la catégorie {category.code}"

def get_players_details():
    categories = category_repository.get_all()
    rankings = ranking_repository.get_all()
    embed = Embed(title=messages.NB_INSCRITS_BY_CAT, color=settings.EMBED_COLOR)
    players_rankings_ids = player_repository.get_rankings_ids()
    message = generate_ranking_message(rankings, players_rankings_ids)
    embed.add_field(name=messages.TOTAL, value=message, inline=False)
    for category in categories:
        players_rankings_ids_by_category = player_repository.get_rankings_ids_by_category(category.id)
        message = generate_ranking_message(rankings, players_rankings_ids_by_category)
        embed.add_field(name=category.code, value=message, inline=False)
    return embed

def get_players_details_by_category(category):
    rankings = ranking_repository.get_all()
    embed = Embed(title=messages.NB_INSCRITS, color=settings.EMBED_COLOR)
    players_rankings_ids_by_category = player_repository.get_rankings_ids_by_category(category.id)
    message = generate_ranking_message(rankings, players_rankings_ids_by_category)
    embed.add_field(name=category.code, value=message, inline=False)
    return embed

def generate_ranking_message(rankings, players_rankings_ids_by_category):
    message = ""
    for ranking in rankings:
        if ranking.id in players_rankings_ids_by_category:
            message += f"{ranking.simple.ljust(4)} : {players_rankings_ids_by_category.count(ranking.id)}\n"
    return message

def generate_match_info_message(match):
    if match.status_enum == MatchStatus.FINISHED:
        return match.generate_match_finish_info()
    return match.generate_match_not_finish_info_message()

def generate_schedule_message(matches, date):
    message = messages.PG.replace("DATE", date)
    for match in matches:
        if match.double:
            team1_name = match.team1.get_full_name_with_ranking()
            team2_name = match.team2.get_full_name_with_ranking()
            message += f"{match.hour} : {team1_name} contre {team2_name}\n"
        else:
            player1_name = match.player1.get_full_name_with_ranking()
            player2_name = match.player2.get_full_name_with_ranking()
            message += f"{match.hour} : {player1_name} contre {player2_name}\n"
    return message

async def yes_or_not(bot, ctx, message):
    return await question(bot, ctx, message, messages.YES_OR_NO)

async def question(bot, ctx, message, choices):
    while len(choices) > 0:
        question_choices = choices[:4]
        if len(question_choices) == 4:
            question_choices.append(messages.QUESTION_MORE)
        result = await question_5_max(bot, ctx, message, question_choices)
        if result != "Next":
            return result
        choices = choices[4:]

async def question_5_max(bot, ctx, message, choices):

    def check(i):
        return i.user.id == ctx.author.id and i.message.id == choice.id

    buttons = generate_buttons(choices)
    view = View()
    for button in buttons :
        view.add_item(button)
    choice = await ctx.send(message, view=view)
    interaction = await bot.wait_for("interaction", check=check)
    custom_id = interaction.data['custom_id']
    await interaction.response.edit_message(content=f"{message} ({custom_id})")
    if custom_id.isdigit() :
        return int(custom_id)
    return custom_id

def generate_buttons(choices):
    buttons = []
    for (index, choice) in enumerate(choices):
        style = find_style(index, choice[2] if len(choice) >  2 else None)
        button = Button(label=choice[0], custom_id=choice[1], style=style)
        buttons.append(button)
    return buttons

def find_style(index, value):
    if value is not None and value.lower() == constants.GREEN:
        return ButtonStyle.green
    if value is not None and value.lower() == constants.RED:
        return ButtonStyle.red
    if value is not None and value.lower() == constants.BLUE:
        return ButtonStyle.blue
    if index % 3 == 0:
        return ButtonStyle.green
    if index % 3 == 1:
        return ButtonStyle.red
    return ButtonStyle.blue

def get_current_date():
    return date.now() + timedelta(hours=0)