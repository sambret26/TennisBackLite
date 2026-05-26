from sqlalchemy.sql import func
from datetime import datetime
from database import db
from infrastructure.database.models.enums.match_status import MatchStatus

class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.BigInteger, primary_key=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.id'), nullable=False)
    grid_id = db.Column(db.BigInteger, db.ForeignKey('grids.id'), nullable=False)
    double = db.Column(db.Boolean, nullable=False, default=False)
    label = db.Column(db.String)
    player1_id = db.Column(db.BigInteger, db.ForeignKey('players.id'))
    player2_id = db.Column(db.BigInteger, db.ForeignKey('players.id'))
    team1_id = db.Column(db.BigInteger, db.ForeignKey('teams.id'))
    team2_id = db.Column(db.BigInteger, db.ForeignKey('teams.id'))
    future_player1 = db.Column(db.String)
    future_player2 = db.Column(db.String)
    day = db.Column(db.String)
    hour = db.Column(db.String)
    court_id = db.Column(db.BigInteger, db.ForeignKey('courts.id'))
    status = db.Column(db.Integer)
    winner_id = db.Column(db.BigInteger, db.ForeignKey('players.id'))
    team_winner_id = db.Column(db.BigInteger, db.ForeignKey('teams.id'))
    notif = db.Column(db.Boolean, nullable=False, default=False)
    score = db.Column(db.String)
    next_round =db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #Relationship
    category = db.relationship('Category', foreign_keys=[category_id])
    player1 = db.relationship('Player', foreign_keys=[player1_id])
    player2 = db.relationship('Player', foreign_keys=[player2_id])
    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])
    court = db.relationship('Court', foreign_keys=[court_id])
    winner = db.relationship('Player', foreign_keys=[winner_id])
    team_winner = db.relationship('Team', foreign_keys=[team_winner_id])
    grid = db.relationship('Grid', foreign_keys=[grid_id])

    @classmethod
    def from_fft(cls, data):
        return cls(
            id=int(data['matchId']),
            double=data["epreuveIsDouble"],
            court_id=data['courtId'] if data['courtId'] is not None else None
        )

    def to_dict(self):
        return {
            'fftId': self.id,
            'categoryId': self.category_id,
            'categoryLabel' : self.category.label if self.category is not None else "NC",
            'gridId': self.grid_id,
            'double': self.double,
            'label': self.label,
            'player1Id': self.player1_id if not self.double else self.team1_id,
            'player2Id': self.player2_id if not self.double else self.team2_id,
            'futurPlayer1': self.future_player1,
            'futurPlayer2': self.future_player2,
            'day': self.day,
            'hour': self.hour,
            'courtId': self.court_id,
            'winnerId': self.winner_id if not self.double else self.team_winner_id,
            'notif': self.notif,
            'score': self.score,
            'nextRound': self.next_round,
            'player1' : self.get_player1_for_mini_dict(),
            'player2' : self.get_player2_for_mini_dict(),
            'court' : self.court.to_dict() if self.court else None,
            'winner' : self.get_winner_for_mini_dict()
        }

    def get_player1_for_mini_dict(self):
        if self.player1:
            return self.player1.to_mini_dict()
        if self.team1:
            return self.team1.to_mini_dict()
        return None

    def get_player2_for_mini_dict(self):
        if self.player2:
            return self.player2.to_mini_dict()
        if self.team2:
            return self.team2.to_mini_dict()
        return None

    def get_winner_for_mini_dict(self):
        if self.winner:
            return self.winner.to_mini_dict()
        if self.teamWinner:
            return self.team_winner.to_mini_dict()
        return None


    def are_different(self, match):
        return (self.label != match.label or
                self.player1_id != match.team1_id or
                self.player2_id != match.team2_id or
                self.team1_id != match.team1_id or
                self.team2_id != match.team2_id or
                self.day != match.day or
                self.hour != match.hour or
                self.court_id != match.court_id or
                self.status != match.status or
                self.winner_id != match.winner_id or
                self.team_winner_id != match.team_winner_id or
                self.next_round != match.next_round)

    def get_formatted_date(self):
        day = self.day.split('-')
        if len(day) != 3 :
            return self.day
        return f"{day[2]}/{day[1]}"

    def get_formatted_hour(self):
        return self.hour.replace(':', 'h')

    def generate_match_finish_info(self):
        entity1 = self.team1 if self.double else self.player1
        entity2 = self.team2 if self.double else self.player2
        match_info = f"Le match {self.label} a opposé {entity1.getFullName()} et {entity2.getFullName()}"
        if self.day:
            match_info += f" le {self.get_formatted_date()}"
        if self.hour:
            match_info += f" à {self.get_formatted_hour()}"
        if self.court:
            match_info += f" sur le {self.court.name.lower()}"
        match_info += '.'
        if self.winner:
            match_info += f" Le gagnant est {self.winner.getFullName()}"
            if self.score:
                match_info += f" ({self.score})"
            match_info += '.'
        if self.team_winner:
            match_info += f" La paire gagnante est {self.team_winner.getFullName()}"
            if self.score:
                match_info += f" ({self.score})"
            match_info += '.'
        return match_info

    def generate_match_not_finish_info_message(self):
        entity1 = self.team1 if self.double else self.player1
        entity2 = self.team2 if self.double else self.player2
        if entity1 and entity2:
            info = f"Le match {self.label} opposera {entity1.getFullName()} à {entity2.getFullName()}"
        elif entity1:
            info = f"Le match {self.label} opposera {entity1.getFullName()} à ?"
        elif entity2:
            info = f"Le match {self.label} opposera {entity2.getFullName()} à ?"
        else:
            info = f"Le match {self.label} se jouera "
        if self.day:
            info += f" le {self.get_formatted_date()}"
        if self.hour:
            info += f" à {self.get_formatted_hour()}"
        if self.court:
            info += f" sur le {self.court.name.lower()}"
        info += "."
        return info

    @property
    def status_enum(self) -> MatchStatus:
        return MatchStatus(self.status)

    @status_enum.setter
    def status_enum(self, value: MatchStatus):
        self.status = int(value)