import numpy as np
from scipy.io import wavfile
from datetime import datetime as dt
from enum import Enum
import xml.etree.ElementTree as et
import json

########### LOAD ##############

events_root = et.parse('events.xml').getroot()
with open('originatorcodes.json') as f:
    org_codes = json.load(f)

###############################

# SAME event categories
class SAMEEventCat(Enum):
    warning = 1
    watch = 2
    advisory = 3
    test = 4


# SAME event object
class SAMEEvent:
    def __init__(self, event_code, cat, name):
        self.event_code = event_code
        self.cat = cat
        self.name = name


# Definitions of all possible SAME events
required_monthly_test = SAMEEvent("RMT", SAMEEventCat.test, "Required Monthly Test")
required_weekly_test = SAMEEvent("RWT", SAMEEventCat.test, "Required Weekly Test")
demonstration_message = SAMEEvent("DMO", SAMEEventCat.test, "Demonstration Message")
emergency_action_notification = SAMEEvent("EAN", SAMEEventCat.warning, "Emergency Action Notification")
emergency_action_termination = SAMEEvent("EAT", SAMEEventCat.warning, "Emergency Action Termination")


# The definition of the preamble used in all digitally encoded SAME header and EOMs (End Of Message).
preamble = np.full(16, 0xAB, dtype='B')


# returns a SAME digital header as binary data and its text representation.
def create_header(originator, event, location_codes, purge_time, issue_time, station_call_sign):
    s = "ZCZC-" + originator + "-" + event.event_code + "-"
    for i in range(len(location_codes) - 1):
        s += location_codes[i] + "-"
    else:
        s += location_codes[len(location_codes) - 1] + "+"
    s += purge_time + "-" + str(issue_time.now().timetuple().tm_yday).zfill(3) + "-"
    s += str(issue_time.now().timetuple().tm_hour).zfill(2)
    s += str(issue_time.now().timetuple().tm_min).zfill(2) + "-"
    s += station_call_sign + "-"

    content = np.asarray([ord(c) for c in s])
    data = np.empty(len(preamble) + len(content), dtype=np.dtype('B'))
    data[:len(preamble)] = preamble
    data[len(preamble):] = content
    return np.unpackbits(data, bitorder='little'), s


# Encodes a digital PCM audio signal based on binary data using FSK, with each bit lasting 1.92 ms.
def binary_to_signal(binary_data, sample_rate):
    bit_length = 1.92
    samples_per_bit = int(bit_length * sample_rate / 1000)

    t = np.arange(0, 1.0, 1 / samples_per_bit)

    mark_bit = np.sin(8.0 * np.pi * t)
    space_bit = np.sin(6.0 * np.pi * t)
    arr = np.empty(samples_per_bit * len(binary_data))

    for i in range(len(binary_data)):
        if binary_data[i]:
            arr[i * samples_per_bit:(i + 1) * samples_per_bit] = mark_bit
        else:
            arr[i * samples_per_bit:(i + 1) * samples_per_bit] = space_bit
    return arr


# Writes signal as a WAV audio file.
def write_audio_file(audio, date_time):
    scaled_audio = np.int16(audio * 32767)
    wavfile.write(date_time.strftime("SAME %Y%m%d %H%M%S.wav"), 44100, scaled_audio)

###########################################

def check_1(str): ###### FIX - Seperate data from code
    s = str.upper()
    if s == 'PEP' or s == 'CIV' or s == 'WXR' or s == 'EAS':
        return s, 0, s + ' - ' + org_codes[s]
    if s == 'EAN':
        return s, 1, 'Originator code EAN - EAN Network is no longer in use'
    return s, 2, '\"' + s + '\" is not a valid originator code'

def check_2(str):
    if len(str) == 3:
        s = str.upper()
        elem = events_root.find('*[@code=\''+s+'\']')
        if elem is None:
            return s, 2, '\"' + s + '\" is not a valid event code'
        if elem.attrib['us'] == 'NI':
            return s, 1, 'Event \"'+ elem.text + '\" (' + s + ') isn\'t being used by any US agency'
        return s, 0, s + ' - ' + elem.text
    # s = str.lower() ##### FIX - make not case sensetive
    s = str
    elem = events_root.find('*[.=\'' + s + '\']')
    if elem is None:
        return s, 2, 'There is no event called \"' + s + '\" (watch for typos, or use code instead of name)'
    val = elem.attrib['code']
    if elem.attrib['us'] == 'NI':
        return val, 1, 'Event \"' + s + '\" (' + val + ') isn\'t being used by any US agency'
    return val, 0, val + ' - ' + s


###########################################

def test_code():
    lcds = ["000000"]
    now = dt.now()
    sm_bin, sm_text = create_header("PEP", emergency_action_notification, lcds, "0001", now, "EASSIMPC")
    print(sm_text)
    aud = binary_to_signal(sm_bin, 44100)
    write_audio_file(aud, now)

while 1:
    rtrn, res, msg = check_1(input())
    if res == 0:
        print('Chose value: ' + msg)
    elif res == 1:
        print('WARNING: ' + msg)
    elif res == 2:
        print('ERROR: ' + msg)
