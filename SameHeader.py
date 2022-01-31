import numpy as np
from scipy.io import wavfile
from datetime import datetime as dt
from enum import Enum
# import matplotlib.pyplot as plt


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


# Test code
lcds = ["000000"]
now = dt.now()
sm_bin, sm_text = create_header("PEP", emergency_action_notification, lcds, "0001", now, "EASSIMPC")
print(sm_text)
aud = binary_to_signal(sm_bin, 44100)
write_audio_file(aud, now)