# pySame
## Step 1: Originator Code
The originator code is a 3-letter code which specifies the type of authority / organization which issued the message. In real-life EAS equipment, this value is programmed per unit when put into use, and cannot be altered by the operator.

There are five originator codes defined for the EAS:

•	`PEP` – Primary Entry Point System.  
•	`CIV` – Civil Authorities.  
•	`WXR` – National Weather Service.  
•	`EAS` – EAS Participant.  
•	`EAN` – Emergency Action Notification Network. (no longer in use)

To choose an originator code for your SAME header, simply enter the desired 3-letter code. For example: `PEP`.

If you type `EAN` as your originator, a warning will appear:
> `WARNING: Originator code EAN - EAN Network is no longer in use`

Any other input value is invalid and will result in an error:
> `ERROR: ABC is not a valid originator code`

To learn more about originator codes, please refer to the ['Header format' paragraph in the SAME Wikipedia page](https://en.wikipedia.org/wiki/Specific_Area_Message_Encoding#Header_format), or the [official SAME protocol](https://www.nws.noaa.gov/directives/sym/pd01017012curr.pdf).

## Step 2: Event Code
Every SAME header carries an event code - a 3-letter code which describes the type of event in question. pySame only supports actual codes which have been defined for use in the EAS (There are around 80 of them).

To choose an event code, you can either enter the code itself, or its corresponding event name. For example:

`TOR` / `Tornado Warning`

Those input values are identical; Both will result in the `TOR` (Tornado Warning) event code being applied to your SAME header.

Some event codes have been defined for the EAS, but are no longer or never have been listed as being in use. Choosing such a code is possible, but will result in a warning. For example, when entering `EAT` / `Emergency Action Termination`, the following warning will be shown:
> `WARNING: Event EAT - Emergency Action Termination is not in use`

As mentioned earlier, you cannot use fake / fictional / nonexistant event codes or names. Invalid input values will show errors.

A full list of event codes is available in the ['Event codes' paragraph under the SAME Wikipedia page](https://en.wikipedia.org/wiki/Specific_Area_Message_Encoding#Event_codes).
