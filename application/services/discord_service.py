from common.constants import constants

from infrastructure.database.repositories.channel_repository import ChannelRepository
from infrastructure.database.repositories.category_repository import CategoryRepository
from infrastructure.database.repositories.match_repository import MatchRepository

channel_repository = ChannelRepository()
category_repository = CategoryRepository()
match_repository = MatchRepository()

async def check(ctx):
    await ctx.send(messages.CONNECTED)

async def nb(bot, ctx):
    category = channel_repository.get_category_by_channel_id(ctx.channel.id)
    if category is None:
        await ctx.send(generate_total_message())
    else:
        await ctx.send(generate_number_by_category_message(category))
    details = await discordHelpers.yes_or_not(bot, ctx, messages.ASK_DETAILS) #TODO
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
    match = match_repository.get_match_by_label(match_label)
    if match is None:
        await ctx.send(messages.NO_MATCH.replace("MATCH_LABEL", match_label))
        return
    message = generate_match_info_message(match)
    await ctx.send(message)

async def pgw(bot):
    channel_id = channel_repository.get_log_channel_id("WA")
    channel = await bot.fetch_channel(channel_id)
    date = utils.get_current_date().strftime("%d/%m")
    request_date = utils.get_current_date().strftime("%Y-%m-%d")
    matches = match_repository.get_matches_by_date(request_date)
    if matches in (None, []):
        await channel.send(messages.NO_PG.replace("DATE", date))
    else:
        await channel.send(generate_schedule_message(matches, date))

async def auth(ctx, value: int = 0):
    if value == 0 or value == 1:
        settingRepository.setAuthError(value)
        await ctx.send(constants.AUTH_ERROR_SET.replace("VALUE", str(value)))
        return
    await ctx.send(constants.AUTH_ERROR_INVALID_PARAM)

async def cmd(ctx):
    await ctx.send(messages.COMMANDS_LIST)

async def clear(ctx, nombre: int = 100):
    await ctx.channel.purge(limit=nombre+1, check=lambda msg: not msg.pinned)

# ---------------------- Private methods ------------------------

def generate_total_message():
    categories = category_repository.get_all_categories()
    total = player_repository.get_total_players()
    message = f"Il y a {total} inscrit{'' if total < 2 else 's'} dans le tournoi"
    for category in categories:
        message += f"\n\t\t{generate_number_by_category_message(category)}"
    return message

def generate_number_by_category_message(category):
    players_number = player_categories_repository.get_player_number_by_category(category.id)
    return f"Il y a {players_number} inscrit{'' if players_number < 2 else 's'} dans la catégorie {category.code}"

def get_players_details():
    categories = category_repository.get_all_categories()
    rankings = ranking_repository.get_all_rankings()
    embed = Embed(title=messages.NB_INSCRITS_BY_CAT, color=discordHelpers.EMBED_COLOR)
    players_rankings_ids = player_repository.get_rankings_ids()
    message = generate_ranking_message(rankings, players_rankings_ids)
    embed.add_field(name=messages.TOTAL, value=message, inline=False)
    for category in categories:
        players_rankings_ids_by_category = player_repository.get_rankings_ids_by_category(category.id)
        message = generate_ranking_message(rankings, players_rankings_ids_by_category)
        embed.add_field(name=category.code, value=message, inline=False)
    return embed

def get_players_details_by_category(category):
    rankings = ranking_repository.get_all_rankings()
    embed = Embed(title=messages.NB_INSCRITS, color=discordHelpers.EMBED_COLOR)
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
            team1_name = match.team1.getFullNameWithRanking()
            team2_name = match.team2.getFullNameWithRanking()
            message += f"{match.hour} : {team1_name} contre {team2_name}\n"
        else:
            player1_name = match.player1.getFullNameWithRanking()
            player2_name = match.player2.getFullNameWithRanking()
            message += f"{match.hour} : {player1_name} contre {player2_name}\n"
    return message