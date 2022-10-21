import server

dp = server.Dispatcher()
res = server.Resolver(dp)

def example(_, head):
    f = open("index.html", "r")
    file = f.read()
    return file+"\n\nData: "+head[0]
dp.add_handler(example, {"type": "GET", "path": "/"})

res.polling("localhost", 80)