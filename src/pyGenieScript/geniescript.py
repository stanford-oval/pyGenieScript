import subprocess
import requests


class Genie:
    def __init__(self,
                 nlu_server_address : str,
                 thingpedia_dir : str,
                 log_file_name : str = 'log.log') -> None:
        # initialize genie server and retrieve the randomly assigned port number
        self.command = 'genie contextual-genie --nlu-server {} --thingpedia-dir {} --log-file-name {}'.format(nlu_server_address, thingpedia_dir, log_file_name)
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while True:
            output = self.process.stdout.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output and "Server port number at" in output.strip().decode():
                print(output.strip().decode())
                self.port_number = int(output.strip().decode().split(',')[-1].strip())
                break
        
        print(self.port_number)

        self.url = "http://127.0.0.1:{}/".format(self.port_number)
        
    def query(self, query : str):
        params = {'q': query}
        r = requests.get(url = self.url + "query", params = params)
        res = r.json()
        return res

    def quit(self):
        r = requests.post(url = self.url + "quit")
        return r.json()
        
        

if __name__ == '__main__':
    genie = Genie("http://127.0.0.1:8400",
                  "/Users/shichengliu/Desktop/Monica_research/thingpedia-common-devices/geniescript",
                  'log.log')
    print(genie.query('find me a restaurant'))
    print(genie.quit())
    