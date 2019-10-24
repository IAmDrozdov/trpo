from rest_framework import status

from .test_utils import APITestCase
from . import factories

class TripTestCase(APITestCase):
    LOCATION_URL = '/api/trips/{}/location'

    def _get_url(self, road):
        return self.trip.format(road)

    def _create_test_trip(self):
        self.create_temp_user()
        location_first = factories.LocationFactory(location=self.test_location)
        location_second = factories.LocationFactory(location=self.test_location)
        self.first_test_trip = factories.TripFactory(
            land_location=self.loc_first,
            owner=self.temp_user,
        )
        self.secondtest_trip = factories.TripFactory(
            land_location=self.loc_second,
            owner=self.temp_user
        )

    def setUp(self):
        super().setUp()
        self._create_test_trips()

    def test_retrieve_location(self):
        response = self.client.get(self._get_url(self.first_test_trip.id))
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['location'], self.location.id)

    def test_update_location(self):
        location_dict = factories.LocationDictFactory()
        location_dict['data'] = factories.LocationDictFactory()
        location_dict['data']['location'] = self.test_location.id
        response = self.client.put(
            self._get_url(self.first_test_trip.id),
            data=location__dict,
            format='json',
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        response_dict = response.data['data']
        self.assertDictsEqual(response_dict['data'], location_dict['data'])

    def test_update_location_negative(self):
        non_existing_location_id = Locations.objects.last().id + 1
        location_dict = factories.LocationDictFactory()
        location_dict['data'] = factories.LocationDictFactory()
        location_dict['data']['location'] = non_existing_location_id
        response = self.client.put(
            self._get_url(self.first_test_trip.id),
            data=location_dict,
            format='json',
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('location' in response.data['errors']['data'])

    def test_create_location(self):
        location_dict = factories.LocationDictFactory()
        location_dict['data'] = factories.LocationDictFactory()
        location_dict['data']['location'] = self.test_location.id
        response = self.client.post(
            self._get_url(self.first_test_trip.id),
            data=location_dict,
            format='json',
        )
        self.assertStatusCode(response, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_location(self):
        response = self.client.delete(self._get_url(self.first_test_trip.id))
        self.assertStatusCode(response, status.HTTP_405_METHOD_NOT_ALLOWED)
