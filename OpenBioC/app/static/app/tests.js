
/*
* Run with window.test.test() 
*/
(function (){
	var ret = {};

	/*
	* https://ghostinspector.com/blog/simulate-drag-and-drop-javascript-casperjs/ 
	*/
	var triggerDragAndDrop = function (selectorDrag, selectorDrop) {

	  // function for triggering mouse events
	  var fireMouseEvent = function (type, elem, centerX, centerY) {
	    var evt = document.createEvent('MouseEvents');
	    evt.initMouseEvent(type, true, true, window, 1, 1, 1, centerX, centerY, false, false, false, false, 0, elem);
	    elem.dispatchEvent(evt);
	  };

	  // fetch target elements
	  var elemDrag = document.querySelector(selectorDrag);
	  var elemDrop = document.querySelector(selectorDrop);
	  if (!elemDrag || !elemDrop) return false;

	  // calculate positions
	  var pos = elemDrag.getBoundingClientRect();
	  var center1X = Math.floor((pos.left + pos.right) / 2);
	  var center1Y = Math.floor((pos.top + pos.bottom) / 2);
	  pos = elemDrop.getBoundingClientRect();
	  var center2X = Math.floor((pos.left + pos.right) / 2);
	  var center2Y = Math.floor((pos.top + pos.bottom) / 2);
	  
	  // mouse over dragged element and mousedown
	  fireMouseEvent('mousemove', elemDrag, center1X, center1Y);
	  fireMouseEvent('mouseenter', elemDrag, center1X, center1Y);
	  fireMouseEvent('mouseover', elemDrag, center1X, center1Y);
	  fireMouseEvent('mousedown', elemDrag, center1X, center1Y);

	  // start dragging process over to drop target
	  fireMouseEvent('dragstart', elemDrag, center1X, center1Y);
	  fireMouseEvent('drag', elemDrag, center1X, center1Y);
	  fireMouseEvent('mousemove', elemDrag, center1X, center1Y);
	  fireMouseEvent('drag', elemDrag, center2X, center2Y);
	  fireMouseEvent('mousemove', elemDrop, center2X, center2Y);
	  
	  // trigger dragging process on top of drop target
	  fireMouseEvent('mouseenter', elemDrop, center2X, center2Y);
	  fireMouseEvent('dragenter', elemDrop, center2X, center2Y);
	  fireMouseEvent('mouseover', elemDrop, center2X, center2Y);
	  fireMouseEvent('dragover', elemDrop, center2X, center2Y);
	  
	  // release dragged element on top of drop target
	  fireMouseEvent('drop', elemDrop, center2X, center2Y);
	  fireMouseEvent('dragend', elemDrag, center2X, center2Y);
	  fireMouseEvent('mouseup', elemDrag, center2X, center2Y);

	  return true;
	};
	// triggerDragAndDrop('#tools_search_jstree_id a', '#tools_dep_jstree_id')
	// $('#tools_dep_jstree_id').mouseup() 

	ret.click = function(id) {
		$('#' + id).click()
	};

	ret.insert = function(id, text) {
		$('#' + id).val(text).trigger('input');
	};

	var click_plus_search_tools_button = function() {
		ret.click('toolsDataPlusBtn');
	};

	var tools_set_name = function() {
		ret.insert('generalName', ret.prefix)
	};

	var tools_set_version = function() {
		ret.insert('generalVersion', '1');
	}

	var tools_set_description = function() {
		ret.insert('generalDescription', 'description');
	}

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
	}

	var tools_close_all_accordions = function() {
		M.Collapsible.getInstance($('#createToolDataAccordion')).close()
	}

	var tools_open_all_accordions = function() {
		M.Collapsible.getInstance($('#createToolDataAccordion')).open();
	}

	var tool_save_button = function() {
		ret.click('tool_save_button_id')
	}

	var test_2 = function() {
		ret.insert('leftPanelSearch', 'draft');
	}

	var build_chain = function(fns, i) {

		if (i>=fns.length) {
			return;
		}

		setTimeout(function() {
			console.log('Running test:', i+1)
			fns[i]();
			build_chain(fns, i+1);
		}, 1000)
	};


	var create_new_tool = function() {
		var actions = [
			click_plus_search_tools_button,
			tools_close_all_accordions,
			tools_open_all_accordions,
			tools_set_name,
			tools_set_version,
			tools_set_description,
			tools_select_os_posix,
			tool_save_button
		];

		return build_chain(actions, 0)
	};

	ret.test = function(prefix) {

		ret.prefix = prefix;

		var actions = [
			create_new_tool
		];

		return build_chain(actions, 0);
	};


	window.test = ret;
	//return ret;
})();


