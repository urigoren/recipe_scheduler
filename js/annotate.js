const validation_resource_prefix = 'VALID';
const served_resource_id = "SERVE";
const trash_resource_id = "TRASH";
const unused_resource_id = "VALID_UNUSED";
const get_last_timestamp = () => dp.events.list.map(x=>date(x.end).getDayOfYear()-1).reduce((x,y)=>(x>y?x:y),0);
const get_ingredients_at_timestamp = (ts) => dp.events.list.filter(x=>(ts===date(x.end).getDayOfYear()-1) && (ing2type(x.action)===AssignedTypes.INGREDIENT));
const on_start_date = (obj)=>(obj.hasOwnProperty('e')?date(obj.e.data.start).value.startsWith(dp.startDate):date(obj.start).value.startsWith(dp.startDate));
const on_validation_resource = (obj)=>(obj.hasOwnProperty('e')?obj.e.data.resource.startsWith(validation_resource_prefix):obj.resource.startsWith(validation_resource_prefix));
const on_nonconsequent = (obj)=> date(obj.start).getDayOfYear() - get_last_timestamp() > 1;
const compare_events_at_timestamps = (x,y)=>JSON.stringify(dp.events.list.filter(t=>date(t.end).getDayOfYear()-1===x).map(t=>[t.resource,t.action]).sort())===JSON.stringify(dp.events.list.filter(t=>date(t.end).getDayOfYear()-1===y).map(t=>[t.resource,t.action]).sort());
function prev_resource_empty(obj)
{
    if (on_validation_resource(obj))
        return false;
    if (isNaN(obj.resource[obj.resource.length-1])) // not an ordered resource
        return false;
    const parts = obj.resource.match(/([a-zA-Z_]+)(\d+)/);
    const res_base = parts[1];
    const res_num = parts[2];
    const prev_res = res_base +''+ (res_num-1);
    if (flat_resources.filter(r=>r.id===prev_res).length===0) // non existing
        return false;
    return dp.events.list.filter(e=>(e.start===obj.start) && (e.resource===prev_res)).length===0;
}
const clone = (obj)=>Object.assign({},obj);
const display = (action_id)=>dp.actions.filter(x=>x.id===action_id).map(x=>x.display)[0] || "";
const AssignedTypes = {
    INGREDIENT: 0,
    ACTIVITY: 1,
    TIME_LENGTH: 2,
    TOOL: 3,
}
function getUrlParam(name) {
  var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
  return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : null;
}

function append_checkboxes(elid, header, dict) {
    const el= document.getElementById(elid);
    let html = (header?"<h3>" + header + "</h3>":el.innerHTML);
    let v="";
    for (const k in dict) {
        v = dict[k];
        html+='<div class="form-check"><input type="checkbox" class="form-check-input event_item" id="'+k+'"><label class="form-check-label" for="'+k+'">'+v+'</label></div>';
    }
    el.innerHTML=html;
}
function append_options(elid, dict) {
    const el= document.getElementById(elid);
    let html = "";
    let v="";
    for (const k in dict) {
        v = dict[k];
        html+='<option value="'+k+'">'+v+'</option>';
    }
    el.innerHTML=html;
}
function append_li(elid, lst) {
    const el= document.getElementById(elid);
    let html = "";
    let i=0;
    for (i=0;i<lst.length;i++) {
        html+='<li>'+lst[i]+'</li>';
    }
    el.innerHTML=html;
}
function cellColor(args) {
  if ((args.cell.start.getDayOfYear() === 1) || args.cell.resource.startsWith(validation_resource_prefix)) {
    args.cell.backColor = "#e0e0e0";
  }
}
function add_missing_ingredient(item) {
    // This is some seriously messed up code
    const kv=Object.entries(item)[0];
    append_checkboxes("modal_body_ingredients", undefined,item);
    document.getElementById("ul_ingredients").innerHTML+="<li>"+kv[1]+"</li>";
    dp.actions.push({"display": kv[1], "id": kv[0], "color": "#00cc00"});
    setTimeout(() => $('#search_ingredients').val(""), 50);
}
function msgbox(title, body)
{
    const event_dialog_shown = (jQuery("#event_dialog").data('bs.modal') || {})._isShown;
    const msgbox_dialog = jQuery('#msgbox_dialog');
    if (event_dialog_shown)
        msgbox_dialog.css("z-index", 3000);
    else
        msgbox_dialog.css("z-index", "");
    jQuery('#msgbox_title').text(title);
    jQuery('#msgbox_body').html(body);
    msgbox_dialog.modal('show');
    msgbox_count+=1;
}
function ing2type(ing_id) {
    switch (ing_id[0]) {
        case "I": return AssignedTypes.INGREDIENT;
        case "M": return AssignedTypes.ACTIVITY;
        case "L": return AssignedTypes.TIME_LENGTH;
        case "T": return AssignedTypes.TOOL;
        default: return null;
    }
}
function date(dt) {
    if (typeof(dt)==="string")
            return DayPilot.Date(dt);
    return dt;
}
function verify_annotation()
{
    //verify unused ingredients doesn't grow
    const n_ts=get_last_timestamp();
    let i=0;
    let unused=[], next_unused=[], reused_issues=[];
    const last_unused=get_ingredients_at_timestamp(n_ts).filter(x=>x.resource===unused_resource_id).map(x=>x.action);
    next_unused=last_unused;
    for (i=n_ts-1;i>0;i--) {
        unused=get_ingredients_at_timestamp(i).filter(x=>x.resource===unused_resource_id).map(x=>x.action);
        reused_issues=next_unused.filter(x=>unused.indexOf(x)<0);
        if (reused_issues.length>0)
        {
            msgbox("Ingredients cannot be marked as unused", "The following ingredients were marked as unused, despite being used previously:<ul><li>" +
            reused_issues.map(display).join("<li>")+"</ul>");
            return false;
        }
        next_unused=unused;
    }
    // Verify that one resource changes per timestamp
    let prev_list_resources = flat_resources.map(x=>x.id).filter(r=>(!r.startsWith(validation_resource_prefix)) && (r!==trash_resource_id) && (get_ingredients_at_timestamp(2).map(x=>x.resource).indexOf(r)>=0));
    let list_resources = [];
    for (i=2;i<=n_ts;i++) {
        list_resources = flat_resources.map(x=>x.id).filter(r=>(!r.startsWith(validation_resource_prefix)) && (r!==trash_resource_id) && (get_ingredients_at_timestamp(i).map(x=>x.resource).indexOf(r)>=0));
        const newly_added_resources = list_resources.filter(r=>prev_list_resources.indexOf(r)<0);
        if (newly_added_resources.length>1) {
            msgbox("More than one resource introduced at a given timestamp", "At timestamp " + i +
                ", multiple resources were introduced:<ul><li>" +
                newly_added_resources.map(r=> flat_resources.filter(x=>x.id===r)[0]["name"]).join("<li>") +
            "</ul> Please split it into multiple steps");
            return false;
        }
        const modified_resources = list_resources.filter(r=>prev_list_resources.indexOf(r)>=0).filter(r=>
        JSON.stringify(get_ingredients_at_timestamp(i).filter(x=>x.resource===r).map(x => x.action).sort()) !== JSON.stringify(get_ingredients_at_timestamp(i - 1).filter(x=>x.resource===r).map(x => x.action).sort())
        )
        if (modified_resources.length+newly_added_resources.length>1) {
            msgbox("More than one resource modified a given timestamp", "At timestamp " + i +
                ", multiple resources were modified:<ul><li>" +
                modified_resources.concat(newly_added_resources).map(r=> flat_resources.filter(x=>x.id===r)[0]["name"]).join("<li>") +
            "</ul> Please split it into multiple steps");
            return false;
        }
        prev_list_resources = list_resources;
    }
    //verify that what gets put in the trash, stays there
    let prev_trashed=get_ingredients_at_timestamp(1).filter(x=>x.resource===trash_resource_id).map(x=>x.action);
    let trashed=[], untrashed=[];
    for (i=1;i<=n_ts;i++) {
        trashed=get_ingredients_at_timestamp(i).filter(x=>x.resource===trash_resource_id).map(x=>x.action);
        untrashed=prev_trashed.filter(x=>trashed.indexOf(x)<0);
        if (untrashed.length>0)
        {
            msgbox("Ingredients cannot be used after trashed", "The following ingredients were marked as trash, Then reused:<ul><li>" +
            untrashed.map(display).join("<li>")+"</ul>");
            return false;
        }
        prev_trashed=trashed;
    }
    //verify duplicate ingredients
    const ingredients = dp.actions.map(x=>x.id).filter(x=>ing2type(x)===AssignedTypes.INGREDIENT).sort();
    for (let ts=1;ts<=n_ts;ts++) {
        const ing_at_ts = get_ingredients_at_timestamp(ts).filter(x=>!on_validation_resource(x)).map(x=>x.action);
        for (let i=0;i<ingredients.length;i++) {
            const ing = ingredients[i];
            if (ing_at_ts.filter(i => i===ing).length > 1) {
                msgbox("Ingredient used twice at the same time", '"' + display(ing) + "\" was used twice at the same time.");
                return false;
            }
        }
    }
    //verify columns do not repeat themselves
    for (let ts=1;ts<n_ts;ts++) {
        if (compare_events_at_timestamps(ts,ts+1)) {
                msgbox("Column Repetition Detected", "Timestamp "+ts+" seem to be exactly the same as the consequent timestamp.");
                return false;
        }
    }
    //check if substring match an ingredient
    const instruction=instructions[instruction_index].toLowerCase();
    const mentioned_ingredients=ingredients.filter(ing=>instruction.includes(display(ing)));
    const mentioned_unused = last_unused.filter(x=>mentioned_ingredients.indexOf(x)>-1);
    if (mentioned_unused.length>1) {
        msgbox("Ingredient mentioned but not unused", "The following ingredients were mentioned in the instruction, but not used:<ul><li>" +
        mentioned_unused.map(display).join("<li>")+"</ul>");
        return false;
    }
    // validation from `validations` variable
    // const validated_unused = last_unused.filter(x=>validations[instruction_index].indexOf(x)>-1);
    // if (validated_unused.length>0) {
    //     msgbox("Conflict with previous annotation", "The following ingredients should be used in this instruction according to a previous annotator:<ul><li>" +
    //     validated_unused.map(display).join("<li>")+"</ul>");
    //     return false;
    // }
    //verify last instruction
    if (instructions.length===1+instruction_index) // last instruction
    {
        unused=get_ingredients_at_timestamp(n_ts).filter(x=>x.resource===unused_resource_id);
        if (unused.length>0) {
            msgbox("Unused Ingredients", "Last step cannot have unused ingredients");
            return false;
        }
        const served=get_ingredients_at_timestamp(n_ts).filter(x=>((x.resource===served_resource_id)||(x.resource===trash_resource_id)) && (ing2type(x.action)===AssignedTypes.INGREDIENT)).map(x=>x.action).sort();
        if (JSON.stringify(ingredients)!=JSON.stringify(served)) {
            msgbox("Dish Not Served", "The last step should be serving the dish.<br />Some ingredients were not served or trashed.");
            return false;
        }
    }
    return true;
}
function populate_unused_resource(start)
{
    if (start==dp.startDate)
        return;
    truncate(unused_resource_id, start);
    const used_ingredients = dp.events.list.filter(x=>x.start==start).map(x=>x.action);
    if (used_ingredients.length===0)
        return;
    const unused_ingredients = dp.actions.map(a=>a.id).filter(a=>ing2type(a)==AssignedTypes.INGREDIENT).filter(a=>(used_ingredients.filter(x=>x===a)).length===0);
    add_events_by_action_id(unused_ingredients, {"start": start, "resource": unused_resource_id});
}
function populate_mixtures() {
    const res_prefix = "VALID_MIX";
    const cmap = get_clustered_ingredients();
    for(let day_i=0;day_i<cmap.length;day_i++) {
        const start=dp.startDate.addDays(day_i);
        let mix_i=0;
        let clusters ={};
        for (let ing_id in cmap[day_i])
        {
            const ing_cluster = cmap[day_i][ing_id];
            if (clusters.hasOwnProperty(ing_cluster))
                clusters[ing_cluster].push(ing_id);
            else
                clusters[ing_cluster]=[ing_id];
        }
        for (let ing_cluster in clusters)
        {
            if (clusters[ing_cluster].length>1){
                mix_i+=1;
                const res=res_prefix + '' + (mix_i);
                if (flat_resources.filter(r=>r.id===res).length>0) {
                    add_events_by_action_id(clusters[ing_cluster], {
                        "start": start,
                        "resource": res
                    });
                }
            }
        }
    }
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
    if (!on_validation_resource(event_data)) {
        populate_unused_resource(event_data.start);
        populate_mixtures();
    }

}
function set_reference_time_range(latest_events)
{
    if  ((typeof latest_events === "undefined") || (latest_events.length==0))
    {
        // use all ingredients, set as unused
        latest_events=dp.actions.filter(a=>ing2type(a.id)===AssignedTypes.INGREDIENT).map(a=>({
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
    populate_mixtures();
}
function truncate(resource, start)
{
    if  (typeof start === "undefined")
        start=DayPilot.Date(dp.startDate);
    let i=0;
    dp.events.list.filter((x)=>(x["resource"]==resource) && (x["start"]==start)).forEach((e)=>{
        dp.events.removeById(e.id);
    });
    if (resource!==unused_resource_id)
        populate_unused_resource(start);
}
function event_dialog_save()
{
    const selected_action_ids=jQuery(".event_item").filter((i,v)=>v.checked).map((i,v)=>v.id).toArray();
    const instruction_length_id = document.getElementById("instruction_length").value;
    //Verify annotations contains tools
    let only_tools = true;
    for(let i=0;i<selected_action_ids.length;i++) {
        only_tools = only_tools && (ing2type(selected_action_ids[i])!==AssignedTypes.INGREDIENT);
    }
    if (only_tools && (selected_action_ids.length>0))
    {
        msgbox("No ingredients marked", "There's no need to mark steps that do not contain ingredients <ul>" +
            "<li>If the tools you chose contain ingredients within them, please mark them.</li>"+
            "<li>Otherwise, do not mark anything.</li>" +
            "</ul>"
        );
        return;
    }
    //Verify clusters
    for(let i=0;i<selected_action_ids.length;i++)
    {
        if (ing2type(selected_action_ids[i])!==AssignedTypes.INGREDIENT)
            continue;
        const ing=selected_action_ids[i];
        const sel_cluster_count= selected_action_ids.filter(x=>clustered_ingredients[ing]===clustered_ingredients[x]).length;
        let cluster_count=0;
        for (let j in clustered_ingredients)
        {
            cluster_count += (clustered_ingredients[ing]==clustered_ingredients[j]?1:0);
        }
        if (sel_cluster_count < cluster_count) {
            if (confirm("Some ingredients were merged in the past, and must be selected\n\nWould you like to auto-correct ?")) {
                for (let j in clustered_ingredients)
                {
                    if (clustered_ingredients[ing]==clustered_ingredients[j])
                    {
                        document.getElementById(j).checked=true;
                    }
                }
            }
            return;
        }
    }
    // Update events
    truncate(selected_time_range.resource, selected_time_range.start);
    add_events_by_action_id(selected_action_ids, {
        "start": selected_time_range.start,
        "end:": selected_time_range.end,
        "resource": selected_time_range.resource,
    });
    //instruction length special event:
    if (instruction_length_id!="") {
        add_events_by_action_id([instruction_length_id], {
            "start": selected_time_range.start,
            "end:": selected_time_range.end,
            "resource": selected_time_range.resource,
        });
    }
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
    const max_dt = get_last_timestamp();
    return dp.events.list.filter(x=>(date(x.end).getDayOfYear()-1==max_dt) && (ing2type(x.action)!==AssignedTypes.TIME_LENGTH));
}
function get_clustered_ingredients()
{
    let ingredients_cluster={}, i=0, j=0;
    dp.actions.map(x=>x.id).filter(x=>ing2type(x)===AssignedTypes.INGREDIENT).sort().forEach(x=>{ingredients_cluster[x]=i;i++;});
    let ret=[];
    let merged_ingredients={};
    const mergers=flat_resources.filter(x=>x.merger).map(x=>x.id);
    const n_ts=get_last_timestamp();
    for (let ts=1;ts<=n_ts;ts++)
    {
        merged_ingredients={}
        get_ingredients_at_timestamp(ts).filter(x=>mergers.indexOf(x.resource)>-1).forEach(x=>{merged_ingredients[x.resource]=(merged_ingredients[x.resource]||[]).concat([x.action]);});
        for (i in merged_ingredients)
        {
            const merged_in_res=merged_ingredients[i].sort();
            if (merged_in_res.length<2)
                continue
            const new_cluster=ingredients_cluster[merged_in_res[0]];
            for(j=0;j<merged_ingredients[i].length;j++)
            {
                ingredients_cluster[merged_ingredients[i][j]]=new_cluster;
            }
        }
        ret.push(clone(ingredients_cluster));
    }
    return ret;
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
    document.getElementById('instruction').innerHTML="<h3><span class=\"label label-info\">"+(instruction_index+1)+"/"+instructions.length+"</span></h3>"+instruction;
    document.getElementById('frm_events').value=JSON.stringify(events);
    const el = document.getElementById('next_instruction');
    if (instruction_index+1==instructions.length)
        el.classList.add("last_instruction");
    else
        el.classList.remove("last_instruction");
    jQuery('.scheduler_default_timeheadercol_inner:contains("1")').css('background-color', 'gray')
    jQuery('.scheduler_default_rowheader_inner:contains("Unused")').css('background-color', 'gray')
    // renumerate time headers
    let last_dt_idx=0, i=0;
    while (i<instruction_index)
    {
        last_dt_idx += events[i].map(x=>date(x.start).getDayOfYear()-1).reduce((x,y)=>(x>y?x:y),0);
        i++;
    }
    document.querySelectorAll(".scheduler_default_timeheader_cell_inner").forEach((e,i)=>{e.innerHTML=last_dt_idx+i;});
}
function expand_resources()
{
    let i=0;
    let children=[];
    let active_resources=[];
    for (i=0;i<dp.resources.length;i++)
    {
        if (!dp.resources[i].children)
            continue;
        children=dp.resources[i].children.map(x=>x.id);
        active_resources=dp.events.list.map(e=>e.resource);
        dp.resources[i].expanded= dp.resources[i].expanded || children.map(c=>active_resources.indexOf(c)).filter(i=>i>-1).length>0;
    }
}
function save()
{
    const form = document.getElementById("mturk_form");
    const turk_submit = getUrlParam('turkSubmitTo');
    if (turk_submit) {
        form.action=turk_submit + '/mturk/externalSubmit';
        document.getElementById("assignmentId").value = getUrlParam('assignmentId');
    }
    document.getElementById('frm_events').value=JSON.stringify(events);
    document.getElementById('frm_msgbox_count').value=JSON.stringify(msgbox_count);
    document.getElementById('frm_seconds_spent').value=JSON.stringify(seconds_spent);
    form.submit();

}
function status_updated() {
    const feedback = document.getElementById("frm_feedback_grp");
    const status = document.getElementById("frm_status");
    feedback.style.display=(status.value>=0?"none":"block");
    console.log("status_updated " +status.value);
}
function onEventClicked(args) {
    if (on_start_date(args))
    {
        msgbox("Reference Time-range cannot be changed", "The first time range is read only and cannot be modified");
        return;
    }
    if (on_validation_resource(args))
    {
        msgbox("Validation Resource cannot be modified", "Validation resources (such as Unused Ingredients) are populated automatically, there's no need to specify them manually");
        return;
    }
    selected_time_range=args.e.data;
    clustered_ingredients=get_clustered_ingredients()[date(selected_time_range.start).getDayOfYear()-2];
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
    previously_selected=previously_selected.filter(x=>ing2type(x)==AssignedTypes.TIME_LENGTH);
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
    if (on_validation_resource(args))
    {
        msgbox("Validation Resource", "Validation resources (such as Unused Ingredients) are populated automatically, there's no need to specify them manually");
        return;
    }
    if (on_nonconsequent(args))
    {
        msgbox("Skipped a timeframe ?", "Time frames (columns) must be consequent, skipping is not allowed.");
        return;
    }
    if (prev_resource_empty(args))
    {
        msgbox("Numbered resources must be set in order", "This resource has multiple instances, please use them in order (1 before 2, 2 before 3, etc...)");
        return;
    }
    if ((args.resource==served_resource_id) && (instruction_index<instructions.length-1))
    {
        msgbox("Cannot Serve", "You cannot serve the dish just yet, this is not the last instruction.");
        return;
    }
    selected_time_range=args;
    clustered_ingredients=get_clustered_ingredients()[selected_time_range.start.getDayOfYear()-2];
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
