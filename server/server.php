<?php
ini_set('display_errors', 1);
ini_set('log_errors', 1);
ini_set('error_log', dirname(__FILE__) . '/error_log.txt');
error_reporting(E_ALL);
include('bd.php');
/*
 CREATE TABLE `b32_8116289_vk`.`users` (
`ID` INT NOT NULL AUTO_INCREMENT PRIMARY KEY ,
`token` VARCHAR( 255 ) NOT NULL ,
`access_token` VARCHAR( 512 ) NOT NULL
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci;
*/

if(isset($_GET['action'])){
    if($_GET['action']=='get_token'){
        mysql_query("INSERT INTO `users` (`token`, `access_token`) VALUES (MD5('".rand().time()."'),'')") or die('Database Error '.mysql_error());
        $q = mysql_query("SELECT `token` FROM `users` ORDER BY `ID` DESC LIMIT 0,1") or die('Database Error '.mysql_error());
    
        echo('http://api.vkontakte.ru/oauth/authorize?client_id='.$_GET['app_id'].'&scope='.$_GET['rights'].'&redirect_uri=http://peinguin.byethost32.com/redirect.php?token='.mysql_result($q,0,0).'&display=page&response_type=token '."\n".mysql_result($q,0,0)."\n");
    }
    if($_GET['action']=='access_token'){
        $q = mysql_query("SELECT `access_token` FROM `users` WHERE `token` = '".mysql_escape_string($_GET['token'])."'") or die('Database Error '.mysql_error());
    
        echo(mysql_result($q,0,0)."\n");
    }
}
?>