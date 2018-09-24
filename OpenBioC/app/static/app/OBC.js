
var tool_installation_editor = ace.edit("tool_installation_editor");
tool_installation_editor.setTheme("ace/theme/textmate");
tool_installation_editor.session.setMode("ace/mode/sh");


var tool_validation_editor = ace.edit("tool_validation_editor");
tool_validation_editor.setTheme("ace/theme/textmate");
tool_validation_editor.session.setMode("ace/mode/sh");

/*
* It is important to register these events AFTER load so that they are triggered after custom JSTREE functions
* More: https://groups.google.com/forum/#!topic/jstree/BYppISuCFRE
*/
window.onload = function () {

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

		//console.log('Stopped:', this_id);
		//console.log('Stopped ID:', this_id_array[3]);

		if (this_id_array[3] === "1") { // We are moving an item from the tool search tree
			if (target.closest('#tools_dep_jstree_id').length) { // We are dropping it to the dependency tool js tree div
				var tool = {
					'name': this_id_array[0],
					'version': this_id_array[1],
					'edit': this_id_array[2],
				};

				//console.log('Right stop');
				//console.log(tool);

				angular.element($('#angular_div')).scope().$apply(function(){
					angular.element($('#angular_div')).scope().tool_get_dependencies(tool);
				});
			}
		}
		else if (this_id_array[3] == "3") { // We are moving a variable from the dependency + variable tree
			if (target.closest('#tool_installation_editor').length) { // Adding to installation bash editor
				// https://stackoverflow.com/a/42797383/5626738 
				if (!tool_installation_editor.getReadOnly()) {
					tool_installation_editor.session.insert(tool_installation_editor.getCursorPosition(), '$' + this_id_array[0]);
				}
			}
			else if (target.closest('#tool_validation_editor').length) { // Adding to validation bash editor
				if (!tool_validation_editor.getReadOnly()) {
					tool_validation_editor.session.insert(tool_validation_editor.getCursorPosition(), '$' + this_id_array[0]);
				}
			}
		}

	});

	/*
	* JSTree item moves. Change the class (for visualization only)
	*/
	$(document).on('dnd_move.vakata', function (e, data) {
//		$('#vakata-dnd').find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
//		return;
		var target = $(data.event.target);
		var this_id = data.data.nodes[0]; // plink/1.9/3/1"

		//var this_id_array = this_id.split('/'); //[ "plink", "1.9", "3", "1" ]
		var this_id_array = JSON.parse(this_id);


		if (this_id_array[3] == '1') { // This is an item from tools_search tree

			//We allow it if it is over the div with the tree AND the the tool_installation_editor is not readonly (this is a workaround to avoid checking angular: tools_info_editable)
			if (target.closest('#tools_dep_jstree_id').length && (!tool_installation_editor.getReadOnly())) { 
				data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
			}
			else {
				data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
			}
		}

		else if (this_id_array[3] == "3") { // This is an item from validation js tree

			if (
				(target.closest('#tool_installation_editor').length && (!tool_installation_editor.getReadOnly())) || 
				(target.closest('#tool_validation_editor').length   && (!tool_validation_editor.getReadOnly()))       ) {
				data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
			}
			else {
				data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
			}

		}


	});

	//Disable drop event. So that users cannot drop tool nodes in the installation/validation editors
	tool_installation_editor.container.addEventListener("drop", function (e) {
		//This doesn't work
    	//e.preventDefault();
    	//return false;

      	//Curiously.. this works!
    	tool_installation_editor.undo();
	});

	tool_validation_editor.container.addEventListener("drop", function (e) { // drop
    	tool_validation_editor.undo();
	});

	//COLA SETUP
	var height = 500;
	var width = 960;
	var svg = d3.select("#d3wf").append("svg")
	        //.attr("width", width)
	        .attr("width", '100%')
	        .attr("height", height)
	        .style("border-style", "solid")
	        .style("border-width", "1px");


	var ark_cola = cola.d3adaptor(d3)
	        .linkDistance(100)
	        .avoidOverlaps(true)
	        .handleDisconnected(false)
			.size([width, height]);

};
