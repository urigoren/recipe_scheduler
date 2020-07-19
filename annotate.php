<?php
include "inc.php";

if (array_key_exists("id", $_GET) && annotation_exists($_GET['id']))
{
    $id=$_GET['id'];

    $data = get_annotation($_GET['id']);
    $resources=array();
    foreach ($data["normalized_ingredients"] as $key => $value) {
        $resources[]=array("name"=>$value, "id"=>$key);
    }
    $actions=json_decode(file_get_contents("actions.json"));
    $events=$data["labels"];
    $event0=json_encode($events[0]);
    include "templates/annotate.php";
 } else {
    header("HTTP/1.0 404 Not Found");
    echo "<h1>Not Found</h1>";
}
