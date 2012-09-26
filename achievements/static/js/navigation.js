$(document).ready(function() {
    // Slide
    $("#menu1 > li > a.expanded + ul").slideToggle("medium");
    $("#menu1 > li > a").click(function() {
        $(this).toggleClass("expanded").toggleClass("collapsed").parent().find('> ul').slideToggle("medium");
    });
});
