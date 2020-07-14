<?php
include "inc.php";

if (array_key_exists("id", $_GET) && annotation_exists($_GET['id']))
{
    $data = get_annotation($_GET['id']);
    $resources=$data["normalized_ingredients"];
    $actions=file_get_contents("actions.json");
    $html=file_get_contents("scheduler.html");
    $html=inject_js("schedule", "dp.resources=$resources;\ndp.actions=$actions;", $html);
    echo $html;
 } else {
    header("HTTP/1.0 404 Not Found");
}
