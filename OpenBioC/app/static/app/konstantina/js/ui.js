/*

DONE:
1. Signup error (i.e. confirm password not match)
2. Toast. after signup "success", with "X" button. Programmatically close. 

*/

// ui.js
// style.css ->konstantina
// navbar2.html


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


window.onload = function () {

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // ------------------------------------------------------------------- Initializations ------------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    var animationEnded;
    function init() {

        

        var avatarImg = '/static/app/images/konstantina/img_avatar.png';
        var avatars = document.getElementsByClassName('imgAvatar');
        for (var i = 0; i < avatars.length; i++) {
            $(avatars[i]).attr('src', avatarImg);
        }

        // ----------------------------------- Sidebar for navbar initialization -----------------------------------------
        $('.sidenav').sidenav();
        // ---------------------------------------- Modal initialization -------------------------------------------------
        $('.modal').modal();
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
        var collapsibles = document.getElementsByClassName('collapsible expandable');
        for (var i = 0; i < collapsibles.length; i++) {
            var elem = collapsibles[i];
            var instance = M.Collapsible.init(elem, {
                accordion: false,
                // Callback function called before collapsible is opened
                onOpenStart: function (event) {
                    // Workflows right panel collapsible
                    if (event.id == 'workflows') {
                        if (document.getElementById('workflowsRightPanel').style.display == 'none') {
                            document.getElementById('workflowsRightPanel').style.display = 'block';
                            $('#workflowsRightPanel').animateCss('slideInDown', function () {
                            });
                        }
                    }
                    // Disabled collapsible
                    if (!event.classList.contains('disabled')) {
                        event.getElementsByClassName('arrow')[0].innerHTML = 'keyboard_arrow_down';
                    }
                },
                // Callback function called after collapsible is opened
                onOpenEnd: function (event) {
                    // Disabled collapsible
                    if (event.classList.contains('disabled')) {
                        event.classList.remove('active');
                    }
                },
                // Callback function called before collapsible is closed
                onCloseStart: function (event) {
                    // Workflows right panel collapsible
                    if (event.id == 'workflows') {
                        if (document.getElementById('workflowsRightPanel').style.display == 'block') {
                            $('#workflowsRightPanel').animateCss('slideOutUp', function () {
                                document.getElementById('workflowsRightPanel').style.display = 'none';
                                disableEditWorkflow();
                            });
                        }
                    }
                    // Disabled collapsible
                    if (!event.classList.contains('disabled')) {
                        event.getElementsByClassName('arrow')[0].innerHTML = 'keyboard_arrow_right';
                    }
                }
            });
        }

        // ------------------------------------ Initializations for profile page -----------------------------------------
        // animationEnded = true;
        // var activeBtn = document.getElementById('leftPanelButtons').getElementsByClassName('active')[0];
        // showPanel(activeBtn.id.substring(0, activeBtn.id.indexOf("Btn")) + 'Panel');

        // $('#profilePublicInfo').val(
        //     'Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute, non cupidatat skateboard dolor brunch. Food truck.');
        // M.textareaAutoResize($('#profilePublicInfo'));
        // M.updateTextFields();

        // -------------------------------- Listener for DISABLE EDIT workflow button ------------------------------------
        document.getElementById('disableEditWorkflowBtn').addEventListener("click", disableEditWorkflow);

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
    document.getElementById('cancelToolDataBtn').addEventListener("click", function () {
        if (document.getElementById('createToolDataDiv').style.display == 'block') {
            $('#createToolDataDiv').animateCss('slideOutUp', function () {
                document.getElementById('createToolDataDiv').style.display = 'none';
                closeCollapsiblesOfAccordion('createToolDataAccordion');
            });
        }
    });

    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // --------------------------------------------------------- Enable Edit Workflow Button Click ----------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    document.getElementById('enableEditWorkflowBtn').addEventListener("click", function () {
        var collapsibles = document.getElementById('editWorkflowAccordion').getElementsByTagName('li');
        for (var i = 0; i < collapsibles.length; i++) {
            if (collapsibles[i].classList.contains('disabled')) {
                collapsibles[i].classList.remove('disabled');
            }
        }
        var instance = M.Collapsible.getInstance($('#editWorkflowAccordion'));
        instance.open(0);
    });

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
    // -------------------------------------------------------- Profile Page Collection Buttons Listener ----------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    // ---------------------------------------- Hide panel with given id ---------------------------------------------
    function hidePanel(panelId) {
        animationEnded = false;
        $('#' + panelId).animateCss('fadeOut', function () {
            document.getElementById(panelId).style.display = 'none';
            animationEnded = true;
        });
    }

    // ---------------------------------------- Show panel with given id ---------------------------------------------
    function showPanel(panelId) {
        animationEnded = false;
        document.getElementById(panelId).style.display = 'block';
        $('#' + panelId).animateCss('fadeIn', function () {
            animationEnded = true;
        });
    }

    // --------------------------------------------- Find active panel -----------------------------------------------
    function findBlockPanelId() {
        var panels = document.getElementById('rightPanel').getElementsByClassName('panel');
        for (var i = 0; i < panels.length; i++) {
            if (panels[i].style.display == 'block') {
                return panels[i].id;
            }
        }
        return null;
    }

    // ------------------------------------------ Collection buttons listener ----------------------------------------
    // document.getElementById('leftPanelButtons').addEventListener('click', function (event) {
    //     if (animationEnded) {

    //         var clickedBtn;
    //         if (event.target.tagName == 'I') {
    //             clickedBtn = event.target.parentNode;
    //         }
    //         else {
    //             clickedBtn = event.target;
    //         }

    //         var activeButtons = clickedBtn.parentNode.getElementsByClassName('active');
    //         for (var i = 0; i < activeButtons.length; i++) {
    //             activeButtons[i].classList.remove('active');
    //         }
    //         document.getElementById(clickedBtn.id).classList.add('active');


    //         if (clickedBtn.id == 'profileBtn') {
    //             var blockPanelId = findBlockPanelId();
    //             if ((blockPanelId != null) && (blockPanelId != 'profilePanel')) {
    //                 hidePanel(blockPanelId);
    //             }
    //             if (document.getElementById('profilePanel').style.display == 'none') {
    //                 showPanel('profilePanel');
    //                 M.textareaAutoResize($('#profilePublicInfo'));
    //                 M.updateTextFields();
    //             }
    //         }
    //         else if (clickedBtn.id == 'inboxBtn') {
    //             var blockPanelId = findBlockPanelId();
    //             if ((blockPanelId != null) && (blockPanelId != 'inboxPanel')) {
    //                 hidePanel(blockPanelId);
    //             }
    //             if (document.getElementById('inboxPanel').style.display == 'none') {
    //                 showPanel('inboxPanel');
    //             }
    //         }
    //         else if (clickedBtn.id == 'notificationsBtn') {
    //             var blockPanelId = findBlockPanelId();
    //             if ((blockPanelId != null) && (blockPanelId != 'notificationsPanel')) {
    //                 hidePanel(blockPanelId);
    //             }
    //             if (document.getElementById('notificationsPanel').style.display == 'none') {
    //                 showPanel('notificationsPanel');
    //             }
    //         }
    //         else if (clickedBtn.id == 'settingsBtn') {
    //             var blockPanelId = findBlockPanelId();
    //             if ((blockPanelId != null) && (blockPanelId != 'settingsPanel')) {
    //                 hidePanel(blockPanelId);
    //             }
    //             if (document.getElementById('settingsPanel').style.display == 'none') {
    //                 showPanel('settingsPanel');
    //             }
    //         }
    //     }
    // });


    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // --------------------------------------------------------------------- Splitter Bar -------------------------------------------------------------------------------------------
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    var splitterWidth = '20px';
    var splitterImg = '/static/app/images/konstantina/dehaze.png';
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

        var img = document.createElement('img');
        img.src = splitterImg;
        img.style.paddingTop = '10px';
        $(img).attr('id', 'splitterImg');

        newDiv.append(img);

        splitterBar = $(newDiv);
        splitterBar.css('background-color', '#cfd8dc');
        splitterBar.css('box-shadow', '0 0 10px rgba(0, 0, 0, 0.6)');
        splitterBar.css('z-index', '100');
        splitterBar.css('width', splitterWidth);
        splitterBar.css('height', '100%');
        splitterBar.css('cursor', 'w-resize');
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
            if (leftWidth <= parseInt(splitterWidth, 10)) {
                if (dragEnabled) {
                    leftSide.width(minPanelWidth);
                }
                else {
                    leftSide.width(screenWidth);
                }
            }
            // Show right panel
            else if (rightWidth <= parseInt(splitterWidth, 10)) {
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
            var newLeftWidth = Math.floor($(window).width() - parseInt(splitterWidth, 10));
            document.getElementsByClassName('leftPanel')[0].setAttribute('style', 'width:' + newLeftWidth + 'px');
        }
        else {
            dragEnabled = true;
            var newLeftWidth = Math.floor(($(window).width() - parseInt(splitterWidth, 10)) / 2);
            document.getElementsByClassName('leftPanel')[0].setAttribute('style', 'width:' + newLeftWidth + 'px');
        }
    }

    // Sets the height of splitter container
    function setSplitterContainerHeight() {
        var screenHeight = Math.floor($(window).height());
        var navbarHeight = document.getElementById('navbar').offsetHeight;
        document.getElementsByClassName('splitter-container')[0].style.height = (screenHeight - navbarHeight) + 'px';
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


    // https://github.com/ezraroi/ngJsTree/issues/20
    // We have to register the event on the document.. 
    $(document).on('dnd_stop.vakata', function (e, data) {


        console.log('tessssttt');

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

                angular.element($('#angular_div')).scope().$apply(function(){
                    angular.element($('#angular_div')).scope().tool_get_dependencies(tool, 1); // 1 = drag from search jstree to dependencies jstree
                });
            }
            else if (target.closest('#d3wf').length) { // We are dropping it to the workflow graph editor

                angular.element($('#angular_div')).scope().$apply(function(){
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
                (target.closest('#d3wf').length) // The Workflow graph editor
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
                (target.closest('#tool_validation_editor').length   && (!tool_validation_editor.getReadOnly()))       ) {
                data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
            }
            else {
                data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
            }

        }


    });


};