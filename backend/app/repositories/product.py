from typing import List

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: AsyncDatabase):
        self.products = db["products"]

    @staticmethod
    def format_product(product: dict):
        return Product(
            name=product["name"],
            price=product["price"],
            id=str(product["_id"]),
            created_at=product["created_at"],
        )

    async def get_product_by_id(self, id: ObjectId) -> Product | None:
        if not ObjectId.is_valid(id):
            return None
        product = await self.products.find_one({"_id": ObjectId(id)})
        return self.format_product(product) if product else None

    async def get_product_by_name(self, name: str) -> Product:
        product = await self.products.find_one({"name": name})
        return self.format_product(product) if product else None

    async def get_list_of_products(self) -> List[Product]:
        products = await self.products.find().sort("name", 1).to_list(length=100)
        return [self.format_product(product) for product in products]

    async def create_product(self, product: Product):
        payload = product.model_dump(exclude={"id"})
        result = await self.products.insert_one(payload)
        product.id = str(result.inserted_id)
        return product

    async def delete_product(self, product_id: ObjectId):
        return await self.products.delete_one({"_id": ObjectId(product_id)})
