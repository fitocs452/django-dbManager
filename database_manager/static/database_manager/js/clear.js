$(function() {
    // wire up Add Item button click event
    $("#clear-button").click(function(event) {
        event.preventDefault(); // cancel default behavior
        $("#id_query").val('');
        return false;
    });
});
