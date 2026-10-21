from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import ProductNotFound, ProductNameTaken
from app.dependencies import get_current_user, get_product_repository
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductPublic
from app.services.product import ProductService
from app.models.user import User


router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductPublic])
async def get_all_products(repo: ProductRepository = Depends(get_product_repository),
                           _current_user: User = Depends(get_current_user)):
    service = ProductService(repo)
    return await service.list_products()


@router.get("/{product_id}", response_model=ProductPublic)
async def get_product_by_id(product_id: str, repo: ProductRepository = Depends(get_product_repository),
                            _current_user: User = Depends(get_current_user)):
    service = ProductService(repo)
    try:
        return await service.get_product(product_id)
    except ProductNotFound:
        raise HTTPException(status_code=404, detail="Product not found")


@router.post("", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
async def create_product(
        body: ProductCreate,
        repo: ProductRepository = Depends(get_product_repository),
        _current_user: User = Depends(get_current_user)):
    service = ProductService(repo)
    try:
        return await service.create_product(body)
    except ProductNameTaken as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product name taken")


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, current_user: User = Depends(get_current_user),
                         repo: ProductRepository = Depends(get_product_repository)):
    service = ProductService(repo)
    try:
        return await service.delete_product(product_id)
    except ProductNotFound:
        raise HTTPException(status_code=404, detail="Product not found")
