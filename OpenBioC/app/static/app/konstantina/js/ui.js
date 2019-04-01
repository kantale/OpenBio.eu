
/*
* generateToast('success message here', 'green lighten-2 black-text', 'stay on');
*/
function generateToast(message, classes, duration) {
    var htmlMessage = '<span>' + message + '</span><button onclick="M.Toast.dismissAll()" class="btn-flat"><i class="material-icons">close</i></button>';
    M.toast({
        html: htmlMessage,
        classes: classes,
        displayLength: duration
    });
}

// ---------------------------------------------- Warning Modal --------------------------------------------------
// $('#warningModal').modal({
//     // Callback function called before modal is closed.
//     onCloseStart: function () {
//         alert('closed');
//     },
//     dismissible: false 
// });


window.onload = function () {

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // ------------------------------------------------------------------- Initializations ------------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    function init() {

        var avatarImg = '/static/app/images/konstantina/img_avatar.png';
        var avatars = document.getElementsByClassName('imgAvatar');
        for (var i = 0; i < avatars.length; i++) {
            $(avatars[i]).attr('src', avatarImg);
        }

        // ---------------------------------------- Pushpin initialization -----------------------------------------------
        $('#scrollspyMenu').pushpin();
        // ---------------------------------------- Scrollspy initialization ---------------------------------------------
        $('.scrollspy').scrollSpy({
            scrollOffset: 200
        });
        // ----------------------------------- Sidebar for navbar initialization -----------------------------------------
        $('.sidenav').sidenav();
        // ---------------------------------------- Modal initialization -------------------------------------------------
        $('#warningModal').modal({
            dismissible: false
        });
        // -------------------------------------- Dropdown initialization ------------------------------------------------
        $(".dropdown-trigger").dropdown();
        // --------------------------------------- Tooltip initialization ------------------------------------------------
        $('.tooltipped').tooltip();

        // ---------------------------------------- Chips initialization -------------------------------------------------
        $('.chips').chips({
            placeholder: 'Enter keywords',
            secondaryPlaceholder: '+ keyword',
            autocompleteOptions: {
                data: {
                    'Apple': null,
                    'Microsoft': null,
                    'Google': null
                },
                limit: Infinity,
                minLength: 1
            }
        });

        // --------------------------------- Fixed action button initialization ------------------------------------------
        var elems = document.querySelectorAll('.fixed-action-btn');
        var instances = M.FloatingActionButton.init(elems, {
            direction: 'top',
            hoverEnabled: false
        });

        // ----------------------------------------- Sign up / Sign in Modal ---------------------------------------------
        $('#signModal').modal({
            // Callback for Modal close
            onCloseEnd: function () {
                document.getElementById('signUpForm').style.display = 'none';
                document.getElementById('signInForm').style.display = 'block';
            }
        });

        // ---------------------------------------------- Accordion ------------------------------------------------------
        var collapsibles = document.getElementsByClassName('collapsible');
        for (var i = 0; i < collapsibles.length; i++) {
            var elem = collapsibles[i];
            var instance = M.Collapsible.init(elem, {
                accordion: false,
                // Callback function called before collapsible is opened
                onOpenStart: function (event) {
                    // Workflows right panel collapsible
                    //                    if (event.id == 'workflows') {
                    //                        if (document.getElementById('workflowsRightPanel').style.display == 'none') {
                    //                            document.getElementById('workflowsRightPanel').style.display = 'block';
                    //                            $('#workflowsRightPanel').animateCss('slideInDown', function () {
                    //                            });
                    //                        }
                    //                    }
                    // Disabled collapsible
                    if (!event.classList.contains('disabled')) {
                        event.getElementsByClassName('arrow')[0].innerHTML = 'keyboard_arrow_down';
                    }
                },
                // Callback function called after collapsible is opened
                onOpenEnd: function (event) {
                    //Update all inputs and text areas so that labels are above.
                    updateTextFieldsCustom();

                    // Disabled collapsible
                    if (event.classList.contains('disabled')) {
                        event.classList.remove('active');
                    }
                    if ((event.id == 'workflowRightPanelGeneral') || (event.id == 'workflowRightPanelStep')) {
                        cy.resize();
                    }
                },
                // Callback function called before collapsible is closed
                onCloseStart: function (event) {
                    // // Workflows right panel collapsible
                    // if (event.id == 'workflows') {
                    //     if (document.getElementById('workflowsRightPanel').style.display == 'block') {
                    //         $('#workflowsRightPanel').animateCss('slideOutUp', function () {
                    //             document.getElementById('workflowsRightPanel').style.display = 'none';
                    //             // disableEditWorkflow(); // This disables the edit workflow window
                    //         });
                    //     }
                    // }
                    // Disabled collapsible
                    if (!event.classList.contains('disabled')) {
                        event.getElementsByClassName('arrow')[0].innerHTML = 'keyboard_arrow_right';
                    }
                },
                // Callback function called after collapsible is closed
                onCloseEnd: function (event) {
                    if ((event.id == 'workflowRightPanelGeneral') || (event.id == 'workflowRightPanelStep')) {
                        cy.resize();
                    }
                }

            });
        }

        // ------------------------------------ Initializations for profile page -----------------------------------------
        $('#profilePublicInfo').val(
            'Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute, non cupidatat skateboard dolor brunch. Food truck.');
        M.textareaAutoResize($('#profilePublicInfo'));
        M.updateTextFields();

        // -------------------------------- Listener for DISABLE EDIT workflow button ------------------------------------
        // document.getElementById('disableEditWorkflowBtn').addEventListener("click", disableEditWorkflow);

        // --------------------------------------- Splitter bar initialization -------------------------------------------
        $('.splitter-container').SplitterBar();
        document.getElementById('splitterBar').addEventListener('mousedown', mouseDown);
        document.getElementById('splitterBar').addEventListener('mouseup', mouseUp);
        document.addEventListener('mousedown', docMouseDown);
        document.addEventListener('mouseup', docMouseUp);
        document.addEventListener('mousemove', docMouseMove);

        document.getElementById('splitterBar').addEventListener('touchstart', mouseDown);
        document.getElementById('splitterBar').addEventListener('touchend', mouseUp);
        document.getElementById('splitterBar').addEventListener('touchcancel', mouseUp);
        document.getElementById('splitterBar').addEventListener('touchmove', docMouseMove);

        setSplitterbarPosition();
        setRowAlignment();


    }


    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // ------------------------------------------------------------ Sign up / Sign in Animations ------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    // ------------------------------------------ Sign up button clicked ---------------------------------------------
    document.getElementById('modalSignUpBtn').addEventListener('click', function () {
        $('#signInForm').animateCss('fadeOut', function () {
            document.getElementById('signInForm').style.display = 'none';
            document.getElementById('signUpForm').style.display = 'block';
            $('#signUpForm').animateCss('fadeIn', function () {
            });
        });
    });
    // ------------------------------------------ Sign in button clicked ---------------------------------------------
    document.getElementById('modalSignInBtn').addEventListener('click', function () {
        $('#signUpForm').animateCss('fadeOut', function () {
            document.getElementById('signUpForm').style.display = 'none';
            document.getElementById('signInForm').style.display = 'block';
            $('#signInForm').animateCss('fadeIn', function () {
            });
        });
    });

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // ----------------------------------------------------- Expand All / Collapse All Button Click ---------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // --------------------------------------- Expand All button clicked ---------------------------------------------
    document.getElementById('expandAllBtn1').addEventListener('click', function () {
        var instance = M.Collapsible.getInstance($('#createToolDataAccordion'));
        var childrenNum = instance.el.childElementCount;
        for (var i = 0; i < childrenNum; i++) {
            instance.open(i);
        }
    });
    document.getElementById('expandAllBtn2').addEventListener('click', function () {
        var instance = M.Collapsible.getInstance($('#editWorkflowAccordion'));
        var childrenNum = instance.el.childElementCount;
        for (var i = 0; i < childrenNum; i++) {
            instance.open(i);
        }
    });

    // -------------------------------------- Collapse All button clicked --------------------------------------------
    document.getElementById('collapseAllBtn1').addEventListener('click', function () {
        var instance = M.Collapsible.getInstance($('#createToolDataAccordion'));
        var childrenNum = instance.el.childElementCount;
        for (var i = 0; i < childrenNum; i++) {
            instance.close(i);
        }
    });
    document.getElementById('collapseAllBtn2').addEventListener('click', function () {
        var instance = M.Collapsible.getInstance($('#editWorkflowAccordion'));
        var childrenNum = instance.el.childElementCount;
        for (var i = 0; i < childrenNum; i++) {
            instance.close(i);
        }
    });

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // -------------------------------------------------------- Create Tool Data Button Click ---------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    /*
    * This function is called when the the createToolDataBtn is clicked
    * We also call this function inside angular whenever a node in the dependency tree on search panel is selected.
    * Since we want to call this from angular we have to globally register it. FIXME!!!!
    */

    window.createToolDataBtn_click = function () {
        if (document.getElementById('createToolDataDiv').style.display == 'none') {
            document.getElementById('createToolDataDiv').style.display = 'block';
            $('#createToolDataDiv').animateCss('slideInDown', function () {
                var instance = M.Collapsible.getInstance($('#createToolDataAccordion'));
                instance.open(0);
            });
        }

    };


    //    document.getElementById('createToolDataBtn').addEventListener("click", window.createToolDataBtn_click);

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // --------------------------------------------------------- Cancel Tool Data Button Click --------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    window.cancelToolDataBtn_click = function () {
        //document.getElementById('cancelToolDataBtn').addEventListener("click", function () {
        if (document.getElementById('createToolDataDiv').style.display == 'block') {
            $('#createToolDataDiv').animateCss('slideOutUp', function () {
                document.getElementById('createToolDataDiv').style.display = 'none';
                closeCollapsiblesOfAccordion('createToolDataAccordion');
            });
        }
    };

    // SHOW WORKFLKOW ACCORDION RIGHT  
    window.createWorkflowBtn_click = function () {
        if (document.getElementById('workflowsRightPanel').style.display == 'none') {
            document.getElementById('workflowsRightPanel').style.display = 'block';
            $('#workflowsRightPanel').animateCss('slideInDown', function () {
            });
        }
    };

    // HIDE WORKFLOW ACCORDION RIGHT 
    window.cancelWorkflowBtn_click = function () {
        if (document.getElementById('workflowsRightPanel').style.display == 'block') {
            document.getElementById('workflowsRightPanel').style.display = 'none';
            $('#workflowsRightPanel').animateCss('slideInDown', function () {
            });
        }
    };

    // Workflows --> Edit --> Open
    window.openEditWorkflowBtn_click = function () {
        M.Collapsible.getInstance($('#editWorkflowAccordion')).open(0);
    };

    // Workflows --> Edit --> Close
    window.closeEditWorkflowBtn_click = function () {
        M.Collapsible.getInstance($('#editWorkflowAccordion')).close(0);
    };


    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // --------------------------------------------------------- Enable Edit Workflow Button Click ----------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    //    document.getElementById('enableEditWorkflowBtn').addEventListener("click", function () {
    //        var collapsibles = document.getElementById('editWorkflowAccordion').getElementsByTagName('li');
    //        for (var i = 0; i < collapsibles.length; i++) {
    //            if (collapsibles[i].classList.contains('disabled')) {
    //                collapsibles[i].classList.remove('disabled');
    //            }
    //        }
    //        var instance = M.Collapsible.getInstance($('#editWorkflowAccordion'));
    //        instance.open(0);
    //    });

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // -------------------------------------------------------- Disable Edit Workflow Button Click ----------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    function disableEditWorkflow() {
        closeCollapsiblesOfAccordion('editWorkflowAccordion');
        var collapsibles = document.getElementById('editWorkflowAccordion').getElementsByTagName('li');
        for (var i = 0; i < collapsibles.length; i++) {
            if (!collapsibles[i].classList.contains('disabled')) {
                collapsibles[i].classList.add('disabled');
            }
        }
    }

    // Closes all collapsibles of the accordion with the given id
    function closeCollapsiblesOfAccordion(accordionId) {
        var instance = M.Collapsible.getInstance($('#' + accordionId));
        var collapsibles = document.getElementById(accordionId).getElementsByTagName('li');
        for (var i = 0; i < collapsibles.length; i++) {
            instance.close(i);
        }
    }

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // --------------------------------------------------------------------- Splitter Bar -------------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    var splitterWidth = '5px';
    var splitterWidthEdges = '15px';
    // var splitterImg = '/static/app/images/konstantina/dehaze.png';
    var minPanelWidth = 320;
    var isDragging = false;
    var mousedown = false;
    var dragEnabled;

    var offsetX = 0;
    var offsetY = 0;
    var lastX, lastY;
    var dragHash;

    var leftSide;
    var rightSide;
    var leftWidth;
    var splitterBar;

    $.fn.SplitterBar = function () {
        $(this).css('display', 'flex');

        leftSide = $(this).children('.leftPanel').first();
        rightSide = $(this).children('.rightPanel').first();

        leftWidth = Math.floor($(window).width() / 2);
        leftSide.css('width', leftWidth + 'px');

        rightSide.css('flex', '1');

        var newDiv = document.createElement('div');
        $(newDiv).attr('id', 'splitterBar');

        splitterBar = $(newDiv);
        splitterBar.css('background-color', '#cfd8dc');
        splitterBar.css('box-shadow', '0 0 10px rgba(0, 0, 0, 0.6)');
        splitterBar.css('z-index', '100');
        splitterBar.css('height', '100%');
        splitterBar.css('cursor', 'w-resize');
        if (Math.floor($(window).width()) < ((2 * minPanelWidth) + parseInt(splitterWidth, 10))) {
            splitterBar.css('width', splitterWidthEdges);
        }
        else {
            splitterBar.css('width', splitterWidth);
        }
        leftSide.after(splitterBar);

        setSplitterContainerHeight();
    }

    // ----------------------------------------- Splitter bar mousedown and touchstart ---------------------------------------------
    function mouseDown(event) {
        isDragging = true;
        mousedown = true;

        lastX = parseInt(event.clientX - offsetX);
        lastY = parseInt(event.clientY - offsetY);
        if (Number.isNaN(lastX) && Number.isNaN(lastY)) {
            lastX = parseInt(event.changedTouches[0].clientX - offsetX);
            lastY = parseInt(event.changedTouches[0].clientY - offsetY);
        }
        dragHash = 0;

        return false;
    };

    // ------------------------------------------- Splitter bar mouseup and touchend ---------------------------------------------
    function mouseUp(event) {
        isDragging = false;
        mousedown = false;

        mouseX = parseInt(event.clientX - offsetX);
        mouseY = parseInt(event.clientY - offsetY);
        if (Number.isNaN(mouseX) && Number.isNaN(mouseY)) {
            mouseX = parseInt(event.changedTouches[0].clientX - offsetX);
            mouseY = parseInt(event.changedTouches[0].clientY - offsetY);
        }

        // It's a click
        if ((dragHash <= 5) || (!dragEnabled)) {
            var leftOfLeft = leftSide.position().left;
            var screenWidth = Math.floor($(window).width());
            var eventPageX = event.pageX;
            if (eventPageX == undefined) {
                eventPageX = parseInt(event.changedTouches[0].pageX);
            }
            var leftWidth = eventPageX - leftOfLeft - splitterBar.width() / 2;
            var rightWidth = screenWidth - (eventPageX + leftOfLeft + splitterBar.width() / 2);

            // Show left panel
            if (leftWidth <= parseInt(splitterWidthEdges, 10)) {
                if (dragEnabled) {
                    leftSide.width(minPanelWidth);
                }
                else {
                    leftSide.width(screenWidth - parseInt(splitterWidthEdges, 10));
                }
            }
            // Show right panel
            else if (rightWidth <= parseInt(splitterWidthEdges, 10)) {
                if (dragEnabled) {
                    leftSide.width(screenWidth - minPanelWidth - parseInt(splitterWidth, 10));
                }
                else {
                    leftSide.width(0);
                }
            }
            // Hide left panel
            else if (leftWidth <= minPanelWidth + parseInt(splitterWidth, 10)) {
                leftSide.width(0);
            }
            // Hide right panel
            else if (rightWidth <= minPanelWidth + parseInt(splitterWidth, 10)) {
                leftSide.width(screenWidth);
            }
            setRowAlignment();
            setSlitterbarWidth();
        }

        return false;
    };

    // ------------------------------------------------ Mouse down ---------------------------------------------------
    function docMouseDown(event) {
        mousedown = true;
    };

    // ------------------------------------------------- Mouse up ----------------------------------------------------
    function docMouseUp(event) {
        mousedown = false;
    };

    // ------------------------------------------------ Mousemove and touchmove ---------------------------------------------------
    function docMouseMove(event) {
        if (isDragging) {
            mouseX = parseInt(event.clientX - offsetX);
            mouseY = parseInt(event.clientY - offsetY);
            if (Number.isNaN(mouseX) && Number.isNaN(mouseY)) {
                mouseX = parseInt(event.changedTouches[0].clientX - offsetX);
                mouseY = parseInt(event.changedTouches[0].clientY - offsetY);
            }

            var dx = mouseX - lastX;
            var dy = mouseY - lastY;
            lastX = mouseX;
            lastY = mouseY;

            // accumulate the drag distance 
            // (used in mouseup to see if this is a drag or click)
            dragHash += Math.abs(dx) + Math.abs(dy);

            if ((dragHash > 5) && dragEnabled) {
                // it's a drag operation
                var leftOfLeft = leftSide.position().left;
                var screenWidth = Math.floor($(window).width());
                var eventPageX = event.pageX;
                if (eventPageX == undefined) {
                    eventPageX = parseInt(event.changedTouches[0].pageX);
                }
                var leftWidth = eventPageX - leftOfLeft - splitterBar.width() / 2;
                var rightWidth = screenWidth - (eventPageX + leftOfLeft + splitterBar.width() / 2);

                // Hide left panel
                if (leftWidth <= minPanelWidth) {
                    if (eventPageX <= minPanelWidth - ((2 / 3) * minPanelWidth)) {
                        leftSide.width(0);
                        setRowAlignment();
                        setSlitterbarWidth();
                    }
                    if (!mousedown) {
                        isDragging = false;
                    }
                    return;
                }
                // Hide right panel
                else if (rightWidth <= minPanelWidth) {
                    if (eventPageX >= screenWidth - (minPanelWidth - ((2 / 3) * minPanelWidth))) {
                        leftSide.width(screenWidth);
                        setRowAlignment();
                        setSlitterbarWidth();
                    }
                    if (!mousedown) {
                        isDragging = false;
                    }
                    return;
                }
                // Move splitter bar
                else {
                    leftSide.width(eventPageX - leftOfLeft - splitterBar.width() / 2);
                    setRowAlignment();
                    setSlitterbarWidth();
                    return;
                }
            }
        }
    };

    // ---------------------------------------------- Window resize --------------------------------------------------
    window.onresize = function (event) {
        setSplitterContainerHeight();
        setSplitterbarPosition();
        setRowAlignment();
    };

    // ----------------------------------- Sets Splitter bar in the middle of screen ---------------------------------
    function setSplitterbarPosition() {
        var screenWidth = Math.floor($(window).width());

        if (screenWidth < ((minPanelWidth * 2) + parseInt(splitterWidth, 10))) {
            dragEnabled = false;
            var newLeftWidth = Math.floor($(window).width() - parseInt(splitterWidthEdges, 10));
            document.getElementById('splitterBar').style.width = splitterWidthEdges;
            document.getElementsByClassName('leftPanel')[0].setAttribute('style', 'width:' + newLeftWidth + 'px');
        }
        else {
            dragEnabled = true;
            var newLeftWidth = Math.floor(($(window).width() - parseInt(splitterWidth, 10)) / 2);
            document.getElementById('splitterBar').style.width = splitterWidth;
            document.getElementsByClassName('leftPanel')[0].setAttribute('style', 'width:' + newLeftWidth + 'px');
        }
        setSlitterbarWidth();
    }

    // Sets the height of splitter container
    function setSplitterContainerHeight() {
        var screenHeight = Math.floor($(window).height());
        var navbarHeight = document.getElementById('navbar').offsetHeight;
        document.getElementsByClassName('splitter-container')[0].style.height = (screenHeight - navbarHeight) + 'px';
    }

    function setSlitterbarWidth() {
        var leftWidth = document.getElementsByClassName('leftPanel')[0].offsetWidth;
        var rightWidth = document.getElementsByClassName('rightPanel')[0].offsetWidth;

        if (leftWidth == 0 || rightWidth == 0) {
            document.getElementById('splitterBar').style.width = splitterWidthEdges;
        }
        else {
            document.getElementById('splitterBar').style.width = splitterWidth;
        }
    }

    // -------------------------------------- Update text inputs and textareas ---------------------------------------
    //To permanently remove label animation with JQuery: $('#editWorkflowNameLabel').addClass('active')
    function updateTextFieldsCustom() {
        M.updateTextFields();
        var textareas = document.getElementsByClassName('materialize-textarea');
        for (var i = 0; i < textareas.length; i++) {
            M.textareaAutoResize($(textareas[i]));
        }
    }

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // ----------------------------------------------------------------- Responsive Panels ------------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    // ---------------------------------------- Fix row alignment for panels -----------------------------------------    
    function setRowAlignment() {
        var sizeForLeft = getSizeForPanelWidth(document.getElementsByClassName('leftPanel')[0].offsetWidth);
        var sizeForRight = getSizeForPanelWidth(document.getElementsByClassName('rightPanel')[0].offsetWidth);

        var itemsLeftPanel = getElementsWithGridClass(document.getElementsByClassName('leftPanel')[0].getElementsByClassName('col'));
        var itemsRightPanel = getElementsWithGridClass(document.getElementsByClassName('rightPanel')[0].getElementsByClassName('col'));

        setGridClassToElements(itemsLeftPanel, sizeForLeft);
        setGridClassToElements(itemsRightPanel, sizeForRight);

        // Update text inputs and textareas
        updateTextFieldsCustom();

        //When moving splitter , readjust cytoscape positions. 
        //Cytospcape avoids doing that, for efficiency
        if (typeof cy !== 'undefined') {
            cy.resize();
        }
    }

    // -------------------------------- Get elements which row alignment should be fixed  ----------------------------    
    function getElementsWithGridClass(elements) {
        var elementsGrid = [];
        for (var i = 0; i < elements.length; i++) {
            var classList = elements[i].classList;
            for (k = 0; k < classList.length; k++) {
                if (classList[k].indexOf('grid') !== -1) {
                    elementsGrid.push(elements[i]);
                    break;
                }
            }
        }
        return elementsGrid;
    }

    // ------------------------------------- Get appropiate size for panel width --------------------------------------    
    function getSizeForPanelWidth(panelWidth) {
        if (panelWidth <= 600) {
            return 'small';
        }
        else if (panelWidth <= 992) {
            return 'medium';
        }
        else {
            return 'large';
        }
    }

    // ----------------------------------- Set element width relative to panel width ---------------------------------    
    function setGridClassToElements(itemsPanel, sizePanel) {
        for (var i = 0; i < itemsPanel.length; i++) {
            var classList = itemsPanel[i].classList;
            for (k = 0; k < classList.length; k++) {
                if (classList[k].indexOf('grid') !== -1) {
                    var str = classList[k];
                    var small, medium, large;
                    str = str.split('-');
                    if (str[1].charAt(0) == 's') {
                        small = str[1].split('s')[1];
                    }
                    if (str[2].charAt(0) == 'm') {
                        medium = str[2].split('m')[1];
                    }
                    if (str[3].charAt(0) == 'l') {
                        large = str[3].split('l')[1];
                    }
                    break;
                }
            }

            for (k = 0; k < classList.length; k++) {
                if (classList[k].indexOf('gridRow') !== -1) {
                    itemsPanel[i].classList.remove(classList[k]);
                    break;
                }
            }

            if (sizePanel == 'small') {
                itemsPanel[i].classList.add('gridRow' + small);
            }
            else if (sizePanel == 'medium') {
                itemsPanel[i].classList.add('gridRow' + medium);
            }
            else {
                itemsPanel[i].classList.add('gridRow' + large);
            }
        }
    }

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // --------------------------------------------------------------- Animate Css --------------------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    $.fn.extend({
        animateCss: function (animationName, callback) {
            var animationEnd = (function (el) {
                var animations = {
                    animation: 'animationend',
                    OAnimation: 'oAnimationEnd',
                    MozAnimation: 'mozAnimationEnd',
                    WebkitAnimation: 'webkitAnimationEnd',
                };

                for (var t in animations) {
                    if (el.style[t] !== undefined) {
                        return animations[t];
                    }
                }
            })(document.createElement('div'));

            this.addClass('animated ' + animationName).one(animationEnd, function () {
                $(this).removeClass('animated ' + animationName);

                if (typeof callback === 'function') callback();
            });

            return this;
        },
    });

    init();

    // END OF KONSTANTINA'S CODE

    // START OF KANTALE'S CODE

    if (true) {

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
    }

    //* It is important to register these events AFTER load so that they are triggered after custom JSTREE functions
    //* More: https://groups.google.com/forum/#!topic/jstree/BYppISuCFRE

    // https://github.com/ezraroi/ngJsTree/issues/20
    // We have to register the event on the document.. 
    $(document).on('dnd_stop.vakata', function (e, data) {


        //console.log('tessssttt');

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

            //The tools that we are dragging.
            var tool = {
                'name': this_id_array[0],
                'version': this_id_array[1],
                'edit': this_id_array[2]
            };

            //console.log(tool);

            if (target.closest('#tools_dep_jstree_id').length) { // We are dropping it to the dependency tool js tree div

                //console.log('Right stop');
                //console.log(tool);
                angular.element($('#angular_div')).scope().$apply(function () {
                    angular.element($('#angular_div')).scope().tool_get_dependencies(tool, 1); // 1 = drag from search jstree to dependencies jstree
                });
            }
            else if (target.closest('#cywf').length) { // We are dropping it to the workflow graph editor. //Changed from old: d3wf

                angular.element($('#angular_div')).scope().$apply(function () {
                    angular.element($('#angular_div')).scope().tool_get_dependencies(tool, 2); // 2 = drag from search jstree to workflow editing
                });

                //window.update_workflow();
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
        else if (this_id_array[2] == '4') { // this is an item from workflows_search_tree droped on the cytoscape window. The id is the 3rd element
            if (target.closest('#cywf').length && (!workflow_step_editor.getReadOnly())) {

                var workflow = {
                    name : this_id_array[0],
                    edit : this_id_array[1]
                };

                angular.element($('#angular_div')).scope().$apply(function () {
                    angular.element($('#angular_div')).scope().workflow_add_workflow(workflow); 
                });
            }
            else {
                // Do nothing
            }
        }

    });



    /*
    * JSTree item moves. Change the class (for visualization only)
    */
    $(document).on('dnd_move.vakata', function (e, data) {
        //      $('#vakata-dnd').find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
        //      return;
        var target = $(data.event.target);
        var this_id = data.data.nodes[0]; // plink/1.9/3/1"

        //var this_id_array = this_id.split('/'); //[ "plink", "1.9", "3", "1" ]
        var this_id_array = JSON.parse(this_id);


        if (this_id_array[3] == '1') { // This is an item from tools_search tree

            if (
                (target.closest('#tools_dep_jstree_id').length && (!tool_installation_editor.getReadOnly())) || //We allow it if it is over the div with the tree AND the the tool_installation_editor is not readonly (this is a workaround to avoid checking angular: tools_info_editable)
                (target.closest('#cywf').length && (!workflow_step_editor.getReadOnly())) // The Workflow graph editor . // changed from . d3wf
            ) {
                data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
            }
            else {
                data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
            }
        }

        else if (this_id_array[3] == "3") { // This is an item from validation js tree

            if (
                (target.closest('#tool_installation_editor').length && (!tool_installation_editor.getReadOnly())) ||
                (target.closest('#tool_validation_editor').length && (!tool_validation_editor.getReadOnly()))) {
                data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
            }
            else {
                data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
            }

        }
        else if (this_id_array[2] == '4') { // this is an item from workflows_search_tree. The id is the 3rd element
            if (target.closest('#cywf').length && (!workflow_step_editor.getReadOnly())) {
                data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
            }
            else {
                data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
            }
        }


    });

    // END OF KANTALE'S CODE

    // START OF GALATEIA'S CODE

    //Cytoscape Galateia's code
    if (true) {

        /**
        global vars intiialization
        **/
        //var cy;

        //openIds = [];

        /*
        * Creates a "unique" id from a workflow
        * ATTENTION! This should be in accordance with the python function create_workflow_id in views.py
        */
        function create_workflow_id(workflow) {
            return workflow.name + '__' + workflow.edit; //It is ok if this is wf1__null
        }

        /*
        * Create a step ID. This contains: name of step, name of workflow, edit of workflow
        */
        function create_step_id(step, workflow) {
            return step.name + '__' + create_workflow_id(workflow);
        }

        /*
        * Create a unique input/output variable ID. This contains the input/output name, name workflow and edit of worfkflow
        */
        function create_input_output_id(input_output, workflow) {
            return input_output.name + '__' + create_workflow_id(workflow);
        }

        /*
        * Create a suitable worfklow name
        */
        function create_workflow_label(workflow) {
            if (workflow.edit) {
                return workflow.name + '/' + workflow.edit;
            }
            return workflow.name;
        }

        /*
        * Create a "unique" id for an edge 
        * ATTENTION! This should be in accordance with the python function create_workflow_edge_id in views.py
        */
        function create_workflow_edge_id(source_id, target_id) {
            return source_id + '..' + target_id;
        }

        /*
        * parse data from openbioc to meet the cytoscape.js requirements
        * Create cytoscape nodes and edges
        * incomingData: List of nodes to add
        * belongto: the workflow to be added to
        */
        function parseWorkflow(incomingData, belongto) {
            console.log('parseWorkflow incomingData:');
            console.log(incomingData);

            console.log('belongto:');
            console.log(belongto);

            var myNodes = [], myEdges = [];

            /*initialize my data object*/
            incomingData.forEach(function (d) {

                var this_node_wf_belong_to = d.belongto ? d.belongto : belongto; // In which worfklow does this node belong to? 
                var this_node_wf_belong_to_id = create_workflow_id(this_node_wf_belong_to);


                //INPUTS/OUTPUTS
                if (d.type === 'input' || d.type === 'output') {
                    var this_input_output_id = create_input_output_id(d, this_node_wf_belong_to);

                    var myNode = {data: {id: this_input_output_id, label: d.name, name: d.name, type: d.type, description: d.description, belongto: this_node_wf_belong_to}};
                    myNodes.push(myNode);
                    //Connect with belongto workflow
                    myEdges.push({data: {source: this_node_wf_belong_to_id, target: this_input_output_id, id: create_workflow_edge_id(this_node_wf_belong_to_id, this_input_output_id)}});
                }
				

                //TOOLS 
                if (d.type === "tool") {
      
                    //If d.id is a JSON string parse it. d.id might come either from jstree (needs parsing) or cytoscape (does not need parsing)
                    if (d.id.indexOf('[')>-1) {
                        d.id = JSON.parse(d.id).join('__');
                        /*remove special characters*/
                        //d.id = d.id.replace(/\./g,''); // CYTOSCAPE ALLOWS . IN IDS
                    }

                    if ("parent" in d) {
                        d.dep_id = d.parent;
                        d.parent = '#';
                    }

                    if (d.dep_id != "#") {
                        if (d.dep_id.indexOf('[')>-1) { // Parse it if this is JSON. 
                            d.dep_id = JSON.parse(d.dep_id).join('__');
                            /*remove special characters*/
                           // d.dep_id = d.dep_id.replace(/\./g,''); //CYTOSCAPE ALLOWS . IN IDS
                        }

                        //var myNode = { data: { id: d.id, text:d.text, label: d.text, name: d.data.name, version: d.data.version, edit: d.data.edit, type: d.data.type, root: 'no', variables: d.variables } };
                        var myNode = { data: { id: d.id, text:d.text, label: d.text, name: d.name, version: d.version, edit: d.edit, type: d.type, root: 'no', dep_id: d.dep_id, variables: d.variables, belongto: this_node_wf_belong_to } };

                        myNodes.push(myNode);
                        var myEdge = { data: { id: create_workflow_edge_id(d.dep_id, d.id), weight: 1, source: d.dep_id, target: d.id } };
                        myEdges.push(myEdge);
						
                    } else {
                        //var myNode = { data: { id: d.id, label: d.text, name: d.data.name, version: d.data.version, edit: d.data.edit, type: d.data.type, root: 'yes', variables: d.variables } };
                        var myNode = { data: { id: d.id, text:d.text, label: d.text, name: d.name, version: d.version, edit: d.edit, type: d.type, root: 'yes', dep_id: d.dep_id, variables: d.variables, belongto: this_node_wf_belong_to } };
                        myNodes.push(myNode);
                        myEdges.push({data: {source: this_node_wf_belong_to_id, target: d.id, id: create_workflow_edge_id(this_node_wf_belong_to_id, d.id)}});
                    }

                }
				
				 //WORKFLOWS
				 if (d.type === "workflow") {
					//TODO add root feature (different than tools): wfroot:yes
				    
                    var this_workflow_id = create_workflow_id(d);

                    var myNode = { data: { id: this_workflow_id, name: d.name, edit: d.edit, label: create_workflow_label(d), type: 'workflow', belongto: this_node_wf_belong_to} };
                    myNodes.push(myNode);
                    myEdges.push({data: {source: this_node_wf_belong_to_id, target: this_workflow_id, id:create_workflow_edge_id(this_node_wf_belong_to_id, this_workflow_id)}});
                }


                //STEPS
                if (d.type === "step") {
                    //Why this redundancy?
                    //jstree uses d.name, cytoscape uses d.label and we also need an id...
                    var this_step_id = create_step_id(d, this_node_wf_belong_to);
                    var myNode = { data: { id: this_step_id, name:d.name, label: d.name, type: d.type, bash: d.bash, tools:d.tools, steps:d.steps, inputs:d.inputs, outputs:d.outputs, belongto: this_node_wf_belong_to } };
                    myNodes.push(myNode);
                    
                    //Connect with belong workflow
                    myEdges.push({data: {source:this_node_wf_belong_to_id, target: this_step_id, id:create_workflow_edge_id(this_node_wf_belong_to_id, this_step_id) }});
                    
                    //create edges to tools and/or steps
                    if (typeof d.tools !== "undefined") {
                        //replace special characters

                        d.tools.forEach(function (element) {
                            //element = element.replace(/\[/g, '').replace(/]/g, '').replace(/"/g, '').replace(/,/g, '').replace(/ /g, '');

                            var myEdge = { data: { 'id': create_workflow_edge_id(this_step_id, element)  , 'weight': 1, 'source': this_step_id, 'target': element } };
                            myEdges.push(myEdge);

                        });
                    }

                    if (typeof d.steps !== "undefined") {
                        d.steps.forEach(function (element) {
							
                            var myEdge = { data: { 'id': create_workflow_edge_id(this_step_id, element), 'weight': 1, 'source': this_step_id, 'target': element } };
                            myEdges.push(myEdge);

                        });
                    }
					
					
					 if (typeof d.inputs !== "undefined") {
                        d.inputs.forEach(function (element) {
                            var myEdge = { data: { 'id': create_workflow_edge_id(element, this_step_id), 'weight': 1, 'source': element, 'target': this_step_id } };
                            myEdges.push(myEdge);

                        });
                    }
					
					if (typeof d.outputs !== "undefined") {
                        d.outputs.forEach(function (element) {
                            var myEdge = { data: { 'id': create_workflow_edge_id(this_step_id, element), 'weight': 1, 'source': this_step_id, 'target': element } };
                            myEdges.push(myEdge);

                        });
                    }
                }

            });

            console.log('NODES:');
            console.log(myNodes);
            console.log('EDGES:');
            console.log(myEdges);



            return {
                nodes: myNodes,
                edges: myEdges
            };



        }
		
		
		/*
		* This function closes the successors of a workflow and/or tool except the input/output
		* Should be use every time a tool or workflow is dr&dropped in the workflow editor
		* and everytime a tool or workflow is clicked in the right menu
		*/
		window.cy_close_successors = function(){
			
			// close all successors of root node or workflow node	: except inputs and outputs or other wfs
            cy.json().elements.nodes.forEach(function (node) {
				
				//close the successors of a (previous saved) workflow  except the inouts/outputs
				if(node.data.type==="workflow"  &&  node.data.edit!=="null"){
					cy.$("#" + node.data.id).successors().targets().forEach(function (element) {
				
						if(element['_private'].data.type ==='input' || element['_private'].data.type ==='output' || element['_private'].data.type ==='workflow' ){
								element.style("display", "element");
						}else{					
							element.style("display", "none");
						}
								
					});
					
					//cy.$("#" + node.data.id).successors().targets().style("display", "none");
				}
				
				if(node.data.type==="tool" && typeof node.data.root !== 'undefined' && node.data.root === 'yes')
					 cy.$("#" + node.data.id).successors().targets().style("display", "none");
				
               // if (typeof node.data.root !== 'undefined' && node.data.root === 'yes') //TODO check for "wfroot:yes"
               //    cy.$("#" + node.data.id).successors().targets().style("display", "none");

            });
			
			
		}

        /*
        * After importing a graph or adding new nodes, we need to register cytoscape events.
        * This function is called from buildtree and also from angular when we do: cy.json(data['workflow']) from angular
        */
        window.cy_setup_events = function() {
            // collapse - expand nodes
            cy.on('click', 'node', function (event) {
                //connectedEdges: next level
                //successors: next levels recursively

                if (this['_private'].data.type !== "step") { //steps should never collapse
                    if (this.successors().targets().style("display") == "none") {
                        this.connectedEdges().targets().style("display", "element");
                    } else {
                        //hide the children nodes and edges recursively  
						this.successors().targets().forEach(function (element) {
								//check if node has flag(open)								
								if(typeof element['_private'].data.flag ==='undefined' || element['_private'].data.flag !=='open'){
									element.style("display", "none");
								}
								
							});
                    }
                }
                if (this['_private'].data.type == "step") { // Click at a step node
                    //Call angular function
                    var this_data = this['_private'].data;
                    angular.element($('#angular_div')).scope().$apply(function () {
                        angular.element($('#angular_div')).scope().workflop_step_node_clicked(this_data); 
                    });
                }

            });

            /* show tooltip */
            cy.on('mouseover', 'node', function (event) {
                  

                nodeId = this._private.data.id
                myNode = cy.getElementById(nodeId);

               console.log("SHOW TOOLTIP : ");
               console.log(nodeId);  

                //tippy
                var makeTippy = function (node, text) {
                    return tippy(node.popperRef(), {
                        content: function () {
                            var div = document.createElement('div');
                            div.innerHTML = text;
                            return div;
                        },
                        trigger: 'manual',
                        arrow: true,
                        placement: 'right',
                        hideOnClick: false,
                        multiple: true,
                        //followCursor: true,
                        //theme: 'light', 
                        sticky: true
                    });
                };

                myTippy = makeTippy(myNode, nodeId);
                myTippy.show();


            });

            // hide tooltip
            cy.on('mouseout', 'node', function (event) {
               console.log("HIDE TOOLTIP");
               console.log(this._private.data.id);

                myTippy.destroy();    
                //myTippy.hide();
            });

        }

        function initializeTree() {

            cy = cytoscape({
                container: document.getElementById('cywf'), // container to render in
                elements:[],

                //elements: [ // list of graph elements to start with
                //      { // node a
                //        data: { id: 'a' }
                //      },
                //      { // node b
                //        data: { id: 'b' }
                //      },
                //      { // edge ab
                //        data: { id: 'ab', source: 'a', target: 'b' }
                //      }
                //],

                style: [ // the stylesheet for the graph
                    {
                        selector: 'node',
                        "style": {
                            "shape": "round-rectangle",
							"background-color": "#AFB4AE",
                            //"label": "data(id)",
                            "label": "data(label)",
                            //"height": 15,
                            //"width": 15
                        }
                    },
                    {
                        selector: 'node[type="step"]',
                        "style": {
                            'shape': 'ellipse',
							'background-color': '#007167',
                            //'background-color': '#E8E406',
                            //"height": 15,
                            //"width": 15
                        }
                    },
                    {
                        selector: 'node[type="input"]',
                        "style": {
                            'shape': 'round-rectangle',
							'border-width' : '3',
							'border-color' : '#43A047',
                            'background-color': '#AFB4AE',
                            //"height": 15,
                            //"width": 15
                        }
                    },
                    {
                        selector: 'node[type="output"]',
                        "style": {
                            'shape': 'round-rectangle',
							'border-width' : '3',
							'border-color' : '#E53935',
                            'background-color': '#AFB4AE',
                            //"height": 15,
                            //"width": 15
                        }
                    },
					
					{
                        selector: 'node[type="workflow"]',
                        "style": {
                            'shape': 'diamond',
							'border-width' : '3',
							'border-color' : '#E53935',
                            'background-color': '#AFB4AE',
                            //"height": 15,
                            //"width": 15
                        }
                    },
//                    {
//                        //Do not show the root workflow 
//                        selector: 'node[type="workflow"][!belongto]',
//                        "style": {
//                            "display": "none"
//                        }
//                    },
                    {
                        selector: 'edge',
                        "style": {
                            'curve-style': 'bezier',
                            'target-arrow-shape': 'triangle',
                            'width': 2,
                            'line-color': '#ddd',
                            'target-arrow-color': '#ddd'
                        }
                    }
                ],

                //zoom: 1,
                pan: { x: 0, y: 0 },

                layout: {
                    name: 'breadthfirst',
                    directed: true,
                    padding: 2
                }



            });

            /* add menu on node right click*/

            cy.cxtmenu({
                selector: 'node',
                commands: [
                    {
                        content: 'Edit',
                        select: function (ele) {
                            console.log("edit");
                        }
                    },
                    {
                        content: 'Delete',
                        select: function (ele) {
                            var j = cy.$('#' + ele.id());
                            
							/* remove node successors*/
							j.successors().targets().forEach(function (element) {
									cy.remove(element);
								
							})
							/*remove node*/
							cy.remove(j);

                        }
                    }
                ]

            });


            //This removes the attribute: position: 'absolute' from the third layer canvas in cytoscape.
            document.querySelector('canvas[data-id="layer2-node"]').style.position = null;

        }


        initializeTree();


        /* 
        * add new data to the graph
        * activate the collapse-expand option
        * This function is getting called from angular
        * myworkflow: list of nodes to add
        * belongto: The worfklow node. myworkflow data will be added to belongto
        */
        window.buildTree = function (myworkflow, belongto) {
            //function buildTree(myworkflow) {

            // get existing data if any
            currentElements = cy.json().elements;

            console.log('currentElements');
            console.log(currentElements);

            // parse incoming data and transform to cytoscape format
            var treeData = parseWorkflow(myworkflow, belongto);
            var openId;
            
            //concat all data
            if (typeof currentElements.nodes !== 'undefined') {
				
                /* check if new node exists in current data */
				 treeData.nodes.forEach(function(element) {
					 currentElements.nodes.forEach(function(celement){
						if(element.data.id===celement.data.id){
		    				openId=celement.data.id;						
						}
					 });      
				});

			
                var allNodes = [], allEdges = [];
                allNodes = currentElements.nodes.concat(treeData.nodes);
				
                if (typeof currentElements.edges !== 'undefined' && typeof treeData.edges !== 'undefined') {
                    allEdges = currentElements.edges.concat(treeData.edges);
                }
                else {
                    if (typeof currentElements.edges !== 'undefined')
                        allEdges = currentElements.edges;
                    if (typeof treeData.edges !== 'undefined')
                        allEdges = treeData.edges;
                }
                treeData = {
                    nodes: allNodes,
                    edges: allEdges
                };

                console.log('treedata');
                console.log(treeData);	
            }

            // this is needed because cy.add() causes multiple instances of layout
            initializeTree();

            cy.json({ elements: treeData });   // Add new data
            cy.ready(function () {           // Wait for nodes to be added  
                cy.layout({                   // Call layout
                    name: 'breadthfirst',
                    directed: true,
                    padding: 2
                }).run();

            });

		  
            //Add open flag for nodes that should always stay open (these are the nodes that belong to more than one tool)
            cy.$('#'+openId).data('flag', 'open');
			
			
            

			console.log("start setup events");
            window.cy_setup_events();
			console.log("stop setup events");
        }


        /*
        * Deletes all elements
        * Adds a root workflow node
        */
        window.clear = function (name) {
            //cy.destroy();
            cy.remove('edge, node');

             cy.json({
                elements: {
                    nodes: [{data: {id: create_workflow_id({name:name, edit: null}), label: name, name:name, edit: null, type: "workflow", belongto:null}}]
                }
            });

            cy.resize();
            cy.reset();
            cy.center();

        }

		/*
		* Fits workflow's content in center
		*/
        window.fit = function () {
            cy.reset();
            cy.center();

        }
		
		/*
		* Re-run the layout of cytoscape
		*/
		window.redraw = function(){
			
		   cy.layout({// Call layout
                    name: 'breadthfirst',
                    directed: true,
                    padding: 2
                }).run();	
			
		}
    }


    // END OF GALATEIA'S CODE


};