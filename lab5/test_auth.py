from .test_utils import M2APITestCase
from .factories import BaseUserFactory

class BaseUserTestCase(APITestCase):

    REGISTER_USER_URL = '/api/users/register'
    LOGIN_USER_URL = '/api/users/login'
    ME_USER_URL = '/api/users/me'
    VERIFY_CLIENT_PHONE_URL = '/api/users/{}/verify-phone-number'
    LOGOUT_USER_URL = '/api/users/logout'
    CLIENT_PHONE = '96601300966'

    def setUp(self):
        super().setUp()

        self.user_data = factories.BaseUserDictFactory()
        self.another_user_data = factories.BaseUserDictFactory()
        self.dispatcher_data = factories.BaseUserDictFactory()
        self.login_email_credentials = {
            'username': self.user_data['email'],
        }
        self.dispatcher_credentials = {
            'username': self.dispatcher_data['email'],
        }
    def _register_client(self, data):
        register_response = self.client.post(self.REGISTER_USER_URL, data=data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.client.credentials(**self.get_auth_token_from_response(register_response))
        return register_response

    @staticmethod
    def get_auth_token_from_response(response):
        return dict(HTTP_AUTHORIZATION='Token {}'.format(response.data['data']['token']))

    @staticmethod
    def get_user_by_token(response):
        try:
            return Token.objects.get(key=response.data['data']['token']).user
        except Token.DoesNotExists:
            return None


class TestClients(BaseUserTestCase):
    CLIENTS_URL = '/api/clients'

    def test_list_clients(self):
        response = self._register_client(self.user_data)
        first_client_id = response.data['data']['id']

        first_dispatcher, second_dispatcher = self._create_dispatchers()
        self.login_dispatcher(first_dispatcher)
        response = self.client.get(self.CLIENTS_URL)
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(first_client_id, response.data['data'][0]['id'])

    def test_password_reset(self):
        response = self.client.post(self.REGISTER_CLIENT_URL, data=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = self.get_user_by_token(response)
        self.assertTrue(user and not user.is_temporary)
        self.assertTrue(user.check_password(self.user_data['password']))

        response_reset = self.client.post(self.RESET_PASSWORD_URL, data={
            'phone': user.phone
        })
        user = self.get_user_by_token(response)
        self.assertTrue(response_reset.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password(self.CLIENT_PASSWORD))


class TestRegister(BaseUserTestCase):

    def test_dispatcher_register(self):
        response = self.client.post(
            self.REGISTER_DISPATCHER_URL,
            data=self.dispatcher_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_client_skip_register(self):
        response = self.client.post(self.REGISTER_CLIENT_URL, data=self.skip_registration)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        temp_user = self.get_user_by_token(response)
        self.assertTrue(temp_user and temp_user.is_temporary)

    def test_client_register(self):
        response = self.client.post(self.REGISTER_CLIENT_URL, data=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = self.get_user_by_token(response)
        self.assertTrue(user and not user.is_temporary)
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_client_register_after_skip(self):
        skip_response = self.client.post(self.REGISTER_CLIENT_URL, data=self.skip_registration)
        self.client.credentials(**self.get_auth_token_from_response(skip_response))
        self.assertEqual(skip_response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.REGISTER_CLIENT_URL, data=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = self.get_user_by_token(response)
        self.assertTrue(user and not user.is_temporary)
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_client_register_with_no_full_data(self):
        response = self.client.post(self.REGISTER_CLIENT_URL, data=self.login_email_credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_register_with_existing_phone(self):
        response_register = self.client.post(self.REGISTER_CLIENT_URL, data=self.user_data)
        self.assertEqual(response_register.status_code, status.HTTP_201_CREATED)
        response_verify = self.client.put(self.VERIFY_CLIENT_PHONE_URL.format(response_register.data['data']['id']), {
            'idtoken': self.TEST_ID_TOKEN
        })
        self.assertEqual(response_verify.status_code, status.HTTP_200_OK)
        response_register_again = self.client.post(
            self.REGISTER_CLIENT_URL,
            data={**self.another_user_data, 'phone': self.user_data['phone']}
        )
        self.assertEqual(response_register_again.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('phone' in response_register_again.data['errors'])

    def test_client_registered_register_again(self):
        self._register_client(self.user_data)
        register_response = self.client.post(self.REGISTER_CLIENT_URL, data=self.another_user_data)
        self.assertEqual(register_response.status_code, status.HTTP_403_FORBIDDEN)



class TestMe(BaseUserTestCase):

    def _client_values_to_update(self):
        return {
            'name': 'Jane',
        }
    def test_client_get_me_unauthorized(self):
        self.client.credentials()
        response = self.client.get(self.ME_CLIENT_URL)
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    def test_client_update_me_after_register(self):
        self._register_client(self.user_data)

        to_update = self._client_values_to_update()
        response = self.client.patch(self.ME_CLIENT_URL, data=to_update)
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertDictsEqual(to_update, response.data['data'])

    def test_client_update_me_unauthorized(self):
        self.client.credentials()

        to_update = self._client_values_to_update()
        response = self.client.put(self.ME_CLIENT_URL, data=to_update)
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    def test_client_update_me_temporary(self):
        skip_response = self.client.post(self.REGISTER_CLIENT_URL, data=self.skip_registration)
        self.assertEqual(skip_response.status_code, status.HTTP_201_CREATED)
        self.client.credentials(**self.get_auth_token_from_response(skip_response))

        to_update = self._client_values_to_update()
        response = self.client.put(self.ME_CLIENT_URL, data=to_update)
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    def test_client_update_me_partial(self):
        self._register_client(self.user_data)

        to_update = {'name': 'Aska Langley 02'}
        response = self.client.patch(self.ME_CLIENT_URL, data=to_update)
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertTrue(to_update['name'], response.data['data']['name'])

    def test_update_same_fcm_token(self):
        response_first = self._register_client(self.user_data)
        self.client.logout()
        self._register_client(self.another_user_data)

        to_update = {'fcm_token': self.user_data['fcm_token']}
        response_update = self.client.patch(self.ME_CLIENT_URL, data=to_update)

        self.assertStatusCode(response_update, status.HTTP_200_OK)
        self.assertTrue(to_update['fcm_token'], response_update.data['data']['fcm_token'])

        self.assertIsNone(get_user_model().objects.get(pk=response_first.data['data']['id']).fcm_token)

    def test_dispatcher_get_me(self):
        first_dispatcher, second_dispatcher = self._create_dispatchers()
        self.login_dispatcher(first_dispatcher)
        response = self.client.get(self.dispatcherS_ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], first_dispatcher.email)
        self.logout_user()

        self.login_dispatcher(second_dispatcher)
        response = self.client.get(self.dispatcherS_ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], second_dispatcher.email)

    def test_dispatcher_get_me_unauthorized(self):
        response = self.client.get(self.dispatcherS_ME_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dispatcher_update_me(self):
        first_dispatcher, _ = self._create_dispatchers()
        self.login_dispatcher(first_dispatcher)
        response = self.client.put(self.dispatcherS_ME_URL, data=self.dispatcher_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dispatcher_data.pop('password')
        self.assertDictsEqual(self.dispatcher_data, response.data['data'])

    def test_update_me_dispatcher_unauthorized(self):
        response = self.client.get(self.dispatcherS_ME_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_me_dispatcher_partial(self):
        first_dispatcher, second_dispatcher = self._create_dispatchers()
        new_name = 'Ayanamy'
        self.login_dispatcher(first_dispatcher)
        response = self.client.patch(self.DISPATCHERS_ME_URL, data={'name': new_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], new_name)
