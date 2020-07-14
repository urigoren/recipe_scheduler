<?php
if (!array_key_exists("id", $_POST)||!is_numeric($_POST["id"]))
    die("Missing id");
$id = $_POST["id"];
$data = file_get_contents("annotations/$id.json");
$data = json_decode($data, TRUE);
$data['labels']=json_decode($_POST['events']);
$data['status']=1;
$data = json_encode($data);
file_put_contents("annotations/$id.json", $data);
?>