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

import cmd, sys, copy

import cryptoim.xmpp

if sys.version_info < (3, 0):
    import ConfigParser as configparser
else:
    import configparser as configparser


class CryptoShell(cmd.Cmd):
    """
        CryptoShell
    """

    intro = 'Welcome to CryptoIM!   Type help or ? to list commands.\n'
    prompt = '(cryptoim) '
    xmpp_client = None
    current_chat = None
    test_mode = False


    def __init__(self, config_file):
        """
            CryptoShell init
        """

        # super().__init__() # Python 3 only
        cmd.Cmd.__init__(self)
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.config_file = config_file

        # Logging
        self.received_msg_list = []
        self.received_jid_list = []
        self.sent_msg_list = []
        self.sent_jid_list = []

    # -- basic commands --
    def do_exit(self, arg):
        'Quit CryptoIM'

        self.do_disconnect(arg)
        self.print_cmd('Thank you for using CryptoIM!')
        quit()

    def do_q(self, arg):
        'Alias for quit'
        self.do_exit(arg)


    # -- overrides --
    def emptyline(self):
        pass

    # -- xmpp commands --
    def do_connect(self, arg):
        'connect JID PASSWORD or connect CONNECTION_NAME'
        splitted = arg.split(' ')

        if sanit_arg_count(splitted, 0, 2) == False:
            self.print_cmd('Invalid number of arguments!')
            return self.return_cli(False)

        if self.xmpp_client and self.xmpp_client.is_connected():
            self.print_cmd('Already connected!')
            return self.return_cli(False)

        conn_jid = None
        conn_pass = None

        if sanit_arg_count_exact(splitted, 1) == True:
            if splitted[0] in self.config.sections():
                username = self.config.get(arg, 'Username') # self.config[arg]['Username']
                host = self.config.get(arg, 'Host') # self.config[arg]['Host']
                conn_jid = username + '@' + host
                conn_pass = self.config.get(arg, 'Password') # self.config[arg]['Password']
            else:
                self.print_cmd('Connection ' + splitted[0] + ' doesn\'t exist')
                return self.return_cli(False)

        elif sanit_arg_count_exact(splitted, 2) == True:
            conn_jid = splitted[0]
            conn_pass = splitted[1]

        conn_jid += '/cryptoim' # Adds a static resource
        self.xmpp_client = cryptoim.xmpp.XMPPClient(conn_jid, conn_pass, self)
        self.xmpp_client.connect_server()
        return self.return_cli(True)


    def do_disconnect(self, arg):
        """
            disconnect
        """

        if not self.xmpp_client or not self.xmpp_client.is_connected():
            self.print_cmd('Already disconnected!')
            return self.return_cli(False)

        if arg: # arg nonempty
            self.print_cmd('Usage: disconnect, not disconnect <argument>')

        self.xmpp_client.disconnect_server()
        self.print_cmd('Disconnected from server.')
        return self.return_cli(True)


    def do_addconnection(self, arg):
        """
            Usage: addconnection <username> <JID> <password>
        """
        splitted = arg.split(' ')

        if self.config_find(splitted[0]):
            self.print_cmd(splitted[0] + ' is already in your connection list')
            return self.return_cli(False)
        if not sanit_arg_count_exact(splitted, 3):
            self.print_cmd('Usage: addconnection <username> <JID> <password>')
            return self.return_cli(False)
        if not sanit_is_jid(splitted[1]):
            self.print_cmd('JID has form of username@host.')
            self.print_cmd('Usage: addconnection <username> <JID> <password>')
            return self.return_cli(False) 

        self.config.add_section(splitted[0])
        self.config.set(splitted[0], 'username', splitted[0])
        self.config.set(splitted[0], 'host', (splitted[1].split('@') [1]) )
        self.config.set(splitted[0], 'password', splitted[2])

        with open(self.config_file, 'w') as conf:
            self.config.write(conf)
        return self.return_cli(True)

    def do_removeconnection(self, arg):
        """
            Usage removeconnection <username>
        """
        splitted = arg.split(' ')

        if not self.config_find(splitted[0]):
            self.print_cmd(splitted[0] + ' is not in your connection list')
            return self.return_cli(False)

        if not sanit_arg_count_exact(splitted, 1) or sanit_is_jid(splitted[0]):
            self.print_cmd('Usage: removeconnection <username>')
            return self.return_cli(False)

        self.config.remove_section(splitted[0])

        with open(self.config_file, 'w') as conf:
            self.config.write(conf)
        return self.return_cli(True) 

    def do_s(self, arg):
        'send toJID or username msg'
        return(self.do_send(arg))

    def do_send(self, arg):
        'send toJID or username msg'
        if not self.xmpp_client or not self.xmpp_client.is_in_session():
            self.print_cmd('Connect first!')
            return self.return_cli(False)

        splitted = arg.split(' ')

        if self.current_chat: # if chat mode
            if len(arg)==0:
                self.print_cmd('Please enter your message.')
                return self.return_cli(False)
            recipient = self.current_chat
            message = ' '.join(splitted)

        else: # if chat mode off
            if sanit_arg_count_exact(splitted, 0):
                #input: send (empty argument)
                self.print_cmd('Usage: send <username> or send <JID>')
                return self.return_cli(False)

            if self.config_find(splitted[0]): # if sending to friend
                recipient = self.config_find(splitted[0])
            elif sanit_is_jid(splitted[0]): # if sending to jid
                recipient = splitted[0]
            else: # error: username not defined or jid isnt jid
                self.print_cmd(splitted[0] + ' is not recognized. Please enter valid JID or username.')
                self.print_cmd('Usage: send <username> <message> or send <JID> <message>')
                return self.return_cli(False)

            message = ' '.join(splitted[1:])
            if len(message) == 0:
                self.print_cmd('Please enter your message.')
                return self.return_cli(False)

        self.xmpp_client.send_message(recipient, message)
        self.print_cmd(address_format(self.xmpp_client.xmpp.jid, message))

        return self.return_cli(True)

    def do_addfriend(self, arg):
        'addfriend name jid'
        splitted = arg.split(' ')

        if self.config_find(splitted[0]):
            self.print_cmd('Already in your friend list.')
            return 

        self.config.set('friends', splitted[0], splitted[1])
        with open(self.config_file, 'w') as conf:
            self.config.write(conf)
        return 

    def do_removefriend(self, arg):
        'removefriend name'
        splitted = arg.split(' ')

        if self.config_find(splitted[0]):
            self.print_cmd('Not in your friend list.')
            return 

        self.config.remove_option('friends', splitted[0])
        with open(self.config_file, 'w') as conf:
            self.config.write(conf)
        return 

    def do_chat(self, arg):
        """
            chat JID
        """
        if not arg:
            self.print_cmd('Usage: chat <JID> or chat <username>')
            return self.return_cli(False)

        if sanit_is_jid(arg):
            self.print_cmd('Opening chat window with: ' + arg.split(' ')[0])
            self.current_chat = arg.split(' ')[0]
            self.prompt = '(' + self.current_chat.split('@')[0] + ') '
            return self.return_cli(True)

        if not sanit_is_jid(arg) and self.config_find(arg):
            arg = self.config_find(arg)
            self.print_cmd('Opening chat window with: ' + arg.split(' ')[0])
            self.current_chat = arg.split(' ')[0]
            self.prompt = '(' + self.current_chat.split('@')[0] + ') '
            return self.return_cli(True)

        if not sanit_is_jid(arg) and not self.config_find(arg):
            self.print_cmd('Unknown JID or username, please check JID or try addfriend <username> <JID>')
            return self.return_cli(False)

    def do_stopchat(self, arg):
        """
            stopchat
        """
        if not self.current_chat:
            self.print_cmd('No open chat to close.')
            return self.return_cli(False)
        if arg is not None:
            self.print_cmd('Usage: stopchat, not stopchat <argument>')

        self.prompt = '(cryptoim) '
        self.current_chat = None
        self.print_cmd('Closing chat window.')
        return self.return_cli(True)

    # -- tools --

    def print_cmd(self, string):
        """
            Prints a string to the console
        """
        self.stdout.write(string + '\n')
        self.stdout.flush()

    def print_msg(self, jid, msg):
        """
            Prints a message (jid + msg), correctly formatted using address_format
            without erasing typed content.
        """

        backup = copy.copy(self.prompt)
        self.stdout.write('\r')
        self.stdout.flush()
        self.print_cmd(address_format(jid, msg))
        self.stdout.write(backup)
        self.stdout.flush()

    def print_debug(self, msg):
        """
            Prints debug messages
        """
        #self.print_cmd('DEBUG: ' + msg)
        pass

    def config_find(self, param, section='friends'):
        """
            Finds a parameter in section in config, returns the value, or None if not found
        """
        if self.config:
            if self.config.has_option(section, param):
                return self.config.get(section, param)
        return None

    def return_cli(self, value):
        if self.test_mode:
            return value
        else:
            return 

# End of class


def sanit_arg_count(input_array, number_lo, number_hi):
    """
        Returns True, if length of input array is in <number_lo, number_hi>
    """
    if len(input_array) <= number_hi and len(input_array) >= number_lo:
        return True
    return False

def sanit_arg_count_exact(input_array, number):
    """
        Returns True, if length of input_array is equal to number
    """
    return sanit_arg_count(input_array, number, number)

def sanit_is_jid (string):
    """
        returns true if the string is a JID
    """
    if '@' not in string:
        return False

    splitted = string.split('@')
    for string_part in splitted:
        string_part = string_part.strip('.').strip('/')
        if string_part.isalnum() == True:
            return True
        return False

def address_format(jid, msg):
    """
        Formats a jid and message to correctly display in the log
    """
    return(jid + ': ' + msg)

def test_cli(parameter):
    if parameter == 'true':
        return True
    return False
