
/*
* Testing suite for OpenBio.eu
* Run with test.test(prefix); i.e. test.test('test1')
*/
(function (){
	var ret = {};

	/*
	* https://github.com/kemokid/scripting-sortable/blob/master/script_sortable_dnd_more_general.js
	*/
	var triggerDragAndDrop2 = function (selectorDrag, selectorDrop, callback) {
	  var DELAY_INTERVAL_MS = 10;
	  var MAX_TRIES = 10;
	  var dragStartEvent;

	  // fetch target elements
	  var elemDrag = document.querySelector(selectorDrag);
	  var elemDrop = document.querySelector(selectorDrop);

	  if (!elemDrag || !elemDrop) {
	    console.log("can't get elements");
	    return false;
	  }

	  var startingDropRect = elemDrop.getBoundingClientRect();

	  function rectsEqual(r1, r2) {
	    return r1.top === r2.top && r1.right === r2.right && r1.bottom === r2.bottom && r1.left === r2.left;
	  }

	  // function for triggering mouse events
	  function fireMouseEvent(type, elem, dataTransfer) {
	    var evt = document.createEvent('MouseEvents');
	    evt.initMouseEvent(type, true, true, window, 1, 1, 1, 0, 0, false, false, false, false, 0, elem);
	    if (/^dr/i.test(type)) {
	      evt.dataTransfer = dataTransfer || createNewDataTransfer();
	    }

	    elem.dispatchEvent(evt);
	    return evt;
	  };

	  function createNewDataTransfer() {
	    var data = {};
	    return {
	      clearData: function(key) {
	        if (key === undefined) {
	          data = {};
	        } else {
	          delete data[key];
	        }
	      },
	      getData: function(key) {
	        return data[key];
	      },
	      setData: function(key, value) {
	        data[key] = value;
	      },
	      setDragImage: function() {},
	      dropEffect: 'none',
	      files: [],
	      items: [],
	      types: [],
	      // also effectAllowed      
	    }
	  };

	  // trigger dragging process on top of drop target
	  // We sometimes need to do this multiple times due to the vagaries of
	  // how Sortable manages the list re-arrangement
	  var counter = 0;
	  function dragover() {
	    counter++;
	    console.log('DRAGOVER #' + counter);

	    var currentDropRect = elemDrop.getBoundingClientRect();
	    if (rectsEqual(startingDropRect, currentDropRect) && counter < MAX_TRIES) {
	      if (counter != 1) console.log("drop target rect hasn't changed, trying again");

	      // mouseover / mouseout etc events not necessary
	      // dragenter / dragleave events not necessary either
	      fireMouseEvent('dragover', elemDrop, dragStartEvent.dataTransfer);

	      setTimeout(dragover, DELAY_INTERVAL_MS);
	    } else {
	      if (rectsEqual(startingDropRect, currentDropRect)) {
	        console.log("wasn't able to budge drop target after " + MAX_TRIES + " tries, aborting");
	        fireMouseEvent('drop', elemDrop, dragStartEvent.dataTransfer);

	        //$(selectorDrop).mouseup(); 
	        if (callback) callback(false);
	      } else {
	        setTimeout(drop, DELAY_INTERVAL_MS);
	      }
	    }
	  }

	  function drop() {
	    console.log('DROP');
	    // release dragged element on top of drop target
	    fireMouseEvent('drop', elemDrop, dragStartEvent.dataTransfer);
	    fireMouseEvent('mouseup', elemDrop);    // not strictly necessary but I like the symmetry
	    if (callback) callback(true);
	  }

	  // start dragging process
	  console.log('DRAGSTART');
	  fireMouseEvent('mousedown', elemDrag);
	  dragStartEvent = fireMouseEvent('dragstart', elemDrag);

	  // after a delay, do the first dragover; this will run up to MAX_TRIES times
	  // (with a delay between each run) and finally run drop() with a delay:
	  setTimeout(dragover, DELAY_INTERVAL_MS);

	  return true;
	};


	ret.click = function(id) {
		$('#' + id).click()
	};

	ret.insert = function(id, text) {
		$('#' + id).val(text).trigger('input');
		setTimeout(function(){M.updateTextFields()}, 10);
	};

	var click_plus_search_tools_button = function() {
		ret.click('toolsDataPlusBtn');
	};

	var click_plus_search_workflows_button = function() {
		ret.click('workflowsPlusBtn');
	};

	var tools_set_name = function(args) {
		ret.insert('generalName', args['name'])
	};

	var workflows_set_name = function(args) {
		ret.insert('generalWorkflowName', args['name'])
	};

	var tools_set_version = function() {
		ret.insert('generalVersion', '1');
	};

	var tools_set_description = function() {
		ret.insert('generalDescription', 'description');
	};

	var tools_dnd_search_dep = function() {
		triggerDragAndDrop2('#tools_search_jstree_id a', '#tools_dep_jstree_id');
		setTimeout(function() { $('#tools_dep_jstree_id').mouseup(); }, 1000);
	};

	/*
	* To run this, you need to.. move the mouse pointer inside the browser window
	*/
	var workflows_dnd_tool_graph = function() {
		triggerDragAndDrop2('#tools_search_jstree_id a', '#cywf');
		setTimeout(function() { $('#cywf').mouseup(); }, 1000);
	};

	var workflows_set_description = function() {
		ret.insert('workflowsGeneralDescription', 'description');
	};

	var tools_select_os_posix = function() {
		//M.FormSelect.getInstance($('#tool_os_choices_select')).dropdown.open();
		// Select the first option
		//$('#tool_os_choices_select').val("object:15");
		//$('#tool_os_choices_select').formSelect();

		angular.element($('#angular_div')).scope().$apply(function () {
			var scope = angular.element($('#angular_div')).scope();

        	scope.tool_os_choices_tmp = [
 				{
    				"group": "Generic",
    				"name": "POSIX system",
    				"value": "posix"
  				}
			];

            scope.tool_os_choices = [];
            scope.os_choices.forEach(function (element){
                for (var i=0; i<scope.tool_os_choices_tmp.length; i++) {
                    if (scope.tool_os_choices_tmp[i].value === element.value) {
                        scope.tool_os_choices.push(element);
                    }
                }
            });

            $('#tool_os_choices_select').formSelect();
        });
	};

	var tools_close_all_accordions = function() {
		M.Collapsible.getInstance($('#createToolDataAccordion')).close();
	};

	var tools_open_all_accordions = function() {
		M.Collapsible.getInstance($('#createToolDataAccordion')).open();
	};

	var tool_save_button = function() {
		ret.click('tool_save_button_id');
	};

	var workflow_save_button = function() {
		ret.click('workflow_save_button_id');
	};

	var tool_cancel_button = function() {
		ret.click('tool_cancel_button_id');
	};

	var workflow_cancel_button = function() {
		ret.click('workflow_cancel_button_id');
	};

	var remove_toast = function() {
		$('.toast').remove();
	};

	var global_search = function(args) {
		ret.insert('leftPanelSearch', args['search']);
	};

	var global_search_empty = function() {
		ret.insert('leftPanelSearch', '');
	};

	var global_search_open_accordions = function() {
		M.Collapsible.getInstance($('#searchResultsCollapsible')).open();
	};

	var global_search_close_accordions = function() {
		M.Collapsible.getInstance($('#searchResultsCollapsible')).close();
	};

	var build_chain = function(fns, i) {

		if (i>=fns.length) {
			return;
		}

		setTimeout(function() {
			console.log('Running test:', i+1)
			if (typeof fns === 'function') {
				fns[i]();	
			}
			else if (typeof fns === 'object') {
				fns[i][0](fns[i][1]);
			}
			
			build_chain(fns, i+1);
		}, 1000)
	};


	var create_new_tool = function(args) {

		var actions = [
			click_plus_search_tools_button,
			tools_close_all_accordions,
			tools_open_all_accordions,
			[tools_set_name, {'name': args['name']}],
			tools_set_version,
			tools_set_description,
			tools_select_os_posix,
			// tools_dnd_search_dep,
			tool_save_button,
			tool_cancel_button,
			remove_toast
		];

		return build_chain(actions, 0);
	};

	var create_new_workflow = function(args) {
		var actions = [
			click_plus_search_workflows_button,
			[workflows_set_name, {'name': args['name']}],
			workflows_set_description,
			global_search, {'name': args['import_tool_name']},
			global_search_open_accordions,
			workflows_dnd_tool_graph,
			workflow_save_button,
			workflow_cancel_button,
			remove_toast,
			global_search_empty,
			global_search_close_accordions
		]

		return build_chain(actions, 0);
	};

	ret.test = function(prefix) {

		ret.prefix = prefix;
		ret.args = {};

		var actions = [
			//create_new_tool,
			//create_new_workflow
		];

		return build_chain(actions, 0);
	};


	window.test = ret;
	//return ret;
})();


