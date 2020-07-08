<?php
if (array_key_exists("ingredients", $_POST) && array_key_exists("resources", $_POST))
{
    $ingredients=$_POST["ingredients"];
    $resources=$_POST["resources"];
    file_put_contents("ingredients.json", $ingredients);
    file_put_contents("resources.json", $resources);
    $html=file_get_contents("scheduler.html");
    $injected="dp.resources=$resources;\ndp.ingredients=$ingredients;";
    $tag="auto-generated";
    $html=preg_replace("/<$tag>.*<\\/$tag>/s","<$tag>\n$injected\n//<\\/$tag>",$html);
    echo $html;
 } else {?>
<form method="post">
<table><tr><td>
<h1>Ingredients</h1>
<textarea name="ingredients" cols=80 rows=40><?php echo file_get_contents("ingredients.json");?></textarea>
</td><td>
<h1>Resources</h1>
<textarea name="resources" cols=80 rows=40><?php echo file_get_contents("resources.json");?></textarea>
</td></tr></table>
<input type="submit" value="Run">
</form>
<?php
}
