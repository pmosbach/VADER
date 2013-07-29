var http = require('http'); 

http.createServer(function (inreq, res){

  var body = '';

  inreq.on('data', function (data){
     body += data;
  });

 inreq.on('end', function(){


   var user = { 
      jsonrpc: '2.0', 
      id: '1', 
      method: 'GUI.ShowNotification',
      params: {
         title: 'HAYLEY AND PETER ROCK!',
         message: body 
     }
   }; 

var userString = JSON.stringify(user); 

var headers = { 
   'Content-Type': 'application/json', 
   'Content-Length': userString.length 
};
 
var options = { 
   host: '10.12.3.65', 
   port: 80, 
   path: '/jsonrpc', 
   method: 'POST', 
   headers: headers 
}; 


// Setup the request. The options parameter is 
// the object we defined above. 

var outreq = http.request(options, function(res) { 
   res.setEncoding('utf-8'); 
   var responseString = ''; 
   res.on('data', function(data) {
   responseString += data;
 }); 

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

}).listen(8124);
