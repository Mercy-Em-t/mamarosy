"""Shop and product catalog models for provisioning data into another system."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import asdict, dataclass, field
from typing import Optional

CANONICAL_IMPORT_FIELDS: tuple[str, ...] = (
    "sku",
    "product_name",
    "category",
    "subcategory",
    "brand_supplier",
    "size_quantity",
    "unit_price_kes",
    "bulk_pricing_discounts",
    "stock_availability",
    "reorder_level",
    "expiry_date",
    "product_image",
    "short_description",
    "benefits_key_features",
    "usage_how_to_use",
    "diet_health_tags",
    "origin_source",
    "processing_type",
    "nutritional_info",
    "ratings_reviews",
    "promotional_tag",
    "packaging_type",
    "delivery_option",
    "recipe_pairing_suggestions",
    "video_demo_link",
)

_HEADER_ALIASES = {
    "sku": "sku",
    "sku_product_code": "sku",
    "product_name": "product_name",
    "category": "category",
    "subcategory": "subcategory",
    "brand_supplier": "brand_supplier",
    "size_quantity": "size_quantity",
    "unit_price_kes": "unit_price_kes",
    "bulk_pricing_discounts": "bulk_pricing_discounts",
    "stock_availability": "stock_availability",
    "reorder_level": "reorder_level",
    "expiry_date": "expiry_date",
    "product_image": "product_image",
    "short_description": "short_description",
    "benefits_key_features": "benefits_key_features",
    "usage_how_to_use": "usage_how_to_use",
    "diet_health_tags": "diet_health_tags",
    "origin_source": "origin_source",
    "processing_type": "processing_type",
    "nutritional_info": "nutritional_info",
    "ratings_reviews": "ratings_reviews",
    "promotional_tag": "promotional_tag",
    "packaging_type": "packaging_type",
    "delivery_option": "delivery_option",
    "recipe_pairing_suggestions": "recipe_pairing_suggestions",
    "video_demo_link": "video_demo_link",
}

_CATEGORY_ALIASES = {
    "cereals": "Cereals & Grains",
    "cereals & grains": "Cereals & Grains",
    "pulses": "Pulses & Legumes",
    "pulses & legumes": "Pulses & Legumes",
    "nuts": "Nuts & Nut Products",
    "nuts & seeds": "Nuts & Nut Products",
    "nuts & nut products": "Nuts & Nut Products",
    "seeds": "Seeds",
    "spices": "Spices & Seasonings",
    "spices & seasonings": "Spices & Seasonings",
    "supplements": "Health Supplements",
    "health supplements": "Health Supplements",
    "natural products": "Natural Sweeteners & Additives",
    "natural sweeteners": "Natural Sweeteners & Additives",
    "teas & wellness": "Herbal Teas & Drinks",
    "herbal teas & drinks": "Herbal Teas & Drinks",
}

_VALID_STOCK_AVAILABILITY = {"available", "limited", "out of stock", "preorder"}
_REQUIRED_IMPORT_FIELDS = {
    "sku",
    "product_name",
    "category",
    "subcategory",
    "brand_supplier",
    "size_quantity",
    "unit_price_kes",
    "stock_availability",
}


def _normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _normalize_category(value: str) -> str:
    cleaned = _normalize_text(value)
    return _CATEGORY_ALIASES.get(cleaned.lower(), cleaned)


def _split_multi_value(value: str) -> list[str]:
    normalized = _normalize_text(value)
    if not normalized or normalized == "-":
        return []
    parts = re.split(r"\s*(?:\||;|,)\s*", normalized)
    return [part for part in parts if part]


def _parse_price_kes(value: str) -> float:
    cleaned = _normalize_text(value).replace(",", "")
    cleaned = re.sub(r"^kes\s*", "", cleaned, flags=re.IGNORECASE)
    try:
        return float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Invalid unit price KES value: {value!r}") from exc


def _parse_expiry_date(value: str) -> Optional[str]:
    cleaned = _normalize_text(value)
    if not cleaned or cleaned == "-":
        return None
    for date_format in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(cleaned, date_format).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Invalid expiry date format: {value!r}")


def canonicalize_catalog_row(raw_row: dict[str, str]) -> dict[str, str]:
    """Map external headers and normalize values into canonical import format."""
    canonical: dict[str, str] = {field: "" for field in CANONICAL_IMPORT_FIELDS}
    for header, value in raw_row.items():
        normalized_header = _normalize_header(header)
        canonical_field = _HEADER_ALIASES.get(normalized_header)
        if canonical_field is None:
            continue
        canonical[canonical_field] = _normalize_text(str(value))
    canonical["category"] = _normalize_category(canonical["category"])
    canonical["unit_price_kes"] = str(_parse_price_kes(canonical["unit_price_kes"]))
    canonical["stock_availability"] = canonical["stock_availability"].lower()
    if canonical["stock_availability"] not in _VALID_STOCK_AVAILABILITY:
        raise ValueError(
            f"Invalid stock availability value: {canonical['stock_availability']!r}"
        )
    canonical["expiry_date"] = _parse_expiry_date(canonical["expiry_date"]) or ""
    canonical["diet_health_tags"] = "|".join(_split_multi_value(canonical["diet_health_tags"]))
    canonical["promotional_tag"] = "|".join(_split_multi_value(canonical["promotional_tag"]))
    canonical["delivery_option"] = "|".join(_split_multi_value(canonical["delivery_option"]))
    canonical["recipe_pairing_suggestions"] = "|".join(
        _split_multi_value(canonical["recipe_pairing_suggestions"])
    )
    return canonical


def clean_catalog_rows(raw_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Validate and clean raw catalog rows into ingestion-safe canonical rows."""
    cleaned_rows = [canonicalize_catalog_row(row) for row in raw_rows]
    missing_requirements: list[str] = []
    sku_set: set[str] = set()
    for index, row in enumerate(cleaned_rows, start=1):
        missing_fields = [field for field in _REQUIRED_IMPORT_FIELDS if not row[field]]
        if missing_fields:
            missing_requirements.append(f"Row {index} missing required fields: {missing_fields}")
        sku = row["sku"]
        if sku in sku_set:
            missing_requirements.append(f"Duplicate SKU found in row {index}: {sku!r}")
        sku_set.add(sku)
    if missing_requirements:
        raise ValueError("; ".join(missing_requirements))
    return cleaned_rows


@dataclass
class ProductQuantity:
    """Represents a purchasable quantity/variant of a product."""

    label: str
    unit_price_kes: float
    bulk_price_kes: Optional[float] = None
    min_order_quantity: Optional[str] = None


@dataclass
class Product:
    """Represents a product in the digital catalog."""

    sku: str
    name: str
    category: str
    subcategory: str
    quantities: list[ProductQuantity]
    reorder_level: str = ""
    expiry_date: Optional[str] = None
    product_image: str = ""
    stock_status: str = "In stock"
    supplier_name: str = "Default Supplier"
    stock_quantity: Optional[float] = None
    cost_price_kes: float = 0.0
    short_description: str = ""
    benefits: list[str] = field(default_factory=list)
    usage: str = ""
    diet_tags: list[str] = field(default_factory=list)
    health_tags: list[str] = field(default_factory=list)
    origin: str = "Local"
    processing_type: str = "Raw"
    nutritional_info: str = ""
    rating_reviews: str = ""
    packaging_type: str = "Packaged"
    delivery_options: list[str] = field(default_factory=lambda: ["Same-day", "Next-day"])
    promotional_tags: list[str] = field(default_factory=list)
    recipe_pairing_suggestions: list[str] = field(default_factory=list)
    video_demo_link: str = ""

    def to_canonical_row(self) -> dict[str, str]:
        """Return this product as one canonical catalog import row."""
        unit_variant = self.quantities[0]
        stock_status = self.stock_status.strip().lower()
        if stock_status in {"in stock", "instock"}:
            stock_status = "available"
        bulk_text = (
            f"{unit_variant.min_order_quantity}={unit_variant.bulk_price_kes}"
            if unit_variant.min_order_quantity and unit_variant.bulk_price_kes
            else ""
        )
        return {
            "sku": self.sku,
            "product_name": self.name,
            "category": _normalize_category(self.category),
            "subcategory": self.subcategory,
            "brand_supplier": self.supplier_name,
            "size_quantity": unit_variant.label,
            "unit_price_kes": str(unit_variant.unit_price_kes),
            "bulk_pricing_discounts": bulk_text,
            "stock_availability": stock_status,
            "reorder_level": self.reorder_level,
            "expiry_date": self.expiry_date or "",
            "product_image": self.product_image,
            "short_description": self.short_description,
            "benefits_key_features": "|".join(self.benefits),
            "usage_how_to_use": self.usage,
            "diet_health_tags": "|".join([*self.diet_tags, *self.health_tags]),
            "origin_source": self.origin,
            "processing_type": self.processing_type,
            "nutritional_info": self.nutritional_info,
            "ratings_reviews": self.rating_reviews,
            "promotional_tag": "|".join(self.promotional_tags),
            "packaging_type": self.packaging_type,
            "delivery_option": "|".join(self.delivery_options),
            "recipe_pairing_suggestions": "|".join(self.recipe_pairing_suggestions),
            "video_demo_link": self.video_demo_link or "-",
        }

    def operational_payload(self) -> dict[str, object]:
        """Return operational inventory-focused fields."""
        return {
            "sku": self.sku,
            "supplier_name": self.supplier_name,
            "stock_status": self.stock_status,
            "stock_quantity": self.stock_quantity,
            "reorder_level": self.reorder_level,
            "expiry_date": self.expiry_date,
            "cost_price_kes": self.cost_price_kes,
            "quantities": [asdict(quantity) for quantity in self.quantities],
        }

    def merchandising_payload(self) -> dict[str, object]:
        """Return client-facing display fields."""
        return {
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory,
            "image": self.product_image,
            "short_description": self.short_description,
            "benefits": self.benefits,
            "usage": self.usage,
            "diet_tags": self.diet_tags,
            "health_tags": self.health_tags,
            "processing_type": self.processing_type,
            "nutritional_info": self.nutritional_info,
            "rating_reviews": self.rating_reviews,
            "promotional_tags": self.promotional_tags,
            "packaging_type": self.packaging_type,
            "delivery_options": self.delivery_options,
            "recipe_pairing_suggestions": self.recipe_pairing_suggestions,
            "video_demo_link": self.video_demo_link,
            "quantities": [asdict(quantity) for quantity in self.quantities],
        }


@dataclass
class HomePageConfig:
    """Represents mobile-first homepage content for a shop subdomain."""

    brand_name: str
    tagline: str
    primary_cta: dict[str, str]
    secondary_cta: dict[str, str]
    category_shortcuts: list[dict[str, str]]
    best_seller_filter_route: str
    offers_filter_route: str
    bundles: list[dict[str, object]]
    value_props: list[str]
    order_steps: list[str]
    testimonials: list[str]
    footer: dict[str, str]
    whatsapp_cta_url: str
    mobile_first_rules: dict[str, object]


def build_default_homepage_config(shop_name: str, whatsapp_phone: str) -> HomePageConfig:
    """Build structured, route-linked homepage content for one shop subdomain."""
    encoded_phone = re.sub(r"[^\d]", "", whatsapp_phone)
    return HomePageConfig(
        brand_name=shop_name,
        tagline="Fresh • Affordable • Trusted",
        primary_cta={"label": "Shop Now", "route": "/menu"},
        secondary_cta={"label": "View Offers", "route": "/menu?filter=offers"},
        category_shortcuts=[
            {"label": "Cereals", "icon": "🌾", "route": "/menu?category=cereals"},
            {"label": "Beans", "icon": "🫘", "route": "/menu?category=beans"},
            {"label": "Nuts & Seeds", "icon": "🥜", "route": "/menu?category=nuts-seeds"},
            {"label": "Spices", "icon": "🌶️", "route": "/menu?category=spices"},
            {"label": "Supplements", "icon": "💊", "route": "/menu?category=supplements"},
            {"label": "Natural Products", "icon": "🍯", "route": "/menu?category=natural-products"},
        ],
        best_seller_filter_route="/menu?filter=bestseller",
        offers_filter_route="/menu?filter=offers",
        bundles=[
            {
                "name": "Healthy Starter Pack",
                "items": ["Oats", "Chia Seeds", "Honey"],
                "price_kes": 500,
                "route": "/menu?bundle=healthy-starter-pack",
            },
            {
                "name": "Protein Pack",
                "items": ["Peanut Butter", "Almonds"],
                "price_kes": 800,
                "route": "/menu?bundle=protein-pack",
            },
        ],
        value_props=[
            "Fresh & Quality Products",
            "Affordable Prices",
            "Fast Delivery",
            "Trusted by Customers",
        ],
        order_steps=[
            "Browse products",
            "Select items",
            "Order via WhatsApp",
            "Get delivery",
        ],
        testimonials=["Great quality products!", "Fast delivery and fresh items"],
        footer={
            "delivery_info": "Same-day and next-day delivery options available.",
            "contact_phone": whatsapp_phone,
            "menu_route": "/menu",
        },
        whatsapp_cta_url=(
            f"https://wa.me/{encoded_phone}?text=Hi%20I%20want%20to%20order"
            if encoded_phone
            else ""
        ),
        mobile_first_rules={
            "layout": "single-column",
            "max_width_px": 480,
            "section_padding_px": 16,
            "button_min_height_px": 48,
            "quick_category_jump": True,
            "lightweight_media": True,
        },
    )


@dataclass
class Shop:
    """Represents a shop instance with details used for system provisioning."""

    shop_id: str
    name: str
    owner: str
    address: str
    phone: str
    email: str
    category: str
    description: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True
    tags: list[str] = field(default_factory=list)
    products: list[Product] = field(default_factory=list)
    homepage_config: Optional[HomePageConfig] = None

    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    _PHONE_RE = re.compile(r"^\+?[\d\s\-().]{7,20}$")

    def __post_init__(self) -> None:
        if not self._EMAIL_RE.match(self.email):
            raise ValueError(f"Invalid email address: {self.email!r}")
        if not self._PHONE_RE.match(self.phone):
            raise ValueError(f"Invalid phone number: {self.phone!r}")
        skus = [product.sku for product in self.products]
        if len(skus) != len(set(skus)):
            raise ValueError("Each product SKU must be unique within a shop catalog.")

    def add_product(self, product: Product) -> None:
        """Add a product to the shop catalog."""
        if any(existing.sku == product.sku for existing in self.products):
            raise ValueError(f"Product with SKU {product.sku!r} already exists.")
        self.products.append(product)

    def provision(self) -> dict:
        """Return a dictionary payload suitable for provisioning into another system."""
        return asdict(self)

    def build_provisioning_package(self) -> dict[str, object]:
        """Return canonical catalog rows and homepage/menu payload for ingestion."""
        homepage = self.homepage_config or build_default_homepage_config(self.name, self.phone)
        catalog_rows = clean_catalog_rows([product.to_canonical_row() for product in self.products])
        return {
            "shop": {
                "shop_id": self.shop_id,
                "name": self.name,
                "owner": self.owner,
                "address": self.address,
                "phone": self.phone,
                "email": self.email,
                "category": self.category,
                "description": self.description,
                "website": self.website,
                "is_active": self.is_active,
                "tags": self.tags,
            },
            "catalog_rows": catalog_rows,
            "products_operational": [product.operational_payload() for product in self.products],
            "products_merchandising": [product.merchandising_payload() for product in self.products],
            "homepage_config": asdict(homepage),
            "menu_config": {
                "route": "/menu",
                "description": "Full product catalog",
                "filters": ["category", "diet_health_tags", "unit_price_kes", "bestseller", "offers"],
                "bundle_routes": [bundle["route"] for bundle in homepage.bundles],
            },
        }

    def __repr__(self) -> str:
        return f"Shop(shop_id={self.shop_id!r}, name={self.name!r}, owner={self.owner!r})"


INVENTORY_SEED: list[tuple[str, str, str]] = [
    ("Cereals & Grains", "Cereals", "Maize (whole)"),
    ("Cereals & Grains", "Flour", "Maize flour (unga ya ugali)"),
    ("Cereals & Grains", "Cereals", "Wheat grains"),
    ("Cereals & Grains", "Flour", "Wheat flour (all-purpose)"),
    ("Cereals & Grains", "Rice", "Brown rice"),
    ("Cereals & Grains", "Rice", "White rice"),
    ("Cereals & Grains", "Rice", "Basmati rice"),
    ("Cereals & Grains", "Rice", "Pishori rice"),
    ("Cereals & Grains", "Cereals", "Millet (wimbi)"),
    ("Cereals & Grains", "Cereals", "Sorghum (mtama)"),
    ("Cereals & Grains", "Breakfast", "Oats (rolled oats)"),
    ("Cereals & Grains", "Breakfast", "Instant oats"),
    ("Cereals & Grains", "Cereals", "Barley"),
    ("Cereals & Grains", "Cereals", "Quinoa"),
    ("Cereals & Grains", "Cereals", "Amaranth (terere seeds)"),
    ("Cereals & Grains", "Flour", "Semolina"),
    ("Cereals & Grains", "Breakfast", "Cornflakes"),
    ("Cereals & Grains", "Breakfast", "Breakfast muesli"),
    ("Cereals & Grains", "Breakfast", "Granola mix"),
    ("Cereals & Grains", "Flour", "Porridge flour mix"),
    ("Pulses & Legumes", "Beans", "Yellow beans"),
    ("Pulses & Legumes", "Beans", "Red beans"),
    ("Pulses & Legumes", "Beans", "Kidney beans"),
    ("Pulses & Legumes", "Beans", "Rose coco beans"),
    ("Pulses & Legumes", "Legumes", "Green grams (ndengu)"),
    ("Pulses & Legumes", "Legumes", "Chickpeas"),
    ("Pulses & Legumes", "Legumes", "Lentils (red)"),
    ("Pulses & Legumes", "Legumes", "Lentils (green)"),
    ("Pulses & Legumes", "Beans", "Black beans"),
    ("Pulses & Legumes", "Legumes", "Cowpeas"),
    ("Pulses & Legumes", "Legumes", "Pigeon peas (mbaazi)"),
    ("Pulses & Legumes", "Legumes", "Soya beans"),
    ("Pulses & Legumes", "Legumes", "Split peas"),
    ("Nuts & Nut Products", "Nuts", "Groundnuts (raw)"),
    ("Nuts & Nut Products", "Nuts", "Groundnuts (roasted)"),
    ("Nuts & Nut Products", "Nuts", "Cashew nuts"),
    ("Nuts & Nut Products", "Nuts", "Almonds"),
    ("Nuts & Nut Products", "Nuts", "Walnuts"),
    ("Nuts & Nut Products", "Nuts", "Macadamia nuts"),
    ("Nuts & Nut Products", "Nuts", "Hazelnuts"),
    ("Nuts & Nut Products", "Nuts", "Pistachios"),
    ("Nuts & Nut Products", "Nut Butters", "Peanut butter (smooth)"),
    ("Nuts & Nut Products", "Nut Butters", "Peanut butter (crunchy)"),
    ("Nuts & Nut Products", "Nut Butters", "Almond butter"),
    ("Nuts & Nut Products", "Nuts", "Mixed nuts pack"),
    ("Seeds", "Seeds", "Chia seeds"),
    ("Seeds", "Seeds", "Flax seeds"),
    ("Seeds", "Seeds", "Pumpkin seeds"),
    ("Seeds", "Seeds", "Sunflower seeds"),
    ("Seeds", "Seeds", "Sesame seeds (white)"),
    ("Seeds", "Seeds", "Sesame seeds (black)"),
    ("Seeds", "Seeds", "Hemp seeds"),
    ("Seeds", "Seeds", "Poppy seeds"),
    ("Seeds", "Seeds", "Basil seeds (sabja)"),
    ("Seeds", "Seeds", "Mixed seed blend"),
    ("Spices & Seasonings", "Spices", "Black pepper"),
    ("Spices & Seasonings", "Spices", "White pepper"),
    ("Spices & Seasonings", "Spices", "Turmeric powder"),
    ("Spices & Seasonings", "Spices", "Curry powder"),
    ("Spices & Seasonings", "Spices", "Paprika"),
    ("Spices & Seasonings", "Spices", "Chili powder"),
    ("Spices & Seasonings", "Spices", "Cayenne pepper"),
    ("Spices & Seasonings", "Spices", "Cinnamon sticks"),
    ("Spices & Seasonings", "Spices", "Cinnamon powder"),
    ("Spices & Seasonings", "Spices", "Cloves"),
    ("Spices & Seasonings", "Spices", "Cardamom pods"),
    ("Spices & Seasonings", "Spices", "Cumin seeds"),
    ("Spices & Seasonings", "Spices", "Coriander seeds"),
    ("Spices & Seasonings", "Spices", "Garam masala"),
    ("Spices & Seasonings", "Spices", "Mixed herbs"),
    ("Spices & Seasonings", "Spices", "Bay leaves"),
    ("Spices & Seasonings", "Spices", "Ginger powder"),
    ("Spices & Seasonings", "Spices", "Garlic powder"),
    ("Spices & Seasonings", "Spices", "Onion powder"),
    ("Spices & Seasonings", "Seasonings", "Salt (table)"),
    ("Spices & Seasonings", "Seasonings", "Sea salt"),
    ("Spices & Seasonings", "Seasonings", "Himalayan pink salt"),
    ("Natural Sweeteners & Additives", "Sweeteners", "Honey (raw)"),
    ("Natural Sweeteners & Additives", "Sweeteners", "Honey (processed)"),
    ("Natural Sweeteners & Additives", "Sweeteners", "Molasses"),
    ("Natural Sweeteners & Additives", "Sweeteners", "Jaggery"),
    ("Natural Sweeteners & Additives", "Sweeteners", "Brown sugar"),
    ("Natural Sweeteners & Additives", "Sweeteners", "White sugar"),
    ("Natural Sweeteners & Additives", "Sweeteners", "Icing sugar"),
    ("Natural Sweeteners & Additives", "Sweeteners", "Maple syrup (imported niche)"),
    ("Natural Sweeteners & Additives", "Sweeteners", "Date syrup"),
    ("Health Supplements", "Supplements", "Multivitamins"),
    ("Health Supplements", "Supplements", "Vitamin C tablets"),
    ("Health Supplements", "Supplements", "Vitamin D supplements"),
    ("Health Supplements", "Supplements", "Calcium supplements"),
    ("Health Supplements", "Supplements", "Iron supplements"),
    ("Health Supplements", "Supplements", "Zinc supplements"),
    ("Health Supplements", "Supplements", "Magnesium tablets"),
    ("Health Supplements", "Supplements", "Omega-3 capsules"),
    ("Health Supplements", "Supplements", "Probiotics"),
    ("Health Supplements", "Supplements", "Protein powder (whey)"),
    ("Health Supplements", "Supplements", "Protein powder (plant-based)"),
    ("Health Supplements", "Supplements", "Collagen powder"),
    ("Health Supplements", "Supplements", "Creatine"),
    ("Health Supplements", "Supplements", "Energy boosters (herbal)"),
    ("Health Supplements", "Supplements", "Immune boosters"),
    ("Health Supplements", "Supplements", "Herbal capsules"),
    ("Herbal Teas & Drinks", "Teas", "Green tea"),
    ("Herbal Teas & Drinks", "Teas", "Black tea"),
    ("Herbal Teas & Drinks", "Teas", "Chamomile tea"),
    ("Herbal Teas & Drinks", "Teas", "Hibiscus tea"),
    ("Herbal Teas & Drinks", "Teas", "Ginger tea"),
    ("Herbal Teas & Drinks", "Teas", "Lemon tea"),
    ("Herbal Teas & Drinks", "Teas", "Detox tea blends"),
    ("Herbal Teas & Drinks", "Drinks", "Matcha powder"),
    ("Dried Fruits", "Dried Fruits", "Raisins"),
    ("Dried Fruits", "Dried Fruits", "Sultanas"),
    ("Dried Fruits", "Dried Fruits", "Dates"),
    ("Dried Fruits", "Dried Fruits", "Dried apricots"),
    ("Dried Fruits", "Dried Fruits", "Dried mango"),
    ("Dried Fruits", "Dried Fruits", "Dried pineapple"),
    ("Dried Fruits", "Dried Fruits", "Dried bananas"),
    ("Dried Fruits", "Dried Fruits", "Prunes"),
    ("Dried Fruits", "Dried Fruits", "Cranberries"),
    ("Cooking Essentials", "Cooking Oils", "Cooking oil (sunflower)"),
    ("Cooking Essentials", "Cooking Oils", "Cooking oil (vegetable)"),
    ("Cooking Essentials", "Cooking Oils", "Olive oil"),
    ("Cooking Essentials", "Cooking Oils", "Coconut oil"),
    ("Cooking Essentials", "Condiments", "Vinegar (white)"),
    ("Cooking Essentials", "Condiments", "Apple cider vinegar"),
    ("Cooking Essentials", "Condiments", "Soy sauce"),
    ("Cooking Essentials", "Baking", "Baking powder"),
    ("Cooking Essentials", "Baking", "Baking soda"),
    ("Cooking Essentials", "Baking", "Yeast"),
    ("Ready-to-Eat / Convenience", "Convenience", "Instant noodles"),
    ("Ready-to-Eat / Convenience", "Convenience", "Ready porridge mix"),
    ("Ready-to-Eat / Convenience", "Convenience", "Energy bars"),
    ("Ready-to-Eat / Convenience", "Convenience", "Protein bars"),
    ("Ready-to-Eat / Convenience", "Convenience", "Breakfast biscuits"),
    ("Ready-to-Eat / Convenience", "Convenience", "Instant soup mix"),
    ("Optional Expansion", "Wellness", "Body wellness teas"),
    ("Optional Expansion", "Wellness", "Detox powders"),
    ("Optional Expansion", "Wellness", "Herbal oils"),
    ("Optional Expansion", "Wellness", "Essential oils"),
    ("Optional Expansion", "Wellness", "Natural skincare powders (like turmeric masks)"),
]


def _default_quantities(category: str) -> list[ProductQuantity]:
    if category == "Health Supplements":
        return [
            ProductQuantity(label="30 caps", unit_price_kes=850.0, min_order_quantity="1 pack"),
            ProductQuantity(label="60 caps", unit_price_kes=1500.0, bulk_price_kes=1400.0),
        ]
    if category == "Herbal Teas & Drinks":
        return [
            ProductQuantity(label="25 bags", unit_price_kes=320.0),
            ProductQuantity(label="50 bags", unit_price_kes=580.0, bulk_price_kes=540.0),
        ]
    if category == "Cooking Essentials":
        return [
            ProductQuantity(label="500ml", unit_price_kes=240.0),
            ProductQuantity(label="1L", unit_price_kes=430.0, bulk_price_kes=400.0),
        ]
    return [
        ProductQuantity(label="250g", unit_price_kes=120.0, min_order_quantity="250g"),
        ProductQuantity(label="500g", unit_price_kes=220.0),
        ProductQuantity(label="1kg", unit_price_kes=420.0, bulk_price_kes=390.0),
    ]


def build_default_inventory() -> list[Product]:
    """Build a broad supermarket-style inventory list for catalog seeding."""
    products: list[Product] = []
    for index, (category, subcategory, name) in enumerate(INVENTORY_SEED, start=1):
        sku = f"PRD{index:03d}"
        products.append(
            Product(
                sku=sku,
                name=name,
                category=category,
                subcategory=subcategory,
                quantities=_default_quantities(category),
                cost_price_kes=80.0,
                short_description=f"{name} - quality product for daily use.",
                benefits=["Quality sourced", "Fresh stock"],
                usage="Refer to packaging for recommended use.",
                diet_tags=["Vegan"] if category != "Health Supplements" else [],
                health_tags=["High-fiber"] if category in {"Cereals & Grains", "Seeds"} else [],
                origin="Local" if category != "Health Supplements" else "Imported",
                processing_type="Raw" if category not in {"Spices & Seasonings", "Health Supplements"} else "Processed",
                packaging_type="Airtight bag",
                promotional_tags=["Best Seller"] if index <= 10 else [],
            )
        )
    return products
