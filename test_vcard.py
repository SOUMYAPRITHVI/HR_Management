import csv

import gen_vcard
 
def test_create_card_valid_data():
    card=gen_vcard.create_vcard('Mason','Nicole','Buyer, retail','nicol.mason@gibson.com','(871)967-6024x82190')
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
    card=gen_vcard.create_vcard('Mason','Nicole','Buyer, retail','nicol.mason@gibson.com','(871)967-6024x82190')
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
def test_read_input_csv():
    data = [['Mason', 'Nicole', 'Buyer, retail', 'nicol.mason@gibson.com', '(871)967-6024x82190'], 
                           ['Walker', 'Steve', 'Accommodation manager', 'steve.walke@hicks.info', '(876)953-8282x713']]

    with open('news.csv', 'w',newline='') as csvfile:
        w = csv.writer(csvfile)
        for row in data:
            w.writerow(row)

    # Call the function with the file-like object
    result = gen_vcard.read_input_csv('news.csv')
    expected_result = [['Mason', 'Nicole', 'Buyer, retail', 'nicol.mason@gibson.com', '(871)967-6024x82190'], 
                        ['Walker', 'Steve', 'Accommodation manager', 'steve.walke@hicks.info', '(876)953-8282x713']]

    assert result == expected_result