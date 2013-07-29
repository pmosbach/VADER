var http = require('http'); 

http.createServer(function (req, res) { 
  

   if (req.method == 'POST') { //loop that checks it is post 
      var body = '';   //creating that body variable
      req.on('data', function (data) { //function that takes in the data 
         body += data;   //concatenats the incoming data with the body variable
      });

      req.on('end', function () { //think of as my trigger, only stops collecting data when it ends
        var command = JSON.parse(body); //parses the body according to json library
        // use POST 
        res.writeHead(200, {'Content-Type': 'application/json'});  //writes the header
        res.end(command.method); //end response, filters out body and prints it in data section
   }); 

}

 }).listen(8124); 

console.log('Server running at http://127.0.0.1:8124/');  //tells us the server is active


function createreq(){   //do i need this?

//hey, give me your information



}

function handleres(){
//the response will handle the IP address, building, org

//i can handle taking this information in

//oh, so this is your information? Let me print it out for you!
   //res.end(ipaddress, building, org);

}
