
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

	//We assume that only a single node is been moved
	if (data.data.nodes.length != 1) {
		return;
	}

	var this_id = data.data.nodes[0]; // plink/1.9/3/1"
	//var this_id_array = this_id.split('/'); //[ "plink", "1.9", "3", "1" ]
	var this_id_array = JSON.parse(this_id);

	console.log('Stopped:', this_id);
	console.log('Stopped ID:', this_id_array[3]);

	if (this_id_array[3] === "1") { // We are moving an item from the tool search tree
		if (target.closest('#tools_dep_jstree_id').length) { // We are dropping it to the dependency tool js tree div
			var tool = {
				'name': this_id_array[0],
				'version': this_id_array[1],
				'edit': this_id_array[2],
			};

			console.log('Right stop');
			console.log(tool);

			angular.element($('#angular_div')).scope().$apply(function(){
				angular.element($('#angular_div')).scope().tool_get_dependencies(tool);
			});
		}
	}
	else if (this_id_array[3] == "3") { // We are moving a variable from the dependency + variable tree
		if (target.closest('#tool_installation_editor').length) { // Adding to installation bash editor
			// https://stackoverflow.com/a/42797383/5626738 
			tool_installation_editor.session.insert(tool_installation_editor.getCursorPosition(), '$' + this_id_array[0]);
		}
		else if (target.closest('#tool_validation_editor').length) { // Adding to validation bash editor
			tool_validation_editor.session.insert(tool_validation_editor.getCursorPosition(), '$' + this_id_array[0]);
		}
	}

	//Do nothing 

//    angular.element($('#angular_div')).scope().$apply(function(){
//				angular.element($('#angular_div')).scope().addNewNode_2();
//	});
});

/*
* JSTree item moves. Change the class (for visualization only)
*/
$(document).on('dnd_move.vakata', function (e, data) {
	var target = $(data.event.target);
	var this_id = data.data.nodes[0]; // plink/1.9/3/1"

	//var this_id_array = this_id.split('/'); //[ "plink", "1.9", "3", "1" ]
	var this_id_array = JSON.parse(this_id);


	if (this_id_array[3] == '1') { // This is an item from tools_search tree

		//console.log('Distance:', target.closest('#tools_dep_jstree_id').length);

		if (target.closest('#tools_dep_jstree_id').length) {
			data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
		}
		else {
			data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
		}
	}

	else if (this_id_array[3] == "3") { // This is an item from validation js tree
		if (target.closest('#tool_installation_editor').length) {
			console.log('in');
			console.log(data);
			data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
		}
		else {
			console.log('out');
			data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
		}
	}


});