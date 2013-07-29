var http = require('http'); 

http.createServer(function (req, res) { 
  

   if (req.method == 'POST') { 
      var body = '';
      req.on('data', function (data) { 
         body += data;
      });

      req.on('end', function () { //think of as my triggah
        var command = JSON.parse(body); 
        // use POST 
        res.writeHead(200, {'Content-Type': 'application/json'});
        res.end(command.method); //end response
   }); 
}

 }).listen(8124); 
console.log('Server running at http://127.0.0.1:8124/');
