import unittest

from shop import Shop, build_default_inventory


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


if __name__ == "__main__":
    unittest.main()
