"""Python wrapper for the Cloud Foundry API.
"""
# pylint: disable=protected-access
# pylint: disable=invalid-name
#
# The protected-access warnings are disabled because the decorator
# function uses protected members of the CfApi class outside the class.
# When this is the case it is acceptable to disable these warnings.
#
# The invalid-name warnings are disabled to allow for the use of one
# letter variables in anonymous instances or functions.

from __future__ import absolute_import
import sys
import json
import urllib
from time import time
from functools import wraps
from six.moves import urllib

filter_name = 'name:{0}'


def require_access_token(func):
    """Decorator function to handle getting/renewing access token.
    """

    @wraps(func)
    def wrapped_f(self, *args, **kwargs):
        # pylint: disable=missing-docstring
        #
        # Disabled because it does not make sense to document the
        # inner function.
        if self._access_token is None:
            self.login()
        elif time() > self._access_token_expire_time:
            self.refresh_token()
        return func(self, *args, **kwargs)

    return wrapped_f


class CfApi(object):

    def __init__(self, **kwargs):
        self.api_host = kwargs.get('api_host', '')
        self.login_host = kwargs.get('login_host', '')
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')
        self.org_name = kwargs.get('org_name', '')
        self.space_name = kwargs.get('space_name', '')
        self.org_guid = None
        self.space_guid = None
        self._access_token = None
        self._access_token_expire_time = 0
        self._refresh_token = None
        self._client_id = 'cf'
        self._client_secret = ''
        self._resolve_instance_guids()

    @property
    def bearer_token(self):
        return 'Bearer {0}'.format(self._access_token)

    @staticmethod
    def _request(url, headers=None, params=None, body=None, method='GET'):
        """Construct and send HTTP request.

        Should be considered internal to this class.  This is used by other
        high level functions to create a request object and send the request
        to the remote host.

        Args:
            url (str): The url to send the request to.

        Keyword Args:
            headers (Optional[dict]): A dict of HTTP headers that should be
                attached to the request.
            params (Optional[dict]): A dict of query parameters that should be
                attached to the request.  Should be simple key value pairs that
                will be converted to a query string and appended to the url.
            body (Optional[dict]): The body of the request.  Dict will be
                converted to urlencoded string and attached to the request.
            method (Optional[str]): The HTTP method to use for the request.
                This will default to a GET if no method is provided.

        Returns:
            object: The deserialized JSON response from the remote host.
        """
        headers = headers if headers else {}
        if params:
            url = '?'.join([url, urllib.parse.urlencode(params)])
        req = urllib.request.Request(url)
        for k, v in headers.items():
            req.add_header(k, v)
        req.get_method = lambda: str(method).upper()
        if body is not None:
            try:
                body = urllib.parse.urlencode(body)
            except TypeError:
                # pylint: disable=redefined-variable-type
                #
                # Certain API calls expect the content type to be
                # urlencoded but the body to actually be a json string
                # rather than an urlencoded string.  If we get a
                # TypeError here we assume the caller knows what they
                # are doing and just pass it along.
                pass
            req.add_header(
                'Content-Type', 'application/x-www-form-urlencoded')
            res = urllib.request.urlopen(req, body.encode('utf-8'))
        else:
            res = urllib.request.urlopen(req)

        response = res.read()

        if response:
            response = json.loads(response)
        return response

    def _request_all(self, *args, **kwargs):
        """Generator function to get all pages when present in response.

        Should be considered internal to this class.  This should be used
        if you expect a paged response from the server.  See _request
        for supported args and kwargs.
        """
        while True:
            response = self._request(*args, **kwargs)
            yield response
            if 'next_url' in response and response['next_url']:
                params = urllib.parse.urlparse(response['next_url']).query.split('&')
                kwargs['params'] = dict([p.split('=') for p in params])
            else:
                break

    @staticmethod
    def _json(data):
        """Serializes python object to JSON.

        Args:
            data (object): The object to serialize.

        Returns:
            str: A JSON string representation of the object.
        """
        return json.dumps(data, indent=4, sort_keys=True)

    def _update_tokens(self, response):
        """Updates all token attributes for the class instance.

        Internal function to update all token related attributes whenever
        login or refresh_token is called.

        Args:
            response (dict): The server response from a token-based operation
                deserialized to a python dict.
        """
        expire_time = int(time() - 60) + int(response['expires_in'])
        self._access_token = response['access_token']
        self._refresh_token = response['refresh_token']
        self._access_token_expire_time = expire_time

    def _resolve_instance_guids(self):
        """Resolve org and space names to GUIDs.

        Internal function to resolve org and space names to GUIDs when org
        and space names are passed into the class constructor.
        """
        try:
            if self.org_name:
                self.org_guid = self.get_org_guid(self.org_name)
                if self.space_name:
                    spaces = self.org_spaces(self.org_guid)
                    space_guid = [
                        s['metadata']['guid'] for s in spaces
                        if s['entity']['name'] == self.space_name
                    ]
                    if space_guid:
                        self.space_guid = space_guid[0]
        except urllib.error.HTTPError as e:
            print('Error: {0}'.format(e.read()))
            sys.exit(127)

    def login(self):
        """Login to UAA and store token for future calls.

        Uses username and password attributes to login to the UAA instance
        defined in login_host.  The token and all information needed to refresh
        the token on expiry are also stored as local attributes to the class
        instance.
        """
        url = "https://{0}/oauth/token".format(self.login_host)
        body = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'client_id': self._client_id
        }
        headers = {'Authorization': 'Basic Y2Y6', 'Accept': 'application/json'}
        response = self._request(
            url, headers=headers, body=body, method='POST')
        self._update_tokens(response)

    def refresh_token(self):
        """Refresh an expired token.

        This will use the refresh_token to renew the access token.  Typically
        not called directly since token operations for most other functions
        that require tokens use the require_access_token decorator.
        """
        url = "https://{0}/oauth/token".format(self.login_host)
        body = {
            'grant_type': 'refresh_token',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'refresh_token': self._refresh_token
        }
        headers = {'Accept': 'application/json'}
        response = self._request(
            url, headers=headers, body=body, method='POST')
        self._update_tokens(response)

    @require_access_token
    def orgs(self, filters=None):
        """Retrieves a list of Cloud Foundry organizations.

        Pull a list of Cloud Foundry organizations and organization metadata
        from the Cloud Foundry API.

        Keyword Args:
            filters (Optional[dict]): A dict of query params that can be used
                to filter results on the server side.  See Cloud Foundry API
                documentation for supported parameters.

        Returns:
            list(dict): A list of organizations.
        """
        url = 'https://{0}/v2/organizations'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        resources = []
        for r in self._request_all(url, params=filters, headers=headers):
            resources = resources + r['resources']
        return resources

    @require_access_token
    def get_org_guid(self, org_name=None):
        """Retrieves the guid for specific org name.

        Args:
            org_name (str): The name of the Cloud Foundry org.

        Returns:
            str: The GUID for the org or an empty string.
        """
        guid = ''
        filters = {'q': filter_name.format(org_name)}
        org = self.orgs(filters=filters)
        if org:
            guid = org[0]['metadata']['guid']
        return guid

    @require_access_token
    def org_spaces(self, org_guid, filters=None):
        """Gets all spaces for an organization.

        Pull a list of space metadata for an organization by GUID.

        Args:
           org_guid (str): The org GUID to pull space metadata for.

        Keyword Args:
            filters (Optional[dict]): A dict of query params that can be used
                to filter results on the server side.  See Cloud Foundry API
                documentation for supported parameters.

        Returns:
            list(dict): A list of dict objects containing metadata for all
                spaces in the org.
                :param org_guid:
                :param filters:
        """
        url = 'https://{0}/v2/organizations/{1}/spaces'.format(
            self.api_host, org_guid
        )
        headers = {'Authorization': self.bearer_token}
        resources = []
        for r in self._request_all(url, params=filters, headers=headers):
            resources = resources + r['resources']
        return resources

    @require_access_token
    def services(self, filters=None):
        """Retrieves a list of Cloud Foundry services.

        Pull a list of services from the Cloud Controller.  This is not a list
        of provisioned services but service brokers that provide services to
        be provisioned.

        Keyword Args:
            filters (Optional[dict]): A valid query filter for the v2 services
                api in cloud foundry.  See cloud foundry documentation for
                supported filters.

        Returns:
            list: A list of resources and resource metadata.
        """
        url = 'https://{0}/v2/services'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        resources = []
        for r in self._request_all(url, params=filters, headers=headers):
            resources = resources + r['resources']
        return resources

    @require_access_token
    def service_guids(self, service_name=None):
        """Retrieves a lookup dict containing broker name to GUID mappings.

        This function will pull a dict of service broker names to service
        broker GUIDs for use in other operations.  Certain operations may
        require the broker GUID instead of the common name.  Results can be
        filtered by service broker name by using the service_name arg.

        Keyword Args:
            service_name (str): A single broker name to filter results.

        Returns:
            dict: A dict of broker names to guids.
        """
        if service_name is not None:
            filters = {'q': 'label:{0}'.format(service_name)}
            services = self.services(filters=filters)
        else:
            services = self.services()
        service_guids = dict([
            (s['entity']['label'], s['metadata']['guid']) for s in services
        ])
        return service_guids

    @require_access_token
    def app_guids(self, app_name=None):
        """Retrieves a lookup dict containing broker name to GUID mappings.

        This function will pull a dict of service broker names to service
        broker GUIDs for use in other operations.  Certain operations may
        require the broker GUID instead of the common name.  Results can be
        filtered by service broker name by using the service_name arg.

        Keyword Args:
            app_name (str): A single broker name to filter results.

        Returns:
            dict: A dict of broker names to guids.
        """
        if app_name is not None:
            filters = {'q': filter_name.format(app_name)}
            apps = self.apps(filters=filters)
        else:
            apps = self.apps()
        apps_guids = dict([
            (s['entity']['name'], s['metadata']['guid']) for s in apps
        ])
        return apps_guids

    @require_access_token
    def service_instance_guids(self, service_instance=None):
        """Retrieves a lookup dict containing broker name to GUID mappings.

        This function will pull a dict of service broker names to service
        broker GUIDs for use in other operations.  Certain operations may
        require the broker GUID instead of the common name.  Results can be
        filtered by service broker name by using the service_name arg.

        Keyword Args:
            app_name (str): A single broker name to filter results.

        Returns:
            dict: A dict of broker names to guids.
        """
        if service_instance is not None:
            filters = {'q': filter_name.format(service_instance)}
            service_instances = self.service_instances(filters=filters)
        else:
            service_instances = self.service_instances()
        service_instances_guids = dict([
            (s['entity']['name'], s['metadata']['guid']) for s in service_instances
        ])
        return service_instances_guids

    @require_access_token
    def create_user_provided_service(self, name, parameters=None, log_drain_url=None):
        """Create a new user-provided service.

        This will create a new user-provided service based on the information
        passed in with the parameters argument.

        Args:
            name (str): The name of the new user-provided service.
            parameters (dict): A dictionary of service parameters.  This will
                become the credentials for the service upon service binding.
            log_drain_url (str): syslog_drain_url which is passed in the service.    

        Returns:
            dict: A dict containing metadata on the newly created service.
        """
        url = 'https://{0}/v2/user_provided_service_instances'.format(
            self.api_host
        )
        body = {
            'space_guid': self.space_guid,
            'name': name,
            'credentials': {}
        }
        headers = {'Authorization': self.bearer_token}
        if parameters:
            body['credentials'] = parameters
        if log_drain_url:
            body['syslog_drain_url'] = log_drain_url
        json_body = json.dumps(body)
        response = self._request(
            url, headers=headers, body=json_body, method='POST')
        return response

    @require_access_token
    def user_provided_service_instances(self, filters=None):
        """Retrieve a list of existing user-provided services.

        Returns a list of resources containing all user-provided services.
        Optionally the list can be filtered with the filters parameter.  See
        Cloud Foundry API documentation for supported filters.

        Keyword Args:
            filters (Optional[dict]): A valid query filter for the v2
                service plans api in cloud foundry.  See Cloud Foundry
                documentation for supported filters.

        Returns:
            list: A list of resources and resource metadata.
        """
        url = 'https://{0}/v2/user_provided_service_instances'.format(
            self.api_host
        )
        headers = {'Authorization': self.bearer_token}
        resources = []
        for r in self._request_all(url, params=filters, headers=headers):
            resources = resources + r['resources']
        return resources

    @require_access_token
    def create_service(self, name, broker_name, plan_name, parameters=None):
        """Create a new instance of a managed service instance.

        Args:
            name (str): The name of the new service instance.
            broker_name (str): The name of the service broker that will
                provision the service instance.
            plan_name (str): The service plan name to use when provisioning
                the new service instance.
            parameters (Optional[dict]): Optional parameters that the broker
                should use when provisioning a new service instance.  Valid
                parameters will vary from broker to broker.  See specific
                broker documentation for supported parameters.

        Returns:
            dict: A dict containing metadata on the newly created service.
        """
        url = 'https://{0}/v2/service_instances'.format(
            self.api_host)
        service_guids = self.service_guids(service_name=broker_name)
        if broker_name in service_guids:
            service_guid = service_guids[broker_name]
        else:
            raise ValueError('Unknown service broker.')
        plan_guids = self.service_plan_guids(service_guid)
        if plan_name in plan_guids:
            plan_guid = plan_guids[plan_name]
        else:
            raise ValueError('Invalid service plan')
        params = {'accepts_incomplete': 'true'}
        body = {
            'name': name,
            'service_plan_guid': plan_guid,
            'space_guid': self.space_guid,
            'parameters': {},
            'tags': []
        }
        headers = {'Authorization': self.bearer_token}
        if parameters:
            body['parameters'] = parameters
        json_body = json.dumps(body)
        response = self._request(
            url, params=params, headers=headers, body=json_body, method='POST')
        return response

    @require_access_token
    def service_plans(self, filters=None):
        """Retrieve metadata for all service plans.

        Returns a list of resources containing all service plan data you are
        authorized to see.  Supports and optional query filters for limiting
        the results.  See Cloud Foundry API documentation for supported
        filters.

        Keyword Args:
            filters (Optional[dict]): A valid query filter for the v2
                service plans API in Cloud Foundry.  See Cloud Foundry
                documentation for supported filters.

        Returns:
            list: A list of resources and resource metadata.
        """
        url = 'https://{0}/v2/service_plans'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        resources = []
        for r in self._request_all(url, params=filters, headers=headers):
            resources = resources + r['resources']
        return resources

    @require_access_token
    def service_plan_guids(self, service_guid):
        """Retrieve a mapping of service plans to service guids for a service.

        Returns a dict of service plan names to service plan guids for all
        plans available on from the service specified by the service_guid
        arg.  This requires the service_guid which can be retrieved with the
        service_guids method.

        Args:
            service_guid (str): The GUID for the service.

        Returns:
            dict: A dict with service plan names as keys and service plan
                guids as values.
        """
        filters = {'q': 'service_guid:{0}'.format(service_guid)}
        service_plans = self.service_plans(filters=filters)
        service_plan_guids = dict([
            (s['entity']['name'], s['metadata']['guid'])
            for s in service_plans
        ])
        return service_plan_guids

    @require_access_token
    def service_instances(self, filters=None):
        """Retrieves a list of Cloud Foundry service instances.

        Pull a list of service instance from the Cloud Controller.

        Keyword Args:
            filters (Optional[dict]): A dict of query params that can be used
                to filter results on the server side.  See Cloud Foundry API
                documentation for supported parameters

        Returns:
            list[dict]: A list of service instances and service metadata.
        """
        url = 'https://{0}/v2/service_instances'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        resources = []
        for r in self._request_all(url, params=filters, headers=headers):
            resources = resources + r['resources']
        return resources

    @require_access_token
    def service_keys(self, filters=None):
        """Retrieves a list of Cloud Foundry service instances.

        Pull a list of service instance from the Cloud Controller.

        Keyword Args:
            filters (Optional[dict]): A dict of query params that can be used
                to filter results on the server side.  See Cloud Foundry API
                documentation for supported parameters

        Returns:
            list[dict]: A list of service instances and service metadata.
        """
        url = 'https://{0}/v2/service_keys'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        resources = []
        for r in self._request_all(url, params=filters, headers=headers):
            resources = resources + r['resources']
        return resources

    @require_access_token
    def create_service_keys(self, service_instance_guid, service_key_name):
        """Create a application in the current org/space.

        This will create a new application in the current space.  It does
        not actually push the application and additional API calls are
        needed to do so.  This is only implemented for a specific use
        case at the moment and should really be used only to extract
        credentials for a service brokered service instance.

        Args:
            app_name (str): The name of the application to create.

        Returns:
            dict: A dictionary of application metadata.
            :param service_key_name:
            :param service_instance_guid:
        """
        url = 'https://{0}/v2/service_keys'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        json_body = json.dumps({
            'service_instance_guid': service_instance_guid,
            'name': service_key_name
        })
        print("Create service keys cf.py... ", url, json_body)
        response = self._request(
            url, headers=headers, body=json_body, method='POST')
        return response

    @require_access_token
    def apps(self, filters=None):
        """Retrieves a list of Cloud Foundry applications.

        Pull a list of Cloud Foundry applications and application metadata.  By
        default this will pull all applications you have permissions to view.
        Optionally you can use filters to limit the number of applications
        returned in the response.  See Cloud Foundry documentation for
        supported filters.

        Keyword Args:
            filters (Optional[dict]): A dict of query params that can be used
                to filter results on the server side.  See Cloud Foundry API
                documentation for supported parameters

        Returns:
            list[dict]: A list of resource and resource metadata.
        """
        url = 'https://{0}/v2/apps'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        resources = []
        for r in self._request_all(url, params=filters, headers=headers):
            resources = resources + r['resources']
        return resources

    @require_access_token
    def create_app(self, app_name):
        """Create a application in the current org/space.

        This will create a new application in the current space.  It does
        not actually push the application and additional API calls are
        needed to do so.  This is only implemented for a specific use
        case at the moment and should really be used only to extract
        credentials for a service brokered service instance.

        Args:
            app_name (str): The name of the application to create.

        Returns:
            dict: A dictionary of application metadata.
        """
        url = 'https://{0}/v2/apps'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        json_body = json.dumps({
            'name': app_name,
            'space_guid': self.space_guid
        })
        response = self._request(
            url, headers=headers, body=json_body, method='POST')
        return response

    @require_access_token
    def delete_app(self, app_guid):
        """Delete an application from the current org/space.

        Args:
            app_guid (str): The GUID of the application to delete.

        """
        url = 'https://{0}/v2/apps/{1}'.format(self.api_host, app_guid)
        headers = {'Authorization': self.bearer_token}
        self._request(url, headers=headers, method='DELETE')

    @require_access_token
    def delete_service(self, service_guid):
        """Delete an application from the current org/space.

        Args:
            service_guid (str): The GUID of the service to delete.

        """
        url = 'https://{0}/v2/service_instances/{1}'.format(self.api_host, service_guid)
        headers = {'Authorization': self.bearer_token}
        self._request(url, headers=headers, method='DELETE')

    @require_access_token
    def bind_service(self, service_guid, app_guid):
        """Bind an existing service to an application.

        Args:
            service_guid (str): The GUID of the service instance.
            app_guid (str): The GUID of the application to bind to.
        """
        url = 'https://{0}/v2/service_bindings'.format(self.api_host)
        headers = {'Authorization': self.bearer_token}
        json_body = json.dumps({
            'service_instance_guid': service_guid,
            'app_guid': app_guid
        })
        response = self._request(
            url, headers=headers, body=json_body, method='POST')
        return response

    @require_access_token
    def unbind_service(self, binding_guid):
        """Unbind a service from an application.

        Args:
            binding_guid (str): The GUID for the service binding.
        """
        url = 'https://{0}/v2/service_bindings/{1}?'.format(
            self.api_host, binding_guid)
        headers = {'Authorization': self.bearer_token}
        response = self._request(url, headers=headers, method='DELETE')
        return response

    @require_access_token
    def create_task(self, command, name, app_guid, memory_in_mb=512, disk_in_mb=512):
        """This will create a new cf task which runs the command asynchronously.

        :param command: Command to run as a cf task in a separate container.
        :param name: Name of the task. This is used to query the status of the task run.
        :param app_guid: Unique identifier of an application where the task is required to run.
        :param memory_in_mb: Memory used to run the task. Default: 512 MB.
        :param disk_in_mb: Disk used to run the task. Default: 512 MB.

        :return: dict: A dict containing metadata on the newly created task.
        """

        url = 'https://{0}/v3/apps/{1}/tasks'.format(
            self.api_host,
            app_guid
        )
        body = {
            # /home/vcap/app
            'command': command,
            'name': name,
            'memory_in_mb': memory_in_mb,
            'disk_in_mb': disk_in_mb
        }
        headers = {'Authorization': self.bearer_token}
        try:
            return self._request(url, headers=headers, body=body, method='POST')
        except urllib.error.HTTPError as err:
            task_type, value, exec_traceback = sys.exc_info()
            print('Error creating task %s: %s, %s' % (task_type, value, exec_traceback))

            if err.code == 422:
                err_body = err.read().decode()
                print(json.dumps(json.loads(err_body)))

            raise err

    @require_access_token
    def get_task(self, task_guid):
        """This will get the details of a task.

        :param task_guid: Unique identifier of a task.

        :return: dict: A dict containing metadata on the newly created task.
        """

        url = 'https://{0}/v3/tasks/{1}'.format(
            self.api_host,
            task_guid
        )
        headers = {'Authorization': self.bearer_token}

        try:
            return self._request(url, headers=headers)
        except urllib.error.HTTPError as err:
            task_type, value, exec_traceback = sys.exc_info()
            print('Error getting task %s: %s, %s' % (task_type, value, exec_traceback))

            if err.code == 422:
                err_body = err.read().decode()
                print(json.dumps(json.loads(err_body)))

            raise err

    @require_access_token
    def list_task(self, app_guid=None):
        """This will lists cf tasks which are assigned to this app_guid.
        If app_guid is not passed, this will list all tasks.

        :param app_guid: Unique identifier of an application where the task is required to run.

        :return: dict: A dict containing metadata on the newly created task.
        """

        if app_guid is None:
            url = 'https://{0}/v3/tasks'.format(self.api_host)
        else:
            url = 'https://{0}/v3/apps/{1}/tasks'.format(
                self.api_host,
                app_guid
            )

        headers = {'Authorization': self.bearer_token}

        try:
            return self._request(url, headers=headers)
        except urllib.error.HTTPError as err:
            task_type, value, exec_traceback = sys.exc_info()
            print('Error listing task %s: %s, %s' % (task_type, value, exec_traceback))

            if err.code == 422:
                err_body = err.read().decode()
                print(json.dumps(json.loads(err_body)))

            raise err
