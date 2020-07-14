<!DOCTYPE html>
<html>

<head>
    <title>Annotate</title>

    <!-- head -->
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700" rel="stylesheet" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <script src="js/daypilot-uri.min.js?v=2020.2.4517"></script>
    <!-- /head -->

</head>

<body>


    <div id="content">
        <div class="row"><div class="col-sm-12"><h1><?=$data['title']?></h1></div></div>
        <div class="row">
            <div class="col-sm-3">
                <img src="<?=$data['photo_url']?>" width=200>
            </div>
            <div class="col-sm-9">
            <ul>
                    <?php
                    foreach ($data['ingredients'] as $key => $value) {
                        echo "<li>$value</li>";
                    }
                    ?>
            </ul>
            </div>
        </div>
        <div class="row"><div class="col-sm-12"></div></div>
        <div class="row"><div class="col-sm-12"></div></div>
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
            { groupBy: "Hour", format: "H" }
        ];

        dp.contextMenu = new DayPilot.Menu({
            items: [
                {
                    text: "Delete", onClick: function (args) {
                        dp.events.remove(args.source);
                    }
                },
                { text: "-" },
                {
                    text: "Select", onClick: function (args) {
                        dp.multiselect.add(args.source);
                    }
                },
            ]
        });

        dp.treeEnabled = true;
        dp.treePreventParentUsage = true;
        dp.resources = <?php echo json_encode($resources);?>;
        dp.actions = <?php echo json_encode($actions);?>;

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
            var action_map = dp.actions.reduce((obj, ing) => { obj[ing.id] = ing.display; return obj; }, {});
            DayPilot.Modal.prompt("Assign Ingredient:", action_map).then(function (modal) {
                dp.clearSelection();
                var selected_action = modal.result;
                if (!selected_action) return;
                selected_action = dp.actions.filter(x => x.id == selected_action)[0];
                var e = new DayPilot.Event({
                    start: args.start,
                    end: args.end,
                    id: DayPilot.guid(),
                    action: selected_action.id,
                    resource: args.resource,
                    text: selected_action.display,
                    barColor: selected_action.color
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
        alert = console.log;

        function done() {
            const hour = s => parseInt(s[11] + s[12])
            window.events = dp.events.list.map(x => {
                var ret = {};
                ret["ingredient"] = x.ingredient;
                ret["resource"] = x.resource;
                ret["start"] = hour(x.start.value);
                ret["end"] = hour(x.end.value);
                return ret;
            });
        }

    </script>


</body>

</html>