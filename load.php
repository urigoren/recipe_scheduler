<?php
if (!array_key_exists("id", $_GET)||!is_numeric($_GET["id"]))
    die("Missing id");
$id = $_GET["id"];
$data = file_get_contents("annotations/$id.json");
$data = json_decode($data, TRUE);

header('Content-type: application/json');
echo json_encode( $data );