
var tool_installation_editor = ace.edit("tool_installation_editor");
tool_installation_editor.setTheme("ace/theme/textmate");
tool_installation_editor.session.setMode("ace/mode/sh");


var tool_validation_editor = ace.edit("tool_validation_editor");
tool_validation_editor.setTheme("ace/theme/textmate");
tool_validation_editor.session.setMode("ace/mode/sh");

// https://github.com/ezraroi/ngJsTree/issues/20
// We have to register the event on the document.. 
$(document).on('dnd_stop.vakata', function (e, data) {
	var target = $(data.event.target);
	var this_id = data.data.nodes[0]; // plink/1.9/3/1"

	var this_id_array = this_id.split('/'); //[ "plink", "1.9", "3", "1" ]
	console.log('Stopped:', this_id);

	//Do nothing 

//    angular.element($('#angular_div')).scope().$apply(function(){
//				angular.element($('#angular_div')).scope().addNewNode_2();
//	});
});

//JSTree item moves
$(document).on('dnd_move.vakata', function (e, data) {
	var target = $(data.event.target);
	var this_id = data.data.nodes[0]; // plink/1.9/3/1"

	var this_id_array = this_id.split('/'); //[ "plink", "1.9", "3", "1" ]


	if (this_id_array[3] == '1') { // This is an item from tools_search tree

		//console.log('Distance:', target.closest('#tools_dep_jstree_id').length);

		if (target.closest('#tools_dep_jstree_id').length) {
			data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
		}
		else {
			data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
		}
	}


});