# pySame
## Basic Operation
### Start
### Step 1: Originator Code
Five originator codes have been defined for the EAS:

•	`PEP` – Primary Entry Point System  
•	`CIV` – Civil Authorities  
•	`WXR` – National Weather Service  
•	`EAS` – EAS Participant  
•	`EAN` – Emergency Action Notification Network _(no longer in use)_

Use any of the above. For example:  
> `PEP`
#### Errors / Warnings
Other input values will result in an error:
> `ERROR: ABC invalid originator code`

If you choose `EAN`, you'll see this warning:
> `WARNING: Originator code EAN - EAN Network is no longer in use`



## Step 2: Event Code
There are 77 valid event codes. They're stored in `pySame/events.xml`.  
The data was collected from [this](https://en.wikipedia.org/wiki/Specific_Area_Message_Encoding#Event_codes) Wikipedia page.

Choose event either by three-letter code, or by name. For example:  
> `TOR` = `Tornado Warning` _(This will give an identical result)_
#### Errors / Warnings
Unrecognized values will result in an error:
> `ERROR: ABC invalid event code`  
> `ERROR: No event called Red Alert`

Some event codes (For example, `EAT`) will give this warning:
> `WARNING: Event EAT - Emergency Action Termination is not in use`

## Step 3: Location Codes
Use zero for the entire Unites States:
> `0`

For US states use state name / abbreviation. Separate with full stops (`.`). For example:  
> `Massachusetts. Connecticut. Rhode Island` = `MA. CT. RI` _(This will give an identical result)_

For US counties use county name + comma (`,`) + state name / abv. Separate with full stops. For example:  
> `New York, NY. Bronx, NY. Kings, NY. Queens, NY. Richmond, NY`

You may pick any combination of states and counties. For example:  
> `District of Columbia. Montgomery, MD. Prince Georges, MD. Arlington, VA`
#### Errors / Warnings
US states / counties which don't exist will cause these errors:
> `ERROR: Washington DC is not a state`  
> `ERROR: County Washington DC not found in District of Columbia`

If you use full stops / commas incorrectly, you may get an error:
> `ERROR: Doesn't understand "Bronx, NY,"`

If you specify more than 31 locations, you'll get this error (this is due to SAME protocol):
> `ERROR: 40 location codes entered (maximum is 31)`
