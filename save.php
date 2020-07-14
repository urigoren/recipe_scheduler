<?php
require "inc.php";
if (!array_key_exists("id", $_POST)||!annotation_exists($_POST["id"]))
    die("Missing id");
$id = $_POST["id"];
$data = get_annotation($id);
$data['labels']=json_decode($_POST['events']);
$data['status']=1;
save_annotation($id, $data);
//header('Content-type: application/json');
//echo $data;
header("Location: https://goren.ml/recipe_scheduler/");
?>