<?php
include "inc.php";

if (array_key_exists("id", $_GET) && annotation_exists($_GET['id']))
{
    $id=$_GET['id'];
    $view="kitchen";
    if (array_key_exists("view", $_GET))
        $view=$_GET["view"];

    $data = get_annotation($_GET['id']);
    if ($view=="kitchen")
    {
        // ingredients as actions
        $resources = json_decode(file_get_contents("resources.json"));
        $actions=array();
        $actions[] =array("display"=>"__ALL__", "id"=>-1, "color"=>"#ffffff");
        $actions[] =array("display"=>"__PASTE__", "id"=>-2, "color"=>"#ffffff");
        foreach ($data["normalized_ingredients"] as $key => $value) {
            $actions[]=array("display"=>$value, "id"=>$key, "color"=>"#00ff00");
        }
    }
    else {
        // ingredients as resources
        $resources=array();
        foreach ($data["normalized_ingredients"] as $key => $value) {
            $resources[]=array("name"=>$value, "id"=>$key);
        }
        $actions=json_decode(file_get_contents("actions.json"));
    }
    $events=$data["labels"];
    $event0=json_encode($events[0]);
    include "templates/annotate.php";
 } else {
    header("HTTP/1.0 404 Not Found");
    echo "<h1>Not Found</h1>";
}
