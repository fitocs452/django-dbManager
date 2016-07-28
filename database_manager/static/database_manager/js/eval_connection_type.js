$(window).bind("load", function() {
    $("#id_collection").css('visibility', 'hidden');
    $("label[for='id_collection']").css('visibility', 'hidden');
});
$('html').on('change', '#id_type', function(){
    var text = $(this).find('option:selected').text();
    if (text === 'Mongo') {
        $("#id_collection").css('visibility', 'visible');
        $("label[for='id_collection']").css('visibility', 'visible');
    } else if (text === 'MySQL') {
        $("#id_collection").css('visibility', 'hidden');
        $("label[for='id_collection']").css('visibility', 'hidden');
    }
});
