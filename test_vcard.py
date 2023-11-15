import os

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


def test_valid_parse_input_csv():
    result = gen_vcard.parse_input_csv(('Mason', 'Nicole', 'Buyer, retail', 'nicol.mason@gibson.com', '(871)967-6024x82190'))
    expected_result = 'NMason.vcf', '\nBEGIN:VCARD\nVERSION:2.1\nN:Mason;Nicole\nFN:Nicole Mason\nORG:Authors, Inc.\nTITLE:Buyer, retail\nTEL;WORK;VOICE:(871)967-6024x82190\nADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America\nEMAIL;PREF;INTERNET:nicol.mason@gibson.com\nREV:20150922T195243Z\nEND:VCARD\n'

    assert result == expected_result


def test_invalid_parse_input_csv():
    result = gen_vcard.parse_input_csv(('Mason', 'Nicole', 'Buyer, retail', 'nicol.mason@gibson.com', '(871)967-6024x82190'))
    expected_result = 'NMason.vcf', '\nBEGIN:VCARD\nVERSION:2.1\nN:Mason;\nFN:Nicole Mason\nORG:Authors, Inc.\nTITLE:Buyer, retail\nTEL;WORK;VOICE:(871)967-6024x82190\nADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America\nEMAIL;PREF;INTERNET:nicol.mason@gibson.com\nREV:20150922T195243Z\nEND:VCARD\n'

    assert not result == expected_result

def test_create_qr_code():
    result = gen_vcard.create_qr_code(('Mason', 'Nicole', 'Buyer, retail', 'nicol.mason@gibson.com', '(871)967-6024x82190'))
    assert result[0] == 'NMason.qr.png' and result[1].status_code == 200

def test_generate_output():
    op_directory=os.path.join(os.getcwd(),"V_cards")
    gen_vcard.generate_output(op_directory)
    assert os.path.exists(op_directory)