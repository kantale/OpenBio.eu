
var tool_installation_editor = ace.edit("tool_installation_editor");
tool_installation_editor.setTheme("ace/theme/textmate");
tool_installation_editor.session.setMode("ace/mode/sh");


var tool_validation_editor = ace.edit("tool_validation_editor");
tool_validation_editor.setTheme("ace/theme/textmate");
tool_validation_editor.session.setMode("ace/mode/sh");

// https://github.com/ezraroi/ngJsTree/issues/20
// We have to register the event on the document.. 
$(document).on('dnd_stop.vakata', function (e, data) {
    console.log('Stopped');

    angular.element($('#angular_div')).scope().$apply(function(){
				angular.element($('#angular_div')).scope().addNewNode_2();
	});
});