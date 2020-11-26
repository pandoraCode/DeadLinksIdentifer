var http = require('http');  
var url = require('url');  
var fs = require('fs');
var path = require('path');

// Receiving parameters
if (process.argv.length == 5) {
  var hostname = process.argv[2];
  var port = process.argv[3];
  var path_website = process.argv[4];
} else {
  console.error('\nPlease, type: node server.js <hostname> <port> <directory_with_website>\n');
  process.exit(1);
}

// TODO: NATIVE APPLICATION: DOES NOT RENDER CSS. HAVE TO ADD ROUTES MANUALLY
var server = http.createServer(function(request, response) {  
    var full_path = path.join(path_website, 'index.html');
    switch (full_path) {   
        case full_path:  
            fs.readFile(full_path, function(error, data) {  
                if (error) {  
                    response.writeHead(404);  
                    response.write(error);  
                    response.end();  
                } else {  
                    response.writeHead(200, {  
                        'Content-Type': 'text/html'
                    });  
                    response.write(data);  
                    response.end();  
                }  
            });  
            break;  
        default:  
            response.writeHead(404);  
            response.write("Error 404! Website does not exist! Maybe it's missing the file index.html");  
            response.end();  
            break;  
    }  
});  
server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});