# coding=utf-8

import urllib
import urllib.request
import uuid
from json import dumps, loads
from os import path

from os.path import basename

from ifj2017.test.base import TestReport
from .. import __PROJECT_ROOT__


class BenchmarkUploader(object):
    TOKEN_FILE = path.join(__PROJECT_ROOT__, '.TOKEN')

    def __init__(self, _api_hostname):
        self._api_hostname = _api_hostname
        self._reports = []  # type: list[TestReport]
        self._token = None

    def authenticate_user(self):
        try:
            with open(self.TOKEN_FILE) as f:
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
        leader = input('Login of your leader? ')
        login = input('Your login? ')

        response = self._request('/api/v1/generate-author-token', dict(
            leader=leader,
            login=login
        ))
        return response.get('token') if response.get('success') else None

    def collect_report(self, report):
        # type: (TestReport) -> None
        self._reports.append(report)

    def send_reports(self):
        # type: (dict) -> dict
        if not self._reports:
            return {}
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
        with open(self.TOKEN_FILE, 'w') as f:
            f.write(token)

    def _request(self, url, data):
        request = urllib.request.Request(''.join((self._api_hostname, url)))
        request.add_header('Content-type', 'application/json')
        response = urllib.request.urlopen(request, bytes(dumps(
            data
        ), encoding='utf-8'))
        body = response.read()
        response.close()
        return loads(str(body, encoding='utf-8'), encoding='utf-8')
