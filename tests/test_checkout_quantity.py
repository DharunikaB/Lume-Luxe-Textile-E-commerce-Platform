import unittest
from unittest.mock import patch

from flask_jwt_extended import create_access_token
import app as checkout_app


class CheckoutQuantityTests(unittest.TestCase):

    def setUp(self):
        self.app = checkout_app.app
        self.client = self.app.test_client()

        with self.app.app_context():
            token = create_access_token(identity="test@example.com")

        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    @patch("payments.razorpay.Client")
    @patch("payments.db.session.commit")
    @patch("payments.db.session.add")
    @patch("payments.Order")
    @patch("payments.Product")
    @patch("payments.User")
    def test_invalid_quantities_have_no_side_effects(
        self,
        mock_user,
        mock_product,
        mock_order,
        mock_add,
        mock_commit,
        mock_razorpay,
    ):
        invalid_quantities = [
            0,
            -1,
            "abc",
            "",
            None,
            1.5,
            True,
            "2.5",
        ]

        for quantity in invalid_quantities:
            with self.subTest(quantity=quantity):
                response = self.client.post(
                    "/api/payments/create_order",
                    json={
                        "product_id": 1,
                        "quantity": quantity,
                    },
                    headers=self.headers,
                )

                self.assertEqual(
                    response.status_code,
                    400,
                    f"Unexpected response for quantity={quantity!r}: "
                    f"{response.get_data(as_text=True)}",
                )

                self.assertIn("error", response.get_json())

        # Invalid quantities must be rejected before database/payment work.
        mock_user.query.filter_by.assert_not_called()
        mock_product.query.get.assert_not_called()
        mock_order.assert_not_called()
        mock_add.assert_not_called()
        mock_commit.assert_not_called()
        mock_razorpay.assert_not_called()

    @patch("payments.razorpay.Client")
    @patch("payments.db.session.commit")
    @patch("payments.db.session.add")
    @patch("payments.Order")
    @patch("payments.Product")
    @patch("payments.User")
    def test_missing_quantity_defaults_to_one(
        self,
        mock_user,
        mock_product,
        mock_order,
        mock_add,
        mock_commit,
        mock_razorpay,
    ):
        user = mock_user.query.filter_by.return_value.first.return_value
        user.id = 7

        product = mock_product.query.get.return_value
        product.id = 1
        product.price = 100

        mock_razorpay.return_value.order.create.return_value = {
            "id": "order_test_123"
        }

        self.app.config["RAZORPAY_KEY"] = "test_key"
        self.app.config["RAZORPAY_SECRET"] = "test_secret"

        response = self.client.post(
            "/api/payments/create_order",
            json={"product_id": 1},
            headers=self.headers,
        )

        self.assertEqual(
            response.status_code,
            200,
            response.get_data(as_text=True),
        )

        # Verify the application defaults the omitted quantity to 1.
        self.assertEqual(mock_order.call_args.kwargs["quantity"], 1)

        mock_razorpay.return_value.order.create.assert_called_once()
        mock_add.assert_called_once()
        mock_commit.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
