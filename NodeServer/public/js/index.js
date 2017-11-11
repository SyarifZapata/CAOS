var socket = io();
var temp;
var relayState = false;

socket.on('connect', function() {
    console.log('connected to the server');


});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
});

socket.on('temp', function (data) {
    console.log(data)
   temp = data;
});

var getTemp = function () {
    console.log(temp);
   document.getElementById('temp').innerHTML = temp.message;
};

var turnOnRelay = function () {
    console.log("Request to turning on the relay");
    socket.emit("relayON", {message: "relayToggle"});
    if(!relayState){
        socket.emit("relayON", {message: "relayToggle"});
        relayState = true;
    }else{
        socket.emit("relayOFF", {message: "relayToggle"});
        relayState = false;
    }

};
