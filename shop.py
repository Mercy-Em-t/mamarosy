"""Shop and product catalog models for provisioning data into another system."""

import re
from dataclasses import asdict, dataclass, field
from typing import Optional


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
    stock_status: str = "In stock"
    supplier_name: str = "Default Supplier"
    cost_price_kes: float = 0.0
    short_description: str = ""
    benefits: list[str] = field(default_factory=list)
    usage: str = ""
    diet_tags: list[str] = field(default_factory=list)
    health_tags: list[str] = field(default_factory=list)
    origin: str = "Local"
    processing_type: str = "Raw"
    packaging_type: str = "Packaged"
    delivery_options: list[str] = field(default_factory=lambda: ["Same-day", "Next-day"])
    promotional_tags: list[str] = field(default_factory=list)


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
