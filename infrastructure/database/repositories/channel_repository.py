from infrastructure.database.models.category import Category
from infrastructure.database.models.channel import Channel


class ChannelRepository:

    @staticmethod
    def get_category_by_channel_id(channel_id):
        return (Category.query.join(Channel, Category.code == Channel.category)
            .filter(Channel.id == channel_id).first())

    @staticmethod
    def get_log_channel_id(category):
        return Channel.query.filter_by(category=category, channel_type='Logs').first().id

    @staticmethod
    def get_logs_channel_map():
        return {channel.category: channel.id for channel in Channel.query.filter_by(channel_type='Logs').all()}