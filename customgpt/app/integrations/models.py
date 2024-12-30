from app import db

bots_integrations = db.Table(
    "bots_integrations",
    db.Model.metadata,
    db.Column("integration_id", db.Integer, db.ForeignKey("integrations.id")),
    db.Column("bot_id", db.Integer, db.ForeignKey("bots.id")),
)


# Модель интеграции бота
class Integration(db.Model):
    __tablename__ = "integrations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    bots = db.relationship("Bot", secondary=bots_integrations, back_populates="integrations")
