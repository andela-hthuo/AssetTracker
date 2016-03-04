(function () {
	'use strict';
	angular.module('assetsApp', [], function($interpolateProvider) {
		    $interpolateProvider.startSymbol('[[');
		    $interpolateProvider.endSymbol(']]');
		})
		.controller('AssetsController', ['$scope' ,'$http' , function ($scope, $http) {
			$scope.assetsUrl = $('#assetsUrl').val();
			$scope.loadAssets = function() {
				$scope.loading = true;
				$scope.error = false;
				$scope.assets = [];
				$http({
					method: 'GET',
					url: $scope.assetsUrl
				}).then(function successCallback(response) {
				    $scope.loading = false;
				    $scope.assets = response.data;
				    // console.log($scope.assets);
				}, function errorCallback(response) {
				    $scope.loading = false;
				    $scope.error = true;
				    console.log(response);
				});
			}

			$scope.loadAssets();
		}]);

	angular.element(document).ready(function() {
		angular.bootstrap(document.getElementById('assets-app'), ['assetsApp']);
	});
})();