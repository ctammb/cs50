//This span is used to measure the size of the textarea
//it should have the same font and text with the textarea and should be hidden
var span = $('<span>').css('display','inline-block')
                      .css('word-break','break-all')
                      .appendTo('body').css('visibility','hidden');
function initSpan(textarea){
  span.text(textarea.text())
      .width(textarea.width())
      .css('font',textarea.css('font'));
}
$('textarea').on({
    input: function(){
       var text = $(this).val();
       span.text(text);
       $(this).height(text ? span.height() : '1.1em');
    },
    focus: function(){
       initSpan($(this));
    },
    keypress: function(e){
       //cancel the Enter keystroke, otherwise a new line will be created
       //This ensures the correct behavior when user types Enter
       //into an input field
       if(e.which == 13) e.preventDefault();
    }
});
