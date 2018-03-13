$(document).ready(function(){
    $("textarea").on('keydown', function(e){
        if(e.keyCode == 9) {
            e.preventDefault();
            var indent = '    ';
            var start = this.selectionStart;
            var end = this.selectionEnd;
            var selected = window.getSelection().toString();
            selected = indent + selected.replace(/\n/g, '\n' + indent)
            this.value = this.value.substring(0, start) + selected + this.value.substring(end);
            this.setSelectionRange(start + indent.length, start + selected.length);
        }
    });

    $("#title").addClass("form-control");
    $("#flask-pagedown-pagedown").addClass("form-control");

    $("#flask-pagedown-pagedown").css({"resize":"none","overflow":"scroll"});


});