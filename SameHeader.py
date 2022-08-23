# ###    ######    ###
#
# ###    PySame    ###
#
# ###    ######    ###
#
# ###  version 1.0
# 
# September 1 2022
# Author: SenorTite
#
# DISCLAIMER: PySame is provided for entertainment, educational and demonstrative
# purposes only, without warranty of any kind, either expressed or implied. By
# using the software, you hereby consent that you will be solely responsible for
# any subsequent event or action taking place from any usage of EAS tones generated
# during such use. The software and its author are not affiliated, approved by, or
# otherwise related to any organization or authority which uses or implements the
# Specific Area Message Encoding protocol (SAME) for official purposes. UNDER NO
# CIRCUMSTANCE SHALL THE AUTHOR OF THE SOFTWARE BE ACCOUNTABLE FOR ANY LOSS OR
# DAMAGE OR HAVE ANY OTHERWISE VALID LIABILITY ASSOCIATED IN ANY WAY WITH USAGE OF
# EAS TONES GENERATED USING THE SOFTWARE.
#
#

import numpy as np
from scipy.io import wavfile
from datetime import datetime as dt, timezone
from enum import Enum
import xml.etree.ElementTree as et
import json

##############################################################

events_root = et.parse('events.xml').getroot()
orgcds_root = et.parse('originatorcodes.xml').getroot()
fips_root = et.parse('fips.xml').getroot()
with open('uspsAbs.json') as f:
    state_abvs = json.load(f)

preamble = np.full(16, 0xAB, dtype='B')

stages = {
    1: "Originator code",
    2: "Event code",
    3: "Location codes",
    4: "Purge time",
    5: "Issue time",
    6: "Station callsign"
}


##############################################################


# returns a SAME digital header as binary data and its text representation.
def create_header(lst):
    s = "ZCZC-"
    for i in range(len(lst)):
        s += lst[i]
        if i == 2:
            s += '+'
        else:
            s += '-'

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
def write_audio_file(filename, samplerate, audio):
    scaled_audio = np.int16(audio * 32767)
    wavfile.write(filename, samplerate, scaled_audio)


###########################################


# Originator code
def check_1(stri):
    s = stri.upper()
    fnd = orgcds_root.find(s)

    if fnd is None:
        return s, 2, s + ' invalid originator code'
    if len(fnd.attrib) != 0:
        return s, 1, 'Originator code ' + s + ' - ' + fnd.text + ' is no longer in use'
    return s, 0, ''


# Event code
def check_2(stri):
    if len(stri) == 3:
        s = stri.upper()
        elem = events_root.find('*[@code=\''+s+'\']')
        if elem is None:
            return s, 2, '\"' + s + '\" invalid event code'
        if elem.attrib['us'] == 'NI':
            return s, 1, 'Event ' + s + ' - ' + elem.text + ' is not in use'
        return s, 0, ''

    s = stri.lower()

    for elem in events_root:
        if elem.text.lower() == s:
            val = elem.attrib['code']
            if elem.attrib['us'] == 'NI':
                return val, 1, 'Event ' + val + ' - ' + elem.text + ' is not in use'
            return val, 0, ''
    return stri, 2, 'No event called \"' + stri + '\"'


# Location codes
def check_3(stri):
    if stri == '0':
        return '000000', 0, ''
    
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
            found_county_flag = False
            if len(state) == 2:
                state = state.upper()
                if state not in state_abvs.keys():
                    return stri, 2, state + ' is not a state'
                chosen_state_element = fips_root.find('*[@name=\'' + state_abvs[state] + '\']')
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
                for elem_county in chosen_state_element:
                    if elem_county.text.lower() == county.lower():
                        rtn.append('0' + chosen_state_element.attrib['id'] + elem_county.attrib['id'])
                        found_county_flag = True
                        break
                if not found_county_flag:
                    return stri, 2, 'County ' + county + ' not found in ' + chosen_state_element.attrib['name']

    if len(lcds) > 31:
        return stri, 2, + str(len(lcds)) + ' location codes entered (maximum is 31)'

    rtn_final = ''
    for i in range(len(rtn)):
        rtn_final += rtn[i]
        if i != (len(rtn) - 1):
            rtn_final += '-'
    return rtn_final, 0, ''


# Purge time
def check_4(stri):
    if stri == '0':
        return '0000', 0, ''

    if not stri.isnumeric() or len(stri) != 4:
        return stri, 2, 'Incorrect format, input must be in hhmm format'

    hour = int(stri[:2])
    minute = int(stri[2:])

    if hour == 0:
        if minute % 15 == 0 and minute <= 45:
            return stri, 0, ''
        else:
            return stri, 2, 'Purge time under 1 hour must be in 15 minute increments'
    if hour < 6:
        if minute == 0 or minute == 30:
            return stri, 0, ''
        else:
            return stri, 2, 'Purge time between 1 to 6 hours must be in 30 minute increments'
    if minute == 0:
        return stri, 0, ''
    else:
        return stri, 2, 'Purge time beyond 6 hours must be in 1 hour increments'


# Issue time
def check_5(stri):
    if stri == '0':
        noww = dt.now(timezone.utc).strftime('%j%H%M')
        return noww, 0, ''

    try:
        dtm = dt.strptime(stri, "%d/%m %H:%M").now(timezone.utc).strftime('%j%H%M')
        return dtm, 0, ''
    except ValueError as e:
        return stri, 2, 'incorrect date format'


# Station call sign
def check_6(stri):
    if len(stri) != 8:
        return stri, 2, 'Station callsign must be 8 characters long'

    if any(c in "!@#$\\%^&*()-+?_=,<>\"" for c in stri):
        return stri, 2, 'Station callsign must not contain special characters except for \'/\''

    return stri, 0, ''


###########################################


def main_loop():
    rtrnfinal = []
    rtrn = ''
    res = 0
    msg = ''
    i = 0

    while i < 6:
        print("Field " + str(i+1) + " - " + stages[i+1] + "\nEnter value: ")
        instri = input()
        if i == 0:
            rtrn, res, msg = check_1(instri)
        elif i == 1:
            rtrn, res, msg = check_2(instri)
        elif i == 2:
            rtrn, res, msg = check_3(instri)
        elif i == 3:
            rtrn, res, msg = check_4(instri)
        elif i == 4:
            rtrn, res, msg = check_5(instri)
        elif i == 5:
            rtrn, res, msg = check_6(instri)
        
        if res == 0:
            rtrnfinal.append(rtrn)
            i += 1
            print()
        elif res == 1:
            print('WARNING: ' + msg + '\nWould you still like to proceed? (Y for yes, enter to revert)')
            instri = input()
            if instri == 'y' or instri == 'Y':
                rtrnfinal.append(rtrn)
                i += 1
            print()
        elif res == 2:
            print('ERROR: ' + msg + " - Please try again.\n")
    
    return rtrnfinal


###########################################


print("Welcome to PySame\nRefer to README for instructions.\n")
mylist = main_loop()

binaryData, stringData = create_header(mylist)
aud = binary_to_signal(binaryData, 44100)
filename = dt.now().strftime("SAME %Y%m%d %H%M%S.wav")

print('Header created - ' + stringData + '\nPress Enter to save as WAV file . . .')
input()
write_audio_file(filename, 44100, aud)
print("File saved as " + filename)
