$(document).ready(function(){
    $('.table').DataTable({
        searching: true
    });
    $("#alert").animate({
    opacity: 1,
    }, 2000, function() {
        $("#alert").delay(4000).fadeOut();
    });
});