# Basic Application Example

import server

dp = server.Dispatcher()
res = server.Resolver(dp)

def example(payload, headers): # payload - list, headers - list
    f = open("index.html", "r")
    file = f.read()
    return file+"\n\nPayload: "+str(payload)+"\n\nHeaders: "+str(headers)
dp.add_handler(example, {"type": "GET", "path": "/"})

res.polling("localhost", 80)
