from sqlalchemy.orm import Session
from models.user import User

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_name(db: Session, name: str):
        # Recherche par nom complet ou partiel
        full_name = name.strip()
        # Essayer d'abord une correspondance exacte
        user = db.query(User).filter(
            (User.first_name + " " + User.last_name) == full_name
        ).first()
        if user:
            return user
        # Sinon, rechercher par prénom ou nom
        user = db.query(User).filter(
            (User.first_name == full_name) | (User.last_name == full_name)
        ).first()
        return user
