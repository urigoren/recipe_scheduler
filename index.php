<?php
require "inc.php";
$annotations = all_annotaions();
$table = array();
foreach ($annotations as $id => $data)
{
    $table[] = array(
        "id"=>$id,
        "title"=>$data["title"],
        "num_ing"=>count($data["ingredients"]),
        "num_instruct"=>count($data["instructions"]),
        "status"=>$data["status"]
);
}
include "templates/list.php";
