<?php
include "inc.php";

if (array_key_exists("id", $_GET) && annotation_exists($_GET['id']))
{
    $id=$_GET['id'];
    $data = get_annotation($id);

    // ingredients as actions
    $resources = json_decode(file_get_contents("data/resources.json"));
    $tools = json_decode(file_get_contents("data/tools.json"));
    $implicits = json_decode(file_get_contents("data/implicit_ingredients.json"));
    $actions=array();
    foreach ($tools as $key => $value) {
        $actions[]=array("display"=>$value, "id"=>$key, "color"=>"#ff0000");
    }
    foreach ($implicits as $key => $value) {
        $actions[]=array("display"=>$value, "id"=>$key, "color"=>"#0000ff");
    }
    foreach ($data["normalized_ingredients"] as $key => $value) {
        $actions[]=array("display"=>$value, "id"=>$key, "color"=>"#00ff00");
    }

    $events=$data["labels"];
    $event0=json_encode($events[0]);
    include "templates/annotate.php";
 } else {
    header("HTTP/1.0 404 Not Found");
    echo "<h1>Not Found</h1>";
}
