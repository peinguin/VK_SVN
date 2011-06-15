#!/usr/bin/python
import urllib
import urllib2, cookielib
import mimetools, mimetypes
import os, stat
import re
from cStringIO import StringIO
import xml.dom.minidom
import sys
import getopt
import json

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable
class MultipartPostHandler(urllib2.BaseHandler):
    handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first

    def http_request(self, request):
        data = request.get_data()
        if data is not None and type(data) != str:
            v_files = []
            v_vars = []
            try:
                 for(key, value) in data.items():
                     if type(value) == file:
                         v_files.append((key, value))
                     else:
                         v_vars.append((key, value))
            except TypeError:
                systype, value, traceback = sys.exc_info()
                raise TypeError, "not a valid non-string sequence or mapping object", traceback

            if len(v_files) == 0:
                data = urllib.urlencode(v_vars, doseq)
            else:
                boundary, data = self.multipart_encode(v_vars, v_files)

                contenttype = 'multipart/form-data; boundary=%s' % boundary
                if(request.has_header('Content-Type')
                   and request.get_header('Content-Type').find('multipart/form-data') != 0):
                    print "Replacing %s with %s" % (request.get_header('content-type'), 'multipart/form-data')
                request.add_unredirected_header('Content-Type', contenttype)

            request.add_data(data)
        
        return request

    def multipart_encode(vars, files, boundary = None, buf = None):
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buf is None:
            buf = StringIO()
        for(key, value) in vars:
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"' % key)
            buf.write('\r\n\r\n' + value + '\r\n')
        for(key, fd) in files:
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            filename = fd.name.split('/')[-1]
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
            buf.write('Content-Type: %s\r\n' % contenttype)
            # buffer += 'Content-Length: %s\r\n' % file_size
            fd.seek(0)
            buf.write('\r\n' + fd.read() + '\r\n')
        buf.write('--' + boundary + '--\r\n\r\n')
        buf = buf.getvalue()
        return boundary, buf
    multipart_encode = Callable(multipart_encode)

    https_request = http_request

app_id = '2365243'
app_rights = '131073' # App rights (documents access)
autorization_type = 'loginpass' # 'loginpass' or 'server'

def post(url, postfields, head = 0):
    useragent="Mozilla/5.0 (X11; Linux x86_64; rv:2.2a1pre) Gecko/20110324 Firefox/4.2a1pre";
    request = urllib2.Request(url)
    request.add_header(useragent)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()), MultipartPostHandler)
    response = opener.open(request, postfields)
    if(head):
        response = response.info().headers+response
    return response
def post_file(upload_url, file_name):
    params = { "file" : open(file_name, "rb") }
    return post(upload_url, params); 
def file_get_contents(url, remixsid='', headers = 0):
    useragent="Mozilla/5.0 (X11; Linux x86_64; rv:2.2a1pre) Gecko/20110324 Firefox/4.2a1pre";
    request = urllib2.Request(url)
    request.add_header(useragent)
    if(remixsid!=''):
        request.add_header('Cookie: remixsid='+remixsid+"\r\n")
    opener = urllib2.build_opener()
    response = opener.open(request, postfields)
    if(headers):
        response = response.info().headers 
    return response
def autorize(login='', password=''):
    if (autorization_type=='server'):
        if (isfile('token.key') and open('token.key').read()!=''):
            return open('token.key').read();
        else:
            print "'Please get token\n"
            return false;
    elif(autorization_type=='loginpass'):
        global remixsid
        if( not isfile('remixsid') or open('remixsid').read()==''):
            remixsid = open('remixsid').read()
            if(login!='' or password != ''):
                postfields = {'m' : '1', 'email' : login, 'pass' : password}
                result = post('http://vk.com/login.php', postfields, 1);
                if(result):
                    matches = re.compile('remixsid=([a-z0-9]+)').findall(result)
                    remixsid = matches[1];
                    open('remixsid', 'w').write(remixsid)
                else:
                    print "Connection error\n";
            else:
                print "Please specify login and password\n"

        url = 'http://api.vkontakte.ru/oauth/authorize?client_id='+app_id+'&scope='+app_rights+'&redirect_uri=http://peinguin.byethost32.com/&display=page&response_type=token';
        contents = file_get_contents(url, remixsid);
        pattern = 'https:\/\/api.vkontakte.ru\/oauth\/grant_access\?hash=[a-z0-9]+&client_id=[\d]+&settings=[\d]+&redirect_uri=[\s\S]+&response_type=token&state=';
        matches = re.compile(pattern).findall(result)
        contents = file_get_contents(matches[0], remixsid, 1);
        matches = re.compile('access_token=([a-z0-9]*)').findall(contents)
        open('token.key', 'w').write(matches[1])
        return trim(matches[1]);
    else:
        print 'Please specify the type of authorization'+"\n";
        return false;
def request_vkApi(func, param, token):
    url = 'https://api.vkontakte.ru/method/'+func+'.xml?access_token='+token+'&'+param
    xml = xml.dom.minidom.parseString(file_get_contents(url))
    if(isset(xml.error_code)):
        print('Error'+xml.error_code+"\n")
        print(xml.error_msg+"\n")
        return xml.error_code;
    else:
        return xml

options, remainder = getopt.gnu_getopt(sys.argv[1:], 'o:v', ['get_url', 
                                                         'get_token=',
                                                         'login=',
                                                         'password=',
                                                         'upload_file=',
                                                         'n='])
for opt, arg in options:
    if opt in ('--get_url'):
        action = 'get_url'
        break
    elif opt in ('--get_token'):
        action = 'get_token'
        token = arg
        break
    elif opt in ('--login'):
        login = arg
    elif opt in ('--password'):
        password = arg
    elif opt in ('--upload_file'):
        upload_file = arg
    elif opt in ('-n'):
        sleep_time = arg
        
if(action == 'get_url'):
    print (file_get_contents('http://peinguin.byethost32.com/server.php?action=get_token'));
elif(action == 'get_token'):
    if(token!=''):
        access_token = file_get_contents('http://peinguin.byethost32.com/server.php?action=access_token&app_id='+app_id+'&rights='+app_rights+'&token='+token);
        open('token.key', 'w').write(trim(access_token))
        print("Temporary access token - "+access_token+"\n");
    else:
        print('Specify option `assess token`'+"\n")
else:
    access_token = autorize(login, password)
    if(access_token):
        if(upload_file!=''):
            while True:
                upload_url = request_vkApi('docs.getUploadServer','',access_token);
                if(upload_url):
                    result = post_file(upload_url, upload_file);
                    if(result):
                        arr = explode("|", json.loads(result)['file'])
                        arr[7] = date("d/m/Y H:i:s - ",time())+arr[7]
                        resp = urlencode(implode('|', arr))
                        request_vkApi('docs.save','file='+resp,access_token)
                        print('File '+upload_file+' is succefuly uploaded as '+arr[7]+"\n");
                    else:
                        print "Connection error\n";
                else:
                    sys.exit()
                if(sleep_time==''):
                    break
                else:
                    sleep(sleep_time)
        else:
            print 'Specify option `file name`'+"\n";
