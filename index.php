<?php
include "inc.php";
echo "<h1>Annotations</h1><table>";
$annotations = all_annotaions();
usort($annotations, function($a, $b)
{
    return strcmp($b["status"], $a["status"]);
});
foreach ($annotations as $id => $data) {
    echo "<tr>";
    echo "<td><a href=\"annotate.php?id=$id\">${data['title']}</a></td>";
    echo "<td>${data['status']}</td>";
    echo "</tr>";
}
echo "</table>";
