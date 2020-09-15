<!DOCTYPE html>
<html>

<head>
    <title>Annotate</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700" rel="stylesheet" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
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
            <div class="col-sm-6">
            <ul>
                    <?php
                    foreach ($data['ingredients'] as $key => $value) {
                        echo "<li>$value</li>";
                    }
                    ?>
            </ul>
            </div>
            <h5>Status</h5>
            <div class="col-sm-3">
                <form method="POST" action="save.php">
                <input type="hidden" name="id" value="<?=$id?>">
                <select name="status">
                <option value="1">All OK</option>
                <option value="0">All OK, not finished</option>
                <option value="-1">Missing Tool</option>
                <option value="-2">Missing Resource</option>
                <option value="-3">Missing Ingredient</option>
                <option value="-4">Missing Time Boundry</option>
                <option value="-5">Other issue</option>
                </select>
                <input type="hidden" name="events" id="events" value="[]">
                </form>
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

    </div>
    <div class="modal" tabindex="-1" role="dialog" id="msgbox_dialog">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title"  id="msgbox_title"></h3>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <div class="row"><div class="col-sm-12" id="msgbox_body">
                </div></div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
            </div>
            </div>
        </div>
    </div>
    <div class="modal" tabindex="-1" role="dialog" id="event_dialog">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title"  id="modal-instruction"></h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-sm-6"><h3>Ingredients</h3><?php

                            foreach ($data["normalized_ingredients"] as $key => $value) {
                                echo "<div class=\"form-check\"><input type=\"checkbox\" class=\"form-check-input event_item\" id=\"$key\"><label class=\"form-check-label\" for=\"$key\">$value</label></div>";
                            }

                    ?></div>
                    <div class="col-sm-3"><h3>Tools</h3><?php
                            foreach ($tools as $key => $value) {
                                echo "<div class=\"form-check\"><input type=\"checkbox\" class=\"form-check-input event_item\" id=\"$key\"><label class=\"form-check-label\" for=\"$key\">$value</label></div>";
                            }
                    ?></div>
                    <div class="col-sm-3"><h3>Implicit</h3><?php
                            foreach ($implicits as $key => $value) {
                                echo "<div class=\"form-check\"><input type=\"checkbox\" class=\"form-check-input event_item\" id=\"$key\"><label class=\"form-check-label\" for=\"$key\">$value</label></div>";
                            }
                    ?></div>
                </div>
            </div>
            <div class="modal-footer">
                <select id="instruction_length">
                <option selected value="">Ends Immediately</option>
                <?php
                foreach ($time_lengths as $key => $value) {
                    echo "<option value=\"$key\">$value</option>";
                }
                ?></select>
                <button type="button" class="btn btn-primary" onclick="event_dialog_save()">Save changes</button>
                <button type="button" class="btn btn-secondary" onclick="event_dialog_clipboard()">From Clipboard</button>
                <button type="button" class="btn btn-secondary" onclick="event_dialog_clear()">Clear</button>
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
            </div>
            </div>
        </div>
    </div>
    <script type="text/javascript">
        function msgbox(title, txt)
        {
            jQuery('#msgbox_title').text(title);
            jQuery('#msgbox_body').text(txt);
            jQuery('#msgbox_dialog').modal('show');
        }
        function populate_unused_resource(start)
        {
            truncate(unused_resource_id, start);
            const used_ingredients = dp.events.list.filter(x=>x.start==start).map(x=>x.action);
            const unused_ingredients = dp.actions.map(a=>a.id).filter(a=>a.startsWith('I')).filter(a=>(used_ingredients.filter(x=>x===a)).length===0);
            add_events_by_action_id(unused_ingredients, {"start": start, "resource": unused_resource_id});
        }
        function add_events_by_action_id(ids, event_data)
        {
            const selected_actions=dp.actions.filter(x => ids.filter((y)=>x.id == y).length>0);
            let i=0;
            selected_actions.forEach(function (selected_action) {
                console.log(event_data)
                if (typeof(event_data.start)==="string")
                    event_data.start=DayPilot.Date(event_data.start)
                if (typeof(event_data.end)==="string")
                    event_data.end=DayPilot.Date(event_data.end)
                const e=new DayPilot.Event({
                    start: event_data.start,
                    end: (!!(event_data.end) ? event_data.end : event_data.start.addDays(1)),
                    id: selected_action.id+':'+DayPilot.guid(),
                    action: selected_action.id,
                    resource: event_data.resource,
                    text: selected_action.display,
                    barColor: selected_action.color
                });
                if (dp.events.list.filter(x=>(x.action==e.data.action) && (x.resource==e.data.resource) && (x.start==e.data.start)).length==0)
                {
                    dp.events.add(e);
                }
            });
            if (event_data.resource!=unused_resource_id)
                populate_unused_resource(event_data.start);

        }
        function set_reference_time_range(latest_events)
        {
            if  ((typeof latest_events === "undefined") || (latest_events.length==0))
            {
                // use all ingredients, set as unused
                latest_events=dp.actions.filter(a=>a.id.startsWith('I')).map(a=>({
                    "resource": unused_resource_id,
                    "text": a.display,
                    "barColor": a.color,
                    "action": a.id,
                    "id": a.id+':'+DayPilot.guid()
                    }));
            }
            const start = DayPilot.Date(dp.startDate);
            const end = start.addDays(1);
            dp.events.list.filter(on_start_date).map(e=>e.id).forEach(dp.events.removeById);
            latest_events.forEach(function (event_data) {
                const e=new DayPilot.Event({
                    start: start,
                    end: end,
                    id: event_data.id,
                    action: event_data.action,
                    resource: event_data.resource,
                    text: event_data.text,
                    barColor: event_data.barColor
                });
                dp.events.add(e);
            });
            populate_unused_resource(start);
        }
        function truncate(resource, start)
        {
            if  (typeof start === "undefined") 
                start=DayPilot.Date(dp.startDate);
            let i=0;
            dp.events.list.filter((x)=>(x["resource"]==resource) && (x["start"]==start)).forEach((e)=>{
                dp.events.removeById(e.id);
            });
        }
        function event_dialog_save()
        {
            const selected_action_ids=jQuery(".event_item").filter((i,v)=>v.checked).map((i,v)=>v.id).toArray();
            truncate(selected_time_range.resource, selected_time_range.start);
            add_events_by_action_id(selected_action_ids, {
                "start": selected_time_range.start,
                "end:": selected_time_range.end,
                "resource": selected_time_range.resource,
            });
            //instruction length special event:
            const instruction_length_id = document.getElementById("instruction_length").value;
            add_events_by_action_id([instruction_length_id], {
                "start": selected_time_range.start,
                "end:": selected_time_range.end,
                "resource": selected_time_range.resource,
            });
            jQuery('#event_dialog').modal('hide');
            setTimeout(dp.multirange.clear, 100);
        }
        function event_dialog_clipboard() {
            action_clipboard.forEach(id=>{
                const c=document.getElementById(id);
                if ((!!c) && (c.type==="checkbox"))
                    c.checked=1;
            })
        }
        function event_dialog_clear() {
            jQuery(".event_item").prop("checked", false);
        }
        function prev_actions_for_resource(resource)
        {
            let ret = [];
            events[instruction_index]=dp.events.list;
            for(var i=0;i<=instruction_index;i++)
            {
                events[i].filter((x)=>x["resource"]==resource).map((x)=>x["action"]).forEach(function (aid) {
                    if (!ret.includes(aid))
                        ret.push(aid);
                });
            }
            return ret;
        }
        function get_latest_state_events()
        {
            const max_dt = dp.events.list.map(x=>x.end.ticks).reduce((x,y)=>(x>y?x:y),0);
            return dp.events.list.filter(x=>x.end.ticks==max_dt);
        }
        function next_instruction()
        {
            console.log("next_instruction");
            events[instruction_index]=dp.events.list;
            if (instruction_index+1==instructions.length){
                if (!confirm("You are about to submit the annotations, are you sure ?"))
                    return;
                save();
                return;
            }
            const latest_state_events=get_latest_state_events();
            instruction_index+=1;
            dp.events.list=events[instruction_index];
            set_reference_time_range(latest_state_events);
            expand_resources();
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
            expand_resources();
            dp.update();
            show_instruction();
        }
        function show_instruction()
        {
            let instruction=instructions[instruction_index];
            document.getElementById('modal-instruction').innerHTML=instruction;
            document.getElementById('instruction').innerHTML="<h3>"+(instruction_index+1)+"/"+instructions.length+"</h3>"+instruction;
            document.getElementById('events').value=JSON.stringify(events);
            const el = document.getElementById('next_instruction');
            if (instruction_index+1==instructions.length)
                el.classList.add("last_instruction");
            else
                el.classList.remove("last_instruction");
            jQuery('.scheduler_default_timeheadercol_inner:contains("1")').css('background-color', 'gray')
            jQuery('.scheduler_default_rowheader_inner:contains("Unused")').css('background-color', 'gray')

        }
        function expand_resources()
        {
            let i=0;
            let children=[];
            let active_resources=[];
            for (i=0;i<dp.resources.length;i++)
            {
                children=dp.resources[i].children.map(x=>x.id);
                active_resources=dp.events.list.map(e=>e.resource);
                dp.resources[i].expanded= dp.resources[i].expanded || children.map(c=>active_resources.indexOf(c)).filter(i=>i>-1).length>0;
            }
        }
        function save()
        {
            show_instruction();
            document.forms[0].submit();
            
        }

        var dp = new DayPilot.Scheduler("dp");


        dp.startDate = "2020-01-01";
        const unused_resource_id = "A1";
        const on_start_date = (obj)=>(obj.hasOwnProperty('e')?obj.e.data.start.value.startsWith(dp.startDate):obj.start.value.startsWith(dp.startDate));
        const on_unused = (obj)=>(obj.hasOwnProperty('e')?obj.e.data.resource===unused_resource_id:obj.resource===unused_resource_id);
        dp.days = 5;
        dp.scale = "Day";
        dp.cellWidth=150;
        dp.timeHeaders = [
            //{groupBy: "Month", format: "MMMM yyyy"},
            {groupBy: "Day", format: "d"}
            //{ groupBy: "Hour", format: "H" }
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
                            truncate(args.source.data.resource, args.source.data.start);
                        }
                    }
                },
                {
                    text: "Cut", onClick: function (args) {
                        action_clipboard = dp.multiselect.events().map((x)=>x["data"]["action"]);
                        dp.multiselect.clear();
                        truncate(args.source.data.resource, args.source.data.start);
                    }
                },
                { text: "-" },
                {
                    text: "Paste", onClick: function (args) {
                        const selected_actions=dp.actions.filter(x => action_clipboard.filter((y)=>x.id == y).length>0);
                        add_events_by_action_id(action_clipboard, {
                            "start": args.source.data.start,
                            "end": args.source.data.end,
                            "resource": args.source.data.resource,
                        });
                    }
                },
                /*
                { text: "-" },
                {
                    text: "Select All", onClick: function (args) {
                        const item=args['source']['data'];
                        dp.events.all().filter((x)=>(x["data"]["resource"]==item.resource)&&(x["data"]["start"]==item.start)).forEach(function (e) {
                            dp.multiselect.add(e);
                        });
                    }
                },
                */
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
        dp.allowMultiMove=true;
        dp.allowMultiResize=true;

        dp.events.list = <?=$event0?>;


        dp.eventMovingStartEndEnabled = false;
        dp.eventResizingStartEndEnabled = false;
        dp.timeRangeSelectingStartEndEnabled = false;

        dp.onEventMouseOver = function (args) {
            const hoverEvent = args.e.data;
            dp.multiselect.clear();
            dp.events.all().filter((x)=>(x["data"]["resource"]==hoverEvent.resource)&&(x["data"]["start"]==hoverEvent.start)).forEach(function (e) {
                            dp.multiselect.add(e);
                        });
        }

        // event resizing
        dp.onEventResized = function (args) {
            dp.message("Resized: " + args.e.text());
        };

        // event creating
        dp.onTimeRangeSelected = function (args) {
            if (on_start_date(args))
            {
                msgbox("Reference Time-range cannot be changed", "The first time range is read only and cannot be modified");
                return;
            }
            if (on_unused(args))
            {
                msgbox("Unused ingredients", "Unused Ingredients are populated automatically, there's no need to specify them manually");
                return;
            }
            selected_time_range=args;
            jQuery(".event_item").prop("checked", false);
            const previously_selected = prev_actions_for_resource(args.resource);
            previously_selected.forEach(id=>{
                const c=document.getElementById(id);
                if ((!!c) && (c.type==="checkbox"))
                    c.checked=1;
            })
            jQuery('#event_dialog').modal('show');
        };

        dp.onEventClicked = function (args) {
            if (on_start_date(args))
            {
                msgbox("Reference Time-range cannot be changed", "The first time range is read only and cannot be modified");
                return;
            }
            if (on_unused(args))
            {
                msgbox("Unused ingredients", "Unused Ingredients are populated automatically, there's no need to specify them manually");
                return;
            }
            selected_time_range=args.e.data;
            jQuery(".event_item").prop("checked", false);
            const resource=args.e.data.resource;
            const start=args.e.data.start;
            const end=args.e.data.end;
            const previously_selected = dp.events.list.filter((x)=>(x["resource"]==resource) && (x["start"]==start)).map((x)=>x["action"]);
            previously_selected.forEach(id=>{
                const c=document.getElementById(id);
                if ((!!c) && (c.type==="checkbox"))
                    c.checked=1;
            })
            jQuery('#event_dialog').modal('show');
        };


        // dp.onEventMove = function (args) {
        //     if (args.ctrl) {
        //         var newEvent = new DayPilot.Event({
        //             start: args.newStart,
        //             end: args.newEnd,
        //             text: "Copy of " + args.e.text(),
        //             resource: args.newResource,
        //             id: DayPilot.guid()  // generate random id
        //         });
        //         dp.events.add(newEvent);

        //         // notify the server about the action here

        //         args.preventDefault(); // prevent the default action - moving event to the new location
        //     }
        // };
        expand_resources();
        dp.init();

        dp.scrollTo("2020-01-01");
        alert = console.log;
        let instruction_index=0;
        let instructions=<?=json_encode($data['instructions'])?>;
        let events=<?=json_encode($events)?>;
        let action_clipboard=[];
        let selected_time_range={};
        show_instruction();
        if (dp.events.list.length==0)
        {
            set_reference_time_range();
        }

    </script>


</body>

</html>