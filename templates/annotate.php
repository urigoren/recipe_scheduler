<!DOCTYPE html>
<html>

<head>
    <title>Annotate</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700" rel="stylesheet" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <script src="js/daypilot-uri.min.js?v=2020.2.4517"></script>
    <style>
        #instruction {
            color: navy;
            font-size: 20px;
            font-family: arial;
            text-align: center;
        }
        .last_instruction {
            color: green
        }
    </style>
</head>

<body>


    <div id="content">
        <div class="row"><div class="col-sm-12"><h1><?=$data['title']?></h1></div></div>
        <div class="row">
            <div class="col-sm-3">
                <a href="<?=$data['url']?>"><img src="<?=$data['photo_url']?>" width=200></a>
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
        <div class="row">
            <div class="col-sm-1"><h1 class="glyphicon glyphicon-backward" id="prev_instruction" onclick="prev_instruction();"></h1></div>
            <div class="col-sm-10" id="instruction">
                <h3>1/<?=count($data['instructions'])?></h3><?=$data['instructions'][0]?>
            </div>
            <div class="col-sm-1"><h1 class="glyphicon glyphicon-forward" id="next_instruction" onclick="next_instruction();"></h1></div>
        </div>
        <div class="row"><div class="col-sm-12"></div></div>
        <div id="dp"></div>
        <form method="POST" action="save.php">
            <input type="hidden" name="id" value="<?=$id?>">
            <input type="hidden" name="events" id="events" value="[]">
        </form>

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
                        if (dp.multiselect.events().length==0)
                        {
                            dp.events.remove(args.source);
                        }
                        else
                        {
                            dp.multiselect.events().forEach(dp.events.remove);
                        }
                    }
                },
                { text: "-" },
                {
                    text: "Select", onClick: function (args) {
                        dp.multiselect.add(args.source);
                    }
                },
                {
                    text: "Copy", onClick: function (args) {
                        action_clipboard = dp.multiselect.events().map((x)=>x["data"]["action"]);
                        dp.multiselect.clear();
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

        dp.events.list = <?=$event0?>;


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
                var selected_action_id = modal.result;
                if (selected_action_id===undefined) return;
                let selected_actions = dp.actions.filter(x => x.id >=0);
                if (selected_action_id==-2)//paste
                    selected_actions=selected_actions.filter(x => action_clipboard.filter((y)=>x.id == y).length>0);
                if (selected_action_id>=0)
                    selected_actions=selected_actions.filter(x => x.id == selected_action_id);
                selected_actions.map(function (selected_action) {
                    dp.events.add(new DayPilot.Event({
                        start: args.start,
                        end: args.end,
                        id: selected_action.id+':'+DayPilot.guid(),
                        action: selected_action.id,
                        resource: args.resource,
                        text: selected_action.display,
                        barColor: selected_action.color
                    }));
                });
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
        let instruction_index=0;
        let instructions=<?=json_encode($data['instructions'])?>;
        let events=<?=json_encode($events)?>;
        let action_clipboard=[];

        function next_instruction()
        {
            console.log("next_instruction");
            events[instruction_index]=dp.events.list;
            if (instruction_index+1==instructions.length){
                if (!confirm("You are about to submit the annotations, are you sure ?"))
                    return;
                save();
            }
            instruction_index+=1;
            dp.events.list=events[instruction_index];
            dp.update();
            show_instruction();
        }
        function prev_instruction()
        {
            console.log("prev_instruction");
            events[instruction_index]=dp.events.list;
            if (instruction_index==0)
                return;
            instruction_index-=1;
            dp.events.list=events[instruction_index];
            dp.update();
            show_instruction();
        }
        function show_instruction()
        {
            let instruction=instructions[instruction_index];
            document.getElementById('instruction').innerHTML="<h3>"+(instruction_index+1)+"/"+instructions.length+"</h3>"+instruction;
            document.getElementById('events').value=JSON.stringify(events);
            const el = document.getElementById('next_instruction');
            if (instruction_index+1==instructions.length)
                el.classList.add("last_instruction");
            else
                el.classList.remove("last_instruction");
        }
        function save()
        {
            show_instruction();
            document.forms[0].submit();
            
        }

    </script>


</body>

</html>