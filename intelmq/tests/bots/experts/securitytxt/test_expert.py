# SPDX-FileCopyrightText: 2022 Frank Westers
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# -*- coding: utf-8 -*-
"""
Testing the SecurityTXT Expert Bot
"""

import unittest

import requests_mock

import intelmq.lib.test as test
from intelmq.bots.experts.securitytxt.expert import SecurityTXTExpertBot

EXAMPLE_INPUT_IP = {"__type": "Event",
                    "source.ip": "192.168.123.123"}

EXPECTED_OUTPUT_IP = {"__type": "Event",
                      "source.ip": "192.168.123.123",
                      "source.account": 'test@test.local'}

EXAMPLE_INPUT_FQDN = {"__type": "Event",
                      "source.fqdn": "test.local"}

EXPECTED_OUTPUT_FQDN = {"__type": "Event",
                        "source.fqdn": "test.local",
                        "source.abuse_contact": 'test.local/whitehat'}

EXPECTED_OUTPUT_FQDN_NO_CONTACT = {"__type": "Event",
                                   "source.fqdn": "test.local"}

@requests_mock.Mocker()
@test.skip_exotic()
class TestSecurityTXTExpertBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for the SecurityTXT Expert Bot
    """

    @classmethod
    def set_bot(cls):
        cls.bot_reference = SecurityTXTExpertBot

    def test_ip(self, m: requests_mock.Mocker):
        self._run_generic_test(securitytxt_url=f"https://{EXAMPLE_INPUT_IP['source.ip']}/.well-known/security.txt",
                               securitytxt=f"Contact: {EXPECTED_OUTPUT_IP['source.account']}",
                               input_message=EXAMPLE_INPUT_IP,
                               output_message=EXPECTED_OUTPUT_IP,
                               config={'url_field': 'source.ip', 'contact_field': 'source.account',
                                       'only_email_address': False},
                               m=m)

    def test_fqdn(self, m: requests_mock.Mocker):
        self._run_generic_test(securitytxt_url=f"https://{EXAMPLE_INPUT_FQDN['source.fqdn']}/.well-known/security.txt",
                               securitytxt=f"Contact: {EXPECTED_OUTPUT_FQDN['source.abuse_contact']}",
                               input_message=EXAMPLE_INPUT_FQDN,
                               output_message=EXPECTED_OUTPUT_FQDN,
                               config={'url_field': 'source.fqdn', 'contact_field': 'source.abuse_contact',
                                       'only_email_address': False},
                               m=m)

    def test_only_email_address_true(self, m: requests_mock.Mocker):
        self._run_generic_test(securitytxt_url=f"https://{EXAMPLE_INPUT_FQDN['source.fqdn']}/.well-known/security.txt",
                               securitytxt=f"Contact: {EXPECTED_OUTPUT_FQDN['source.abuse_contact']}",
                               input_message=EXAMPLE_INPUT_FQDN,
                               output_message=EXPECTED_OUTPUT_FQDN_NO_CONTACT,
                               config={'url_field': 'source.fqdn', 'contact_field': 'source.abuse_contact',
                                       'only_email_address': True},
                               m=m)

    def test_expired(self, m: requests_mock.Mocker):
        self._run_generic_test(securitytxt_url=f"https://{EXAMPLE_INPUT_FQDN['source.fqdn']}/.well-known/security.txt",
                               securitytxt=f"Contact: {EXPECTED_OUTPUT_FQDN['source.abuse_contact']}\nExpires: 1900-12-31T18:37:07.000Z",
                               input_message=EXAMPLE_INPUT_FQDN,
                               output_message=EXPECTED_OUTPUT_FQDN_NO_CONTACT,
                               config={'url_field': 'source.fqdn', 'contact_field': 'source.abuse_contact',
                                       'only_email_address': False, 'check_expired': True},
                               m=m)

    def test_not_expired(self, m: requests_mock.Mocker):
        self._run_generic_test(securitytxt_url=f"https://{EXAMPLE_INPUT_FQDN['source.fqdn']}/.well-known/security.txt",
                               securitytxt=f"Contact: {EXPECTED_OUTPUT_FQDN['source.abuse_contact']}\nExpires: 3000-12-31T18:37:07.000Z",
                               input_message=EXAMPLE_INPUT_FQDN,
                               output_message=EXPECTED_OUTPUT_FQDN,
                               config={'url_field': 'source.fqdn', 'contact_field': 'source.abuse_contact',
                                       'only_email_address': False, 'check_expired': True},
                               m=m)

    def _run_generic_test(self, m: requests_mock.Mocker, config: dict, securitytxt_url: str, securitytxt: str,
                          input_message: dict, output_message: dict):
        self.sysconfig = config
        self.prepare_bot()
        m.get(requests_mock.ANY, status_code=404)
        m.get(securitytxt_url, text=securitytxt)
        self.input_message = input_message
        self.run_bot()
        self.assertMessageEqual(0, output_message)
