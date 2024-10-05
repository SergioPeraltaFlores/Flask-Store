'use strict';
function disableScroll(){
  window.scrollTo(0, 0);
}
$(document).ready(function(){

  $("#que_es").click(function(){
    $("#elemento1").css("display", "block");
    $("#elemento2").css("display", "None");
    $("#elemento3").css("display", "None");
    $("#elemento4").css("display", "None");
    $("#elemento5").css("display", "None");
    $("#elemento6").css("display", "None");
  });

  $("#acerca_de_juego").click(function(){
    $("#elemento1").css("display", "none");
    $("#elemento2").css("display", "block");
    $("#elemento3").css("display", "none");
    $("#elemento4").css("display", "none");
    $("#elemento5").css("display", "none");
    $("#elemento6").css("display", "none");
  });

  $("#Leer_cartas").click(function(){
    $("#elemento1").css("display", "none");
    $("#elemento2").css("display", "none");
    $("#elemento3").css("display", "block");
    $("#elemento4").css("display", "none");
    $("#elemento5").css("display", "none");
    $("#elemento6").css("display", "none");
  });

  $("#Tipos_de_cartas").click(function(){
    $("#elemento1").css("display", "none");
    $("#elemento2").css("display", "none");
    $("#elemento3").css("display", "none");
    $("#elemento4").css("display", "block");
    $("#elemento5").css("display", "none");
    $("#elemento6").css("display", "none");
  });

  $("#Tablero").click(function(){
    $("#elemento1").css("display", "none");
    $("#elemento2").css("display", "none");
    $("#elemento3").css("display", "none");
    $("#elemento4").css("display", "none");
    $("#elemento5").css("display", "block");
    $("#elemento6").css("display", "none");
  });

  $("#Como_jugar").click(function(){
    $("#elemento1").css("display", "none");
    $("#elemento2").css("display", "none");
    $("#elemento3").css("display", "none");
    $("#elemento4").css("display", "none");
    $("#elemento5").css("display", "none");
    $("#elemento6").css("display", "block");
  });

});
