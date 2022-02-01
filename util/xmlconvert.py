import xml.etree.ElementTree as et

treeold = et.parse('fips.xml')
rootold = treeold.getroot()
rootnew = et.Element('states')
dictstate = {}

for cty in rootold:
    dictstate.update({cty[2].text:cty[0].text})
for stateid in dictstate:
    rootnew.append(et.Element('state', attrib={'stateid': stateid, 'statename': dictstate[stateid]}))

#print(rootnew.find("*[@stateid='31']").attrib)

for cty in rootold:
    foo = rootnew.find("*[@stateid='"+cty[2].text+"']")
    bar = et.Element('cty', attrib={'code': cty[3].text})
    bar.text = cty[1].text
    foo.append(bar)

treenew = et.ElementTree(element=rootnew)
treenew.write('newmap.xml')
