<script>
//alert(location.href);
if(location.href.search('#')>0){
    window.location = location.href.replace('#', '&');
}

</script>
<?php
if(isset($_GET['access_token']) && isset($_GET['token'])){
    include('bd.php');
    mysql_query('UPDATE `users` SET `access_token` = \''.mysql_escape_string($_GET['access_token']).'\' WHERE `token` = \''.mysql_escape_string($_GET['token']).'\' ');
}?>