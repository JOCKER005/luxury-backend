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

    @field_validator("images", mode="before")
    @classmethod
    def parse_images(cls, v):
        """Convierte el string JSON almacenado en DB a lista Python."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return []


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
    # Datos del comprador (desde MP webhook)
    payer_name:       Optional[str] = None
    payer_email:      Optional[str] = None
    payer_dni:        Optional[str] = None
    payer_phone:      Optional[str] = None
    # Datos de envío (desde el checkout)
    shipping_name:    Optional[str] = None
    shipping_dni:     Optional[str] = None
    shipping_phone:   Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_zip:     Optional[str] = None
    shipping_notes:   Optional[str] = None

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


class ShippingData(BaseModel):
    name:    str
    dni:     str
    phone:   str
    address: str
    zip:     str
    notes:   Optional[str] = ""

    @field_validator("name")
    @classmethod
    def name_required(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre es requerido")
        return v.strip()

    @field_validator("dni")
    @classmethod
    def dni_required(cls, v):
        if not v or not v.strip():
            raise ValueError("El DNI es requerido")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def phone_required(cls, v):
        if not v or not v.strip():
            raise ValueError("El teléfono es requerido")
        return v.strip()

    @field_validator("address")
    @classmethod
    def address_required(cls, v):
        if not v or not v.strip():
            raise ValueError("La dirección es requerida")
        return v.strip()

    @field_validator("zip")
    @classmethod
    def zip_required(cls, v):
        if not v or not v.strip():
            raise ValueError("El código postal es requerido")
        return v.strip()


class PaymentPreferenceRequest(BaseModel):
    items:        List[PaymentItem]
    backUrls:     BackUrls
    shippingData: ShippingData

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
