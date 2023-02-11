import subprocess
import requests
import os
from huggingface_hub import snapshot_download
from pathlib import Path
import shutil
from glob import glob
import time
import logging

current_file_directory = os.path.dirname(os.path.abspath(__file__))

class Genie:
    def __init__(self):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # install genie:
        if (not os.path.exists(os.path.join(current_file_directory, "node_modules", "genie-toolkit", "dist"))):
            self.install_genie()

        
    def initialize(self,
                    nlu_server_address : str,
                    thingpedia_dir : str = 'None',
                    log_file_name : str = 'log.log',
                    force_update_model = False,
                    force_update_manifest = False) -> None:
        actual_server = self.download_or_find_model(nlu_server_address, force_update=force_update_model)
        actual_manifest = self.download_or_find_manifests(thingpedia_dir, force_update=force_update_manifest)
        
        # initialize genie server and retrieve the randomly assigned port number
        command = ['node', 'genie.js', 'contextual-genie',  '--nlu-server', actual_server, '--thingpedia-dir', actual_manifest,  '--log-file-name', log_file_name]
        self.logger.info(command)
        process = subprocess.Popen(command,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        cwd=os.path.join(current_file_directory, "node_modules", "genie-toolkit", "dist", "tool"))
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output and "Server port number at" in output.strip().decode():
                # print(output.strip().decode())
                self.port_number = int(output.strip().decode().split(',')[-1].strip())
                break
        self.url = "http://127.0.0.1:{}/".format(self.port_number)
        
    def query(self, query : str):
        params = {'q': query}
        r = requests.get(url = self.url + "query", params = params)
        res = r.json()
        return res

    def quit(self):
        r = requests.post(url = self.url + "quit")
        return r.json()
    
    def install_genie(self):
        self.logger.info("installing genie-toolkit at {}".format(current_file_directory))
        subprocess.call(["npm", "install", "genie-toolkit"], cwd=current_file_directory)
        
    def download_or_find_model(self, model_name : str, force_update = False):
        if "localhost" in model_name:
            return "http://127.0.0.1:8400"
        
        if "http" in model_name:
            return model_name
        
        if (os.path.exists(model_name)):
            return model_name
        
        # in the future, we will have one model that accomplishes a lot of things
        # so this is only a temporary solution. No need to check for individual models in the future
        if "yelp" in model_name.lower():
            model_dest_dir = os.path.join(current_file_directory, "models", "yelp-tunein")
            if not os.path.exists(model_dest_dir) or force_update:
                Path(model_dest_dir).mkdir(parents=True, exist_ok=True)
                model_dir = snapshot_download(repo_id="stanford-oval/yelp-tunein")
                
                file_names = os.listdir(model_dir)
                for file_name in file_names:
                    shutil.copy(os.path.join(model_dir, file_name), model_dest_dir, follow_symlinks=True)
                    
            return model_dest_dir

        raise ValueError("model name currently not supported: " + model_name)
        
    def download_or_find_manifests(self, manifest_name : str, force_update = False):
        if (os.path.exists(manifest_name)):
            return manifest_name
        
        manifests_dest_dir = os.path.join(current_file_directory, "thingpedia-common-devices", "geniescript")
        if not os.path.exists(manifests_dest_dir):
            subprocess.call(["git clone https://github.com/stanford-oval/thingpedia-common-devices.git"], cwd=current_file_directory, shell=True)
            subprocess.call(["git checkout wip/geniescript"], cwd=os.path.join(current_file_directory, "thingpedia-common-devices"), shell=True)
            subprocess.call(["make geniescript_install_2"], cwd=os.path.join(current_file_directory, "thingpedia-common-devices"), shell=True)
        elif force_update:
            subprocess.call(["git checkout wip/geniescript"], cwd=os.path.join(current_file_directory, "thingpedia-common-devices"), shell=True)
            subprocess.call(["git pull"], cwd=os.path.join(current_file_directory, "thingpedia-common-devices"), shell=True)
            subprocess.call(["make geniescript_install_2"], cwd=os.path.join(current_file_directory, "thingpedia-common-devices"), shell=True)
            
        return manifests_dest_dir
        
    def nlu_server(self, model_dir : str,
                   manifest_dir = "None",
                   force_update_model = False,
                   force_update_manifests = False):
        if "http" in model_dir or "localhost" in model_dir:
            raise ValueError("nlu_server: model must point to an actual file, not a server")
        
        # resolve actual model + manifest directories
        actual_model_dir = self.download_or_find_model(model_dir, force_update = force_update_model)
        if (not actual_model_dir.startswith("file://")):
            actual_model_dir = "file://" + actual_model_dir
        actual_manifest_dir = self.download_or_find_manifests(manifest_dir, force_update=force_update_manifests)
            
        command = ['node', 'genie.js', 'server', '--nlu-model', actual_model_dir, '--thingpedia', actual_manifest_dir]
        self.logger.info(command)
        self.logger.debug("the above command is running in {}".format(os.path.join(current_file_directory, "node_modules", "genie-toolkit", "dist", "tool")))
        process = subprocess.Popen(command, cwd=os.path.join(current_file_directory, "node_modules", "genie-toolkit", "dist", "tool"))
        process.communicate()
            

if __name__ == '__main__':
    # TODO: structure these into useful unit tests
    genie = Genie()
    
    genie.nlu_server('yelp')
    
    genie.initialize("http://127.0.0.1:8400",
                  "/Users/shichengliu/Desktop/Monica_research/thingpedia-common-devices/geniescript",
                  'log.log')
    print(genie.query('find me a restaurant'))
    print(genie.quit())
    