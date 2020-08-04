<!DOCTYPE html>
<html>

<head>
    <title>Recipe List</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    <link href="css/tabulator.min.css" rel="stylesheet">
    <script type="text/javascript" src="js/tabulator.min.js"></script>
</head>
<body>
    <div id="annotations"></div>
    <script>
const tabledata=<?php echo json_encode($table);?>;
function status_color(status) {
    if (status==0)
        return "orange";
    if (status==1)
        return "green";
        if (status==-5)
        return "blue";
    return "red";
}
var table = new Tabulator("#annotations", {
	data:tabledata,           //load row data from array
	layout:"fitColumns",      //fit columns to width of table
    columns:[ 
	 	{title:"Recipe", field:"title", hozAlign:"left", sorter: "string"},
        {title:"Ingredients", field:"num_ing", sorter: "number"},
        {title:"Instructions", field:"num_instruct", sorter: "number"},
	 	{title:"Status", field:"status", formatter:"traffic", sorter: "number",formatterParams:{color: status_color}},
 	],
    rowClick:function(e, row){ //trigger an alert message when the row is clicked
         window.location.href = 'annotate.php?id='+row.getData().id;
 	},
});
    </script>
</body>
</html>