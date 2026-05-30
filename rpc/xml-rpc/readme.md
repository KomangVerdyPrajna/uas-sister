**This demonstration provides a practical implementation of XML-RPC (XML Remote Procedure Call), a protocol that uses XML to encode its calls and HTTP as a transport mechanism. The example illustrates how clients can invoke methods on remote servers, showcasing the request/response pattern, parameter marshaling in XML format, and HTTP-based communication between distributed systems.**<br><br>
To see how the marshalling/unmarshalling work, follow steps below:
1. Install [Postman](https://www.postman.com/downloads/)
2. Run the Server
Keep the Python XML-RPC server from the previous step running. It is listening on http://localhost:8000.
3. Configure Postman
Instead of using a Python client, we will "fudge" the client stub using Postman.
Method: Set to POST.
URL: Enter http://localhost:8000.
Headers: Add Content-Type: text/xml.
Body: Select raw and choose XML from the dropdown.
4. Manually Marshall the Request<br>
   Paste this XML into the Body. This is the Marshalling step usually done by the ServerProxy. You are telling the server exactly which procedure to run and with what variable.
```xml
<?xml version="1.0"?>
<methodCall>
  <methodName>check_price</methodName>
  <params>
    <param>
      <value><string>phone</string></value>
    </param>
  </params>
</methodCall>
```
5. Observe the Unmarshalled Response<br>
   When you hit Send, the server receives your XML, unmarshalls it to find the string "phone," runs the Python function, and marshalls the result back. Postman will show:
```xml
<?xml version='1.0'?>
<methodResponse>
  <params>
    <param>
      <value><int>800</int></value>
    </param>
  </params>
</methodResponse>
```
