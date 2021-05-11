let sequence_id=0;

function name(lst, val) {
    return (lst.filter(x=>x.id==val)[0] || {"name": val})["name"];
}

function refresh_actions(){
    let actions_tbl = $("#actions_tbl").empty();
    let command="";
    let resource="";
    let arg="";
    actions.forEach(item => {
        resource = name(resources, item.resource);
        command = name(commands, item.command);
        arg = name(eval(item.arg_type), item.arg);
        actions_tbl.append("<tr><td> " + item.ts + "</td><td> " + command + "</td>" +
            "<td> " + arg + "</td>" +
            "<td> " + resource + "</td>" +
            "<td><a onclick=\"remove_action(" + item.id + ")\" class=\"delete\" title=\"Delete\" data-toggle=\"tooltip\"><i class=\"material-icons\">&#xE5C9;</i></a></td>" +
            "</tr>");
    });
}
function refresh_ingredients() {
    // Shows cart items to screen, and invokes recipes
    let ingredients_tbl = $("#ingredients_tbl").empty();
    ingredients.forEach(item => {
        ingredients_tbl.append("<tr><td> " + item.name + "</td>" +
            "<td><a onclick=\"remove_ingredient('" + item.id + "')\" class=\"delete\" title=\"Delete\" data-toggle=\"tooltip\"><i class=\"material-icons\">&#xE5C9;</i></a></td>" +
            "</tr>");
    });
    setTimeout(() => $('#search_ingredients').val(""), 100);
}

function add_ingredient(item) {
    // Adds item to cart
    ingredients.push(item);
    refresh_ingredients();
}

function remove_ingredient(id) {
    let actions_diff = 0;
    if (id < 0)
        ingredients = [];
    else {
        ingredients = ingredients.filter(item => item.id != id);
        actions_diff = actions.length;
        actions = actions.filter(item => item.arg != id);
        actions_diff-=actions.length;
    }
    refresh_ingredients();
    if (actions_diff>0)
        refresh_actions();
}

function add_action()
{
    const select_command = document.getElementById("select_command");
    const select_arg = document.getElementById("select_arg");
    const select_resource = document.getElementById("select_resource");
    const txt_ts = document.getElementById("txt_ts");
    if ((select_command.value==="")||(select_arg.value==="")||(select_resource.value===""))
        return;
    actions.push({
        "id": sequence_id,
        "command": select_command.value,
        "ts": parseInt(txt_ts.value),
        "arg": select_arg.value,
        "arg_type": commands.filter(x=>x.id==select_command.value)[0]["arg_type"],
        "resource":select_resource.value
    });
    actions = actions.sort((x,y)=>x.ts-y.ts);
    sequence_id++;
    select_resource.value="";
    select_arg.value="";
    select_command.value="";
    txt_ts.value=1+actions.map(x=>x.ts).reduce((x,y)=>(x>y?x:y),0);
    refresh_actions();
}

function remove_action(id)
{
    if (id < 0)
        actions = [];
    else
        actions = actions.filter(item => item.id != id);
    refresh_actions();
}

function command_change() {
    const command = commands.filter((com)=>com.id==document.getElementById("select_command").value)[0];
    populate_selectbox("select_arg", command["arg_type"]);
}

function populate_selectbox(select, type)
{
    const selectbox = document.getElementById(select);
    selectbox.innerHTML=eval(type).map((x)=>'<option value="'+ x.id +'">' +x.name + '</option>').join("\n");
    selectbox.value="";
}

function simulation_submit() {
    document.getElementById('frm_actions').value=JSON.stringify(actions);
    document.getElementById('frm_ingredients').value=JSON.stringify(ingredients);
    document.getElementById('frm_simulate').submit();
}

function next_instruction()
{
    console.log("next_instruction");
    if (instruction_index+1==instructions.length){
        if (!verify_annotation())
            return;
        if (!confirm("You are about to submit the annotations, are you sure ?"))
            return;
        mturk_submit();
        return;
    }
    instruction_index+=1;
    show_instruction();
}
function prev_instruction()
{
    console.log("prev_instruction");
    if (instruction_index==0)
        return;
    instruction_index-=1;
    show_instruction();
}
function show_instruction()
{
    let instruction=instructions[instruction_index];
    document.getElementById('instruction').innerHTML="<h3><span class=\"label label-info\">"+(instruction_index+1)+"/"+instructions.length+"</span></h3>"+instruction;
    const el = document.getElementById('next_instruction');
    if (instruction_index+1==instructions.length)
        el.classList.add("last_instruction");
    else
        el.classList.remove("last_instruction");
}

function getUrlParam(name) {
  var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
  return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : null;
}

function mturk_submit()
{
    const form = document.getElementById("mturk_form");
    const turk_submit = getUrlParam('turkSubmitTo');
    if (turk_submit) {
        form.action=turk_submit + '/mturk/externalSubmit';
        document.getElementById("assignmentId").value = getUrlParam('assignmentId');
    }
    document.getElementById('frm_actions').value=JSON.stringify(actions);
    document.getElementById('frm_n_actions').value=actions.length;
    document.getElementById('frm_ingredients').value=JSON.stringify(ingredients);
    document.getElementById('frm_seconds_spent').value=JSON.stringify(seconds_spent);
    document.getElementById('frm_msgbox_count').value=JSON.stringify(msgbox_count);
    form.submit();

}
function verify_annotation() {
    const display = (ing)=>ingredients.concat(tools).concat(time_lengths).concat(resources).filter(x=>x.id===ing).map(x=>x.name)[0] || "";
    if (actions.length===0)
    {
        msgbox("Nothing done", "We are sorry, you cannot submit an empty program.");
        return false;
    }
    if (ingredients.length<1)
    {
        msgbox("Nothing done", "We are sorry, you cannot submit an recipe with no ingredients.");
        return false;
    }
    let used_ingredients = {};
    ingredients.forEach(x=>used_ingredients[x.id]=false);
    actions.filter(x=>x.arg_type==="ingredients").forEach(x=>used_ingredients[x.arg]=true);
    const missing_ing = Object.values(used_ingredients).indexOf(false);
    if (missing_ing>=0) {
        msgbox("Unmentioned ingredients",
        "The following ingredients were not used in your program: <br />"+
        display(Object.keys(used_ingredients)[missing_ing])
        );
        return false;
    }

    let ingredient_at_resource = {};
    let mentioned_resources = [];
    ingredients.forEach(x=>ingredient_at_resource[x.id]="");
    tools.forEach(x=>ingredient_at_resource[x.id]="");
    for(i=0;i<actions.length;i++) {
        action = actions[i];
        if ((action.command==0) || (action.command==2)) { //PUT
            if (ingredient_at_resource[actions[i].arg]!="") {
                msgbox("Error on line " + (i+1),
                    "The following ingredient or tool was added despite the fact that it was not removed in a previous instruction<br />"+
                        "<b>"+display(actions[i].arg)+"</b> is still on <b>"+display(ingredient_at_resource[actions[i].arg])+"</b>"+
                    "<br /> Ingredients can only be in a single place simoltanously."
                );
                return false;
            }
            ingredient_at_resource[actions[i].arg]=actions[i].resource;
        }
        if ((action.command==1) || ((action.command==3))) { //REMOVE
            if (ingredient_at_resource[actions[i].arg]=="") {
                msgbox("Error on line " + (i+1),
                    "The following ingredient or tool was removed despite the fact that it was not used previously<br />"+
                        "<b>"+display(actions[i].arg)+"</b>"
                );
                return false;
            }
            ingredient_at_resource[actions[i].arg]="";
        }
        if (action.command==6) { //MOVE_CONTENTS
            if (mentioned_resources.filter(x=>x==actions[i].arg).length===0) {
                msgbox("Error on line " + (i+1),
                    "MOVE_CONTENTS cannot be applied to a resource that was not previously mentioned: <br />"+
                        "<b>"+display(actions[i].arg)+"</b>"
                );
                return false;
            }
        }
        if (action.command==4) { //CHEF_CHECK
            if (mentioned_resources.filter(x=>x==actions[i].resource).length===0) {
                msgbox("Error on line " + (i+1),
                    "CHEF_CHECK cannot be applied to a resource that was not previously mentioned: <br />"+
                    "CHEF_CHECK <b>"+display(actions[i].arg)+"</b> on " +
                        "<b>"+display(actions[i].resource)+"</b> <br />"
                );
                return false;
            }
        }
        mentioned_resources.push(actions[i].resource);
    }
    return true;
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

$(document).ready(function () {
    $("#txt_ts").TouchSpin({
      verticalbuttons: true
    });
    $('#search_ingredients').autocomplete({
        source: ingredients_autocomplete,
        minLength: 2,
        select: function (event, ui) {
            add_ingredient(ui.item.value);
        }
    }).data('ui-autocomplete')._renderItem = function (ul, item) {
        return $("<li class='ui-autocomplete-row'></li>")
            .data("item.autocomplete", item)
            .append(item.label)
            .appendTo(ul);
    };
    populate_selectbox("select_resource", "resources");
    populate_selectbox("select_arg", "resources");
    populate_selectbox("select_command", "commands");
    refresh_ingredients();
    refresh_actions();

    $(document).on("keydown", "form", event=>event.key != "Enter");
    const submitButton = document.getElementById("submitButton");
    if (submitButton){
      submitButton.style.display = "none";
    }
});
