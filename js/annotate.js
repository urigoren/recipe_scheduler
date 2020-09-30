const unused_resource_id = "A1";
const on_start_date = (obj)=>(obj.hasOwnProperty('e')?date(obj.e.data.start).value.startsWith(dp.startDate):date(obj.start).value.startsWith(dp.startDate));
const on_unused = (obj)=>(obj.hasOwnProperty('e')?obj.e.data.resource===unused_resource_id:obj.resource===unused_resource_id);

function msgbox(title, body)
{
    jQuery('#msgbox_title').text(title);
    jQuery('#msgbox_body').html(body);
    jQuery('#msgbox_dialog').modal('show');
}
function date(dt) {
    if (typeof(dt)==="string")
            return DayPilot.Date(dt);
    return dt;
}
function verify_annotation()
{
    let dt = DayPilot.Date(dp.startDate);
    let time_stamps = [];
    let i=0;
    while (dp.events.list.filter(x=>x.start==dt).length>0) {
        time_stamps.splice(0,0,dt);
        dt=dt.addDays(1);
    }
    let next_dt=time_stamps[0];
    let unused=[], next_unused=[], reused_issues=[];
    next_unused=dp.events.list.filter(x=>(x.resource===unused_resource_id)&&(x.start===next_dt)).map(x=>x.action);
    for (i=1;i<time_stamps.length;i++) {
        dt=time_stamps[i];
        unused=dp.events.list.filter(x=>(x.resource===unused_resource_id)&&(x.start===dt)).map(x=>x.action);
        reused_issues=next_unused.filter(x=>unused.indexOf(x)<0);
        if (reused_issues.length>0)
        {
            msgbox("Ingredients cannot be marked as unused", "The following ingredients were marked as unused, despite being used previously:<ul><li>" +
            reused_issues.map(x=>dp.actions.filter(y=>y.id==x)[0].display).join("<li>")+"</ul>");
            return false;
        }
        next_unused=unused;
        next_dt=dt;
    }
    return true;
}
function populate_unused_resource(start)
{
    if (start==dp.startDate)
        return;
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
        event_data.start=date(event_data.start);
        event_data.end=date(event_data.end);
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
    const max_dt = dp.events.list.map(x=>date(x.end).ticks).reduce((x,y)=>(x>y?x:y),0);
    return dp.events.list.filter(x=>(date(x.end).ticks==max_dt) && (!x.action.startsWith('L')));
}
function next_instruction()
{
    console.log("next_instruction");
    events[instruction_index]=dp.events.list;
    if (!verify_annotation())
        return;
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

function onEventClicked(args) {
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
    // checkboxes
    let previously_selected = dp.events.list.filter((x)=>(x["resource"]==resource) && (x["start"]==start)).map((x)=>x["action"]);
    previously_selected.forEach(id=>{
        const c=document.getElementById(id);
        if ((!!c) && (c.type==="checkbox"))
            c.checked=1;
    })
    // selectbox
    const instruction_length_select = document.getElementById("instruction_length");
    previously_selected=previously_selected.filter(x=>x.startsWith('L'));
    instruction_length_select.value=(previously_selected.length>0?previously_selected[0]:"");
    jQuery('#event_dialog').modal('show');
}

function onEventMouseOver(args) {
    const hoverEvent = args.e.data;
    dp.multiselect.clear();
    dp.events.all().filter((x)=>(x["data"]["resource"]==hoverEvent.resource)&&(x["data"]["start"]==hoverEvent.start)).forEach(function (e) {
                    dp.multiselect.add(e);
                });
}

function onTimeRangeSelected(args) {
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
    document.getElementById("instruction_length").value="";
    jQuery('#event_dialog').modal('show');
}