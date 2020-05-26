// Update these if you're using a different name!
const leftcam = "http://leftcam.local:8080/?action=stream";
const rightcam = "http://rightcam.local:8080/?action=stream";

function switchView(parallel, menuitem) {
  $("#left").attr("src", parallel ? leftcam : rightcam);
  $("#right").attr("src", parallel ? rightcam : leftcam);
  $("#viewDropdown").html(parallel ? "View [Parallel]" : "View [Cross]");
  $("#viewMenu a").removeClass("active");
  $(menuitem).addClass("active");
}

function switchFile(type, menuitem) {
  $("input[name='type']").val(type);
  $("#fileMenu a").removeClass("active");
  $(menuitem).addClass("active");
}
