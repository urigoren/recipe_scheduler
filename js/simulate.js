let ingredients= [];

function refresh_ingredients() {
    // Shows cart items to screen, and invokes recipes
    let cart_tbl = $("#ingredients_tbl").empty();
    ingredients.forEach(item => {
        cart_tbl.append("<tr><td> " + item.name + "</td>" +
            "<td><a onclick=\"remove_ingredient('" + item.id + "')\" class=\"delete\" title=\"Delete\" data-toggle=\"tooltip\"><i class=\"material-icons\">&#xE5C9;</i></a></td>" +
            "</tr>");
    });
    setTimeout(() => $('#search_data').val(""), 100);
}

function add_ingredient(item) {
    // Adds item to cart
    ingredients.push(item);
    refresh_ingredients();
}

function remove_ingredient(id) {
    if (id < 0)
        ingredients = [];
    else
        ingredients = ingredients.filter(item => item.id != id);
    refresh_ingredients();
}

$(document).ready(function () {
    $("#ingredients_dialog").dialog({"autoOpen": false, "closeOnEscape": true});
    $('#search_data').autocomplete({
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

});