$('a[name="delete-button"]').on('click', function(e){
    var $form=$(this).closest('form'); 
    e.preventDefault();
    $('#confirm').modal({ backdrop: 'static', keyboard: false })
        .one('click', '#delete', function() {
            $form.trigger('submit'); // submit the form
        });
});
