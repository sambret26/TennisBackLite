from infrastructure.database.repositories.category_repository import CategoryRepository
from infrastructure.database.repositories.channel_repository import ChannelRepository
from infrastructure.database.repositories.message_repository import MessageRepository

category_repository = CategoryRepository()
channel_repository = ChannelRepository()
message_repository = MessageRepository()


async def run(bot):
    channel_map = channel_repository.get_logs_channel_map()
    await send_notification_by_category(bot, "G", channel_map.get("G"))
    categories = category_repository.get_all_categories()
    for category in categories:
        await send_notification_by_category(bot, category.code, channel_map.get(category.code))
    await send_other_notification(bot, channel_map)

async def send_other_notification(bot, channel_map):
    messages = message_repository.get_all_messages()
    messages_by_category = {}
    for message in messages:
        if message.category not in messages_by_category:
            messages_by_category[message.category] = []
        messages_by_category[message.category].append(message)
    messages_id_to_delete = []
    for category, messages_in_category in messages_by_category.items():
        channel_id = channel_map.get(category)
        channel = bot.get_channel(channel_id)
        for i in range(0, len(messages_in_category), 20):
            message = '\n'.join([m.message for m in messages_in_category[i:i + 20]])
            await channel.send(message)
        messages_id_to_delete.extend([m.id for m in messages_in_category])
    message_repository.delete_messages_by_id(messages_id_to_delete)

async def send_notification_by_category(bot, category_code, channel_id):
    messages = message_repository.get_messages_by_category(category_code)
    channel = bot.get_channel(channel_id)
    for i in range(0, len(messages), 20):
        message = '\n'.join([m.message for m in messages[i:i + 20]])
        await channel.send(message)
    message_repository.delete_messages_by_category(category_code)

