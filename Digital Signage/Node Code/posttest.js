var http = require('http'); 

http.createServer(function (inreq, res){

  var body = '';

  inreq.on('data', function (data){
     body += data;
  });

 inreq.on('end', function(){
   res.writeHead(200, {'Content-Type': 'application/json'});
   res.end('{OK}\n');
   var user = { 
      jsonrpc: '2.0', 
      id: '1', 
      method: 'GUI.ShowNotification',
      params: {
         title: 'HAYLEY AND PETER ROCK!',
         message: body 
     }
   }; 
  console.log(body);

var userString = JSON.stringify(user); 

var headers = { 
   'Content-Type': 'application/json', 
   'Content-Length': userString.length 
};
 
var options = { 
   host: '10.128.1.140', 
   port: 80, 
   path: '/jsonrpc', 
   method: 'POST', 
   headers: headers 
}; 
    console.log('Before outgoing request');

// Setup the request. The options parameter is 
// the object we defined above. 

var outreq = http.request(options, function(res) { 
   console.log('start of outgoing request');

   res.setEncoding('utf-8'); 
   var responseString = ''; 
   res.on('data', function(data) {
       responseString += data;
    }); 
   console.log('Leaving outgoing request');
  res.on('end', function() { 
     var resultObject = JSON.parse(responseString); 
  }); 
}); 

outreq.on('error', function(e) { 
   // TODO: handle error. 
   });


outreq.write(userString); 
outreq.end();

});
 console.log('This is the end');
}).listen(8124);
