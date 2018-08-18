
/*
inner_: functions / variables not connected with the UI
show_ : shows / hide divs
*/

app.controller("OBC_ctrl", function($scope, $http) {
    $scope.init = function() {
        $scope.inner_hide_all_navbar();
        $scope.inner_hide_all_error_messages();
    };

    /*
    * Helper function that perform ajax calls
    * success_view: what to do if data were correct and call was successful
    * fail_view: What to do if call was succesful but data where incorrect
    * fail_ajax: what to do if ajax call was incorrect
    */
    $scope.ajax = function(url, data, success_view, fail_view, fail_ajax) {
        // URL should always end with '/'

        console.log('Before Ajax, data:');
        console.log(data);

        data.csrftoken = CSRF_TOKEN;

        $http({
            headers: {
                "Content-Type": 'application/json',
                "Access-Control-Allow-Origin": "*", // TODO : REMOVE THIS!
                //"X-CSRFToken" : getCookie('csrftoken'),
                "X-CSRFToken" : window.CSRF_TOKEN,
            },
            method : "POST",
            url : url,
            data : data
        }).then(function mySucces(response) {
            // $scope.myWelcome = response.data;
            // alert(JSON.stringify(response));
            if (response['data']['success']) {
                console.log('AJAX SUCCESS:');
                console.log(response['data']['success']);
                success_view(response['data']);
            }
            else {
                console.log('AJAX ERROR:');
                fail_view(response['data']);
            }
            
        }, function myError(response) {
            console.log('AJAX SYSTEM ERROR:');
            console.log(response.statusText);
            if (response.statusText) {
                fail_ajax(response.statusText);
            }
            else {
                fail_ajax('Internal Error. Server not responding');
            }
        });
    };

    /*
    * Hide everything 
    */
    $scope.inner_hide_all_navbar = function() {
    	$scope.show_login = false;
        $scope.show_signup = false;
    };

    /*
    * Hide all error messages
    */
    $scope.inner_hide_all_error_messages = function() {
        $scope.signup_error_message = '';
    };

    /*
    * navbar --> Login --> Pressed
    */
    $scope.navbar_login_pressed = function() {
    	$scope.inner_hide_all_navbar();
    	
    	$scope.show_login = true;
    };

    /*
    * Navbar --> Signup --> pressed 
    */
    $scope.navbar_signup_pressed = function() {
    	$scope.inner_hide_all_navbar();

        $scope.show_signup = true;
    };

    /*
    * Navbar --> Signup --> Signup (button) --> Pressed
    */
    $scope.signup_signup_pressed = function() {
        // signup_username
        // signup_password
        // signup_confirm_password
        // signup_email 

        $scope.ajax(
            'register/',
            {
                'signup_username' : $scope.signup_username,
                'signup_password' : $scope.signup_password,
                'signup_confirm_password': $scope.signup_confirm_password,
                'signup_email' : $scope.signup_email
            },
            function (data) {
                $scope.signup_error_message = '';
                $scope.show_signup = false;
            },
            function (data) {
                $scope.signup_error_message = data['error_message'];
            },
            function(statusText) {
                $scope.signup_error_message = statusText;
            }
        );

    };
}); 


