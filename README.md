# mamarosy
Shop provision

A shop provisioning module that defines:
- `Shop` for shop-level details
- `Product` and `ProductQuantity` for a digital catalog that clients can browse and purchase
- `build_default_inventory()` to seed a 100+ item supermarket-style catalog

## Usage

```python
from shop import Shop, build_default_inventory

shop = Shop(
    shop_id="shop-001",
    name="Mamarosy Health Market",
    owner="Jane Doe",
    address="123 Market Street, Antananarivo",
    phone="+261 20 123 4567",
    email="contact@mamarosy.mg",
    category="Cereals + Supplements + Spices",
    description="A retail shop specializing in grains, spices, and wellness products.",
    website="https://mamarosy.mg",
    tags=["cereals", "supplements", "spices"],
    products=build_default_inventory(),
)

# Provision shop details into the system
details = shop.provision()
```

## Shop Fields

| Field         | Type            | Required | Description                              |
|---------------|-----------------|----------|------------------------------------------|
| `shop_id`     | `str`           | Yes      | Unique identifier for the shop           |
| `name`        | `str`           | Yes      | Shop name                                |
| `owner`       | `str`           | Yes      | Name of the shop owner                   |
| `address`     | `str`           | Yes      | Physical address of the shop             |
| `phone`       | `str`           | Yes      | Contact phone number                     |
| `email`       | `str`           | Yes      | Contact email address                    |
| `category`    | `str`           | Yes      | Business category                        |
| `description` | `str` or `None` | No       | Optional description of the shop         |
| `website`     | `str` or `None` | No       | Optional shop website URL                |
| `is_active`   | `bool`          | No       | Whether the shop is active (default True)|
| `tags`        | `list`          | No       | List of tags for categorization          |
| `products`    | `list[Product]` | No       | Catalog products to provision            |

## Product Catalog Fields

Each catalog product supports selling and management attributes including:

- `sku`
- `name`
- `category`
- `subcategory`
- `quantities` (e.g. 250g, 500g, 1kg with pricing)
- `stock_status`
- `supplier_name`
- `cost_price_kes`
- `short_description`
- `benefits`
- `usage`
- `diet_tags`
- `health_tags`
- `origin`
- `processing_type`
- `packaging_type`
- `delivery_options`
- `promotional_tags`
