'use strict';


// THEME COLORS
var style = getComputedStyle(document.body);
var chartColors = ["#696ffb", "#7db8f9", "#05478f", "#00cccc", "#6CA5E0", "#1A76CA"];
var primaryColor = style.getPropertyValue('--primary');
var secondaryColor = style.getPropertyValue('--secondary');
var successColor = style.getPropertyValue('--success');
var warningColor = style.getPropertyValue('--warning');
var dangerColor = style.getPropertyValue('--danger');
var infoColor = style.getPropertyValue('--info');
var darkColor = style.getPropertyValue('--dark');


// BODY ELEMENTS
var Body = $("body");
var TemplateSidebar = $('.sidebar');
var TemplateHeader = $('.t-header');
var PageContentWrapper = $(".page-content-wrapper");
var DesktopToggler = $(".t-header-desk-toggler");
var MobileToggler = $(".t-header-mobile-toggler");

// SIDEBAR TOGGLE FUNCTION FOR MOBILE (SCREEN "MD" AND DOWN)
MobileToggler.on("click", function () {
  $(".page-body").toggleClass("sidebar-collpased");
});


// CHECK FOR CURRENT PAGE AND ADDS AN ACTIVE CLASS FOR TO THE ACTIVE LINK
var current = location.pathname.split("/").slice(-1)[0].replace(/^\/|\/$/g, '');
$('.navigation-menu li a', TemplateSidebar).each(function () {
  var $this = $(this);
  if (current === "") {
    //FOR ROOT URL
    if ($this.attr('href').indexOf("index.html") !== -1) {
      $(this).parents('li').last().addClass('active');
      if ($(this).parents('.navigation-submenu').length) {
        $(this).addClass('active');
      }
    }
  } else {
    //FOR OTHER URL
    if ($this.attr('href').indexOf(current) !== -1) {
      $(this).parents('li').last().addClass('active');
      if ($(this).parents('.navigation-submenu').length) {
        $(this).addClass('active');
      }
      if (current !== "index.html") {
        $(this).parents('li').last().find("a").attr("aria-expanded", "true");
        if ($(this).parents('.navigation-submenu').length) {
          $(this).closest('.collapse').addClass('show');
        }
      }
    }
  }
});

$(".btn.btn-refresh").on("click", function () {
  $(this).addClass("clicked");
  setTimeout(function () {
    $(".btn.btn-refresh").removeClass("clicked");
  }, 3000);
});


$(".btn.btn-like").on("click", function () {
  $(this).toggleClass("clicked");
  $(this).find("i").toggleClass("mdi-heart-outline clicked").toggleClass("mdi-heart");
});

$("#profileEditBtn").on("click", function(){
  if($(this).hasClass("btn-success")){
    $(this).removeClass("btn-success");
    $(this).addClass("btn-danger");
    $(this).html(`<i class="mdi mdi mdi-pencil-off mr-2" id="profileEditIcon"></i>Cancel`);
    $("#profileFieldset").removeAttr("disabled");
    $("#profileSubmitBtn").css({display: "block"});
  }
  else{
    $(this).removeClass("btn-danger");
    $(this).addClass("btn-success");
    $(this).html(`<i class="mdi mdi mdi-pencil mr-2" id="profileEditIcon"></i>Edit`);
    $("#profileFieldset").attr('disabled', 'disabled');
    $("#profileSubmitBtn").css({display: "none"});
  }

});

$("#addEquipmentBtn").on("click", function(){
  $("#addEquipmentForm").css({display: "block"});
  $("#addEquipmentBtn").css({display: "none"});
});

$("#cancelAddEquipment").on("click", function(){
  $("#addEquipmentForm").css({display: "none"});
  $("#addEquipmentBtn").css({display: "block"});
});

$(".showEquipmentBtn").on("click",function(){
  $(this).next().children().eq(0).css({display: "block"});
  $(this).css({display: "none"});
  $(this).nextAll().eq(1).css({display: "block"});
});

$(".hideEquipmentBtn").on("click",function(){
  $(this).prev().children().eq(0).css({display: "none"});
  $(this).css({display: "none"});
  $(this).prevAll().eq(1).css({display: "block"});
});

$(".editEquipmentBtn").on("click",function(){
  $(this).parent().prev().children().eq(0).find(".showEquipmentBtn").next().removeAttr('disabled');
  $(this).parent().prev().children().eq(0).find(".showEquipmentBtn").prev().removeAttr('disabled');
  if($(this).parent().prev().children().eq(0).find(".showEquipmentBtn").css('display')!="none"){
    $(this).parent().prev().children().eq(0).find(".showEquipmentBtn").click();
    $(this).parent().prev().children().eq(0).find(".hideEquipmentBtn").css({display: "none"});
  }
  else{
    $(this).parent().prev().children().eq(0).find(".hideEquipmentBtn").css({display: "none"});
  }
  $(this).css({display: "none"});
  $(this).parent().prev().children().eq(0).find(".deleteEquipmentBtn").css({display: "inline"})
  $(this).nextAll().eq(1).css({display: "none"})
  $(this).next().css({display: "block"})
  $(this).parent().prev().children().eq(0).find(".saveEquipmentBtn").css({display: "inline"})
});

$(".cancelEquipmentBtn").on("click", function(){
  $(this).parent().prev().children().eq(0).find(".showEquipmentBtn").next().attr('disabled','disabled');
  $(this).parent().prev().children().eq(0).find(".showEquipmentBtn").prev().attr('disabled','disabled');
  $(this).parent().prev().children().eq(0).find(".hideEquipmentBtn").css({display: "block"});
  $(this).parent().prev().children().eq(0).find(".showEquipmentBtn").css({display: "block"});
  $(this).parent().prev().children().eq(0).find(".hideEquipmentBtn").click();
  $(this).css({display: "none"});
  $(this).parent().prev().children().eq(0).find(".deleteEquipmentBtn").css({display: "none"});
  $(this).prev().css({display: "block"});
  $(this).parent().prev().children().eq(0).find(".saveEquipmentBtn").css({display: "none"});
  $(this).next().css({display: "block"});
});

$("#saveEquipmentBtn").on("click", function(){
  $("#showEquipmentBtn").next().attr('disabled','disabled');
  $("#showEquipmentBtn").prev().attr('disabled','disabled');
  $("#hideEquipmentBtn").css({display: "block"});
  $("#showEquipmentBtn").css({display: "block"});
  $("#hideEquipmentBtn").click();
  $(this).css({display: "none"});
  $("#deleteEquipmentBtn").css({display: "block"});
  $("#editEquipmentBtn").css({display: "block"});
  $("#cancelEquipmentBtn").css({display: "none"});
  $("#scheduleEquipmentBtn").css({display: "block"});
});

$("#addProjectBtn").on("click", function(){
  $("#addProjectForm").css({display: "block"});
  $("#addProjectBtn").css({display: "none"});
});

$("#cancelAddProject").on("click", function(){
  $("#addProjectForm").css({display: "none"});
  $("#addProjectBtn").css({display: "block"});
});

$(".getTargetInfo").on("click", function(){
  var pid = $(this).parent().parent().parent().parent().parent().find('input[name = "PID"]').val();
  if($(this).parent().parent().next().children().length==0){
    var element = $(this).parent().parent().next();
      $(element).append(`<div class="table-wrapper col-12">
      <table class="table">
        <thead>
          <tr>
            <th>Target Name</th>
            <th>Latitude</th>
            <th>Longitude</th>
          </tr>
        </thead>
        <tbody>
        </tbody>
      </table>
    </div>`);
    element = $(element).find("tbody");
    $.ajax({
      url: '/getTargetInfo',
      type: "POST",
      data: {
          PID: pid
      },
      dataType: "json",
      success: function (data) {
        $.each(data["project_targets"], function(i, item) {
          $(element).append(`<tr><td>`+item.name+`</td><td>`+item.lat+`</td><td>`+item.lon+`</td></tr>`);
        });
      },
      error: function (error) {
          console.log(error);
      }
    
    });
  }

});

$(".getTargetProjectInfo").on("click", function(){
  var pid = $(this).parent().parent().parent().parent().parent().find('input[name = "PID"]').val();
  if($(this).parent().parent().next().children().length==0){
    var element = $(this).parent().parent().next();
      $(element).append(`<div class="table-wrapper col-12">
      <table class="table">
        <thead>
          <tr>
            <th>Target Name</th>
            <th>Latitude</th>
            <th>Longitude</th>
          </tr>
        </thead>
        <tbody>
        </tbody>
      </table>
    </div>`);
    element = $(element).find("tbody");
    $.ajax({
      url: '/getTargetForProjectInfo',
      type: "POST",
      data: {
          PID: pid
      },
      dataType: "json",
      success: function (data) {
        $.each(data["project_targets"], function(i, item) {
          $(element).append(`<tr><td>`+item.name+`</td><td>`+item.lat+`</td><td>`+item.lon+`</td></tr>`);
        });
      },
      error: function (error) {
          console.log(error);
      }
    
    });
  }

});


$(".getPMInfo").on("click", function(){
  var pid = $(this).parent().parent().parent().parent().parent().find('input[name = "PID"]').val();
  console.log("PID: "+pid);
  if($(this).parent().parent().next().children().length==0){
    var element = $(this).parent().parent().next();
    $.ajax({
      url: '/getPMInfo',
      type: "POST",
      data: {
          PID: pid
      },
      dataType: "json",
      success: function (data) {
        $.each(data["project_manager"], function(i, item) {
          $(element).append(`<div class="card-body">
          <dl class="form-group row showcase_row_area">
            <dt class="col-auto">Name: 
            </dt>
            <dd class="col-auto">
              `+item.name+`
            </dd>
            <dt class="col-auto">
              Affiliation:
            </dt>
            <dd class="col-auto">
              `+item.affiliation+`
              
            </dd>
            <dt class="col-auto">
              Title:
            </dt>
            <dd class="col-auto">
              `+item.title+`
              
            </dd>
          </dl>
        </div>`);
        });
      },
      error: function (error) {
          console.log(error);
      }
    
    });
  }

});

function toTitleCase(str) {
  return str.replace(/(?:^|\s)\w/g, function(match) {
      return match.toUpperCase();
  });
}

function toYesorNo(str){
  if(str.toLowerCase(str)=="y"){
    return "Yes";
  }else{
    return "No";
  }
}

$(".getJoinedEquipmentInfo").on("click", function(){
  var pid = $(this).parent().parent().parent().parent().parent().find('input[name = "PID"]').val();
  if($(this).parent().parent().next().children().length==0){
    var element = $(this).parent().parent().next();
    $.ajax({
      url: '/getJoinedEquipmentInfo',
      type: "POST",
      data: {
          PID: pid
      },
      dataType: "json",
      success: function (data) {
        console.log(data["project_equipments"].length);
        if(data["project_equipments"].length == 0){
          $(element).append(`<div class="alert alert-warning fade show" role="alert">No one has joined this project yet</div>`);
        } else {
          $(element).append(`<div class="table-wrapper col-12">
      
    </div>`);
    element = $(element).find(".table-wrapper");
         $.each(data["project_equipments"], function(i, item) {
           $(element).append(`<div class="pl-3 pt-2"><p><strong>Equipment Number `+parseInt(i+1)+` Details</strong></p></div>
           <div class="pl-5">
           <div class="form-group row showcase_row_area">
           <div class="col-md-4"> 
               <label for="siteInput">Aperture: </label>
               <label type="text">`+item.aperture+`</label>
             </div>
             <div class="col-md-4"> 
               <label for="trackingInput">Tracking Accuracy: </label>
              <label type="text">`+item.accuracy+`</label>
             </div>
             <div class="col-md-4"> 
               <label for="mountSelect">Mount Type: </label>
             <label type="text">`+toTitleCase(item.mount_type)+`</label>
             </div>  
           </div>
           <div class="form-group row showcase_row_area"> 
           <div class="col-md-4"> 
               <label for="fovInput">FoV: </label>
             <label type="text">`+item.Fov+`</label>
            </div> 
            <div class="col-md-4"> 
               <label for="limitingInput">Limiting Magnitude: </label>
              <label type="text">`+item.lim_magnitude+`</label>
             </div> 
             <div class="col-md-4"> 
               <label for="pxInput">Pixel Scale: </label>
              <label type="text">`+item.pixel_scale+`</label>
             </div>
           </div>
           <div class="form-group row showcase_row_area">
           <div class="col-md-4"> 
               <label for="elevationInput">Elevation Limit: </label>
             <label type="text">`+item.elevation_lim+`</label>
             </div>     
             <div class="col-md-4"> 
               <label for="cameraInput">Camera Type: </label>
             <label type="text">`+toTitleCase(item.camera_type1)+`, `+toTitleCase(item.camera_type2)+`</label>
             </div>                     
           </div>
           <div class="form-group row showcase_row_area">
           <div class="col-md-3">
               <label for="johnsonBInput">Johnson B:</label>
                <label type="text">`+toYesorNo(item.JohnsonB)+`</label>
             </div>
             <div class="col-md-3">
               <label for="johnsonVInput">Johnson V:</label>
             <label type="text">`+toYesorNo(item.JohnsonV)+`</label>
             </div> 
             <div class="col-md-3">
               <label for="johnsonRInput">Johnson R:</label>
             <label type="text">`+toYesorNo(item.JohnsonR)+`</label>
             </div>
             <div class="col-md-3">
             <label for="sdssuInput">SDSS u: </label>
             <label type="text">`+toYesorNo(item.SDSSu)+`</label>
             </div>
           </div>
           <div class="form-group row showcase_row_area">                  
           <div class="col-md-3">
               <label for="sdssgInput">SDSS g: </label>
             <label type="text">`+toYesorNo(item.SDSSg)+`</label>
             </div>
             <div class="col-md-3">
               <label for="sdssrInput">SDSS r: </label>
             <label type="text">`+toYesorNo(item.SDSSr)+`</label>
             </div> 
             <div class="col-md-3">
             <label for="sdssiInput">SDSS i: </label>
             <label type="text">`+toYesorNo(item.SDSSi)+`</label>
             </div>
             <div class="col-md-3"> 
             <label for="sdsszInput">SDSS z: </label>
             <label type="text">`+toYesorNo(item.SDSSz)+`</label>
             </div>                
           </div></div><hr>`);
              
         });
        }
      },
      error: function (error) {
          console.log(`Error ${error}`);
      }
    
    });
  }

});

$(".joinProject").on("click", function(){

  var pid = $(this).parent().parent().prevAll().eq(3).children().eq(0).val();
  var element = $(this).parent().parent().parent();
  $.ajax({
    url: '/joinProject',
    type: "POST",
    data: {
        PID: pid
    },
    dataType: "json",
    success: function (data) {
      if(data["error"]){
        $(element).parent().prepend(`<div class="alert alert-warning alert-dismissible fade show" role="alert">`+data["error"]+`<button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`);
      }else{
        $(element).parent().prepend(`<div class="alert alert-success alert-dismissible fade show" role="alert">`+data["success"]+`<button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`);
    $(element).next().remove();
    $(element).remove();
        
      }
        
    },
    error: function (error) {
        console.log(error);
    }
});

});

$("#submitsearchTargetbtn").on("click", function(){
  console.log("Entered search button script");
  $("#targetDataList").html("");
  $.ajax({
    url: '/projects/search',
    type: "POST",
    data: {
        search: $("#targetSearchInput").val()
    },
    dataType: "json",
    success: function (data) {
      if(data["target"].length){
        $.each(data["target"], function(i, item) {
          $("#targetDataList").append($("<option>").attr('value', item.name));
        });;
      }      
    },
    error: function (error) {
        console.log(error);
    }
});

});

$("#selectTargetbtn").on("click", function(){
  $.ajax({
    url: '/projects/targetDetails',
    type: "POST",
    data: {
        targetName: $("#inputTargetDataList").val()
    },
    dataType: "json",
    success: function (data) {
      console.log(data);
      var targetDetails = data["targetDetails"][0];
      var element = `<div class="col-11 targetProjectAddList">
      <fieldset disabled class="mb-3">
        <div class="form-group row showcase_row_area">
          <div class="col-md-3 showcase_text_area">
            <label for="showSelectTargetName">Target Name</label>
          </div>
          <div class="col-md-9 showcase_content_area">
            <input id="showSelectTargetName"  type="text" class="form-control"  placeholder="Target Name" value="`+$("#inputTargetDataList").val()+`">
          </div>                         
        </div>
        <input type="hidden" id="hiddenSelectTargetID" type="number"  name="TID" value="`+targetDetails.TID+`">
        <div class="form-group row showcase_row_area">              
          <div class="col-md-3 showcase_text_area">
            <label for="showSelectTargetRA">Target RA (Longitude)</label>
          </div>
          <div class="col-md-9 showcase_text_area">
            <input id="showSelectTargetRA" type="text" class="form-control" value="`+targetDetails.ra+`" >
          </div>
        </div>

        <div class="form-group row showcase_row_area">              
          <div class="col-md-3 showcase_text_area">
            <label for="showSelectTargetDec">Target Dec (Latitude)</label>
          </div>
          <div class="col-md-9 showcase_text_area">
            <input id="showSelectTargetDec" type="text" class="form-control" value="`+targetDetails.dec+`" >
          </div>
        </div>
      </fieldset>
      <p class="text-left">Equipment Requirement for this Target</p>                  
      <div class="form-group row showcase_row_area"><span class="col-12" style="border-bottom: 1px solid grey;"></span></div>

      <div class="form-group row showcase_row_area">
        <div class="col-md-2 showcase_text_area">
          <label for="johnsonBforTargetInput">Johnson B</label>
        </div>
        <div class="col-md-2 showcase_content_area">
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="Johnson_B`+targetDetails.TID+`" value="Yes">
          <label class="form-check-label" for="johnsonBYes">Yes</label>
        </div>
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="Johnson_B`+targetDetails.TID+`"  value="No">
          <label class="form-check-label" for="johnsonBNo">No</label>
        </div>
        </div>
        <div class="col-md-2 showcase_text_area">
          <label for="johnsonVforTargetInput">Johnson V</label>
        </div>
        <div class="col-md-2 showcase_content_area">
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="Johnson_V`+targetDetails.TID+`" value="Yes">
          <label class="form-check-label" for="johnsonVYes">Yes</label>
        </div>
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="Johnson_V`+targetDetails.TID+`" value="No">
          <label class="form-check-label" for="johnsonVNo">No</label>
        </div>
        </div> 
        <div class="col-md-2 showcase_text_area">
          <label for="johnsonRforTargetInput">Johnson R</label>
        </div>
        <div class="col-md-2 showcase_content_area">
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="Johnson_R`+targetDetails.TID+`"  value="Yes">
          <label class="form-check-label" for="johnsonRYes">Yes</label>
        </div>
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="Johnson_R`+targetDetails.TID+`"  value="No">
          <label class="form-check-label" for="johnsonRNo">No</label>
        </div>
        </div>
      </div>

      <div class="form-group row showcase_row_area">  
        <div class="col-md-2 showcase_text_area">
          <label for="sdssuTargetInput">SDSS u</label>
        </div>
        <div class="col-md-2 showcase_content_area">
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_u`+targetDetails.TID+`" value="Yes">
          <label class="form-check-label" for="sdssuYes">Yes</label>
        </div>
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_u`+targetDetails.TID+`" value="No">
          <label class="form-check-label" for="sdssuNo">No</label>
        </div>
        </div>          
        <div class="col-md-2 showcase_text_area">
          <label for="sdssgTargetInput">SDSS g</label>
        </div>
        <div class="col-md-2 showcase_content_area">
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_g`+targetDetails.TID+`" value="Yes">
          <label class="form-check-label" for="sdssgYes">Yes</label>
        </div>
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_g`+targetDetails.TID+`"  value="No">
          <label class="form-check-label" for="sdssgNo">No</label>
        </div>
        </div>
        <div class="col-md-2 showcase_text_area">
          <label for="sdssrTargetInput">SDSS r</label>
        </div>
        <div class="col-md-2 showcase_content_area">
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_r`+targetDetails.TID+`"  value="Yes">
          <label class="form-check-label" for="sdssrYes">Yes</label>
        </div>
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_r`+targetDetails.TID+`"  value="No">
          <label class="form-check-label" for="sdssrNo">No</label>
        </div>
        </div>                  
      </div>

      <div class="form-group row showcase_row_area ">
        <div class="col-md-2 showcase_text_area">
          <label for="sdssiTargetInput">SDSS i</label>
        </div>
        <div class="col-md-2 showcase_content_area ">
        <div class="form-check form-check-inline mb-1 ">
          <input class="form-check-input" type="radio" name="SDSS_i`+targetDetails.TID+`"  value="Yes">
          <label class="form-check-label" for="sdssiYes">Yes</label>
        </div>
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_i`+targetDetails.TID+`" value="No">
          <label class="form-check-label" for="sdssiNo">No</label>
        </div>
        </div>

        <div class="col-md-2 showcase_text_area">
          <label for="sdsszTargetInput">SDSS z</label>
        </div>
        <div class="col-md-2 showcase_content_area">
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_z`+targetDetails.TID+`" value="Yes">
          <label class="form-check-label" for="sdsszYes">Yes</label>
        </div>
        <div class="form-check form-check-inline mb-1">
          <input class="form-check-input" type="radio" name="SDSS_z`+targetDetails.TID+`"  value="No">
          <label class="form-check-label" for="sdsszNo">No</label>
        </div>
        </div>                  
      </div>
    </div>
    <div class="col-1">
      <div>
        <button class="btn btn-sm btn-danger mb-5 deleteTarget"> <i class="mdi mdi-minus-circle "></i></button>
      </div>
    </div><hr mb-3>`;
      
    $("#targetDiv").prepend(element);

    },
    error: function (error) {
        console.log(error);
    }
});

});

$("#selectTargetbtnInterest").on("click", function(){
  $.ajax({
    async: false,
    url: '/projects/targetDetails',
    type: "POST",
    data: {
        targetName: $("#inputTargetDataList").val()
    },
    dataType: "json",
    success: function (data) {      
      var targetDetails = data["targetDetails"][0];
      var element = `<div class="col-11 targetProjectAddList">
      <fieldset disabled class="mb-3">
        <div class="form-group row showcase_row_area">
          <div class="col-md-3 showcase_text_area">
            <label for="showSelectTargetName">Target Name</label>
          </div>
          <div class="col-md-9 showcase_content_area">
            <input id="showSelectTargetName"  type="text" class="form-control"  placeholder="Target Name" value="`+$("#inputTargetDataList").val()+`">
          </div>                         
      </div>
      <div>
        <input type="hidden" id="hiddenSelectTargetID" type="number"  name="TID" value="`+targetDetails.TID+`">
      </div>
      </fieldset>
  </div>
    <div class="col-1">
      <div>
        <button class="btn btn-sm btn-danger mb-5 deleteTargetInterest" type="button"> <i class="mdi mdi-minus-circle "></i></button>
      </div>
    </div><hr mb-3>`;
      
    $("#targetInterestDiv").prepend(element);
    $.ajax({
      async: false,
      url: '/accounts/addInterest',
      type: "POST",
      data: { 
              TID: targetDetails.TID,
      },
      dataType: "json",
      success: function (data) {
        console.log(data);
        $("#inputTargetDataList").val('');
      },
      error: function(error) {
        console.log(error);
      }
    });

    },
    error: function (error) {
        console.log(error);
    }
});

});

$("#targetInterestDiv").on("click", ".deleteTargetInterest", function(){
  var tid = $(this).parent().parent().prev().find('input[name = "TID"]').val();
  $(this).parent().parent().prev().remove();
  $(this).parent().parent().prev().next();
  $(this).parent().parent().remove();

  $.ajax({
    async: false,
    url: '/accounts/deleteInterest',
    type: "POST",
    data: { 
            TID: tid,
    },
    dataType: "json",
    success: function (data) {
      console.log(data);
    },
    error: function(error) {
      console.log(error);
    }
  });


});

$("#targetDiv").on("click", ".deleteTarget", function(){
  $(this).parent().parent().prev().remove();
  $(this).parent().parent().next().remove();
  $(this).parent().parent().remove();
});

// $("#targetDiv").on("click", ".deleteTarget", function(){
//   $(this).parent().parent().prev().remove();
//   $(this).parent().parent().remove();
// });

$("#submitCreateProjectbtn").on("click", function(){
  var myform = document.getElementById("createProjectForm");
  var fd = new FormData(myform );
  $.ajax({
    url: '/accounts/createProject',
    type: "POST",
    data: fd,
    cache: false,
    processData: false,
    contentType: false,
    success: function (data) {
      var projectID = data["projects"];
      var PID = parseInt(projectID);
      $(".targetProjectAddList").each(function(i, item) {  
        var TID = parseInt($(item).find('input[name = "TID"]').val());
        var JohnsonB = $(item).find(`input[name = "Johnson_B`+TID+`"]`).val();
        var JohnsonV = $(item).find(`input[name = "Johnson_V`+TID+`"]`).val();
        var JohnsonR = $(item).find(`input[name = "Johnson_R`+TID+`"]`).val();
        var SDSSu = $(item).find(`input[name = "SDSS_u`+TID+`"]`).val();
        var SDSSg = $(item).find(`input[name = "SDSS_g`+TID+`"]`).val();
        var SDSSr = $(item).find(`input[name = "SDSS_r`+TID+`"]`).val();
        var SDSSi = $(item).find(`input[name = "SDSS_i`+TID+`"]`).val();
        var SDSSz = $(item).find(`input[name = "SDSS_z`+TID+`"]`).val();     
        $.ajax({
          async: false,
          url: '/projects/addTarget',
          type: "POST",
          data: { PID: PID,
                  TID: TID,
                  JohnsonB: JohnsonB,
                  JohnsonV: JohnsonV,
                  JohnsonR: JohnsonR,
                  SDSSu: SDSSu,
                  SDSSg: SDSSg,
                  SDSSr: SDSSr,
                  SDSSi: SDSSi,
                  SDSSz: SDSSz
          },
          dataType: "json",
          success: function (data) {
            console.log("Target: ");
            console.log(data["target"][0]["pht.phavetid"]);
            location.reload();
            $("#addProjectForm").prepend(`<div class="alert alert-success alert-dismissible fade show" role="alert">Project successfully created!<button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>`);
          },
          error: function(error) {
            $("#addProjectForm").prepend(`<div class="alert alert-warning alert-dismissible fade show" role="alert">Project could not be created.<button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>`);
            console.log(error);
          }
        });
      });
    },
    error: function (error) {
        console.log(error);
    }
});

});

$(".addFriend").on("click", function(){
  console.log("entered");
  console.log($(this).prev().prev().prev().val());
  var uid = $(this).prev().prev().prev().val();

  $.ajax({
    url: '/addfriend',
    type: "POST",
    data: {
        UID: uid
    },
    dataType: "json",
    success: function (data) {
      console.log(data);
    },
    error: function (error) {
        console.log(error);
    }
  
  });
  

});