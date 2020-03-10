$(document).delegate('.expander','click',function(){
  $(this).toggleClass('expanded')
    .nextAll('ul:first').toggleClass('expanded');    
    $("html").getNiceScroll().resize();
  return true;
});

$(document).delegate('.expander-li','click',function(){
  var exp_element = $(this).next('div');
  $(exp_element).toggleClass('expanded')
    .nextAll('ul:first').toggleClass('expanded');
    $("html").getNiceScroll().resize();
  return true;
});
