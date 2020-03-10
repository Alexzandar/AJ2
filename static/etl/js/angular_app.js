angular.module('todoApp', [])
  .controller('CustomerController', function($scope, $http) {
$scope.customer = {};
$scope.sys_index = 0;
$scope.systems = [
  {
    erp:1,
    name:'sample',
    client_code:'',
    url:'',
    auth_type:'',
    username: '',
    password: '',
    token: ''
  },
  {
    erp:2,
    name:'',
    client_code:'',
    url:'',
    auth_type: '',
    username: '',
    password: '',
    token: ''
  }
];
$scope.erps = [];

$scope.addRow = function(){
  $scope.systems.push({
    erp:1,
    name:'',
    client_code:'',
    url:'',
    auth_type:'',
    username: '',
    password: '',
    token: ''
  })
}

$scope.delRow = function(index){
  $scope.systems.splice(index,1);
}

$scope.submitForm = function($event){
  var token =  $('input[name="csrfmiddlewaretoken"]').attr('value');
  $http.post('/actionbot/masters/save-customer/',
  {data:{
    customer: $scope.customer,
    systems: $scope.systems
  }
  },
  {headers:{
    'X-CSRFToken' :token,
    'Content-type': 'application/json'
  }}
  ).then( function(response) { 
    $scope.students = response.data; 
 }); 
 $event.preventDefault();
}
$scope.showCredentialPopup = function(index){
  $scope.sys_index = index;
  $('#test2').modal();
}

// $scope.customer.name = 'sanu';    
  }).config(function($locationProvider,$interpolateProvider){
    $locationProvider.html5Mode({
              enabled:true
    });
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');


 });    ;