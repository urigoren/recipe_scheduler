<?php
include "inc.php";

if (array_key_exists("id", $_GET) && annotation_exists($_GET['id']))
{
    $id=$_GET['id'];
    $cmd = "/usr/bin/python3 python/actions.py $id --verbose";
    ob_start();
    passthru($cmd);
    $output = ob_get_contents(); 
    ob_end_clean();
    //echo $output;
  
    echo "<pre>$output</pre>";
 } else {
    header("HTTP/1.0 404 Not Found");
    echo "<h1>Not Found</h1>";
}
