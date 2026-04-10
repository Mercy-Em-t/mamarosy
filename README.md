# mamarosy
Shop provision

A shop provisioning module that defines a `Shop` class used to model and provision shop details into a system.

## Usage

```python
from shop import Shop

shop = Shop(
    shop_id="shop-001",
    name="Mamarosy Boutique",
    owner="Jane Doe",
    address="123 Market Street, Antananarivo",
    phone="+261 20 123 4567",
    email="contact@mamarosy.mg",
    category="Clothing",
    description="A boutique specialising in traditional Malagasy clothing.",
    website="https://mamarosy.mg",
    tags=["clothing", "boutique", "malagasy"],
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
| `tags`        | `list`          | No       | List of tags for categorisation          |
