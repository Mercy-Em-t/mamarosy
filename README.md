# mamarosy
Shop provision

A shop provisioning module that defines:
- `Shop` for shop-level details
- `Product` and `ProductQuantity` for a digital catalog that clients can browse and purchase
- `build_default_inventory()` to seed a 100+ item supermarket-style catalog
- `clean_catalog_rows()` to normalize external CSV rows into a canonical import format
- `build_default_homepage_config()` to generate mobile-first homepage/menu content for each shop subdomain

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

# Provision package for ingestion (clean catalog rows + homepage/menu config)
package = shop.build_provisioning_package()
```

## Canonical Catalog Import Format

`clean_catalog_rows()` maps incoming headers and values into strict canonical fields:

- `sku`
- `product_name`
- `category`
- `subcategory`
- `brand_supplier`
- `size_quantity`
- `unit_price_kes`
- `bulk_pricing_discounts`
- `stock_availability`
- `reorder_level`
- `expiry_date` (normalized to `YYYY-MM-DD`)
- `product_image`
- `short_description`
- `benefits_key_features`
- `usage_how_to_use`
- `diet_health_tags` (`|`-separated)
- `origin_source`
- `processing_type`
- `nutritional_info`
- `ratings_reviews`
- `promotional_tag` (`|`-separated)
- `packaging_type`
- `delivery_option` (`|`-separated)
- `recipe_pairing_suggestions` (`|`-separated)
- `video_demo_link`

Validation covers required fields, SKU uniqueness, valid stock states, numeric prices, and valid expiry dates.

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
- `reorder_level`
- `expiry_date`
- `product_image`
- `nutritional_info`
- `rating_reviews`
- `packaging_type`
- `delivery_options`
- `promotional_tags`
- `recipe_pairing_suggestions`
- `video_demo_link`

## Homepage / Menu Configuration

Each shop can include structured, mobile-first homepage data via `homepage_config`:

- Hero content and CTAs (`/menu`, offers route)
- Category shortcuts routed to filter-ready menu URLs
- Best-seller and offers blocks
- Bundle cards with target routes
- Ordering steps, testimonials, footer contact, and sticky WhatsApp CTA

`Shop.build_provisioning_package()` returns:

1. `catalog_rows` (cleaned canonical rows for ingestion)
2. `homepage_config` and `menu_config` (display/navigation payloads)
3. `products_operational` and `products_merchandising` (separated field sets)
