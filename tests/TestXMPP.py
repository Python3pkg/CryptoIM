#!/usr/bin/env python
# encoding: utf-8

"""
   Copyright 2014 CryptoIM Development Team

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import cryptoim.xmpp as xmpp
from cli_mock import CryptoShell

from nose.tools import ok_, eq_, nottest
import time

def test_xmpp():
    """
        Test for various xmpp methods: connect, send_message, receive message
    """
    xmpp_cli = init_xmpp_cli()
    yield check_connect, xmpp_cli

    xmpp_cli = init_xmpp_cli()
    yield check_send_message, xmpp_cli

    xmpp_cli = init_xmpp_cli()
    yield check_receive_message, xmpp_cli

def init_xmpp_cli():
    """
        Initializes the xmpp_client and connects it
    """
    crypto_shell = CryptoShell()

    xmpp_cli = xmpp.XMPPClient('cryptoim@jabber.de', 'crypto_test', crypto_shell)
    xmpp_cli.connect_server(should_block=False)

    eq_(xmpp_cli.is_connected(), True)
    return xmpp_cli

def check_connect(xmpp_client):
    """
        Check for xmpp.XMPPClient.connect_server and disconnect_server
    """

    waitForConnection(xmpp_client, True)

    xmpp_client.disconnect_server()
    waitForConnection(xmpp_client, False)

    # Uncomment the following to enable a second check -- note, will require a ~10s timeout
    """
    xmpp_client.connect_server(should_block=False)
    waitForConnection(xmpp_client, True)

    xmpp_client.disconnect_server()
    waitForConnection(xmpp_client, False)
    """

def check_send_message(xmpp_client):
    """
        Check for xmpp.XMPPClient.send_message
    """

    waitForConnection(xmpp_client, True)

    while not xmpp_client.is_in_session():
        time.sleep(0.1)

    # TODO Works, but check
    xmpp_client.send_message('cryptoim2@jabber.de', 'Hello, CryptoIM check_send_message!')

    xmpp_client.disconnect_server()
    waitForConnection(xmpp_client, False)



def test_not_connect():
    """
        Check for xmpp.XMPPClient.connect_server and disconnect_server
    """

    crypto_shell = CryptoShell()

    # Wrong host
    xmpp_client = xmpp.XMPPClient('cryptoim@jabber2.de', 'crypto_test', crypto_shell)
    assertDisconnect(xmpp_client)


    # Wrong pass
    xmpp_client = xmpp.XMPPClient('cryptoim@jabber.de', 'wrong_pass', crypto_shell)
    assertDisconnect(xmpp_client)

    # Wrong name
    xmpp_client = xmpp.XMPPClient('cryptoim0@jabber.de', 'crypto_test', crypto_shell)
    assertDisconnect(xmpp_client)

def assertDisconnect(xmpp_client):
    """
        Conencts, disconnects and asserts it happened
    """
    xmpp_client.connect_server(should_block=False, should_reattempt=False)

    waitForConnection(xmpp_client, False)

    xmpp_client.disconnect_server()
    waitForConnection(xmpp_client, False)

def check_receive_message(xmpp_client):
    """
        Check for CryptoXMPP.message
    """

    crypto_shell = CryptoShell()

    # Assert connected

    xmpp_client2 = xmpp.XMPPClient('cryptoim2@jabber.de', 'crypto_test2', crypto_shell)
    xmpp_client2.connect_server(should_block=False)
    waitForConnection(xmpp_client, True)
    waitForConnection(xmpp_client2, True)

    while not (xmpp_client.is_in_session() and xmpp_client2.is_in_session()):
        time.sleep(0.1)

    # Send and receive message
    plaintext = 'Hello, CryptoIM check_receive_message!'
    ciphertext = xmpp_client.send_message(xmpp_client2.xmpp.jid, plaintext)

    # Disconnect
    xmpp_client.disconnect_server();
    waitForConnection(xmpp_client, False)
    xmpp_client2.disconnect_server()
    waitForConnection(xmpp_client2, False)
    waitForConnection(xmpp_client, False)

    # Assert that xmpp_client2 got it (it is bound to be received after disconnect if it waits)
    ok_(0 != len(crypto_shell.msg_list))
    eq_(len(crypto_shell.jid_list), len(crypto_shell.msg_list))
    eq_(plaintext, crypto_shell.msg_list[-1])
    eq_(xmpp_client.xmpp.jid, crypto_shell.jid_list[-1])

def waitForConnection(xmpp_client, should_be_connected):
    """
        Waits until a connection is estabilished
    """
    while not xmpp_client.is_connected() == should_be_connected:
        time.sleep(0.1)
    eq_(xmpp_client.is_connected(), should_be_connected)

