var http = require('http'); 

http.createServer(function (req, res) { 
  

   if (req.method == 'POST') { 
      var body = '';
      req.on('data', function (data) { 
         body += data;
      });

      req.on('end', function () { 
        // var POST = qs.parse(body); 
        // use POST 
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.end(body + '\n'); }); 
}


 }).listen(8124); 
console.log('Server running at http://127.0.0.1:8124/');
