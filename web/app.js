

function stringContains(string1, string2) {
    return (string1.indexOf(string2) >= 0);
}

function stringIsNullOrEmpty(string) {
    return (!string || /^\s*$/.test(string));
}

var application = angular.module("DictionaryOfBritishPlaceNames", ["ngRoute", "ngSanitize"]);

application.config(function ($routeProvider) {
    $routeProvider
        .when("/", { templateUrl: "search.html", controller: "SearchController" })
        .when("/place/:reference", { templateUrl: "place.html", controller: "PlaceController" });
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

application.filter("paginate", function () {
    return function (a, pageNumber, numberOfItemsPerPage) {
        if (a == null || a == undefined) {
            return [];
        }

        if (pageNumber == null) {
            pageNumber = 1;
        }

        if (numberOfItemsPerPage == null) {
            numberOfItemsPerPage = 10;
        }

        var p = (pageNumber - 1) * numberOfItemsPerPage;
        var q = (pageNumber) * numberOfItemsPerPage;

        return a.slice(p, q);
    }
});

application.filter("searchPlaces", function () {
    return function (places, text) {
        if (places == null || places == undefined) {
            return [];
        }

        if (stringIsNullOrEmpty(text)) {
            return places;
        }
        else {
            var matchingPlaces = [];

            places.forEach(place => {

                if (text != "") {
                    if (stringContains(place.PrimaryName.toLowerCase(), text.toLowerCase())) {
                        matchingPlaces.push(place);
                    }
                    else if (stringContains(place.Description.toLowerCase(), text.toLowerCase())) {
                        matchingPlaces.push(place);
                    }
                }

            });

            return matchingPlaces;
        }
    }
});

application.controller("SearchController", ["$scope", "dataService", "$location", "$filter", function SearchController($scope, dataService, $location, $filter) {

    $scope.goToPlacePage = function (place) {
        $location.url("/place/" + place.URLReference);
    }

    $scope.pageNumber = 1;
    $scope.numberOfResultsPerPage = 10;
    $scope.numberOfPages = 1;
    $scope.pages = [];

    $scope.searchResults = [];
    $scope.currentPageSearchResults = [];

    $scope.searchTerms = "";

    dataService.getData().then(function (data) {
        $scope.places = data.Places;

        $scope.updateSearchResults($scope.searchTerms);
    });

    $scope.setPageNumber = function (n) {
        if (n <= 0 || n > $scope.numberOfPages) {
            return;
        }

        $scope.pageNumber = n;
        $scope.setPageNumberRange();
    }

    $scope.setPageNumberRange = function () {

        if ($scope.searchResults == null || $scope.searchResults == undefined) {
            return;
        }

        $scope.currentPageSearchResults = $filter("paginate")($scope.searchResults, $scope.pageNumber, $scope.numberOfResultsPerPage);

        $scope.numberOfPages = Math.ceil($scope.searchResults.length / $scope.numberOfResultsPerPage);
        $scope.pages = [];

        var addEllipses = 0;

        for (var i = 0; i < $scope.numberOfPages; i++) {
            if (i > 0 && i < $scope.numberOfPages - 1 && (i < $scope.pageNumber - 3 || i > $scope.pageNumber + 1)) {
                if (addEllipses == 0) {
                    $scope.pages.push({ "pageNumber": -1, "class": "pagenumber-ellipses" });
                }
                addEllipses = 1;
            }
            else {
                $scope.pages.push({ "pageNumber": i + 1, "class": (i == $scope.pageNumber - 1) ? "pagenumber-selected" : "pagenumber-unselected" });
                addEllipses = 0;
            }
        }
    }

    $scope.updateSearchResults = function (searchTerms) {
        $scope.searchResults = $filter("orderBy")($filter("searchPlaces")($scope.places, searchTerms), "place.PrimaryName");

        $scope.setPageNumberRange();
    }

    $scope.$watch("searchTerms", function (newValue, oldValue) {
        $scope.updateSearchResults(newValue);
    });

}]);

application.controller("PlaceController", ["$scope", "dataService", "$routeParams", "$location", "$filter", function PlaceController($scope, dataService, $routeParams, $location, $filter) {

    dataService.getData().then(function (data) {
        $scope.places = data.Places;
        $scope.abbreviations = data.Abbreviations;

        $scope.place = $scope.places.filter(p => p.URLReference == $routeParams.reference)[0];

        var l = $scope.place.Names.filter(n => n.Language == "latin");
        var mw = $scope.place.Names.filter(n => n.Language == "modern-welsh");
        var mi = $scope.place.Names.filter(n => n.Language == "modern-irish-gaelic");
        var ms = $scope.place.Names.filter(n => n.Language == "modern-scots");
        var msg = $scope.place.Names.filter(n => n.Language == "modern-scottish-gaelic");

        $scope.nameInLatin = (l.length > 0) ? l[0].Text : "";
        $scope.nameInModernWelsh = (mw.length > 0) ? mw[0].Text : "";
        $scope.nameInModernIrish = (mi.length > 0) ? mi[0].Text : "";
        $scope.nameInModernScots = (ms.length > 0) ? ms[0].Text : "";
        $scope.nameInModernScottishGaelic = (msg.length > 0) ? msg[0].Text : "";

        $scope.demonyms = $scope.place.Demonyms.map(d => d.Text).join(", ");
    });

    $scope.getLanguage = function (abbreviation) {
        return $scope.abbreviations(a => a.Name == abbreviation || a.Abbreviation == abbreviation || a.Name.toLowerCase.replace(" ", "-") == abbreviation)[0].Name;
    }

}]);