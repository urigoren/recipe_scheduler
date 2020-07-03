<?php
if (array_key_exists("ingredients", $_POST) && array_key_exists("resources", $_POST))
{
$ingredients=$_POST["ingredients"];
$resources=$_POST["resources"];
file_put_contents("ingredients.json", $ingredients);
file_put_contents("resources.json", $resources);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Temporal Recipe Representation</title>

    <!-- head -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700" rel="stylesheet"/>
    <script src="js/daypilot-uri.min.js?v=2020.2.4517"></script>
    <!-- /head -->

</head>
<body>


<div id=content">
    <div id="dp"></div>
	<input type="button" onClick="javascript:done();" value="Done">

</div>
    <script type="text/javascript">

        var dp = new DayPilot.Scheduler("dp");
		

        dp.startDate = "2020-01-01";
        dp.days = 1;
        dp.scale = "Hour";
        dp.timeHeaders = [
            //{groupBy: "Month", format: "MMMM yyyy"},
            //{groupBy: "Day", format: "d"}
			{groupBy: "Hour", format: "H"}
        ];

        dp.contextMenu = new DayPilot.Menu({
            items: [
                {
                    text: "Delete", onClick: function (args) {
                        dp.events.remove(args.source);
                    }
                },
                {text: "-"},
                {
                    text: "Select", onClick: function (args) {
                        dp.multiselect.add(args.source);
                    }
                },
            ]
        });

        dp.treeEnabled = true;
        dp.treePreventParentUsage = true;
        dp.resources = <?php echo $resources;?>
		dp.ingredients = <?php echo $ingredients;?>
		

        dp.heightSpec = "Max";
        dp.height = 500;

        dp.events.list = [];


        dp.eventMovingStartEndEnabled = false;
        dp.eventResizingStartEndEnabled = false;
        dp.timeRangeSelectingStartEndEnabled = false;

        // event moving
        dp.onEventMoved = function (args) {
            dp.message("Moved: " + args.e.text());
        };

        // event resizing
        dp.onEventResized = function (args) {
            dp.message("Resized: " + args.e.text());
        };

        // event creating
        dp.onTimeRangeSelected = function (args) {
			var ingredients = dp.ingredients.reduce((obj, ing)=>{obj[ing.id]=ing.display;return obj;},{});
            DayPilot.Modal.prompt("Assign Ingredient:", ingredients).then(function (modal) {
                dp.clearSelection();
                var ingredient = modal.result;
                if (!ingredient) return;
				ingredient=dp.ingredients.filter(x=>x.id==ingredient)[0];
                var e = new DayPilot.Event({
                    start: args.start,
                    end: args.end,
                    id: DayPilot.guid(),
					ingredient: ingredient.id,
                    resource: args.resource,
                    text: ingredient.display,
					barColor: ingredient.color
                });
                dp.events.add(e);
                dp.message("Created");
            });
        };

        dp.onEventMove = function (args) {
            if (args.ctrl) {
                var newEvent = new DayPilot.Event({
                    start: args.newStart,
                    end: args.newEnd,
                    text: "Copy of " + args.e.text(),
                    resource: args.newResource,
                    id: DayPilot.guid()  // generate random id
                });
                dp.events.add(newEvent);

                // notify the server about the action here

                args.preventDefault(); // prevent the default action - moving event to the new location
            }
        };

        dp.init();

        dp.scrollTo("2020-02-01");
		alert=console.log;
		
		function done()
		{
			const hour=s=>parseInt(s[11]+s[12])
			window.events = dp.events.list.map(x=>{var ret = {};
			ret["ingredient"]= x.ingredient;
			ret["resource"]=x.resource;
			ret["start"]=hour(x.start.value);
			ret["end"]=hour(x.end.value);
			return ret;
			});
		}

    </script>


</body>
</html>
<?php } else {?>
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
