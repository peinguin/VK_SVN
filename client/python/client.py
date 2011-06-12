#!/usr/bin/python

app_id = '2365243'
app_rights = '131073' # App rights (documents access)
autorization_type = 'loginpass' # 'loginpass' or 'server'

function post($url, $postfields, $head = 0){
    $useragent="Mozilla/5.0 (X11; Linux x86_64; rv:2.2a1pre) Gecko/20110324 Firefox/4.2a1pre";
    $ch = curl_init(); // initialize curl handle
    curl_setopt($ch, CURLOPT_HEADER, $head);
    curl_setopt($ch, CURLOPT_USERAGENT, $useragent);
    curl_setopt($ch, CURLOPT_URL,$url); // set url to post to
    curl_setopt($ch, CURLOPT_FAILONERROR, 1);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);// allow redirects
    curl_setopt($ch, CURLOPT_RETURNTRANSFER,1); // return into a variable
    curl_setopt($ch, CURLOPT_TIMEOUT, 3); // times out after 4s
    curl_setopt($ch, CURLOPT_POST, 1); // set POST method
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postfields); // add POST fields
    $result = curl_exec($ch); // run the whole process 
    curl_close($ch);
    return $result;
}
function post_file($upload_url, $file_name){
    $postfields = array("file" => "@".$file_name);
    return post($upload_url, $postfields);
}
function autorize($login='', $pass=''){
    if (autorization_type=='server'){
        if (is_file('token.key') && ($access_token = file_get_contents('token.key'))!='')
            return $access_token;
        else {
            echo('Please get token'."\n");
            return false;
        }
    }elseif(autorization_type=='loginpass'){
        global $remixsid;
        if(!is_file('remixsid') || ($remixsid = file_get_contents('remixsid'))==''){
            if($login!='' || $pass != ''){
                $postfields = array('m' => '1', 'email' => $login, 'pass' => $pass);
                $result = post('http://vk.com/login.php', $postfields, 1);
                if($result){
                    preg_match('/remixsid=([a-z0-9]+)/', $result, $matches);
                    $remixsid = $matches[1];
                    file_put_contents('remixsid', $remixsid);}
                else{echo("Connection error\n");}
            }else{echo("Please specify login and password\n");}
        }
        $opts = array('http' => array('header'=> 'Cookie: remixsid='.$remixsid."\r\n"));
        $context = stream_context_create($opts);
        $url = 'http://api.vkontakte.ru/oauth/authorize?client_id='.app_id.'&scope='.app_rights.'&redirect_uri=http://peinguin.byethost32.com/&display=page&response_type=token';
        $contents = file_get_contents($url, false, $context);
        $pattern = '/https:\/\/api.vkontakte.ru\/oauth\/grant_access\?hash=[a-z0-9]+&client_id=[\d]+&settings=[\d]+&redirect_uri=[\s\S]+&response_type=token&state=/';
        preg_match($pattern, $contents, $matches);
        $contents = file_get_contents($matches[0], false, $context);
        preg_match('/access_token=([a-z0-9]*)/', $http_response_header[10], $matches);
        file_put_contents('token.key', $matches[1]);
        return trim($matches[1]);
    } else {
        echo('Please specify the type of authorization'."\n");
        return false;
    }
}
function request_vkApi($func, $param, $token){
    $url = 'https://api.vkontakte.ru/method/'.$func.'.xml?access_token='.$token.'&'.$param;
    $xml = simplexml_load_string(file_get_contents($url));
    if(isset($xml->error_code)){
        echo('Error'.$xml->error_code."\n");
        echo($xml->error_msg."\n");
        return $xml->error_code;}
    else{
        return $xml;
    }
}

include('class.args.php');

enable_error_reporting();

$args = new Args();
if($args->flag('get_url')){
    echo (file_get_contents('http://peinguin.byethost32.com/server.php?action=get_token'));
}elseif($args->flag('get_token')){
    if($args->flag('get_token')!=''){
        $access_token = file_get_contents('http://peinguin.byethost32.com/server.php?action=access_token&app_id='.app_id.'&rights='.app_rights.'&token='.$args->flag('get_token'));
        file_put_contents('token.key', trim($access_token));
        echo("Temporary access token - ".$access_token."\n");
    }else{echo('Specify option `assess token`'."\n");}
}elseif($access_token = autorize($args->flag('login'), $args->flag('pass'))){
    if($args->flag('upload_file')){
        if($args->flag('upload_file')!=''){
            do{
                $upload_url = request_vkApi('docs.getUploadServer','',$access_token)->upload_url;
                if($upload_url){
                    $result = post_file($upload_url, $args->flag('upload_file'));
                    if($result){
                        $arr = explode("|", json_decode($result)->file);
                        $arr[7] = date("d/m/Y H:i:s - ",time()).$arr[7];
                        $resp = urlencode(implode('|', $arr));
                        request_vkApi('docs.save','file='.$resp,$access_token);
                        echo('File '.$args->flag('upload_file').' is succefuly uploaded as '.$arr[7]."\n");
                    }else {echo "Connection error\n";}
                }else{die();}
                sleep($args->flag('n'));
            }while($args->flag('n'));
        }else echo('Specify option `file name`'."\n");
    }
}
