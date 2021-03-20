$("#ShowTargetSchedulebtn").on("click", function () {
  console.log("Entered Show target schedule script");
  console.log($('#uhaveid').val())
  console.log($('#ProjectList option:selected').val())
  $.ajax({
    url: '/schedule/schedule_show_target',
    type: "POST",
    data: {
      PID :$('#ProjectList option:selected').val(),
      uhaveid : $('#uhaveid').val()
    },
    datatype: "json",
    success: function (data) {
      console.log(data);
          //  console.log($('#ProjectList option:selected').val())
      // console.log()
    }
  });
});


$("#Showmap").click(function () {
// this is for pop out a map window
  console.log("Entered Show map script");
  window.open("map.html", "popupWindow", "width=600,height=600,scrollbars=yes");
});
