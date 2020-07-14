<?php
require "inc.php";
if (!array_key_exists("id", $_GET)||!annotation_exists($_GET["id"]))
    die("Missing id");
$data = get_annotation($_GET["id"]);

header('Content-type: application/json');
echo json_encode( $data );