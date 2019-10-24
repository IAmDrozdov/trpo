from rest_framework.test import APITestCase

from . import factories

class APITestCase(APITestCase):
    def create_temp_user(self):
        self.temp_user = factories.UserFactory.create(is_temporary=True)
        self.temp_user.save()
        self.client.credentials(**self.temp_user_token_info)

    def create_superuser(self):
        self.super_user = factories.DispatcherFactory()

    def login_dispatcher(self, user):
        code = 'test_code'
        return self.client.post('/api/dispatcher/login', data={'username': user.email, 'code': code})

    def _create_client(self):
        first_client = factories.ClientFactory()
        second_client = factories.ClientFactory()
        return first_client, second_client

    def logout_user(self):
        self.client.logout()

    def assertStatusCode(self, response, status):
        self.assertIsNotNone(response)

        try:
            content = response.content.decode('utf-8')
        except UnicodeDecodeError:
            content = '<not printable {} bytes>'.format(len(response.content))

        self.assertEqual(
            response.status_code,
            status,
            msg='{} != {} with response data {}'.format(
                response.status_code,
                status,
                content
            )
        )
    def assertListsOfDictsEqual(self, request_list, reponse_list, sort_by=''):
        sorted_request = sorted(request_list, key=lambda k: k[sort_by])
        sorted_response = sorted(reponse_list, key=lambda k: k[sort_by])

        for index, item in enumerate(sorted_request):
            self.assertDictsEqual(sorted_response[index], item)

    def assertDictsNotEqual(self, request_dict, response_dict):
        for k, v in request_dict.items():
            self.assertNotEqual(
                response_dict[k],
                v,
                msg='{} is from request. {} is from response. Key is {}'.format(
                    v, response_dict[k], k
                )
            )

    def assertDictsEqual(self, request_dict, response_dict):
        for k, v in request_dict.items():
            self.assertEqual(
                response_dict[k],
                v,
                msg='{} is from request. {} is from response. Key is {}'.format(
                    v, response_dict[k], k
                )
            )
