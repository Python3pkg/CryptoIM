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

from cryptoim import decryptor_core
from cryptoim import encryptor_core
from nose.tools import ok_, eq_

def test_decrypt():
    """
        Test for decryptor_core.decrypt
    """
    decrypt = decryptor_core.decrypt
    encrypt = encryptor_core.encrypt

    def rand_str(limit):
        from string import ascii_letters, digits
        from random import choice

        rand = ""
        for i in range(limit):
            rand += choice(ascii_letters)
        return rand
    
    message = "This is a test message"
    key = rand_str(32)
    CT = encrypt(message,key)
    PT = decrypt(CT, key)
    eq_(message,PT)
    
    # ok_(len(decrypt(message, key)) != 0, "Length wasn't supposed to be 0") # Doesn't work yet

def test_ciphertext_fission():
    """
       Test for decryptor_core.__ciphertext_fission
    """

    ciphertext_fission = decryptor_core.__ciphertext_fission

    CT = '969afe5697ae7805308929daeb94c65b6e85768bc40dccd4bc616dd7345e6ec6'
    ciphertexts = ciphertext_fission(CT)
    for cts in ciphertexts:
        eq_(len(cts),4)
        for row in cts:
            eq_(len(row),4)
            for element in row:
                eq_(len(hex(element)),4)
    
def test_rsub_bytes():
    """
       Test for decryptor_core.__rsub_bytes
    """

    rsub_bytes = decryptor_core.__rsub_bytes
    sub_bytes = encryptor_core.__sub_bytes

    input_mat = [[0x00, 0x01, 0x02, 0x03],
                 [0xab, 0xcd, 0xef, 0xff],
                 [0x1a, 0x2b, 0x3c, 0x4d],
                 [0x2c, 0xe1, 0x12, 0x3a]]

    subbed_mat = sub_bytes(input_mat)
    eq_(input_mat,rsub_bytes(subbed_mat))

def test_rshift_rows():
    """
       Test for decryptor_core.__rshift_rows 
    """

    rshift_rows = decryptor_core.__rshift_rows

    input_mat = [[1,2,3,4],
                 [2,3,4,1],
                 [3,4,1,2],
                 [4,1,2,3]]
    expected_mat = [[1,2,3,4],
                    [1,2,3,4],
                    [1,2,3,4],
                    [1,2,3,4]]
    eq_(rshift_rows(input_mat),expected_mat)
