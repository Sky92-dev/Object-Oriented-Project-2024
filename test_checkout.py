import unittest

from starlette.testclient import TestClient

import main


class CheckoutRoutingTests(unittest.TestCase):
    def setUp(self):
        self.previous_user = main.session.get_current_user()
        self.member = main.Member('Test', 'Customer', '000', 'test@example.com', 'test', 'test')
        self.member.add_basket(main.Basket())
        self.member.get_current_basket().add_basket_item(main.system.get_menu_list()[0], 1)
        main.session.login(self.member)
        self.client = TestClient(main.app)

    def tearDown(self):
        main.session.login(self.previous_user)
        self.client.close()

    def test_selected_fulfillment_survives_revisit_and_payment(self):
        for method in ('pickup', 'delivery'):
            for payment in ('/QR', '/account_num'):
                with self.subTest(method=method, payment=payment):
                    self.client.get('/' + method)
                    if method == 'pickup':
                        branch = main.system.find_branch_from_post('10200')[0]
                        response = self.client.post('/select_branch', data={
                            'district': branch['district'], 'address': branch['address']})
                    else:
                        response = self.client.post('/submit_address', data={'address': '123 Bangkok 10200'})
                    self.assertEqual(response.status_code, 200)
                    selection = self.member.get_order_type()
                    self.client.get('/' + method)
                    self.assertIs(self.member.get_order_type(), selection)
                    self.assertIsNotNone(selection.get_branch())
                    self.assertEqual(self.client.get('/payment').url.path, '/payment')
                    page = self.client.get(payment)
                    self.assertEqual(page.url.path, payment)
                    self.assertIn(f'action="/total/order/{self.member.get_id}"', page.text)
                    response = self.client.post(f'/total/order/{self.member.get_id}')
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.url.path, '/summary')

    def test_incomplete_selection_redirects_before_payment(self):
        for method in ('pickup', 'delivery'):
            self.member.add_order_type(None)
            self.client.get('/' + method)
            for path in ('/payment', '/QR', '/account_num', '/summary'):
                response = self.client.get(path, follow_redirects=False)
                self.assertEqual(response.headers['location'], '/' + method)

    def test_invalid_address_does_not_replace_valid_selection(self):
        self.client.post('/submit_address', data={'address': '123 Bangkok 10200'})
        selection = self.member.get_order_type()
        response = self.client.post('/submit_address', data={'address': 'unknown'})
        self.assertEqual(response.url.path, '/submit_address')
        self.assertIs(self.member.get_order_type(), selection)

    def test_postcode_search_supports_both_stored_types(self):
        for postcode in ('10200', '10150'):
            self.assertTrue(main.system.find_branch_from_post(postcode))


if __name__ == '__main__':
    unittest.main()
