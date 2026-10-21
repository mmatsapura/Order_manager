from pymongo.errors import DuplicateKeyError

from app.core.exceptions import ProductNameTaken, ProductNotFound
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate


class ProductService:
    def __init__(self, product_repo: ProductRepository) -> None:
        self.product_repo = product_repo

    async def list_products(self):
        products = await self.product_repo.get_list_of_products()
        return products

    async def create_product(self, data: ProductCreate) -> Product:
        product = Product(name=data.name, price=data.price)
        try:
            return await self.product_repo.create_product(product)
        except DuplicateKeyError:
            raise ProductNameTaken(product.name)

    async def get_product(self, product_id: str) -> Product:
        product = await self.product_repo.get_product_by_id(product_id)
        if product is None:
            raise ProductNotFound()
        return product

    async def delete_product(self, product_id: str) -> None:
        product = await self.product_repo.get_product_by_id(product_id)
        if product is None:
            raise ProductNotFound()
        await self.product_repo.delete_product(product_id)
        return
