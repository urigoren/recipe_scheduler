<?php
function all_annotaions()
{
    $ret=array();
    $annotations=scandir("annotations");
    foreach ($annotations as $id => $fname) {
        $ext = pathinfo($fname, PATHINFO_EXTENSION);
        $id = pathinfo($fname, PATHINFO_FILENAME);
        if ($ext!="json")
            continue;
        $data=file_get_contents("annotations/".$fname);
        $data=json_decode($data, TRUE);
        $ret[$id]=$data;
    }
    return $ret;
}

function get_annotation($id)
{
    $data = file_get_contents("annotations/$id.json");
    $data = json_decode($data, TRUE);
    return $data;
}

function annotation_exists($id)
{
    return file_exists("annotations/$id.json");
}