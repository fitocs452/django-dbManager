function clearContents(element) {
  element.value = '';
}

$(function() // execute once the DOM has loaded
{

  // wire up Add Item button click event
  $("#clear-button").click(function(event)
  {
    event.preventDefault(); // cancel default behavior
    $("#id_query").val('');
    return false;
    //... rest of add logic
  });
});
