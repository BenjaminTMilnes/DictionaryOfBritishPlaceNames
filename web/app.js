var application = angular.module("DictionaryOfBritishPlaceNames", ["ngRoute", "ngSanitize"]);

application.config(function ($routeProvider) {
    $routeProvider
        .when("/", { templateUrl: "search.html", controller: "SearchController" });
});

application.directive("compile", ["$compile", function ($compile) {
    return function (scope, element, attributes) {
        scope.$watch(function (scope) {
            return scope.$eval(attributes.compile);
        }, function (value) {
            element.html(value);
            $compile(element.contents())(scope);
        });
    };
}]);

application.factory("dataService", ["$http", function ($http) {
    var dataService = {
        data: null,
        getData: function () {
            var that = this;

            if (this.data != null) {
                return new Promise(function (resolve, reject) { return resolve(that.data); });
            }

            return $http.get("places.json").then(function (response) {
                that.data = response.data;

                return that.data;
            });
        }
    };

    return dataService;
}]);

application.controller("SearchController", ["$scope", "dataService", "$location", function SearchController($scope, dataService, $location) {

    dataService.getData().then(function (data) {
        $scope.places = data.Places;
    });

    $scope.goToPlacePage = function (place) {
        $location.url("/place/" + place.URLReference);
    }

}]);