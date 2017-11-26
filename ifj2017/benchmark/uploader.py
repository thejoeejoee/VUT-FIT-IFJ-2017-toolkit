# coding=utf-8

import urllib
import urllib.request
import uuid
from json import dumps, loads
from os.path import basename
from urllib.error import URLError

from ..test.base import TestReport
from ..test.logger import TestLogger


class BenchmarkUploader(object):
    def __init__(self, _api_hostname, token_file):
        self._api_hostname = _api_hostname
        self._reports = []  # type: list[TestReport]
        self._token = None
        self._has_connection = False
        self._token_file = token_file
        self._last_response = None

    @property
    def has_connection(self):
        return self._has_connection

    def check_connection(self):
        request = urllib.request.Request(self._api_hostname)
        request.get_method = lambda: 'GET'

        try:
            data = self._request('/api/v1/service-online', {}, force=True)
        except URLError as e:
            TestLogger.log_warning('Problem with connecting to {} ({}).'.format(self._api_hostname, e))
        else:
            self._has_connection = (
                200 >= self._last_response.status < 400
            ) and data.get('success')
            if data.get('msg'):
                TestLogger.log_warning(data.get('msg'))

    def authenticate_user(self):
        if not self._has_connection:
            return
        try:
            with open(self._token_file) as f:
                token = str(uuid.UUID(f.read(), version=4))
        except (ValueError, OSError):
            token = None

        if not token:
            token = self._generate_token()
            if not token:
                return False
            self._save_token(token=token)
        self._token = token

    def _generate_token(self):
        TestLogger.log(
            TestLogger.HEADER,
            'At first, please, provide your FIT login names for sending benchmark results:'
        )

        def _ask():
            leader = input('Login of your team leader? ')
            login = input('Your login? ')

            return self._request('/api/v1/generate-author-token', dict(
                leader=leader,
                login=login
            ))

        response = _ask()
        while not response.get('success'):
            TestLogger.log_warning('Invalid credentials ({}).'.format(response.get('message')))
            response = _ask()

        return response.get('token')

    def collect_report(self, report):
        # type: (TestReport) -> None
        self._reports.append(report)

    def send_reports(self):
        # type: (dict) -> dict
        if not self._reports:
            return dict(success=True)
        response = self._request(
            '/api/v1/benchmark-result',
            dict(
                token=self._token,
                reports=[
                    dict(
                        section=basename(report.test_info.section_dir),
                        name=report.test_info.name,
                        operand_price=report.state.operand_price,
                        instruction_price=report.state.instruction_price,
                    ) for report in self._reports  # type: TestReport
                ]
            )
        )
        return response

    def _save_token(self, token):
        with open(self._token_file, 'w') as f:
            f.write(token)

    def _request(self, url, data, force=False):
        if not self._has_connection and not force:
            return {}
        request = urllib.request.Request(''.join((self._api_hostname, url)))
        request.add_header('Content-type', 'application/json')
        response = urllib.request.urlopen(request, bytes(dumps(
            data
        ), encoding='utf-8') if data else None)
        body = response.read()
        response.close()
        self._last_response = response
        return loads(str(body, encoding='utf-8'), encoding='utf-8')
