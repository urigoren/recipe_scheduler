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

$(document).ready(function () {
    $('#search_ingredients').autocomplete({
        source: "/ingredients_autocomplete",
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
});