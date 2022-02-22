import numpy as np
from scipy.io import wavfile
from datetime import datetime as dt
from enum import Enum
import xml.etree.ElementTree as et
import json

########### LOAD ##############

events_root = et.parse('events.xml').getroot()
orgcds_root = et.parse('originatorcodes.xml').getroot()
fips_root = et.parse('fips.xml').getroot()
with open('uspsAbs.json') as f:
    state_abvs = json.load(f)


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

def check_1(stri):
    s = stri.upper()
    fnd = orgcds_root.find(s)
    if fnd is None:
        return s, 2, s + ' invalid originator code'
    if len(fnd.attrib) != 0:
        return s, 1, 'Originator code ' + s + ' - ' + fnd.text + ' is no longer in use'
    return s, 0, s + ' - ' + fnd.text

def check_2(stri):
    if len(stri) == 3:
        s = stri.upper()
        elem = events_root.find('*[@code=\''+s+'\']')
        if elem is None:
            return s, 2, '\"' + s + '\" invalid event code'
        if elem.attrib['us'] == 'NI':
            return s, 1, 'Event ' + s + ' - ' + elem.text + ' is not in use'
        return s, 0, s + ' - ' + elem.text
    s = stri.lower()
    for elem in events_root:
        if elem.text.lower() == s:
            val = elem.attrib['code']
            if elem.attrib['us'] == 'NI':
                return val, 1, 'Event ' + val + ' - ' + elem.text + ' is not in use'
            return val, 0, elem.attrib['code'] + ' - ' + elem.text
    return stri, 2, 'No event called \"' + stri + '\"'

def check_3(stri):
    lcds = [x.strip() for x in stri.split('.')]
    for i in range(len(lcds)):
        if lcds[i].strip() == '':
            lcds.pop(i)
    rtn = []
    for location in lcds:
        foo = [x.strip() for x in location.split(',')]
        if len(foo) > 2:
            return stri, 2, 'Doesn\'t understand \"' + location + '\"'
        elif len(foo) == 1:
            state = foo[0]
            if len(state) == 2:
                state = state.upper()
                if state not in state_abvs.keys():
                    return stri, 2, state + ' is not a state'
                rtn.append('0' + fips_root.find('*[@name=\'' + state_abvs[state] + '\']').attrib['id'] + '000')
            else:
                state_l = state.lower()
                found_flag = False
                for elem in fips_root:
                    if elem.attrib['name'].lower() == state_l:
                        # PRONE TO ERROR
                        rtn.append('0' + elem.attrib['id'] + '000')
                        found_flag = True
                        break
                if not found_flag:
                    return stri, 2, state_l + ' is not a state'
        elif len(foo) == 2:
            state = foo[1]
            county = foo[0]
            if len(state) == 2:
                state = state.upper()
                if state not in state_abvs.keys():
                    return stri, 2, state + ' is not a state'

                chosen_state_element = fips_root.find('*[@name=\'' + state_abvs[state] + '\']')
                found_county_flag = False
                for elem_county in chosen_state_element:
                    if elem_county.text.lower() == county.lower():
                        rtn.append('0' + chosen_state_element.attrib['id'] + elem_county.attrib['id'])
                        found_county_flag = True
                        break
                if not found_county_flag:
                    return stri, 2, 'County ' + county + ' not found in ' + chosen_state_element.attrib['name']
            else:
                state_l = state.lower()
                chosen_state_element = None
                found_state_flag = False
                for elem_state in fips_root:
                    if elem_state.attrib['name'].lower() == state_l:
                        chosen_state_element = elem_state
                        found_state_flag = True
                        break
                if not found_state_flag:
                    return stri, 2, state + ' is not a state'
                found_county_flag = False
                for elem_county in chosen_state_element:
                    if elem_county.text.lower() == county.lower():
                        rtn.append('0' + chosen_state_element.attrib['id'] + elem_county.attrib['id'])
                        found_county_flag = True
                        break
                if not found_county_flag:
                    return stri, 2, 'County ' + county + ' not found in ' + chosen_state_element.attrib['name']
    outmsg = ''
    for bar in rtn:
        outmsg += bar + ' '
    if len(lcds) > 31:
        return stri, 2, + str(len(lcds)) + ' location codes entered (maximum is 31)'
    return rtn, 0, outmsg



###########################################

def test_code():
    lcds = ["000000"]
    now = dt.now()
    sm_bin, sm_text = create_header("PEP", emergency_action_notification, lcds, "0001", now, "EASSIMPC")
    print(sm_text)
    aud = binary_to_signal(sm_bin, 44100)
    write_audio_file(aud, now)

while 1:
    inp = input()
    if inp == 'q':
        break
    rtrn, res, msg = check_3(inp)
    if res == 0:
        print('Selected value: ' + msg)
    elif res == 1:
        print('WARNING: ' + msg)
    elif res == 2:
        print('ERROR: ' + msg)
