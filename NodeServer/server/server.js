const path = require('path');
const express = require ('express');
const http = require('http');
const socketIO = require('socket.io');

const publicPath = path.join(__dirname, '../public');
var app = express();
var server = http.createServer(app);
var io = socketIO(server);
var relayState = false;

app.use(express.static(publicPath));


//Copied
function ParseJson(jsondata) {
    try {
        return JSON.parse(jsondata);
    } catch (error) {
        console.log("something went wrong while parsing Json");
    }
}

function sendTime() {
    io.sockets.emit('atime', { time: new Date().toJSON() });
}


io.on('connection', (socket) => {
    console.log("new user connected");
// Copied
    socket.emit('welcome', { message: 'Connected to the Server', relayState: relayState});

    socket.on('connection', function (data) {
        console.log(data);   });

    socket.on('clientPi', function (data) {
       if(data === 'faceDetected'){
           io.sockets.emit('arduino', {message: 'relayON'});
       }else if(data === 'strangerDetected'){
           io.sockets.emit('android', {message: 'callHost'})
       }
       console.log(data)
    });

    socket.on('clientArduino', function (data) {
        sendTime();
        io.sockets.emit('temp',data);
        console.log(data);
    });

    socket.on("relayON", function (message) {
       io.sockets.emit('arduino', {message: 'relayON'});
       relayState = true;
       console.log(message);
    });

    socket.on("relayOFF", function (message) {
        io.sockets.emit('arduino', {message: 'relayOFF'});
        relayState = false;
        console.log(message);
    });


    socket.on('JSON', function (data) {
        // console.log(data);
        var jsonStr = JSON.stringify(data);
        var parsed = ParseJson(jsonStr);
        console.log(parsed);
        // console.log(parsed.sensor);
    });

    socket.on('arduino', function (data) {
        io.sockets.emit('arduino', { message: 'R0' });
        console.log(data);
    });

    socket.on('disconnect', function() {
        console.log('user disconnected from server');
    })
});


server.listen(3008, function() {
    console.log('Started on port 3008');
});

