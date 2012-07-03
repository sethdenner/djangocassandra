#!/usr/bin/node
// NB:- node's http client API has changed since this was written
// this code is for 0.4.x
// for 0.6.5+ see http://nodejs.org/docs/v0.6.5/api/http.html#http.request

var http = require('http');

var data = JSON.stringify({ 'id':'24f285fd-847e-4f95-8efe-9ca510d9a64f', 'value': 'Welcome to Knotis.com. Have an extra nice day!'});
var cookie = 'something=anything'

//http://mbp-ubuntu.local:8888/api/content/
var client = http.createClient(8888, 'mbp-ubuntu.local');

var headers = {
    'Host': 'mbp-ubuntu.local',
    'Cookie': cookie,
    'Content-Type': 'application/json',
    //'Content-Type': 'text/html',
    'Content-Length': Buffer.byteLength(data,'utf8')
};

var request = client.request('PUT', '/api/content/write', headers);

// listening to the response is optional, I suppose
request.on('response', function(response) {

  response.on('data', function(chunk) {
    //console.log('-- begin -- ');
    console.log(chunk.toString('utf8'));
  });

  response.on('end', function(chunk) {
    //console.log('-- end --');
  });
});
// you'd also want to listen for errors in production

request.write(data);

request.end();
