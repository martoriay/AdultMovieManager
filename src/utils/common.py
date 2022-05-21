import re

def id_parser(id):
    if id.startswith('dfe'):
        id='2'+id
    elif id.startswith('jukf'):
        id='h_227'+id
    elif id.startswith('milk'):
        id='h_1240'+id
    elif id.startswith('ddff'):
        id='111'+id
    elif id.startswith('fsdss'):
        id='1'+id
    elif id.startswith('dv'):
        id='53'+id
    elif id.startswith('sdde'):
        id='1'+id
    elif id.startswith('ienfh'):
        id='2'+id
    elif id.startswith('hodv'):
        id='5642hodv'+id[-5:]
    elif id.startswith('pih'):
        id='1'+id
    elif id.startswith('akdl'):
        id='1'+id
    return id

def deparser_id(id):
    if id.startswith('2') or id.startswith('1'):
        id=id[1:]
    elif id.startswith('53'):
        id=id[2:]
    elif id.startswith("111"):
        id=id[3:]
    elif id.startswith("h_227"):
        id=id[5:]
    elif id.startswith("h_1248"):
        id=id[6:]
    elif id.startswith("5642hodv"):
        id="HODV-"+id[8:]
        return id
    
    start=id.find('00')
    title=id[:start].upper()
    num=id[start+2:]
    return title+'-'+num

if __name__ == '__main__':
    print(deparser_id("ipx00080"))