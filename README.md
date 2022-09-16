# pySame

_**PySame - SAME header generator**_

**PySame** is a command line application that generates SAME headers. SAME _(Specific Area Message Encoding)_ headers are short data bursts which are transferred as audio (similarly to fax tones), and are an essential component in several civil defense warning systems, most notably the _Emergency Alert System_ in the United States.

PySame will prompt you to enter the required information (the event in question, the issue time of the message, the areas affected, etc), create a valid SAME header which carries that information - and save it on your computer as a short audio file in WAV format.

# Setup

Since pySame is (meanwhile) only available as a Python source file, it's required to have Python installed on your system, as well as the 3rd party libraries *Numpy* ans *Scipy*.

Once you have those installed, place the *pySame* directory anywhere on your computer. Next, open a terminal window inside this directory, and run the script using the following command:

> &rarr; `python pySame.py`

If the program started correctly, you should be greeted with the following message:

> `Welcome to pySame`\
> `Refer to README for instructions.`

# Operation

Once pySame starts running, it'll ask you for the info required to create a header, step by step. Six data fields are requied:

- Originator code *(indicates who initiated the message)*
- Event code *(identifies the type of event)*
- Location codes *(identifies the physical location affected by the message)*
- Purge time *(the expected duration of the event)*
- Issue time *(the date and time at which the message was issued)*
- Station Callsign *(identifies the station broadcasting the message)*

After all fields have been entered, you can proceed to saving the header on your computer (inside the script's working directory) as a WAV file.

## Basic use-case example

This is an example of how to create a basic SAME header:

> `1. Originator code - enter value:` &rarr; *`PEP`*\
> `2. Event code - enter value:` &rarr; *`EAN`*\
> `3. Location codes - enter value:` &rarr; *`0`*\
> `4. Purge time - enter value:` &rarr; *`0`*\
> `5. Issue time - enter value:` &rarr; *`0`*\
> `6. Station callsign - enter value:` &rarr; *`EASSIMPC`*\
> `Header created - ZCZC-PEP-EAN-000000+0000-2431810-EASSIMPC-`\
> `Press Enter to save as WAV file . . .` &rarr; \
> `File saved as SAME 20220831 211050.wav`



## Detailed usage instructions

Below are specific instructions for all the options available for each data field.

### Originator Code
Five originator codes have been defined for the EAS:

- `PEP` – Primary Entry Point System  
- `CIV` – Civil Authorities  
- `WXR` – National Weather Service  
- `EAS` – EAS Participant  
- `EAN` – Emergency Action Notification Network _(no longer in use)_

Use any of the above. For example:  
> &rarr; `PEP`
#### Errors / Warnings
Other input values will result in an error:
> `ERROR: ABC invalid originator code`

If you choose `EAN`, you'll see this warning:
> `WARNING: Originator code EAN - EAN Network is no longer in use`



### Event Code
There are 77 valid event codes. They're stored in `pySame/events.xml`.  
The data was collected from [this](https://en.wikipedia.org/wiki/Specific_Area_Message_Encoding#Event_codes) Wikipedia page.

Choose event either by three-letter code, or by name. For example:  
> &rarr; `TOR` = `Tornado Warning` _(This will give an identical result)_
#### Errors / Warnings
Unrecognized values will result in an error:
> `ERROR: ABC invalid event code`  
> `ERROR: No event called Red Alert`

Some event codes (For example, `EAT`) will give this warning:
> `WARNING: Event EAT - Emergency Action Termination is not in use`

### Location Codes
Use zero for the entire Unites States:
> &rarr; `0`

For US states, use state name / abbreviation. Separate with full stops (`.`). For example:  
> &rarr; `Massachusetts. Connecticut. Rhode Island` = `MA. CT. RI` _(This will give an identical result)_

For US counties, use county name + comma (`,`) + state name / abv. Separate with full stops. For example:  
> &rarr; `New York, NY. Bronx, NY. Kings, NY. Queens, NY. Richmond, NY`

You may pick any combination of states and counties. For example:  
> &rarr; `District of Columbia. Montgomery, MD. Prince Georges, MD. Arlington, VA`
#### Errors / Warnings
US states / counties which don't exist will cause these errors:
> `ERROR: Washington DC is not a state`  
> `ERROR: County Washington DC not found in District of Columbia`

If you use full stops / commas incorrectly, you may get an error:
> `ERROR: Doesn't understand "Bronx, NY,"`

If you specify more than 31 locations, you'll get this error (this is due to SAME protocol):
> `ERROR: 40 location codes entered (maximum is 31)`

### Purge Time

_Still in process . . ._

### Issue time

_Still in process . . ._

### Station Callsign

_Still in process . . ._

_**Disclaimer:** PySame is provided for entertainment, educational and demonstrative purposes only, without warranty of any kind, either expressed or implied.
**Under no circumstance shall the author of the software be accountable for any loss or damage or have any otherwise valid liability associated in any way with usage of EAS tones generated using the software.**_