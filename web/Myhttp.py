from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer


class MyHandler(BaseHTTPRequestHandler):
    def do_get(self):
        try:
            f = open(self.path[1:],'r')
            self.send_response(200)
            self.send_header('content-type','text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        except IOError:
            self.send_error(404,'file not found: %s' % self.path)

    def main(self):
        try:
            server = HTTPServer(('',80),MyHandler)
            print "welcome"
            print "press ^c once or twice to quit."
            server.serve_forever()
        except KeyboardInterrupt:
            print "^c received,shutting down server"
            server.socket.close()

    if __name__ == '__main__':
        main()
