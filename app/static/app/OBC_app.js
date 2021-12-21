//var app = angular.module("OBC_app", ['ngJsTree', 'ui.select', 'ngSanitize']); // 'ui.tree' , 'treeControl' 


var app = angular.module("OBC_app", ['ngJsTree', 'ui.select', 'ngSanitize']).config(function($sceProvider) {
  // Completely disable SCE.  For demonstration purposes only!
  // Do not use in new projects or libraries.
  // https://docs.angularjs.org/api/ng/service/$sce 
  // 
  // Had to do this because of this issue: https://github.com/angular/angular.js/issues/16593 
  $sceProvider.enabled(false);
}); 

