
/*
* generateToast('success message here', 'green lighten-2 black-text', 'stay on');
*/
function generateToast(message, classes, duration) {
    var htmlMessage = '<span>' + message + '</span><button onclick="closeToastClicked(event)" class="btn-flat"><i class="material-icons">close</i></button>';
    M.toast({
        html: htmlMessage,
        classes: classes,
        displayLength: duration
    });
}
function closeToastClicked (event) {
    var toast = $(event.target).parents('.toast').first();
    var toastInstance = M.Toast.getInstance(toast);
    toastInstance.dismiss();
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
        // ---------------------------------------- Select initialization ------------------------------------------------
        $('select').formSelect();
        // ------------------------------------- Collapsible initialization ----------------------------------------------
        $('.collapsible').collapsible();
        // -------------------------------------- Datepicker initialization ----------------------------------------------
        $('.datepicker').datepicker();

        // ---------------------------------------- Chips initialization -------------------------------------------------
        $('#toolChips').chips({
            placeholder: 'Enter keywords',
            secondaryPlaceholder: '+ keyword',
            autocompleteOptions: {
                data: {
// Some examples
//                    'Apple': null,
//                    'Microsoft': null,
//                    'Google': null
                },
                limit: Infinity,
                minLength: 1
            }
        });

        $('#workflowChips').chips({
            placeholder: 'Enter keywords',
            secondaryPlaceholder: '+ keyword',
            autocompleteOptions: {
                data: {
                },
                limit: Infinity,
                minLength: 1
            }
        });


        $('#searchChips').chips({
            placeholder: 'Enter keywords',
            secondaryPlaceholder: '+ keyword',
            autocompleteOptions: {
                data: {
                },
                limit: Infinity,
                minLength: 1
            }
        });

        // --------------------------------- Fixed action button initialization ------------------------------------------
        $('.fixed-action-btn').floatingActionButton();
        // var elems = document.querySelectorAll('.fixed-action-btn');
        // var instances = M.FloatingActionButton.init(elems, {
        //     direction: 'top',
        //     hoverEnabled: false
        // });

        // ----------------------------------------- Sign up / Sign in Modal ---------------------------------------------
        $('#signModal').modal({
//            // Callback for Modal close
//            onCloseEnd: function () {
//                document.getElementById('signUpForm').style.display = 'none';
//                document.getElementById('signInForm').style.display = 'block';
//            }
        });

        // ---------------------------------------------- Accordion ------------------------------------------------------
        var collapsibles = document.getElementsByClassName('collapsible expandable');
        for (var i = 0; i < collapsibles.length; i++) {
            var elem = collapsibles[i];
            var instance = M.Collapsible.init(elem, {
                accordion: false,
                // Callback function called before collapsible is opened
                onOpenStart: function (event) {
                    // ----------------------------------------------------------------------------------------------
                    // ---------------------------------------- DELETE START ----------------------------------------
                    // ----------------------------------------------------------------------------------------------
                    //if (event.id == 'references') {
                    //    document.getElementById('referencesRightPanel').style.display = 'block';
                    //}
                    //else if (event.id == 'qa') {
                    //    document.getElementById('QARightPanel').style.display = 'block';
                    //}
                    // ----------------------------------------------------------------------------------------------
                    // ---------------------------------------- DELETE END ------------------------------------------
                    // ----------------------------------------------------------------------------------------------


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
                    if (event.id == 'toolsDataInstallation') {
                        $('#tool_os_choices_select').formSelect();
                    }
                    if ((event.id == 'workflowRightPanelGeneral') || (event.id == 'workflowRightPanelStep')) {
                        cy.resize();
                    }
                    if (event.id == 'workflowRightPanelStep') {

                    }
                    if (event.id == 'reportsTimeline') {
                        window.OBCUI.timeline.redraw();
                        window.OBCUI.timeline.fit(); // https://github.com/almende/vis/issues/3193
                    }


                },
                // Callback function called before collapsible is closed
                onCloseStart: function (event) {
                    // Disabled collapsible
                    if (!event.classList.contains('disabled')) {
                        event.getElementsByClassName('arrow')[0].innerHTML = 'keyboard_arrow_right';
                    }

                    // ----------------------------------------------------------------------------------------------
                    // ---------------------------------------- DELETE START ----------------------------------------
                    // ----------------------------------------------------------------------------------------------
                    if (event.id == 'references') {
                        document.getElementById('referencesRightPanel').style.display = 'none';
                    }
                    // ----------------------------------------------------------------------------------------------
                    // ---------------------------------------- DELETE END ------------------------------------------
                    // ---------------------------------------------------------------------------------------------- 
                },
                // Callback function called after collapsible is closed
                onCloseEnd: function (event) {
                    if ((event.id == 'workflowRightPanelGeneral') || (event.id == 'workflowRightPanelStep')) {
                        cy.resize();
                    }
                }

            });
        }

        // Preloader toogle button . TEST progress bar
//        document.getElementById('preloaderBtn').addEventListener('click', function () {
//            if (document.getElementById('leftPanelProgress').style.display == 'block') {
//                document.getElementById('leftPanelProgress').style.display = 'none';
//            }
//            else {
//                document.getElementById('leftPanelProgress').style.display = 'block';
//            }
//        });


        // Refresh btn on installation header
        $('.collapsible-header').click(function (event) {
            // Refresh button
            if ((event.target.id == 'installationRefreshBtn') || (event.target.parentNode.id == 'installationRefreshBtn')) {
                event.stopPropagation();
                //console.log('refresh button clicked');
            }
            // STDOUT button
            else if((event.target.id == 'installationSTDOUT') || (event.target.parentNode.id == 'installationSTDOUT')){
                event.stopPropagation();
                //console.log('stdout button clicked');
            }
            // Add and Unsaved button (left panel)
            else if (event.target.classList.contains('plusBtn') || event.target.parentNode.classList.contains('plusBtn') || event.target.classList.contains('unsavedBtn')) {
                event.stopPropagation();
                var id;
                if (event.target.tagName == 'I') {
                    id = event.target.parentNode.id;
                }
                else {
                    id = event.target.id;
                }
                //console.log('add button clicked with id: ' + id);
            }
        });


//        document.getElementById('toggleReportsBtn').addEventListener('click', function(){
//            console.log('show/hide reports right panel');
//            if(document.getElementById('reportsRightPanel').style.display == 'block'){
//                document.getElementById('reportsRightPanel').style.display = 'none';
//            }
//            else{
//                document.getElementById('reportsRightPanel').style.display = 'block';
//            }
//        });



        // Search filters collapsible
        function closeCollapsible(event) {
            document.getElementById('searchFiltersBtn').getElementsByClassName('material-icons')[0].innerHTML = 'keyboard_arrow_right';
            elem = $('#searchFiltersCollapsible');
            var instance = M.Collapsible.getInstance(elem);
            instance.close(0);
            document.getElementById('searchFiltersBtn').removeEventListener('click', closeCollapsible);
            document.getElementById('searchFiltersBtn').addEventListener('click', openCollapsible);
        }
        function openCollapsible(event) {
            document.getElementById('searchFiltersBtn').getElementsByClassName('material-icons')[0].innerHTML = 'keyboard_arrow_down';
            elem = $('#searchFiltersCollapsible');
            var instance = M.Collapsible.getInstance(elem);
            instance.open(0);
            document.getElementById('searchFiltersBtn').removeEventListener('click', openCollapsible);
            document.getElementById('searchFiltersBtn').addEventListener('click', closeCollapsible);
        }
        document.getElementById('searchFiltersBtn').addEventListener('click', openCollapsible);

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
//    document.getElementById('modalSignUpBtn').addEventListener('click', function () {
//        $('#signInForm').animateCss('fadeOut', function () {
//            document.getElementById('signInForm').style.display = 'none';
//            document.getElementById('signUpForm').style.display = 'block';
//            $('#signUpForm').animateCss('fadeIn', function () {
//            });
//        });
//    });
//    // ------------------------------------------ Sign in button clicked ---------------------------------------------
//    document.getElementById('modalSignInBtn').addEventListener('click', function () {
//        $('#signUpForm').animateCss('fadeOut', function () {
//            document.getElementById('signUpForm').style.display = 'none';
//            document.getElementById('signInForm').style.display = 'block';
//            $('#signInForm').animateCss('fadeIn', function () {
//            });
//        });
//    });

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
                // show floating action button
                // document.getElementById('createNewBtn').style.display = 'block';
            }
            // Show right panel
            else if (rightWidth <= parseInt(splitterWidthEdges, 10)) {
                if (dragEnabled) {
                    leftSide.width(screenWidth - minPanelWidth - parseInt(splitterWidth, 10));
                }
                else {
                    leftSide.width(0);
                    // document.getElementById('createNewBtn').style.display = 'none';
                }
            }
            // Hide left panel
            else if (leftWidth <= minPanelWidth + parseInt(splitterWidth, 10)) {
                leftSide.width(0);
                // document.getElementById('createNewBtn').style.display = 'none';
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
                        // document.getElementById('createNewBtn').style.display = 'none';
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
                        // document.getElementById('createNewBtn').style.display = 'block';
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
                    // document.getElementById('createNewBtn').style.display = 'block';
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
        if (typeof cy_rep !== 'undefined') {
            cy_rep.resize();
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
            // This id array = [ name, value, description, "3" ]
            //console.log(this_id_array);
            var var_to_show = this_id_array[4] + '__' + this_id_array[5] + '__' + this_id_array[6] + '__' + this_id_array[0];

            if (target.closest('#tool_installation_editor').length) { // Adding to installation bash editor
                // https://stackoverflow.com/a/42797383/5626738 
                if (!tool_installation_editor.getReadOnly()) {
                    tool_installation_editor.session.insert(tool_installation_editor.getCursorPosition(), '$' + var_to_show);
                }
            }
            else if (target.closest('#tool_validation_editor').length) { // Adding to validation bash editor
                if (!tool_validation_editor.getReadOnly()) {
                    tool_validation_editor.session.insert(tool_validation_editor.getCursorPosition(), '$' + var_to_show);
                }
            }
        }
        else if (this_id_array[2] == '4') { // this is an item from workflows_search_tree droped on the cytoscape window. The id is the 3rd element
            if (target.closest('#cywf').length && (!workflow_step_editor.getReadOnly())) {

                var workflow = {
                    name: this_id_array[0],
                    edit: this_id_array[1]
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

        // TODO : Change NAMES NAMESPACE UI
        window.OBCUI = {
            sep: '__',
            //call_re: new RegExp('((^call)|([\\s]+call))\\([\\w]+\\)', 'g'), // Matches: "call(a)" , "  call(a)", "ABC call(a)", "ABC   call(a)"
            call_re: new RegExp('step__[\\w]+' ,'g'), 
            //call_re_id: new RegExp('call\\(([\\w]+)\\)'), //
            call_re_id: new RegExp('step__([\\w]+)'), 
            //call_replace: function (bash, old_id, new_id) { return bash.replace(new RegExp('(call[\\s]*\\([\\s]*)' + old_id + '([\\s]*\\))', 'g'), '$1' + new_id + '$2'); },
            call_replace: function (bash, old_id, new_id) { return bash.replace(new RegExp('step__' + old_id, 'g'),  'step__' + new_id); },

            //tool_re: new RegExp('\\$\\{[\\w]+__[\\w\\.]+__[\\d]+__[\\w]+\\}', 'g'), // ${hello__1__1__exec_path}
            tool_re: new RegExp('\\$\\{[\\w]+__[\\w]+__[\\d]+__[\\w]+\\}', 'g'), // ${hello__1__1__exec_path}
            //tool_re_id: new RegExp('\\$\\{([\\w]+__[\\w\\.]+__[\\d]+)__([\\w]+)\\}'),
            tool_re_id: new RegExp('\\$\\{([\\w]+__[\\w]+__[\\d]+)__([\\w]+)\\}'),

//            io_re: new RegExp('\\$\\{(input|output)__[a-zA-Z0-9][\\w]*\\}', 'g'), // [^_\w] Does not work???
//            io_re_id: new RegExp('\\$\\{(input|output)__([\\w]+)\\}'), // TODO: ADD  WHITE SPACEDS JUST LIKE calls
//            io_replace: function (bash, old_id, new_id) { return bash.replace(new RegExp('(\\$\\{(input|output)__)' + old_id + '(\\})'), '$1' + new_id + '$3'); }

            io_re: new RegExp('(input|output)__[a-zA-Z0-9_][\\w]*', 'g'), // [^_\w] Does not work???
            io_re_id: new RegExp('(input|output)__([\\w]+)'), // TODO: ADD  WHITE SPACEDS JUST LIKE calls
            io_replace: function (bash, old_id, new_id) { return bash.replace(new RegExp('((input|output)__)' + old_id, 'g'), '$1' + new_id); },

            //Same codes as models.py class ReportToken used in nodeAnimation_public
            WORKFLOW_STARTED_CODE: 1,
            WORKFLOW_FINISHED_CODE: 2,
            TOOL_STARTED_CODE: 3,
            TOOL_FINISHED_CODE: 4,
            STEP_STARTED_CODE: 5,
            STEP_FINISHED_CODE: 6,
//			CALLSTEP_STARTED_CODE:7,
//			CALLSTEP_FINISHED_CODE:8,
            previous_animation: null, // Object that contains information to restore animations in reports

            //Timeline
			
            timeline: new vis.Timeline(
                document.getElementById('reportTimeline'),
                new vis.DataSet([{id: 1, content: 'item 1', start: '1950-04-20'}]), //Cannot initialize with empty array ???
                {}) // <-- Options
			
        };

        /*
        * Get the data (keywords) from an id chip.
        */
        window.OBCUI.get_chip_data = function (this_id) {
            var data = [];
            M.Chips.getInstance(document.getElementById(this_id)).getData().forEach(function (chip) {
                data.push(chip.tag);
            })

            return data;
        };

        /*
        * Delete all chip data
        */
        window.OBCUI.delete_all_chip_data = function (this_id) {
            //Get all data
            var data = window.OBCUI.get_chip_data(this_id);
            for (var i = 0; i < data.length; i++) {
                M.Chips.getInstance(document.getElementById(this_id)).deleteChip(0);
            }
        };

        /*
        * Set data to id chip
        */
        window.OBCUI.set_chip_data = function (this_id, data) {

            //First delete previous data
            window.OBCUI.delete_all_chip_data(this_id);

            //Set new
            data.forEach(function (datum) {
                M.Chips.getInstance(document.getElementById(this_id)).addChip({ tag: datum });
            });

        };

        /*
        * Disable "x" and input from chip
        */
        window.OBCUI.chip_disable = function (this_id) {
            //Remove "x"
            $('#' + this_id + ' i').css('display', 'none');

            //Disable input
            $('#' + this_id + ' input').prop('disabled', true);
        };

        window.OBCUI.chip_enable = function (this_id) {
            //Add "x"
            $('#' + this_id + ' i').css('display', 'block');

            //Enable input
            $('#' + this_id + ' input').prop('disabled', false);
        };

        /*
        * bash: the bash text
        * apply_to_element_fun: Function to apply to each element found (SIO)
        * find_elements_fun: Function to return all IDs
        * replace_fun: Function that gets an old id
        */
        window.OBCUI.edit_bash = function (bash, apply_to_element_fun, find_elements_fun, replace_fun) {
            var new_bash = bash;
            find_elements_fun(bash).forEach(function (element) {
                //console.log('element');
                //console.log(element);
                //console.log('To be replaced with:');
                //console.log(apply_to_element_fun(element));

                new_bash = replace_fun(new_bash, element, apply_to_element_fun(element));
                //console.log('Whole bash replaced:');
                //console.log(new_bash);
            });
            return new_bash;
        };

        /*
        * Return a list of steps that are called in this bash script
        */
        window.OBCUI.get_steps_from_bash_script = function (t) {
            var steps = [];

            //Remove bash comments
            var no_comments = window.OBCUI.remove_bash_comments(t);

            //console.log('NO COMMENTS BASH SCRIPT:');
            //console.log('-->' + no_comments + '<--');

            var splitted = no_comments.split('\n');

            splitted.forEach(function (line) {
                //console.log("line : ");
                //console.log(line);

                //If this is an empty-ish string, return
                if (!$.trim(line).length) {
                    return;
                }

                var results = line.match(window.OBCUI.call_re);
                //console.log("PROCESSING line: " + line);
                //console.log("FOUND THE FOLLOWING CALLS:");
                //console.log(results);

                if (results) {
                    results.forEach(function (result) {

                        //console.log('PROCESSING THE FOLLOOWING CALL: -->' + result + '<--');

                        var step_id = result.match(window.OBCUI.call_re_id)[1];
                        //console.log("matched step id : ");
                        //console.log(step_id);
                        //Is there a node with type step and id step_id ?
                        if (cy.$("node[type='step'][id='" + step_id + "']").length) {
                            //Add it only if it is not already there
                            if (!steps.includes(step_id)) {
                                steps.push(step_id);
                            }
                        }

                    });
                }
            });

            return steps;

        };

        /*
        * Return a list of input output variables from the bash script 
        */
        window.OBCUI.get_input_outputs_from_bash_script = function (t) {

            //Remove bash comments. DUPLICATE FIXME
            var no_comments = window.OBCUI.remove_bash_comments(t);
            var inputs = [];
            var outputs = [];

            var splitted = no_comments.split('\n');
            splitted.forEach(function (line) {
                var results = line.match(window.OBCUI.io_re);
                if (results) {
                    results.forEach(function (result) {
                        var splitted = result.match(window.OBCUI.io_re_id); // AAAAAAA
                        var input_output = splitted[1];
                        var variable_name = splitted[2];
                        //Does this variable exist in cytoscape?
                        if (cy.$("node[type='" + input_output + "'][id='" + variable_name + "']").length) {
                            //It exists
                            //Add them in their relevant list only if they are not already there
                            if (input_output == "input") {
                                if (!inputs.includes(variable_name)) {
                                    inputs.push(variable_name);
                                }
                            }
                            else if (input_output == "output") {
                                if (!outputs.includes(variable_name)) {
                                    outputs.push(variable_name);
                                }
                            }
                        }
                    });
                }
            });

            return { inputs: inputs, outputs: outputs };

        };

        /*
        * Return a list of tools whose variables are used in this bash script
        */
        window.OBCUI.get_tools_from_bash_script = function (t) {
            var tools = [];

            //Remove bash comments
            var no_comments = window.OBCUI.remove_bash_comments(t);

            var splitted = no_comments.split('\n');
            splitted.forEach(function (line) {
                var results = line.match(window.OBCUI.tool_re);
                if (results) {
                    results.forEach(function (result) {
                        var splitted_ids = result.match(window.OBCUI.tool_re_id);
                        var tool_id = splitted_ids[1] + '__2';
                        var variable_id = splitted_ids[2];

                        //Does tool_id matches any of ids of tool nodes in cytoscape ?
                        //Idially we would only have to do a:
                        //cy.$("node[type='tool'][id='" + tool_id + "']").length > 0  
                        //Unfortunately tool_id might be different than the id of the tool in cytoscape
                        //tool_id is extracted from bash script and we replace dots with _ whereas dots are allowed as tool ids in cytoscape
                        //console.log('tool_id:', tool_id);

                        //Create a new regular expression from the bash tool id, that will match all possible similar tool ids
                        var tool_id_replace_meta = new RegExp(/([a-zA-Z0-9]+)_([a-zA-Z0-9]+?)/, 'g');
                        var tool_id_re_str = tool_id.replace(tool_id_replace_meta, '$1[\\._]$2');  // new RegExp();
                        while (tool_id_replace_meta.test(tool_id_re_str)) {
                            tool_id_re_str =  tool_id_re_str.replace(tool_id_replace_meta, '$1[\\._]$2');
                        }
                        tool_id_re = new RegExp(tool_id_re_str);

                        //console.log('tool_id_re:', tool_id_re);

                        //Get the ids of all tools.
                        cy.$('node[type="tool"]').forEach(function(cy_tool_node){
                            var cy_node_id = cy_tool_node.data('id');
                            //console.log('cy_node_id:', cy_node_id);
                            if (tool_id_re.test(cy_node_id)) {
                                //console.log('MATCHED');
                                //This cytoscape node id has matched the reg exp from bash

                                //Does this tool has a variable with name: variable_id ?
                                var tool_tool_variables = cy_tool_node.data().variables;
                                tool_tool_variables.forEach(function (variable) {
                                    if (variable.name == variable_id) {
                                        //Add it if it is not already there
                                        if (!tools.includes(cy_node_id)) {
                                            tools.push(cy_node_id);
                                        }
                                    }
                                });
                            }
                            else {
                                //console.log('NOT MATCHED');
                            }
                        });



                        // //Does this tool_id exist?
                        // var cy_tool_node = cy.$("node[type='tool'][id='" + tool_id + "']");
                        // if (cy_tool_node.length) {
                        //     //IT EXISTS!

                        //     //Does this tool has a variable with name: variable_id ?
                        //     var tool_tool_variables = cy_tool_node.data().variables;
                        //     tool_tool_variables.forEach(function (variable) {
                        //         if (variable.name == variable_id) {
                        //             //Add it if it is not already there
                        //             if (!tools.includes(tool_id)) {
                        //                 tools.push(tool_id);
                        //             }
                        //         }
                        //     });

                        // }

                    });
                }
            });

            return tools;
        }


        /*
        * Creates a "unique" id from a workflow
        * ATTENTION! This should be in accordance with the python function create_workflow_id in views.py
        */
        function create_workflow_id(workflow) {
            return workflow.name + window.OBCUI.sep + workflow.edit; //It is ok if this is wf1__null
        }

        /*
        * Get the edit of this wotkflow id
        */
        function get_edit_from_workflow_id(workflow_id) {
            return workflow_id.split(window.OBCUI.sep)[1];
            //return workflow_id.split(window.OBCUI.sep)[1];
        }

        /*
        * Check if this workflow_id is root
        */
        function is_workflow_root_from_workflow_id(workflow_id) {
            return get_edit_from_workflow_id(workflow_id) == 'null';
        }

        /*
        * Create a step ID. This contains: name of step, name of workflow, edit of workflow
        */
        function create_step_id(step, workflow) {
            return step.name + window.OBCUI.sep + create_workflow_id(workflow);
        }
        window.create_step_id = create_step_id; // Ugliness. FIXME! We need to make these functions visible everywhere without polluting the namespace

        /*
        * Create a unique input/output variable ID. This contains the input/output name, name workflow and edit of worfkflow
        */
        function create_input_output_id(input_output, workflow) {
            return input_output.name + window.OBCUI.sep + create_workflow_id(workflow);
        }

        /*
        * Helper for Step Input Output (SIO)
        */
        function create_SIO_id(SIO, workflow) {
            return SIO.name + window.OBCUI.sep + create_workflow_id(workflow);
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
        * Get the source_id from the edge id
        */
        function get_source_id_from_edge_id(edge_id) {
            return edge_id.split('..')[0];
        }

        /*
        * Get the target_id from the edge id
        */
        function get_target_id_from_target_id(edge_id) {
            return edge_id.split('..')[1];
        }

        /*
        * Get the workflow id if this is a SIP node. 
        * sio: Step Input Output
        */
        function get_workflow_id_from_SIO_id(sio_id) {
            var sio_id_splitted = sio_id.split(window.OBCUI.sep);
            if (sio_id_splitted.length != 3) {
                return null;
            }
            return create_workflow_id({ name: sio_id_splitted[1], edit: sio_id_splitted[2] });
        }

        /*
        * Check if this SIO id. Belongs to a root workflow
        */
        function is_workflow_root_from_SIO_id(sio_id) {
            return is_workflow_root_from_workflow_id(get_workflow_id_from_SIO_id(sio_id));
        }
        window.is_workflow_root_from_SIO_id = is_workflow_root_from_SIO_id;

        /*
        * Get the name of a SIO (Step Input Output)
        */
        function get_SIO_name_from_SIO_id(sio_id) {
            return sio_id.split(window.OBCUI.sep)[0]
        }

		/*
        * Replace the ids of a list of SIO (in lists of a node: steps[], inputs[], outputs[])
        * old_root_id : Change only SIOs that have as a workflow: old_root_id
        */
        function replace_worfklow_id_of_list_of_SIO_id(array, old_root_id, new_root) {
            array.forEach(function (sio_id) {
                if (get_workflow_id_from_SIO_id(sio_id) === old_root_id) {
                    var index = array.indexOf(sio_id);
                    sio_id = create_SIO_id({ name: get_SIO_name_from_SIO_id(sio_id) }, new_root);
                    array[index] = sio_id;
                }
            });

            return array;
        }

        /*
        * Remove commends from text
        * Everything that starts with '#'
        */
        window.OBCUI.remove_bash_comments = function (t) {
            var no_comments = [];
            var t_splitted = t.split('\n');

            t_splitted.forEach(function (line) {
                //Check if this line is a comment
                if (line.match(/^[\s]*#/)) {
                    //This is a comment. Ignore it
                }
                else {
                    //This is not a comment
                    //Add it only if it is not empty
                    if ($.trim(line).length) {
                        no_comments.push(line);
                    }
                }
            });

            return no_comments.join('\n');

        };

        /*
		*
        * parse data from openbioc to meet the cytoscape.js requirements
        * Create cytoscape nodes and edges
        * incomingData: List of nodes to add
        * belongto: the workflow to be added to
		*
        */
        function parseWorkflow(incomingData, belongto) {

            var myNodes = [], myEdges = [];

            /* initialize my data object */
            incomingData.forEach(function (d) {

                var this_node_wf_belong_to = d.belongto ? d.belongto : belongto; // In which worfklow does this node belong to? 
                var this_node_wf_belong_to_id = create_workflow_id(this_node_wf_belong_to);


                //INPUTS/OUTPUTS
                if ( d.type === 'input' || d.type === 'output' ) {
						var this_input_output_id = create_input_output_id(d, this_node_wf_belong_to);

						var myNode = { data: { id: this_input_output_id, label: d.name, name: d.name, type: d.type, description: d.description, belongto: this_node_wf_belong_to }};
						myNodes.push(myNode);
						//Connect with belongto workflow
						myEdges.push({ data: { source: this_node_wf_belong_to_id, target: this_input_output_id, id: create_workflow_edge_id(this_node_wf_belong_to_id, this_input_output_id), edgebelongto: 'true' }});
                }


                //TOOLS 
                if (d.type === "tool") {

						//If d.id is a JSON string parse it. d.id might come either from jstree (needs parsing) or cytoscape (does not need parsing)
						if (d.id.indexOf('[') > -1) {
							d.id = JSON.parse(d.id).join(window.OBCUI.sep);
							/*remove special characters*/
							//d.id = d.id.replace(/\./g,''); // CYTOSCAPE ALLOWS . IN IDS
						}

						if ("parent" in d) {
							d.dep_id = d.parent;
							d.parent = '#';
						}

						if (d.dep_id != "#") {
							if (d.dep_id.indexOf('[') > -1) { // Parse it if this is JSON. 
								d.dep_id = JSON.parse(d.dep_id).join(window.OBCUI.sep);
								/*remove special characters*/
								// d.dep_id = d.dep_id.replace(/\./g,''); //CYTOSCAPE ALLOWS . IN IDS
							}

							//var myNode = { data: { id: d.id, text:d.text, label: d.text, name: d.data.name, version: d.data.version, edit: d.data.edit, type: d.data.type, root: 'no', variables: d.variables } };
							var myNode = { data: { id: d.id, text: d.text, label: d.text, name: d.name, version: d.version, edit: d.edit, type: d.type, root: 'no', dep_id: d.dep_id, variables: d.variables, belongto: this_node_wf_belong_to }};

							myNodes.push(myNode);
							var myEdge = { data: { id: create_workflow_edge_id(d.dep_id, d.id), weight: 1, source: d.dep_id, target: d.id } };
							myEdges.push(myEdge);

						} else {
							//var myNode = { data: { id: d.id, label: d.text, name: d.data.name, version: d.data.version, edit: d.data.edit, type: d.data.type, root: 'yes', variables: d.variables } };
							var myNode = { data: { id: d.id, text: d.text, label: d.text, name: d.name, version: d.version, edit: d.edit, type: d.type, root: 'yes', dep_id: d.dep_id, variables: d.variables, belongto: this_node_wf_belong_to } };
							myNodes.push(myNode);
							myEdges.push({ data: { source: this_node_wf_belong_to_id, target: d.id, id: create_workflow_edge_id(this_node_wf_belong_to_id, d.id), edgebelongto: 'true' } });
						}

                }

                //WORKFLOWS
                if (d.type === "workflow") {
					
                    //TODO add root feature (different than tools): wfroot:yes
                    var this_workflow_id = create_workflow_id(d);

                    var myNode = { data: { id: this_workflow_id, name: d.name, edit: d.edit, label: create_workflow_label(d), type: 'workflow', belongto: this_node_wf_belong_to } };
                    myNodes.push(myNode);
                    myEdges.push({ data: { source: this_node_wf_belong_to_id, target: this_workflow_id, id: create_workflow_edge_id(this_node_wf_belong_to_id, this_workflow_id), edgebelongto: 'true' } });
					
                }


                //STEPS
                if (d.type === "step") {
                    //Why this redundancy?
                    //jstree uses d.name, cytoscape uses d.label and we also need an id...
                    var this_step_id = create_step_id(d, this_node_wf_belong_to);
                    var myNode = { data: { id: this_step_id, name: d.name, label: d.name, type: d.type, bash: d.bash, main:d.main, tools: d.tools, steps: d.steps, inputs: d.inputs, outputs: d.outputs, belongto: this_node_wf_belong_to } };
                    myNodes.push(myNode);

                    //Connect with belong workflow
                    myEdges.push({ data: { source: this_node_wf_belong_to_id, target: this_step_id, id: create_workflow_edge_id(this_node_wf_belong_to_id, this_step_id), edgebelongto: 'true' } });

                    //create edges to tools and/or steps
                    if (typeof d.tools !== "undefined") {
                        //replace special characters

                        d.tools.forEach(function (element) {
                            //element = element.replace(/\[/g, '').replace(/]/g, '').replace(/"/g, '').replace(/,/g, '').replace(/ /g, '');

                            var myEdge = { data: { 'id': create_workflow_edge_id(this_step_id, element), 'weight': 1, 'source': this_step_id, 'target': element } };
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
			

            return {
                nodes: myNodes,
                edges: myEdges
            };

        }


		/*
		* This function closes the successors of a workflow except the input/output
		* Should be use every time a tool or workflow is dr&dropped in the workflow editor
		* and everytime a tool or workflow is clicked in the right menu
		*/
        window.cy_close_successors = function () {

            // close all successors of root node or workflow node	: except inputs and outputs or other wfs
            cy.json().elements.nodes.forEach(function (node) {

                //close the successors of a (previous saved) workflow  except the inouts/outputs
                if (node.data.type === "workflow" && node.data.edit !== "null") {
                    cy.$("#" + node.data.id).successors().targets().forEach(function (element) {

                        //if (element['_private'].data.type === 'input' || element['_private'].data.type === 'output' || element['_private'].data.type === 'workflow') {
                        if (element['_private'].data.type !== 'tool') {
                            element.style("display", "element");
                        } else {
                            element.style("display", "none");
                        }

                    });

                    //cy.$("#" + node.data.id).successors().targets().style("display", "none");
                }


                //if(node.data.type==="tool" && typeof node.data.root !== 'undefined' && node.data.root === 'yes')
                // cy.$("#" + node.data.id).successors().targets().style("display", "none");


            });


        }
		
		
			/* 
            * Function for creating tooltip on node hover.
			*
            */
            var makeTippy = function (node, text) {
				
                return tippy(node.popperRef(), {
                    content: function () {
                        var div = document.createElement('div');
						var belongto = " - ";
							if(node._private.data.belongto !== null) belongto = node._private.data.belongto.name;
						
						text='name : '+node._private.data.label +'<br>'+ 'version : '+node._private.data.version +'<br>'+ 'edit : '+node._private.data.edit +'<br>'+ 'type : '+node._private.data.type+'<br>'+'variables : '+node._private.data.variables +'<br>'+'belongs to : '+ belongto +'<br>';
                        div.innerHTML = text; 
						div.style.zIndex = "-1000000000000000000000000";	
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



			/* 
            * Function for creating tooltip for setting input node value.
            */
            var makeEditTippy = function (node, text) {
				
				editTippy = tippy(node.popperRef(), {
					
                    	content: function () {
								var div = document.createElement('div');
                                div.setAttribute("id", "tippy_div_" + node._private.data.id);
								div.innerHTML = 
												'<button type="button" class="close">×</button><br>'+  // onclick='+alert($(this).parent());+'
												node._private.data.description+ '<br>'+
												'Add Value For '+ node._private.data.name+' : <br>'+
												'<input type="text" id="tippy_text_'+node._private.data.id+'" name="Add Value"><br>'	+
												'<button id="tippy_button_'+node._private.data.id+'" class="btn btn-click">set</button>'		
												
								div.style.width = "200px";
								div.style.height = "140px";
								div.style.color = "black"; //font color
								div.style.position= "relative";
								//div.style.zIndex = "10000000000";					
								return div;
						},

						onShown: function(){
								//$('.btn-click').off("click").on("click", function(){
								/* code for SET button */
								$('#tippy_button_' + node._private.data.id).off("click").on("click", function(){
									//alert( document.getElementById(this.id.replace('tippy_button_', 'tippy_text_')).value);
									// tippy should be destroyed
									var value = document.getElementById('tippy_text_'+node._private.data.id).value;
									node.data('value', value);
									node.data('label', node._private.data.name+'='+value);
									//$(this).parent().fadeOut('slow', function(c){});
								   // $('#tippy_edit_div_' + node._private.data.id).remove();
									
									//destroy tippy
									editTippy.destroy(editTippy.popper);	
									
								});
								
								/* code for x button */
								$('.close').on('click', function(c){
									//destroy tippy
									editTippy.destroy(editTippy.popper);
									
										//$('#tippy_edit_div_' + node._private.data.id).remove();	
										//$(this).parent().fadeOut('slow', function(c){
									//});
								});	
								
						},
							trigger: 'manual',
							//arrow: true,
							placement: 'bottom',
							interactive: true,	//this should be true for the content to be interactive and clickable
							hideOnClick: false,
							multiple: true,
							followCursor: true,
							theme: 'light', 
							//zIndex: 100001,
							sticky: true
							
				});
				
                return editTippy;
            };
			
		
		/**
		This function gets as input a node and then goes through it's successors and opens or close each one based on predefined assumptions	
		**/		
		var collapse_expand_node = function(this_node){
			
			//connectedEdges: next level
			//successors: next levels recursively
			
		/*
			this_node.successors().targets().forEach(function (target) {

						//if(target['_private'].data.type!=="step" && target['_private'].data.type!=="input" && target['_private'].data.type!=="output" ){
						//if(target['_private'].data.type === "tool"){
								//console.log(target['_private'].data.id);
								
								if(target.style("display") == "none"){
									//console.log("make visible");
									target.style("display", "element");
									
								}else{     
									//console.log("make non visible");
									//hide the children nodes and edges recursively  
										
											//check if node has flag(open)								
											if (target['_private'].data.type === "tool" && (typeof target['_private'].data.flag === 'undefined' || target['_private'].data.flag !== 'open')) {
												target.style("display", "none");
											
												target.successors().targets().forEach(function (element) {	
														if (target['_private'].data.type === "tool" && (typeof element['_private'].data.flag === 'undefined' || element['_private'].data.flag !== 'open')) {
														element.style("display", "none");
													}
												});
											}
										
										
								}				
						//}
				
			});
			*/
			
			/*
			this function searches for open connected edges and if any is found,
			it opens it and returns true,
			else only returns false
			*/
			var openTarget = function (node) {
				var answer=false;
				node.connectedEdges().targets().forEach(function (target) {
					if(target.style("display") == "none"){
						//console.log("make visible");
						target.style("display", "element");
						answer=true;
					}
								
				});	
							
					return answer;
			}
						
			/*
			if selected node has closed connected edges, then open them
			if selected node has all it;s connected edges open, then close them recursively
			*/		
			if(openTarget(this_node)){
				//console.log("opened");
							
			}else{
				this_node.successors().targets().forEach(function (element) {
			    	//check if node has flag(open)								
					if (element['_private'].data.type==="tool"  && (typeof element['_private'].data.flag === 'undefined' || element['_private'].data.flag !== 'open')) {
						element.style("display", "none");
					}

				});
							
			}			
									
		}	
			

        /*
        * After importing a graph or adding new nodes, we need to register cytoscape events.
        * This function is called from buildtree and also from angular when we do: cy.json(data['workflow']) from angular
        */
        window.cy_setup_events = function () {
			
			//initializeTree();		
            // collapse - expand nodes
            cy.on('click', 'node', function (event) {
					
			
					// inputs/outpus and steps should never collapse
					//if (this['_private'].data.type !== "step" && this['_private'].data.type !== "input" && this['_private'].data.type !== "output") { //steps should never collapse
					
					collapse_expand_node(this);
					
					
						if (this['_private'].data.type == "step") { // Click at a step node
							//Call angular function
							var this_data = this['_private'].data;
							angular.element($('#angular_div')).scope().$apply(function () {
								angular.element($('#angular_div')).scope().workflop_step_node_clicked(this_data);
							});
						}

            });




            /* show tooltip */
            var mytippys = []; // array for keeping instances of tooltips, needed for destroying all instances on mouse out
            cy.on('mouseover', 'node', function (event) {

                nodeId = this._private.data.id;
                myNode = cy.getElementById(nodeId);
                myTippy = makeTippy(myNode, nodeId);
                mytippys.push(myTippy);
                myTippy.show();
				
            });
			
			//on right click close tooltip before menu opens
			cy.on('cxttapstart', 'node', function (event){
				//$('#tippy_div_' + this._private.data.id).remove();
				mytippys.forEach(function (mytippy) {
					  //console.log(mytippy);
						mytippy.destroy(mytippy.popper);
				});
				
			});
			

            /* hide tooltip before cxtmenu opens, otherwise they overlap */
            cy.on('mouseout', 'node', function (event) {
					// destroy all instances
					mytippys.forEach(function (mytippy) {
						mytippy.destroy(mytippy.popper);
					});
            });

			 // Right-click menu for input nodes 
			 window.input_menu = cy.cxtmenu({
								menuRadius: 85, 	
								//selector: 'node',
								selector: 'node[type="input"]',
								//zIndex: 199999999, 
								openMenuEvents: 'cxttapstart', 
								commands: [
									{
										content: 'Set',
										select: function (ele) {
																
											editNode= cy.$('node[id="' + ele.id() + '"]');
											if(editNode[0]._private.data.type==="input"){  //check if node is input type
											
												editTippy = makeEditTippy(editNode[0], ele.id());  //add edit tooltip
												editTippy.show();								   //show edit tooltip	
											}
											//input_menu.destroy();
										}
									},
									{
										content: 'Delete',
										select: function (ele) {

											//Ideally the deletion logic should be placed here.
											//Nevertheless upon deletion, we might have to update some angular elements (like inputs/outputs)
											angular.element($('#angular_div')).scope().$apply(function () {
												angular.element($('#angular_div')).scope().workflow_cytoscape_delete_node(ele.id());
											});

											//                           var j = cy.$('#' + ele.id());
											//                           
											//							/* remove node successors*/
											//							j.successors().targets().forEach(function (element) {
											//									cy.remove(element);
											//								
											//							})
											//							/*remove node*/
											//							cy.remove(j);
											//input_menu.destroy();
											
										}
									},
									 {
										content: 'Cancel',
										select: function (ele) {
											//console.log("CANCEL OPTION");
											cy.cxtmenu().destroy();
											//input_menu.destroy();
										}
									}
								]

							});
			
			// Right-click menu for all except input nodes
		    window.menu = cy.cxtmenu({
									menuRadius: 85, 
									//selector: 'node',
									selector: 'node[type!="input"]',
									openMenuEvents: 'cxttapstart', 
									commands: [
										{
											content: 'Edit',
												select: function (ele) {
												//menu.destroy();	
											}
										},
										{
											content: 'Delete',
											select: function (ele) {

												//Ideally the deletion logic should be placed here.
												//Nevertheless upon deletion, we might have to update some angular elements (like inputs/outputs)
												angular.element($('#angular_div')).scope().$apply(function () {
														angular.element($('#angular_div')).scope().workflow_cytoscape_delete_node(ele.id());
												});

												//                           var j = cy.$('#' + ele.id());
												//                           
												//							/* remove node successors*/
												//							j.successors().targets().forEach(function (element) {
												//									cy.remove(element);
												//								
												//							})
												//							/*remove node*/
												//							cy.remove(j);
												
												//menu.destroy();
											}
										},
										 {
											content: 'Cancel',
											select: function (ele) {
												//console.log("CANCEL 2 OPTION");
												cy.cxtmenu().destroy();
												//menu.destroy();
											}
										}
									]

								});
	
        }

			

        /*
        * Initialize WORKFLOW graph
        */
        //function initializeTree() {
		window.initializeTree = function () {
			
            cy = cytoscape({
                container: document.getElementById('cywf'), // container to render in
                elements: [],

                style: [ // the stylesheet for the graph
                    {
                        selector: 'node',
                        "style": {
                            "shape": "round-rectangle",
                            "background-color": "#5A5A5A",
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
                            'border-width': '3',
                            'border-color': '#43A047', 
                            'background-color': '#5A5A5A',
                            //"height": 15,
                            //"width": 15
                        }
                    },
                    {
                        selector: 'node[type="output"]',
                        "style": {
                            'shape': 'round-rectangle',
                            'border-width': '3',
                            'border-color': '#E53935',
                            'background-color': '#5A5A5A',
                            //"height": 15,
                            //"width": 15
                        }
                    },

                    {
                        selector: 'node[type="workflow"]',
                        "style": {
                            'shape': 'octagon',
                            //'border-width': '3',
                            //'border-color': '#5A5A5A',
                            'background-color': '#5A5A5A',
                            //"height": 15,
                            //"width": 15
                        }
                    },
                    {
                        selector: 'edge[edgebelongto="true"]',
                        "style": {
							'curve-style': 'bezier',
                            'target-arrow-shape': 'triangle',
                            'width': 2,
							'line-style': 'dashed',
							'line-dash-pattern': [6, 3], 
							'line-dash-offset': 24,
                            'line-color': '#ddd',
                            'target-arrow-color': '#ddd'
						}
					},
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

            //This removes the attribute: position: 'absolute' from the third layer canvas in cytoscape.
            //document.querySelector('canvas[data-id="layer2-node"]').style.position = null;
			document.getElementById("cywf").querySelector('canvas[data-id="layer2-node"]').style.position = null; 

        }
		
		// cy should be initialize so that angular can access it
		window.initializeTree();
		
		
		window.initializeRepTree = function () {
			
			var cy_rep = cytoscape({
                container: document.getElementById('cyrep'), // container to render in
                elements: [],
                style: [ // the stylesheet for the graph
					{   // * tool default state : initial state * //
                        selector: 'node[type="tool"]',  //[state = "pending"]
                        "style": {
                            "shape": "round-rectangle",
                            "background-color": "#5A5A5A",
                            "label": "data(label)"
                        }
                    },
                    {
                        selector: 'node[type="step"]',
                        "style": {
                            'shape': 'ellipse',
                            'background-color': '#5A5A5A',
							"label": "data(label)"
                        }
                    },
					{
                        selector: 'node[type="input"]',
                        "style": {
                            'shape': 'round-rectangle',
							'border-width': '3',
                            'border-color': '#43A047',
                            'background-color': '#5A5A5A',
							"label": "data(label)"
  
                        }
                    }, 
                    {
                        selector: 'node[type="output"]',
                        "style": {
                            'shape': 'round-rectangle',
							'border-width': '3',
                            'border-color': '#E53935',
                            'background-color': '#5A5A5A',
							"label": "data(label)"

                        }
                    },
                    {
                        selector: 'node[type="workflow"]',
                        "style": {
                            'shape': 'octagon',
                            //'border-width': '3',
                            //'border-color': '#E53935',
                            'background-color': '#5A5A5A',
							"label": "data(label)"

                        }
                    },
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
						/*,
						{
                        selector: 'edge',
                        "style": {
                            'curve-style': 'bezier',
                            'target-arrow-shape': 'triangle',
                            'width': 2,
							'line-dash-pattern': [6, 3], 
							'line-dash-offset': 24,
                            'line-color': '#5A5A5A',
                            'target-arrow-color': '#5A5A5A'
							}
						*/	
                ],

					//zoom: 1,
					pan: { x: 0, y: 0 },

					layout: {
						name: 'breadthfirst',
						directed: true,
						padding: 2
					}
            });
			
			return cy_rep;
			
		}
		
			//initializeRepTree();
		
		
		/*
        * Create REPORT graph
		*
        */
		window.createRepTree = function(workflowToReport){
			//function createRepTree(workflowToReport) {

			cy_rep = initializeRepTree();		
			cy_rep.json({ elements:  workflowToReport});   // Add new data


				cy_rep.ready(function () {           // Wait for nodes to be added  
					cy_rep.layout({                   // Call layout
						name: 'breadthfirst',
						directed: true,
						padding: 2
					}).run();

				
				});
			

			cy_rep.resize();
            //This removes the attribute: position: 'absolute' from the third layer canvas in cytoscape.	
			document.getElementById("cyrep").querySelector('canvas[data-id="layer2-node"]').style.position = null;
	
        }

        /*
        * status_code : The same declared in models.py: class ReportToken 
        * status_fields : Thw results from status parsing 
        */
        window.nodeAnimation_public=function(node_anim_params) {
            //console.log('NODE ANIM PARAMS:');
            //console.log(node_anim_params);

            if (node_anim_params.status_code == window.OBCUI.WORKFLOW_STARTED_CODE) {
                var workflow_id = node_anim_params.status_fields.name.replace(/\//g, '__');
                window.nodeAnimation(workflow_id, 'started');
            }
            else if (node_anim_params.status_code == window.OBCUI.WORKFLOW_FINISHED_CODE) {
                var workflow_id = node_anim_params.status_fields.name.replace(/\//g, '__');
                window.nodeAnimation(workflow_id, 'finished');
            }
            else if (node_anim_params.status_code == window.OBCUI.TOOL_STARTED_CODE) {
                var tool_id = node_anim_params.status_fields.name.replace(/\//g, '__') + '__2';
                window.nodeAnimation(tool_id, "installing");
            }
            else if (node_anim_params.status_code == window.OBCUI.TOOL_FINISHED_CODE) {
                var tool_id = node_anim_params.status_fields.name.replace(/\//g, '__') + '__2';
                window.nodeAnimation(tool_id, "installed");
            }
            else if (node_anim_params.status_code == window.OBCUI.STEP_STARTED_CODE) {
                var step_source = node_anim_params.status_fields.caller;
                var step_target = node_anim_params.status_fields.name;
                window.nodeAnimation(step_target, 'running');
                window.edgeAnimation(step_source, step_target, 'running');
            }
            else if (node_anim_params.status_code == window.OBCUI.STEP_FINISHED_CODE) {
                var step_id = node_anim_params.status_fields.name;
                window.nodeAnimation(step_id, 'finished');
            }


        };

        /*
        * Before applying a new animation we need to restore previous animations
        */
        window.unset_nodeAnimation = function() {

            if (!window.OBCUI.previous_animation) {
                return;
            }

            var node_anim = window.OBCUI.previous_animation.node_anim;
            //var node_anim = cy_rep.$('#' + window.OBCUI.previous_animation.node_anim_id);

            for (var i=0; i<window.OBCUI.previous_animation.actions.length; i++) {
                var action = window.OBCUI.previous_animation.actions[i];
                if (action=='LABEL') {
                    node_anim.data('label', window.OBCUI.previous_animation.label);
                }
                else if (action == 'EDGE LABEL') {
                    window.OBCUI.previous_animation.edge_anim.style('label', '');
                }
                else if (action == 'STYLE') {
                    for (var i_style=0; i_style<window.OBCUI.previous_animation.style.length; i_style++) {
                        var new_style = {};
                        new_style[window.OBCUI.previous_animation.style[i_style][0]] = window.OBCUI.previous_animation.style[i_style][1];
                        node_anim.style(new_style);
                    }
                }
                else if (action == 'BLINK') {
                    node_anim.stop();
                    node_anim.style({'opacity': 1.0});
                }
                else if (action == 'EDGE BLINK') {
                    var edge_anim = window.OBCUI.previous_animation.edge_anim;
                    edge_anim.stop();
                    edge_anim.style({'opacity': 1.0});
                }
            }

        };
		
		/* function for node animation
        * window.nodeAnimation('frequentistadditive__3', 'started') 
        */ 
		window.nodeAnimation = function(node_anim_id, state){

            //Restore previous anumation:
            if (window.OBCUI.previous_animation) {
                window.unset_nodeAnimation();
            }


			// get node by id
			var node_anim = cy_rep.$('#' + node_anim_id);
			var type = node_anim[0]._private.data.type;
			var label = node_anim[0]._private.data.label;
			//var state = node_anim[0]._private.data.state;
			//check given state
            var anim_style = {};
            var anim_label = null;
            var blink = true;


            //Store previous animation so that we unset an animation
            window.OBCUI.previous_animation = {
                node_anim: node_anim,
                label: label,
                style: [],
                actions: []
            };
			
			//console.log('nodeAnimation type:' +  type);
			
			/* Tools have 4 states :  pending (default), installing, installed, failed. */
			if(type === 'tool'){
					if(state==="installing")  {
						anim_style = {'background-color': 'yellow'};
						anim_label = label +  "[installing]";
					}
					else if(state==="installed")  {
						anim_style = {'background-color': '#43A047'};
						anim_label = label + "[installed]";
                        blink = false;
					}
					else if(state==="failed")  {
						anim_style = {'background-color': '#E53935'};
						anim_label = label + "[failed]";
					}
                    else {
                         console.warn('63245');
                    }

			}
			
			/* Steps have 3 states :  "not running" (default), "running", "failed". */
			else if(type === 'step'){
					if(state==="running")  {
						anim_style = {'background-color': 'yellow'};
						anim_label = label + "[running]";
					}
                    else if (state == "finished") {
                        anim_style = {'background-color': '#43A047'};
                        anim_label = label + "[finished]";
                        blink = false;

                    }
					else if(state==="failed")  {
						anim_style = {'background-color': '#E53935'};
						anim_label = label + "[failed]";
					}
                    else {
                        console.warn('63246');
                    }
			}
			
			/* Outputs have 2 states :  "Unset" (default), "Set" */
			else if(type === 'output'){
					if(state==="set")  {
							anim_style = {'background-color': '#43A047'};
							anim_label = label + "setted";
					}
                    else {
                        console.warn('63247');
                    }
			}
			
            else if (type === 'workflow') {
                    if (state==='started') {
                        anim_style = {'background-color': '#43A047'};
                        anim_label = label + '[started]';
                    }
                    else if (state === 'finished') {
                        anim_style = {'background-color': '#000000'};
                        anim_label = label + '[finished]';
                        blink = false;
						
                    }
                    else {
                        console.warn('63248');
                    }
            }
			
			
			//update label
			node_anim.data('label', anim_label);
            window.OBCUI.previous_animation.actions.push('LABEL');

            //Update style
            if (anim_style) {
                for (var anim_item in anim_style) {
                    window.OBCUI.previous_animation.style.push([anim_item, node_anim.style(anim_item)]);
                }
            }
            window.OBCUI.previous_animation.actions.push('STYLE');
			node_anim.style(anim_style);
			
            if (blink) {
    			//make nodes blinking
    			var nodeAni = node_anim.animation({
    							style: {
    								'opacity': 0.1
    							},
    							duration: 200
    						});

    			//create time interval for continous looping of the animation				
    			var myVar = setInterval(nodeTimer, 200);

    			
    			function nodeTimer() {

    				nodeAni
    				  .play() // start
    				  .promise('completed').then(
    						function(){ // on next completed
    							nodeAni
    							  .reverse() // switch animation direction
    							  .rewind() // optional but makes intent clear
    							  .play() // start again
    							;
    				  });

    			}

    			nodeTimer();
                window.OBCUI.previous_animation.actions.push('BLINK');
            }
			
			/*
			return (node_anim.animation({
						  style : anim_style, 	//style: { 'background-color': 'red', 'label':''},
						  duration: 1  			//duration of animation in milliseconds
						}).play()   			//.promise('complete').then(loopEdgeAnimation(edge_anim)) :TODO fic it so that it can loop
					);
			*/
			
		};
						
		/* function for edge animation 
        * window.edgeAnimation('hapmap2__1__2__2', 'md5checkdir__1__2__2', "Running")    63Lf7 
        * ALWAYS CALL THIS FUNCTION AFTER nodeAnimation.
        * Or: Fix: window.OBCUI.previous_animation
        */ 
		window.edgeAnimation = function(source_anim_id, target_anim_id, state){
			//check_it
			// create and call "unset_edgeAnimation"
			
			// get edge by source / target
			var edges  = cy_rep.$("edge"); 
			var edge_blink = true;
            var edge_anim = cy_rep.$('edge[source = "' + source_anim_id + '"][target = "' + target_anim_id + '"]');

            if (!edge_anim.length) {
                if (source_anim_id != 'main') {
                    //console.log('WARNING: COULD NOT FIND EDGE!');
                    //console.log('SOURCE:', source_anim_id);
                    //console.log('TARGET:', target_anim_id);
                }
                return;
            }
				
			/* (1) "Never run", (2) Running blinking, (3) "run at least once" */ 
			//var edge_anim_style=null;
			var edge_anim_label=null;
				
			//if(state==="Never run") edge_anim_style = { 'line-color': 'red', 'target-arrow-color': 'red'};
			if (state==="running") {
			    //edge_anim_style = { 'line-color': 'red', 'target-arrow-color': '#E53935', 'label': 'running'};
				edge_anim_label='running';
			}
            else {
                //console.log('WARNING: Unknown state on edgeAnimation:', state);
                return;
            }
				
			//update label
			edge_anim.style('label', edge_anim_label);
			  	
			//make edges blinking
			var edgeAni = edge_anim.animation({
				style: {'opacity': 0.1},
				duration: 200
				});

            function edgeTimer() {

                edgeAni
                  .play() // start
                  .promise('completed').then(
                        function(){ // on next completed
                            edgeAni
                              .reverse() // switch animation direction
                              .rewind() // optional but makes intent clear
                              .play() // start again
                            ;
                  });
            }

			//create time interval for continous looping of the animation				
			var myVar = setInterval(edgeTimer, 200);
			edgeTimer();
			//window.OBCUI.previous_animation.actions.push('EDGE BLINK');

            window.OBCUI.previous_animation.edge_anim = edge_anim;
            window.OBCUI.previous_animation.actions.push('EDGE BLINK');
            window.OBCUI.previous_animation.actions.push('EDGE LABEL');
			
		};
		
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

            // parse incoming data and transform to cytoscape format
            var treeData = parseWorkflow(myworkflow, belongto);
            var openId;

            //concat all data
            if (typeof currentElements.nodes !== 'undefined') {

                /* check if new node exists in current data */
                treeData.nodes.forEach(function (element) {
                    currentElements.nodes.forEach(function (celement) {
                        if (element.data.id === celement.data.id) {
                            openId = celement.data.id;
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

            }

            // this is needed because cy.add() causes multiple instances of layout
            window.initializeTree();

            cy.json({ elements: treeData });   // Add new data
            cy.ready(function () {             // Wait for nodes to be added  
                cy.layout({                    // Call layout
                    name: 'breadthfirst',
                    directed: true,
                    padding: 2
                }).run();

            });


            //Add open flag for nodes that should always stay open (these are the nodes that belong to more than one tool)
            cy.$('#' + openId).data('flag', 'open');

            window.cy_setup_events();
            //close successors of tool
            cy.$('node[type="tool"][root="yes"]').successors().targets().style("display", "none");

        }


		/**
		** This function updates the workflow so that the can be forked: root edit changes to null
		** fork workflow , workflow fork 
		**/
        window.forkWorkflow = function () {

            var currentElements = cy.json().elements;
            var old_root_id, old_root_name, old_root_edit, old_root_belong;
            var new_root, new_root_id;

            // Find the root workflow and change edit to null
            currentElements.nodes.forEach(function (node) {
                if (node.data.belongto === null) {

                    // Find the root workflow					
                    old_root_id = node.data.id;
                    old_root_name = node.data.name;
                    old_root_edit = node.data.edit;
                    old_root_belong = { name: old_root_name, edit: old_root_edit };

                    // Updated id
                    //new_root = { name: node.data.name, edit: null };
                    new_root = { name: 'root', edit: null };

                    //new_root_id = create_workflow_id(new_root);
                    new_root_id = 'root__null';
                    node.data.id = new_root_id;
                    // Update edit. edit = null
                    node.data.edit = null;
                    node.data.name = 'root';

                }

            });

            //console.log("*************old_root_belong**************");
            //console.log(old_root_belong);


            // Change belongto for the nodes that have root workflow as source
            currentElements.nodes.forEach(function (node) {

                //Root node belongto is null
                if (!node.data.belongto) {
                    return;
                }

                //Unfortunately: 
                // JSON.stringify({a:'a', b:'b'}) === JSON.stringify({a:'a', b:'b'}) --> True
                // JSON.stringify({a:'a', b:'b'}) === JSON.stringify({b:'b', a:'a'}) --> False
                // there isn't any straightforward way of comparing key-pair objects in javascript...
                // https://stackoverflow.com/questions/1068834/object-comparison-in-javascript 
                // Making sure that the order is correct
                var node_root_belong_ordered = { name: node.data.belongto.name, edit: node.data.belongto.edit };
                if (JSON.stringify(node_root_belong_ordered) === JSON.stringify(old_root_belong)) {
                    //node.data.belongto = { name: old_root_name, edit: null };
                    node.data.belongto = { name: 'root', edit: null };
                    if (['step', 'input', 'output'].indexOf(node.data.type) >= 0) {
                        node.data.id = create_step_id(node.data, new_root);
                        //node.data.id = node.data.id.substr(0, node.data.id.lastIndexOf(window.OBCUI.sep))+'__null';
                    }
                }

                /** List os steps, inputs, outputs should also be updated if they contain references to root wf. **/

                // List of steps.			
                if (typeof node.data.steps != 'undefined' && node.data.steps.length > 0) {
                    replace_worfklow_id_of_list_of_SIO_id(node.data.steps, old_root_id, new_root);
                }

                // List of inputs.
                if (typeof node.data.inputs != 'undefined' && node.data.inputs.length > 0) {
                    replace_worfklow_id_of_list_of_SIO_id(node.data.inputs, old_root_id, new_root);
                }

                // List of outputs.
                if (typeof node.data.outputs != 'undefined' && node.data.outputs.length > 0) {
                    replace_worfklow_id_of_list_of_SIO_id(node.data.outputs, old_root_id, new_root);
                }

                /* bash field of node should also be updated if it contains call to step, input, output */

                if (typeof node.data.bash != 'undefined') {  // TODO: 'bash' in node.bash CODING STYLE

                    // Change the step id
                    function change_SIO_id(old_step_id, new_step_id) {
                        if (get_workflow_id_from_SIO_id(old_step_id) == old_root_id) {
                            return create_SIO_id({ name: get_SIO_name_from_SIO_id(old_step_id) }, new_root);
                        }
                        else {
                            return old_step_id;
                        }
                    }


                    //console.log('OLD BASH:');
                    //console.log(node.data.bash);

                    //Change step ids
                    node.data.bash = window.OBCUI.edit_bash(node.data.bash, change_SIO_id, window.OBCUI.get_steps_from_bash_script, window.OBCUI.call_replace);

                    //Change input/output ids
                    node.data.bash = window.OBCUI.edit_bash(node.data.bash, change_SIO_id,
                        function (t) {
                            var ret = window.OBCUI.get_input_outputs_from_bash_script(t);
                            return ret.inputs.concat(ret.outputs);
                        },
                        window.OBCUI.io_replace);

                    //console.log('NEW BASH:')
                    //console.log(node.data.bash);

                    //window.OBCUI.edit_steps_from_bash_scripts(node.data.bash, old_root_id, new_root);

                }
            });


            // change all edges that connect to root.  
            if ('edges' in currentElements) { 
                // There is an extreme case where a workflow may not have any edge! The line above checks for this case.
                currentElements.edges.forEach(function (edge) {

                    /* EDGE SOURCES */

                    //find edges that have as source the root workflow
                    if (edge.data.source === old_root_id) {
                        edge.data.source = new_root_id;
                    }

                    //Find edges that have the root_workflow in their source
                    else if (get_workflow_id_from_SIO_id(edge.data.source) === old_root_id) {
                        edge.data.source = create_SIO_id({ name: get_SIO_name_from_SIO_id(edge.data.source) }, new_root);
                    }

                    //if(edge.data.source.endsWith(old_root))
                    //	edge.data.source = edge.data.source.substr(0, edge.data.source.lastIndexOf(old_root))+new_root; 

                    /* EDGE TARGETS */

                    if (edge.data.target == old_root_id) {
                        edge.data.target = new_root_id;
                    }

                    //Find edges that have the root_workflow in their target
                    else if (get_workflow_id_from_SIO_id(edge.data.target) === old_root_id) {
                        edge.data.target = create_SIO_id({ name: get_SIO_name_from_SIO_id(edge.data.target) }, new_root);
                    }


                    //if(edge.data.target.endsWith(old_root))	//check for steps that ends with old_root
                    //	edge.data.target = edge.data.target.substr(0, edge.data.target.lastIndexOf(old_root))+new_root; 
                    //

                    //Change the id of the edge
                    edge.data.id = create_workflow_edge_id(edge.data.source, edge.data.target);

                });
            }

            /** re run layout **/
            // this initialization is needed because cy.add() causes multiple instances of layout
            window.initializeTree();

            cy.json({ elements: currentElements });   // Add updated data
            cy.ready(function () {          		 // Wait for nodes to be added  
                cy.layout({                   		// Call layout
                    name: 'breadthfirst',
                    directed: true,
                    padding: 2
                }).run();

            });


            //Add open flag for nodes that should always stay open (these are the nodes that belong to more than one tool) : TODO FIX THAT, NOT WORKING LIKE THAT
            //cy.$('#'+openId).data('flag', 'open');		

            window.cy_setup_events();

        }

        /*
        * Called from angular $scope.workflow_info_run_pressed
        * * Check if input options are unset
        * * Get the workflow options
        */
        window.OBCUI.get_workflow_options = function () {
            var workflow_options = {}

            cy.json().elements.nodes.forEach(function (node) {
                if (node.data.type === "input") {  //if node is input check if has value
                    if (typeof node.data.value === 'undefined') {
                        workflow_options[node.data.id] = null;
                    }
                    else {
                        workflow_options[node.data.id] = node.data.value;
                    }
                }

            });

            return workflow_options;


        };


        /*
        * Deletes all elements
        * Adds a root workflow node
        */
        window.clear = function (name) {
            //cy.destroy();
            cy.remove('edge, node');

            cy.json({
                elements: {
                    nodes: [{ data: { id: create_workflow_id({ name: name, edit: null }), label: name, name: name, edit: null, type: "workflow", belongto: null } }]
                }
            });

				cy.resize();
				cy.reset();
				cy.center();

        };

		/*
		* Fits workflow's content in center
		*/
        window.fit = function () {
            //cy.reset();
            //cy.center();
			 cy.layout({// Call layout
                name: 'breadthfirst',
                directed: true,
                padding: 2
            }).run();

        };

    }

	
	
	/***  TIMELINE  ***/
    window.OBCUI.set_timeline = function(timeline_data) {
		
		 var groups = new vis.DataSet([
				{id: 1, content: 'Workflows', value: 1},
				{id: 2, content: 'Tools', value: 2},
				//{id: 3, content: ' ', value: 3}
			  ]);
					
		
        window.OBCUI.timeline.setItems(timeline_data);
        window.OBCUI.timeline.setGroups(groups);
		
		window.OBCUI.timeline.fit();

		window.OBCUI.timeline.on('click', function (properties) {

    		window.OBCUI.timeline.itemsData.getDataSet().forEach(function (myItem) {
    				if(myItem.id===properties.item){						
    					nodeAnimation_public(myItem.params);
    				}
    				
    		});
		}); 
    };
	

    // END OF GALATEIA'S CODE

    /*
    * Handle interinks. Called by the javascript function injected from function replace_interlinks in views.py
    */
    window.OBCUI.interlink = function(args) {
        //console.log('interlink:');
        //console.log(args);

        //Call the angular function
        angular.element($('#angular_div')).scope().$apply(function () {
            angular.element($('#angular_div')).scope().interlink(args); 
        });
    };


    if (window.general_success_message) {
	generateToast(window.general_success_message, 'green lighten-2 black-text', 'stay on');
    }

    if (window.general_alert_message) {
	generateToast(window.general_alert_message, 'red lighten-2 black-text', 'stay on');
    }

    /*
    * Send a validation mail
    */
    window.OBCUI.send_validation_mail = function() {
        angular.element($('#angular_div')).scope().$apply(function () {
            angular.element($('#angular_div')).scope().send_validation_email();
        });
    };

    // Show reset password modal?
    if (window.password_reset_token) {
        setTimeout(function(){ 
            angular.element($('#angular_div')).scope().$apply(function () {
                 angular.element($('#angular_div')).scope().show_reset_password_from_ui();
            });
        }, 1000);

    }

    // Link to a specific RO?
    if (window.init_interlink_args) {
        setTimeout(function(){
            window.OBCUI.interlink(window.init_interlink_args);
        }, 1000);
    }

    //console.log('window.init_interlink_args:');
    //console.log(window.init_interlink_args);
 
};
