import unittest

from shop import Shop, build_default_inventory, clean_catalog_rows


class ShopCatalogProvisioningTests(unittest.TestCase):
    def test_default_inventory_contains_expected_catalog_size(self) -> None:
        products = build_default_inventory()
        self.assertGreaterEqual(len(products), 140)
        self.assertEqual(len({product.sku for product in products}), len(products))

    def test_shop_provision_includes_product_quantities(self) -> None:
        products = build_default_inventory()
        shop = Shop(
            shop_id="shop-001",
            name="Mamarosy Market",
            owner="Mercy",
            address="Antananarivo",
            phone="+261 20 123 4567",
            email="owner@mamarosy.mg",
            category="Cereals + Supplements + Spices",
            products=products[:3],
        )

        payload = shop.provision()
        self.assertIn("products", payload)
        self.assertEqual(len(payload["products"]), 3)
        self.assertIn("quantities", payload["products"][0])
        self.assertGreater(len(payload["products"][0]["quantities"]), 0)

    def test_clean_catalog_rows_normalizes_headers_and_values(self) -> None:
        raw_rows = [
            {
                "SKU / Product Code": "CRS001",
                "Product Name": "Pishori Rice",
                "Category": "Cereals",
                "Subcategory": "Rice",
                "Brand/ Supplier": "East Africa Mills",
                "Size/ Quantity": "1kg",
                "Unit Price (KES)": "150",
                "Bulk Pricing / Discounts": "5kg = 700",
                "Stock Availability": "Available",
                "Reorder Level": "10kg",
                "Expiry Date": "31/12/2026",
                "Product Image": "rice1.jpg",
                "Short Description": "Aromatic long-grain rice",
                "Benefits / Key Features": "Non-sticky, high fiber",
                "Usage / How to Use": "Boil or steam for pilau",
                "Diet / Health Tags": "Vegan, Gluten-free",
                "Origin / Source": "Pakistan",
                "Processing Type": "Whole grain",
                "Nutritional Info": "360kcal/100g",
                "Ratings / Reviews": "⭐⭐⭐⭐☆",
                "Promotional Tag": "Best Seller",
                "Packaging Type": "Airtight bag",
                "Delivery Option": "Same-day",
                "Recipe / Pairing Suggestions": "Lentils, spices",
                "Video / Demo Link": "-",
            }
        ]
        cleaned = clean_catalog_rows(raw_rows)
        self.assertEqual(cleaned[0]["category"], "Cereals & Grains")
        self.assertEqual(cleaned[0]["unit_price_kes"], "150.0")
        self.assertEqual(cleaned[0]["expiry_date"], "2026-12-31")
        self.assertEqual(cleaned[0]["diet_health_tags"], "Vegan|Gluten-free")
        self.assertEqual(cleaned[0]["recipe_pairing_suggestions"], "Lentils|spices")

    def test_build_provisioning_package_contains_catalog_and_homepage(self) -> None:
        shop = Shop(
            shop_id="shop-001",
            name="Mamarosy Market",
            owner="Mercy",
            address="Antananarivo",
            phone="+261 20 123 4567",
            email="owner@mamarosy.mg",
            category="Cereals + Supplements + Spices",
            products=build_default_inventory()[:2],
        )
        package = shop.build_provisioning_package()
        self.assertIn("catalog_rows", package)
        self.assertEqual(len(package["catalog_rows"]), 2)
        self.assertIn("homepage_config", package)
        self.assertEqual(package["homepage_config"]["primary_cta"]["route"], "/menu")
        self.assertIn("menu_config", package)
        self.assertIn("products_operational", package)
        self.assertIn("products_merchandising", package)


if __name__ == "__main__":
    unittest.main()
