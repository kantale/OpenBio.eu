

//$(document).ready(function() {
window.onload = function () {
	$('#system-select').multiselect();

	//Also edit CSS 
	window.installation_ace = ace.edit("installation_ace");
    window.installation_ace.setTheme("ace/theme/github");
    window.installation_ace.getSession().setMode("ace/mode/sh");

	window.validate_installation_ace = ace.edit("validate_installation_ace");
    window.validate_installation_ace.setTheme("ace/theme/github");
    window.validate_installation_ace.getSession().setMode("ace/mode/sh");

	window.log_ace = ace.edit("log_ace");
    window.log_ace.setTheme("ace/theme/github");
    window.log_ace.getSession().setMode("ace/mode/text");
    window.log_ace.setReadOnly(true);

	window.report_doc_ace = ace.edit("report_doc_ace");
    window.report_doc_ace.setTheme("ace/theme/github");
    window.report_doc_ace.getSession().setMode("ace/mode/markdown");

	window.task_doc_ace = ace.edit("task_doc_ace");
    window.task_doc_ace.setTheme("ace/theme/github");
    window.task_doc_ace.getSession().setMode("ace/mode/markdown");

    window.task_ace = ace.edit('task_ace');
    window.task_ace.setTheme("ace/theme/github");
    window.task_ace.getSession().setMode("ace/mode/sh");

    //Create showdown markdown converter
    window.markdown = new showdown.Converter();

// constructs the suggestion engine
var reference_suggestions = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  remote: {
    url: '/reference_suggestions/?query=%QUERY',
    wildcard: '%QUERY'
  }
});

reference_suggestions.initialize();

/*
$('#bloodhound_tools_references .typeahead').typeahead({
  hint: true,
  highlight: true,
  minLength: 1
},
{
  name: 'abcd',
  display: 'value',
  source: reference_suggestions,
  templates: {
  	suggestion : function (data) {
        return '<p><strong>' + data.value + '</strong> - ' + data.html + '</p>';
    }
  }
});
*/
//$('.category-container > > input').tagsinput({
$('#ta_tools_ref').tagsinput({
	typeaheadjs:[
		{
		  hint: true,
		  highlight: true,
		  minLength: 1
		},
		{
		  name: 'abcd',
		  display: 'value',
		  source: reference_suggestions,
		  templates: {
		  	suggestion : function (data) {
		        return '<p><strong>' + data.value + '</strong> - ' + data.html + '</p>';
		    }
		  }
		}
	],
	allowDuplicates: false,
	freeInput: false,
	itemValue: 'value'
}
);
//$('#bloodhound_tools_references').tagsinput('add', { id: 'tag id', label: 'tag lable' });

//Bootstrap table

// Click on row table
//$('#tools_table').on('click-row.bs.table', function (e, row, $element) {
//	angular.element($('#tools_table')).scope().$apply(function(){
//		angular.element($('#tools_table')).scope().tools_table_row_clicked(row);
//	});
//});

// Click on expanded item in row of table 
$('#tools_table')
.on('expand-row.bs.table', function (e, index, row, $detail) {
	var this_id = "tools_table_expand_" + index ;
	$detail.html('<div id="' + this_id + '"></div><script>$("#' + this_id + '").jstree();</script>');

	angular.element($('#tools_table')).scope().$apply(function(){
		angular.element($('#tools_table')).scope().tools_create_jstree(row['name'], this_id, '1', 'tools_table_row_clicked');
	});

})
.on('collapse-row.bs.table', function(e, index, row) {
	var this_id = "tools_table_expand_" + index ;
	$('#' + this_id).jstree("destroy");
});

// tools_dependencies_table
$('#tools_dependencies_table')
.on('expand-row.bs.table', function (e, index, row, $detail) {
	var this_id = "tools_table_dependencies_expand_" + index ;
	//$detail.html('<div id="' + this_id + '"></div><script>$("#' + this_id + '").jstree();</script>');
	$detail.html('<div id="' + this_id + '"></div><script>$("#' + this_id + '").jstree({"core": {check_callback: true}, "plugins": ["dnd"]});</script>');

	angular.element($('#tools_table')).scope().$apply(function(){
		angular.element($('#tools_table')).scope().tools_create_jstree(row['name'], this_id, '2', '');
	});
})
.on('collapse-row.bs.table', function(e, index, row) {
	var this_id = "tools_table_dependencies_expand_" + index ;
	$('#' + this_id).jstree("destroy");
});

//reports_table
$('#reports_table').on('expand-row.bs.table', function (e, index, row, $detail) {
	var this_id = "reports_table_" + index;
	$detail.html('<div id="' + this_id + '"></div><script>$("#' + this_id + '").jstree();</script>');

	angular.element($('#tools_table')).scope().$apply(function(){
		angular.element($('#tools_table')).scope().reports_create_jstree(row['name'], this_id, '1', '');
	});


})
.on('collapse-row.bs.table', function(e, index, row) {
	var this_id = "reports_table_" + index ;
	$('#' + this_id).jstree("destroy");
});


//wf_tools_table : The Tools/Data table on workflows
$('#wf_tools_table').on('expand-row.bs.table', function (e, index, row, $detail) {
	var this_id = "wf_tools_table_" + index;

	$detail.html('<div id="' + this_id + '"></div><script>$("#' + this_id + '").jstree({"core": {check_callback: true}, "plugins": ["dnd"]});</script>');

	angular.element($('#tools_table')).scope().$apply(function(){
		angular.element($('#tools_table')).scope().tools_create_jstree(row['name'], this_id, '4', '');
	});	
})
.on('collapse-row.bs.table', function(e, index, row) {
	var this_id ="wf_tools_table_" + index;
	$('#' + this_id).jstree("destroy");
});

//wf_workflows_table: The workflows table on workflows 
$('#wf_workflows_table').on('expand-row.bs.table', function (e, index, row, $detail) {
	var this_id = "wf_workflows_table_" + index;

	$detail.html('<div id="' + this_id + '"></div><script>$("#' + this_id + '").jstree({"core": {check_callback: true}, "plugins": ["dnd"]});</script>');

	angular.element($('#tools_table')).scope().$apply(function(){
		angular.element($('#tools_table')).scope().wf_create_jstree(row['name'], this_id, '6', '');
	});	
})
.on('collapse-row.bs.table', function(e, index, row) {
	var this_id ="wf_workflows_table_" + index;
	$('#' + this_id).jstree("destroy");
});


//Drophere jstree
$('#jstree_drophere').jstree({
	"core": {check_callback: true},
	"plugins": ["dnd", "types"],
	"dnd": {
		"is_draggable": function (node) {

			var ret = false;
			angular.element($('#tools_table')).scope().$apply(function(){
				ret = !angular.element($('#tools_table')).scope().add_tool_dis_table_clicked;
			});
			return ret;


        }
	},
	"types": {
		"tool": {"icon": "glyphicon glyphicon-flash"},
		"exposed": {"icon" : "glyphicon glyphicon-asterisk"}
	}
});

//This is the tree in workflow tasks with tool/data dependencies
$('#wf_task_jstree').jstree({
	"core": {check_callback: true},
	"plugins": ["dnd", "types"],
	"dnd": {
		"is_draggable": function (node) {
			return true;
        }
	},
	"types": {
		"tool": {"icon": "glyphicon glyphicon-flash"},
		"exposed": {"icon" : "glyphicon glyphicon-asterisk"}
	}
});


// http://jsfiddle.net/DGAF4/517/ 
//$('#jstree_tools').jstree({
//	'core': {check_callback: true},
//	'plugins': ['dnd']
//});
//}).on("copy_node.jstree", function () {
//            alert("copy_node fires");
//}).on("move_node.jstree", function () {
//            alert("move_node fires");
//});

// Jstree. This is the tree on top of Tools Add/Edit
$('#jstree_tools').jstree();


$(document).on('dnd_move.vakata', function (e, data) {
	var t = $(data.event.target);
	var tt = $(data.element).attr('id'); // plink||12_anchor
	//console.log(tt);

	var tt_s = tt.split('_').slice(0,-1).join().split('||'); // Array [ "plink", "12" ]

	if (tt_s[0] == '2') { //We are moving an item from the dependency TABLE
		if (t.closest('#drophere').length) {
			data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
		}
		else {
			data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
		}
	}
	else if (tt_s[0] == '3') { //We are moving an item from the dependecy JSTREE
		if (t.closest('#dropheredelete').length) {
			data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
		}
		else {
			data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
		}		
	}
	else if ((tt_s[0] == '4') || (tt_s[0] == '6')) { // We are moving an item from the workflow tool table OR from the workflow table
		if (t.closest('#d3wf').length) {
			data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
		}
		else {
			data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
		}
	}
	else if (tt_s[0] == '5') { // We are moving an item from the workflow task jstree dependecies/exposed
		//Is this a tool?
		if (tt.indexOf('@@') !== -1) {
			//This is a variable
			if (t.closest('#task_ace').length) {
				data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
			}
			else {
				data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
			}	

		}
		else {
			//This is a tool
			if (t.closest('#wf_task_dropheretodelete').length) {
				data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
			}
			else {
				data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
			}	

		}
	}

});

$(document).on('dnd_stop.vakata', function (e, data) {
	var t = $(data.event.target);
	var tt = $(data.element).attr('id'); // 2||plink||12_anchor
	//Remove the _anchor . https://stackoverflow.com/questions/2729666/javascript-replace-last-occurrence-of-text-in-a-string 
	tt = tt.replace(new RegExp('_anchor$'), '');

	//Split it
	var tt_s = tt.split('||'); // Array [ "2", "plink", "12" ]

	if (tt_s[0] == '2') { //We are moving an item from the dependency TABLE


		if (t.closest('#drophere').length) {

			//Create new dependency
			var new_dependency = {
				'name': tt_s[1], 
				'current_version': +tt_s[2],
			};
			//console.log(new_dependency);

			angular.element($('#tools_table')).scope().$apply(function(){
				angular.element($('#tools_table')).scope().add_tool_dependency(new_dependency);
			});
		}
	}
	else if (tt_s[0] == '3') { //We are moving an item from the dependecy JSTREE 
		if (t.closest('#dropheredelete').length) {
			//console.log('DELETEIT!');
			angular.element($('#tools_table')).scope().$apply(function(){
				angular.element($('#tools_table')).scope().remove_tool_dependency({'name': tt_s[1], 'current_version': +tt_s[2]});
			});
		}
	}
	else if ((tt_s[0] == '4') || (tt_s[0] == '6')) { // We are moving an item from the workflow tool table OR from the workflow table
		if (t.closest('#d3wf').length) {
			angular.element($('#tools_table')).scope().$apply(function(){
				if (tt_s[0] == '4') {
					angular.element($('#tools_table')).scope().wf_add_tool_in_graph({'name': tt_s[1], 'current_version': +tt_s[2]}, true, false);
				}
				else if (tt_s[0] == '6') {
					angular.element($('#tools_table')).scope().wf_add_workflow_in_graph({'name': tt_s[1], 'current_version': +tt_s[2]}, true, false);
				}
			});
		}
	}
	else if (tt_s[0] == '5') { // We are moving an item from the workflow task jstree dependecies/exposed
		//Is this a tool?
		if (tt.indexOf('@@') !== -1) {
			//This is a variable

			if (t.closest('#task_ace').length) {
				task_ace.session.insert(task_ace.getCursorPosition(), '$' + tt_s[1]); // Insert at cursor position 
				//task_ace.setValue(task_ace.getValue() + '$' + tt_s[1], 1); // Insert at the end
			}
		}
		else {
			//This is a tool
		}
	}

});

$('#jstree_tools').on('select_node.jstree', function(e, data){
//	console.log(data);
//	console.log(data.node.original.current_version);
	if (data.event === undefined) {}
	else {
		angular.element($('#tools_table')).scope().$apply(function(){
			row = {'name': data.node.original.name, 'current_version': data.node.original.current_version};
			angular.element($('#tools_table')).scope().tools_table_row_clicked(row);
		});
	}

});


// Button check box
// https://bootsnipp.com/snippets/featured/jquery-checkbox-buttons 
$('.button-checkbox').each(function () {

        // Settings
        var $widget = $(this),
            $button = $widget.find('button'),
            $checkbox = $widget.find('input:checkbox'),
            color = $button.data('color'),
            settings = {
                on: {
                    icon: 'glyphicon glyphicon-check'
                },
                off: {
                    icon: 'glyphicon glyphicon-unchecked'
                }
            };

        // Event Handlers
        $button.on('click', function () {
            $checkbox.prop('checked', !$checkbox.is(':checked'));
            $checkbox.triggerHandler('change');
            updateDisplay();
        });
        $checkbox.on('change', function () {
            updateDisplay();
        });

        // Actions
        function updateDisplay() {
            var isChecked = $checkbox.is(':checked');

            // Set the button's state
            $button.data('state', (isChecked) ? "on" : "off");

            // Set the button's icon
            $button.find('.state-icon')
                .removeClass()
                .addClass('state-icon ' + settings[$button.data('state')].icon);

            // Update the button's color
            if (isChecked) {
                $button
                    .removeClass('btn-default')
                    .addClass('btn-' + color + ' active');
            }
            else {
                $button
                    .removeClass('btn-' + color + ' active')
                    .addClass('btn-default');
            }
        }

        // Initialization
        function init() {

            updateDisplay();

            // Inject the icon if applicable
            if ($button.find('.state-icon').length == 0) {
                $button.prepend('<i class="state-icon ' + settings[$button.data('state')].icon + '"></i> ');
            }
        }
        init();
});

//COLA

	var width = 960, height = 500;
	var zoom_allowed = true;
	var drag_new_line = false;

	var ark_cola = cola.d3adaptor(d3)
	        .linkDistance(100)
	        .avoidOverlaps(true)
	        .handleDisconnected(false)
	        .size([width, height]);

	var ark_drag = ark_cola.drag()
		.on('start', function() {
			//console.log("drag start"); 
		})
		.on('end', function(d) { 
			//console.log("drag end");

					//If this is a task node or a workflow node and the add_edge button is checked
              		if ( ((d.type == "task") || (d.type == "workflow")) && ($('#add_edge_button').data().state) == 'on') {

               			zoom_allowed = false;

               			var new_line = wf_g.append("line");
    					new_line
    							.attr("class", "new_line")
    							.attr("stroke", "blue")
    							.attr("stroke-width", 2)
    							.attr("fill", "none")
    							.attr("x1", d.x)
    							.attr("y1", d.y)
    							.attr("x2", d.x)
    							.attr("y2", d.y);


						var selected_node = d3.select(this);

               			var w = d3.select(window)
               				.on("mousemove", mousemove)
      						.on("mouseup", mouseup);

      					//d3.event.preventDefault();

						function mouseup() {
							//console.log("MOUSE UP");
	
//							console.log(d3.mouse(selected_node.node()));

							var m = d3.mouse(selected_node.node());
							var shortest_distance = Number.MAX_VALUE;
							var shortest_node_index = -1;
							var nodes = ark_cola._nodes;

							for (var i=0; i<nodes.length; i++) {
								if (nodes[i].type != "tool") {
									continue;
								}

								var distance = Math.sqrt(((m[0] - nodes[i].x) * (m[0] - nodes[i].x)) + ((m[1] - nodes[i].y) * (m[1] - nodes[i].y)));
								if (distance < shortest_distance) {
									shortest_distance = distance;
									shortest_node_index = i;
								}
							}
							if ((shortest_node_index > -1) && (shortest_distance <= 10)) {
		               			angular.element($('#tools_table')).scope().$apply(function(){
		               				angular.element($('#tools_table')).scope().wf_add_task_tool_edge(d, nodes[shortest_node_index]);
		               			});
							}

							w.on("mousemove", null).on("mouseup", null);
							zoom_allowed = true;

							//Remove new_line
							new_line.remove();
 						}

      					function mousemove() {


    						var m = d3.mouse(selected_node.node());

    						new_line
    							.attr("x2", m[0] - 1)
    							.attr("y2", m[1] - 1);
  						}

               		}

			
		});

	var svg = d3.select("#d3wf").append("svg")
	        //.attr("width", width)
	        .attr("width", '100%')
	        .attr("height", height)
	        .style("border-style", "solid")
	        .style("border-width", "1px");


	// define arrow markers for graph links
	//http://bl.ocks.org/rkirsling/5001347
	svg.append('svg:defs').append('svg:marker')
	    .attr('id', 'end-arrow')
	    .attr('viewBox', '0 -5 10 10')
	    .attr('refX', 6)
	    .attr('markerWidth', 10)
	    .attr('markerHeight', 10)
	    .attr('orient', 'auto')
	  .append('svg:path')
	    .attr('d', 'M0,-5L10,0L0,5')
	    .attr('fill', '#000');



	var main_g = svg.append("g");
	var wf_g = svg.append("g");


    main_g.append("rect")
        .attr("width", '100%')
        //.attr("width", width)
        .attr("height", height)
        .style("fill", "none")
        .style("pointer-events", "all")
        .call(d3.zoom()
          .filter(function(){return zoom_allowed;})
          .scaleExtent([1 / 2, 4]) // Change this to 1/20 for smaller zoom
          .on("zoom", zoomed));

      // https://bl.ocks.org/mbostock/4e3925cdc804db257a86fdef3a032a45
      function zoomed() {
           wf_g.attr("transform", d3.event.transform);
      }

	window.update_workflow = function(wf) {
		ark_cola
            .nodes(wf.nodes)
            .links(wf.links)
            .groups(wf.groups)
            .start();

        //Nodes
        var pad = 3;
        var node = wf_g.selectAll(".node")
            .data(wf.nodes, function (d) {return d.name;});
        node.exit().remove();

        var nodeEnter = node.enter();
        nodeEnter.append("circle")
//        		.attr("class", "node")
        		.attr("class", function(d) {
        			return  d.type == 'task' ? 'node task' : 'node' ;
        		})
        		.attr("r", 10)

//        nodeEnter.append("rect")
//               .attr("class", "node")
//               .attr("width", function (d) { return d.width - 2 * pad; })
//               .attr("height", function (d) { return d.height - 2 * pad; })
//               .attr("rx", 5).attr("ry", 5) // Eclipse 
               //.style("fill", function (d) { return  "rgb(0,0,255)"; })
               .style("fill", function (d) {
               		switch (d.type) {
               			case "tool":
               				return "Cyan";
               			case "variable":
               				return "LightPink";
               			case "task":
               				return "Gold";
               			case "workflow":
               				return "Black";
               			case "input":
               				return "Blue";
               			case "output":
               				return "Red";
               			default:
               				return "White";
               		} 
               		
               })
               .on("click", function(d) {
               		angular.element($('#tools_table')).scope().$apply(function(){
               			angular.element($('#tools_table')).scope().wf_node_click(d);
               		});

               })
               .on("dblclick", function(d) {
                	//console.log(d.width);
                	angular.element($('#tools_table')).scope().$apply(function(){
                		angular.element($('#tools_table')).scope().wf_node_double_click(d);
                	});
               })
//               .on("mousedown", function(d) {
               .call(ark_drag)
               .append("title")
                  .text(function (d) { return d.name; });

        var node = wf_g.selectAll(".node");


        //Node labels
        var label = wf_g.selectAll(".label")
            .data(wf.nodes, function (d) {return d.name;});

  		//Update old elements
  		label.text(function(d){return d.name});

//		label = wf_g.selectAll(".label")
//            .data(wf.nodes, function (d) {
//            	console.log('NODE 2 LABEL d.name: ' + d.name);
//            	return d.name;})

		//ENTER + UPDATE
        label
           .enter().append("text")
            .attr("class", "label")
            .text(function (d) {return d.name; })
            .call(ark_cola.drag);

        // REMOVE OLD ELEMENTS
        label.exit().remove();


        var label = wf_g.selectAll(".label");

        //Lines as links
        if (false) {
			var link = wf_g.selectAll(".link")
	            .data(wf.links, function (d) {return d.name;});
	        link.exit().remove();
	        link
	          .enter().append("line")
	            .attr("class", "link");

	        var link = wf_g.selectAll(".link");
    	}

    	//Lines as paths
    	if (true) {
    		var path = wf_g.selectAll(".link")
    			.data(wf.links, function(d) {return d.name;});
    		path.exit().remove();
    		path
    		    .enter().append('svg:path')
    		    .attr("class", "link")
    		    .style("marker-end", "url(#end-arrow)");

    		var link = wf_g.selectAll(".link");
    	}

        ark_cola.on("tick", function () {

        	if (false) {
				link.attr("x1", function (d) { return d.source.x; })
	                .attr("y1", function (d) { return d.source.y; })
	                .attr("x2", function (d) { return d.target.x; })
	                .attr("y2", function (d) { return d.target.y; });
	        }

	        if (true) {


				link.attr('d', function(d) {
				    var deltaX = d.target.x - d.source.x;
				    var deltaY = d.target.y - d.source.y;
				    var dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
				    var normX = deltaX / dist;
				    var normY = deltaY / dist;
				    var sourcePadding = 0; //d.left ? 17 : 12,
				    var targetPadding = 15; //d.right ? 17 : 12,
				    var sourceX = d.source.x + (sourcePadding * normX);
				    var sourceY = d.source.y + (sourcePadding * normY);
				    var targetX = d.target.x - (targetPadding * normX);
				    var targetY = d.target.y - (targetPadding * normY);
				    return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
				  });
	        }


        	//node.attr("x", function (d) { return d.x - d.width / 2 + pad; })
            //    .attr("y", function (d) { return d.y - d.width / 2 + pad; });

            node.attr("cx", function(d) {return d.x;})
            	.attr("cy", function(d) {return d.y;})

            label.attr("x", function (d) { return d.x; })
                 .attr("y", function (d) {
                     //var h = this.getBBox().height;
                     //return d.y + h/4;
                     return d.y - 13;
                 });


        });

	};

        //<rect x="160" y="160" height="30" width="30" fill="red" />
//END OF COLA

//}); //document.ready()
}; // window.onload

//function tools_table_detailFormatter(index, row) {
//	console.log(index);
//	console.log(row);
//
//	return '<h2>AAAA</h2>';
//};

