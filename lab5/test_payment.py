from rest_framework import status
from .test_utils import APITestCase


class PaymentTestCase(APITestCase):
  def pay_inspection(self, road_id, trip_id, payment_id):
        url_template = '/api/roads/{}//trips/{}/payment?id={}'

        url = url_template.format(project_id, step_id, payment_id)
        response = self.get(url)
        return response.data['data'], response.status_code

    def test__payment(self, mock_func):
        TEST_PAYMENT_DATE = '2019-10-20T20:56:35.450686Z'
        TEST_PAYMENT_ID = '123213213'

        mock_func.return_value = Mock(created_at=TEST_PAYMENT_DATE, payment_id=TEST_PAYMENT_ID)

        trip_id, trip_status = self.client.create_trip()
        self.assertEquals(project_status, status.HTTP_201_CREATED)
        payment_data, payment_status = self.client.pay_inspection(
            trip_id,
            TEST_PAYMENT_ID
        )

        self.assertEqual(payment_status, status.HTTP_200_OK)
        self.assertEqual(payment_data['status'], TripStatus.PAID.value)
