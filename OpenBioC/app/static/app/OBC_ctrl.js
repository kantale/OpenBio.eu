
app.controller("OBC_ctrl", function($scope) {
    $scope.init = function() {
        $scope.inner_hide_all_navbar();
    };

    /*
    *
    */
    $scope.inner_hide_all_navbar = function() {
    	$scope.show_login = false;
    };

    /*
    *
    */
    $scope.navbar_login_pressed = function() {
    	$scope.inner_hide_all_navbar();
    	
    	$scope.show_login = true;
    };

    /*
    *
    */
    $scope.navbar_signup_pressed = function() {
    	$scope.inner_hide_all_navbar();
    };
}); 


