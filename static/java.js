'use strict';
function disableScroll(){  
  window.scrollTo(0, 0);
};

$(document).ready(function(){
$(".r1").click(function(){
    $(".r1").addClass('ima1');
   $(".r1").delay(900).queue(function (next) { 
    $(".r1").css('display', 'none'); 
    $("#i1").css("display", "block");
    $("#i1").css({"-webkit-transform": "rotateY(0deg)",  }); 
     next(); 
  });
}),




$(".r2").click(function(){

    $(".r2").addClass('ima2');
   $(".r2").delay(900).queue(function (next) { 
    $(".r2").css('display', 'none'); 
    $("#i2").css("display", "block");
    $("#i2").css({"-webkit-transform": "rotateY(0deg)",  }); 
     next(); 
  });

}),




$(".r3").click(function(){
    $(".r3").addClass('ima3');
   $(".r3").delay(900).queue(function (next) { 
    $(".r3").css('display', 'none'); 
    $("#i3").css("display", "block");
    $("#i3").css({"-webkit-transform": "rotateY(0deg)",  }); 
     next(); 
  });

}),



$(".r4").click(function(){
    $(".r4").addClass('ima4');
   $(".r4").delay(900).queue(function (next) { 
    $(".r4").css('display', 'none'); 
    $("#i4").css("display", "block");
    $("#i4").css({"-webkit-transform": "rotateY(0deg)",  }); 
     next(); 
  });
}),



$(".r5").click(function(){
  $(".r5").addClass('ima5');
  $(".r5").delay(900).queue(function (next) { 
   $(".r5").css('display', 'none'); 
   $("#i5").css("display", "block");
   $("#i5").css({"-webkit-transform": "rotateY(0deg)",  }); 
    next(); 
 });
}),


$(".r6").click(function(){
  $(".r6").addClass('ima6');
  $(".r6").delay(900).queue(function (next) { 
   $(".r6").css('display', 'none'); 
   $("#i6").css("display", "block");
   $("#i6").css({"-webkit-transform": "rotateY(0deg)",  }); 
    next(); 
 });
}),



$("#sobre").click(function(){
  $(".r1").addClass('ima1');
  $(".r2").addClass('ima2');
  $(".r3").addClass('ima3');
  $(".r4").addClass('ima4');
  $(".r5").addClass('ima5');
  $(".r6").addClass('ima6');

  $(".r1").delay(700).queue(function (next) { 
    $(".r1").css('display', 'none'); 
    $("#i1").css("display", "block");
    $("#i1").css({"-webkit-transform": "rotateY(0deg)",  }); 
    $(".r2").css('display', 'none'); 
    $("#i2").css("display", "block");
    $("#i2").css({"-webkit-transform": "rotateY(0deg)",  }); 
    $(".r3").css('display', 'none'); 
    $("#i3").css("display", "block");
    $("#i3").css({"-webkit-transform": "rotateY(0deg)",  }); 
    $(".r4").css('display', 'none'); 
    $("#i4").css("display", "block");
    $("#i4").css({"-webkit-transform": "rotateY(0deg)",  }); 
    $(".r5").css('display', 'none'); 
    $("#i5").css("display", "block");
    $("#i5").css({"-webkit-transform": "rotateY(0deg)",  }); 
    $(".r6").css('display', 'none'); 
    $("#i6").css("display", "block");
    $("#i6").css({"-webkit-transform": "rotateY(0deg)",  }); 
     next(); 
  });

  



})
     
});

