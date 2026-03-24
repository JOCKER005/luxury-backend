import json
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

VALID_CATEGORIES = {"anillos", "collares", "aretes", "pulseras"}

# ─── Products ─────────────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    name:        str
    category:    str
    price:       float
    stock:       Optional[int]       = 0
    featured:    Optional[bool]      = False
    active:      Optional[bool]      = True
    rating:      Optional[float]     = 5.0
    reviews:     Optional[int]       = 0
    description: Optional[str]       = ""
    image:       Optional[str]       = ""
    images:      Optional[List[str]] = []   # Lista de URLs adicionales

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v):
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Categoría inválida. Debe ser una de: {', '.join(sorted(VALID_CATEGORIES))}")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v

    @field_validator("rating")
    @classmethod
    def rating_must_be_valid(cls, v):
        if v is not None and not (1.0 <= v <= 5.0):
            raise ValueError("El rating debe estar entre 1 y 5")
        return v

    @field_validator("images")
    @classmethod
    def images_must_be_urls(cls, v):
        if v is None:
            return []
        # Máximo 10 imágenes adicionales
        return v[:10]


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name:        Optional[str]       = None
    category:    Optional[str]       = None
    price:       Optional[float]     = None
    stock:       Optional[int]       = None
    featured:    Optional[bool]      = None
    active:      Optional[bool]      = None
    rating:      Optional[float]     = None
    reviews:     Optional[int]       = None
    description: Optional[str]       = None
    image:       Optional[str]       = None
    images:      Optional[List[str]] = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v):
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f"Categoría inválida. Debe ser una de: {', '.join(sorted(VALID_CATEGORIES))}")
        return v

    @field_validator("rating")
    @classmethod
    def rating_must_be_valid(cls, v):
        if v is not None and not (1.0 <= v <= 5.0):
            raise ValueError("El rating debe estar entre 1 y 5")
        return v

    @field_validator("images")
    @classmethod
    def images_limit(cls, v):
        if v is not None:
            return v[:10]
        return v


class ProductOut(BaseModel):
    id:          int
    name:        str
    category:    str
    price:       float
    stock:       int
    featured:    bool
    active:      bool
    rating:      float
    reviews:     int
    description: str
    image:       str
    images:      List[str] = []
    created_at:  Optional[datetime] = None
    updated_at:  Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Convertimos el objeto SQLAlchemy a dict seguro
        data = obj.__dict__.copy()

        images = data.get("images")

        if isinstance(images, str):
            try:
                data["images"] = json.loads(images)
            except Exception:
                data["images"] = []
        elif images is None:
            data["images"] = []

        return super().model_validate(data, **kwargs)


# ─── Orders ───────────────────────────────────────────────────────────────────

class OrderItemOut(BaseModel):
    id:           int
    product_id:   Optional[int]
    product_name: str
    quantity:     int
    unit_price:   float

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id:               int
    mp_preference_id: Optional[str]
    mp_payment_id:    Optional[str]
    status:           str
    total:            float
    created_at:       Optional[datetime]
    items:            List[OrderItemOut] = []

    model_config = {"from_attributes": True}


# ─── Payments ─────────────────────────────────────────────────────────────────

class PaymentItem(BaseModel):
    productId: int
    name:      str
    price:     float
    quantity:  int
    image:     Optional[str] = ""

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_valid(cls, v):
        if v < 1 or v > 99:
            raise ValueError("La cantidad debe estar entre 1 y 99")
        return v

    @field_validator("productId")
    @classmethod
    def product_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("productId inválido")
        return v


class BackUrls(BaseModel):
    success: str
    failure: str
    pending: str

    @field_validator("success", "failure", "pending")
    @classmethod
    def urls_must_be_valid(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("Las URLs deben empezar con http:// o https://")
        return v


class PaymentPreferenceRequest(BaseModel):
    items:    List[PaymentItem]
    backUrls: BackUrls

    @field_validator("items")
    @classmethod
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("El carrito no puede estar vacío")
        return v


class PaymentPreferenceResponse(BaseModel):
    id:               str
    initPoint:        str
    sandboxInitPoint: str
