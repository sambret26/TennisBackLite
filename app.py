from flask import Flask
import threading
from application.controllers import discord_controller
from config import Config
from database import db
from application.controllers.match_controller import match_bp
from application.controllers.setting_controller import setting_bp
from application.controllers.profile_controller import profile_bp
from application.controllers.user_controller import user_bp
from application.controllers.competition_controller import competition_bp

from infrastructure.database.models.category import Category
from infrastructure.database.models.channel import Channel
from infrastructure.database.models.call_up import CallUp
from infrastructure.database.models.court import Court
from infrastructure.database.models.grid import Grid
from infrastructure.database.models.message import Message
from infrastructure.database.models.player_categories import PlayerCategories
from infrastructure.database.models.ranking import Ranking
from infrastructure.database.models.team import Team
from infrastructure.database.models.url import Url

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config.from_object(Config)
db.init_app(app)


# Registering blueprints
app.register_blueprint(match_bp)
app.register_blueprint(setting_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(user_bp)
app.register_blueprint(competition_bp)


def run_discord_bot():
    with app.app_context():
        discord_controller.main()

# Création des tables
with app.app_context():
    db.create_all()

discordThread = threading.Thread(target=run_discord_bot)
discordThread.start()

if __name__ == '__main__':
    app.run()