from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncDatabase) -> None:
        self.users = db['users']

    @staticmethod
    def format_user(doc: dict) -> User:
        return User(id=str(doc['_id']), email=doc['email'], hashed_password=doc['hashed_password'], is_active=doc.get('is_active', True), profile=doc.get('profile') or None, created_at=doc['created_at'])

    async def get_user_by_id(self, user_id: str) -> (User | None):
        if not (ObjectId.is_valid(user_id)):
            return
        doc = await self.users.find_one({'_id': ObjectId(user_id)})
        if doc:
            return self.format_user(doc)
        return

    async def get_user_by_email(self, email: str) -> (User | None):
        doc = await self.users.find_one({'email': email})
        if doc:
            return self.format_user(doc)
        return

    async def create_user(self, user: User) -> User:
        payload = user.model_dump(exclude={'id'})
        result = await self.users.insert_one(payload)
        user.id = str(result.inserted_id)
        return user
