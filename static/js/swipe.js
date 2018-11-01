 var start = null;
 window.addEventListener("touchstart",function(event){
   if(event.touches.length === 1){
      //just one finger touched
      start = event.touches.item(0).clientX;
    }else{
      //a second finger hit the screen, abort the touch
      start = null;
    }
  });
   window.addEventListener("touchend",function(event){
    var offset = 100;//at least 100px are a swipe
    if(start){
      //the only finger that hit the screen left it
      var end = event.changedTouches.item(0).clientX;

      if(end > start + offset){
          document.location.href = window.location.href + '&delta=-1';
       //a left -> right swipe
      }
      if(end < start - offset ){
          document.location.href = window.location.href + '&delta=1';
       //a right -> left swipe
      }
    }
  });
