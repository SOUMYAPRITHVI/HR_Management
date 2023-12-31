import os

import csv

import gen_vcard
 
def test_create_card_valid_data():
    data='Mason','Nicole','Buyer, retail','nicol.mason@gibson.com','(871)967-6024x82190'
    card=gen_vcard.create_vcard(data,'100 Flat Grape Dr.;Fresno;CA;95555;United States of America')
    assert card=="""
BEGIN:VCARD
VERSION:2.1
N:Mason;Nicole
FN:Nicole Mason
ORG:Authors, Inc.
TITLE:Buyer, retail
TEL;WORK;VOICE:(871)967-6024x82190
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:nicol.mason@gibson.com
REV:20150922T195243Z
END:VCARD
"""

def test_create_card_invalid_data():
    data='Mason','Nicole','Buyer, retail','nicol.mason@gibson.com','(871)967-6024x82190'
    card=gen_vcard.create_vcard(data,'100 Flat Grape Dr.;Fresno;CA;95555;United States of America')
    assert not card=="""
BEGIN:VCARD
VERSION:2.1
N:Mason;Nicole
FN:Nicole Masonson
ORG:Authors, Inc.
TITLE:Buyer, retail
TEL;WORK;VOICE:(871)967-6024x82190
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:nicol.mason@gibson.com
REV:20150922T195243Z
END:VCARD
"""
