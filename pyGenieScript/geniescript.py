# Copyright 2023 The Board of Trustees of the Leland Stanford Junior University
#
# Author: Shicheng Liu <shicheng@cs.stanford.edu>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import subprocess
import requests
import os
from huggingface_hub import snapshot_download
from pathlib import Path
import shutil
from glob import glob
import time
import logging
import json

current_file_directory = os.path.dirname(os.path.abspath(__file__))

class Genie:
    """A Genie instance."""
    def __init__(self, check_genie_version = True):
        """
        Install `genie-toolkit` and prepare it for initialization.
        
        Automatically check if specified `genie-toolkit` version has been installed,
        if not, install the specified version (which can be found in `pyGenieScript/package.json`).
        
        Unless `check_genie_version` is False, always check if installed version matches with specified version
        
        ### Args:
        
        `check_genie_version` (bool, optional): where to check currently installed genie version and re-install if necessary. Default to True.
        """
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.genie_dir = os.path.exists(os.path.join(current_file_directory, "node_modules", "genie-toolkit", "dist"))
        
        # install genie:
        if (not self.genie_dir):
            self.__install_genie()
            
        # check version, if necessary, and re-install
        if (check_genie_version and self.__if_outdated_genie()):
            self.__install_genie()
            
        self.num_results = 1
        self.neglect_filters = []
        self.neglect_projections = []
        self.use_direct_sentence_state = False

        
    def initialize(self,
                    nlu_server_address : str,
                    thingpedia_dir : str = 'None',
                    log_file_name : str = 'log.log',
                    force_update_model = False,
                    force_update_manifest = False) -> None:
        """
        ### Description:
        
        Instantiate and initialize a Genie instance.
        
        This will also establish a back-end server connection with the Genie instance.

        ### Args:
        
        `nlu_server_address` (str): path to nlu files or online models. Use "localhost" if server is initialized by `Genie().nlu_server()`.
            
        `thingpedia_dir` (str, optional): path to thingpedia directory. Defaults to 'None', which will use the latest `wip/geniescript` branch of `thingpedia-common-devices`.
                                            
        `log_file_name` (str, optional): log of genie under `~/.cache/genie-toolkit/`. Defaults to 'log.log'.
            
        `force_update_model` (bool, optional): force to update the model (if download from huggingface). Defaults to False.
            
        `force_update_manifest` (bool, optional): force to update the manifest (if downloaded from git). Defaults to False.
        """
        
        actual_server = self.download_or_find_model(nlu_server_address, force_update=force_update_model)
        if (not actual_server.startswith('http:')):
            actual_server = "file://" + actual_server
        
        actual_manifest = self.download_or_find_manifests(thingpedia_dir, force_update=force_update_manifest)
        
        # initialize genie server and retrieve the randomly assigned port number
        command = ['node', 'genie.js', 'contextual-genie',  '--nlu-server', actual_server, '--thingpedia-dir', actual_manifest,  '--log-file-name', log_file_name]
        self.logger.info(command)
        process = subprocess.Popen(
            command,
            cwd=os.path.join(current_file_directory, "node_modules", "genie-toolkit", "dist", "tool"),
            stdout=subprocess.PIPE)
        port_number = self.__retrieve_port_number(process)
        self.url = "http://127.0.0.1:{}/".format(port_number)
      
        
    def nlu_server(self, model_dir : str,
                   manifest_dir = "None",
                   force_update_model = False,
                   force_update_manifests = False):
        """
        ### Description:
        
        Instatitate a nlu server running on the backend.
        
        Initializing a nlu server typically takes ~5-10 seconds. Thus, it is recommended to keep the nlu
        server running in the back and ask a Genie instance to interacts with it.
        
        This method will initialize such server and register its port number for other Genie instances to use.
        For other Genie instances to use this server, pass "localhost" as `nlu_server_address`

        ### Args:
        
        `model_dir` (str): path to nlu files or online models.
        
        `manifest_dir` (str, optional): path to thingpedia directory. Defaults to 'None', which will use the latest `wip/geniescript` branch of `thingpedia-common-devices`.
        
        `force_update_model` (bool, optional): force to update the model (if download from huggingface). Defaults to False.
        
        `force_update_manifests` (bool, optional): force to update the manifest (if downloaded from git). Defaults to False.

        ### Raises:
        
        `ValueError`: in case if model is not a valid model path nor a valid online model name.
        """
        if "http" in model_dir or "localhost" in model_dir:
            raise ValueError("nlu_server: model must point to an actual file, not a server")
        
        # resolve actual model + manifest directories
        actual_model_dir = self.download_or_find_model(model_dir, force_update = force_update_model)
        if (not actual_model_dir.startswith("file://")):
            actual_model_dir = "file://" + actual_model_dir
        actual_manifest_dir = self.download_or_find_manifests(manifest_dir, force_update=force_update_manifests)
            
        command = ['node', 'genie.js', 'server', '--nlu-model', actual_model_dir, '--thingpedia', actual_manifest_dir, '--random-port']
        self.logger.info(command)
        self.logger.debug("the above command is running in {}".format(os.path.join(current_file_directory, "node_modules", "genie-toolkit", "dist", "tool")))
        process = subprocess.Popen(
            command,
            cwd=os.path.join(current_file_directory, "node_modules", "genie-toolkit", "dist", "tool"),
            stdout=subprocess.PIPE)
        
        # retrieve random port returned by genie server
        port_number = self.__retrieve_port_number(process)
        with open(os.path.join(current_file_directory, '_local_post_binding.txt'), 'w') as fd:
            fd.write(str(port_number))
        
        # prints the rest of the stdout after port has been retrieved
        self.__print_process(process)
        
        process.communicate()
   
    
    def query(
        self,
        query : str,
        num_results = 1,
        neglect_filters = [],
        neglect_projections = [],
        dialog_state = None,
        use_existing_ds = False,
        aux = [],
        use_direct_sentence_state = False
    ):
        """
        ### Description:
        
        Query Genie for response for an optional number of responses.
        
        Return a JSON object.
        
        `response` stores the agent respose, and `results` stores any results as a list.
        
        Note, it is possible for `results` to be an empty list, in case if there is no new result, e.g.,
        during slot-filling or when there is an error.
        
        *Applies to v0.0.0b3*: there is a TBD bug in the first invocation of `query` with `dialog_state`.
        To bypass this bug for now, call `query` without `dialog_state` first before calling it with `dialog_state`.

        ### Args:
        
        `query` (str): query in natural language.
        
        `num_results` (int, optional): number of results Genie should return. In practice, choose between 1, 2, 3, or 10. Defaults to 1.
        
        `dialog_state` (str, optional): dialog state to be put to Genie as context. Defaults to None (use current dialog state in context).

        ### Returns:
        
        ```
        {
            'response': agent response from Genie ([str]),
            'results': results from Genie, if any ([JSON]),
            'user_target': ThingTalk for `query` determined by semantic parser, empty string if error (str),
            'ds': dialog state (in ThingTalk) after executing `user_target` (str),
            'aux': auxciliary info for `ds` (str),
            'delta_verbal': verbalization of sentence state, empty list if error ([str]),
            'full_verbal': verbalization of full state, empty list if error ([str]).
        }
        ```
        """
        
        # only need to POST num_results to Genie if it differs from current one
        if (num_results != self.num_results):
            self.num_results = num_results
            r = requests.post(url = self.url + "setNumResults", json = {
                "numResults": "{}".format(num_results)
            })
            res = r.json()
            if "response" not in res or res["response"] != 200:
                msg = "Setting numResults = {} failed".format(num_results)
                self.logger.warning(msg)
        
        if (neglect_filters != self.neglect_filters):
            self.neglect_filters = neglect_filters
            for i in neglect_filters:
                r = requests.post(url = self.url + "neglectFilters", json= {
                    "name": i
                })
                res = r.json()
                if "response" not in res or res["response"] != 200:
                    msg = "Setting neglectFilters = {} failed".format(neglect_filters)
                    self.logger.warning(msg)
        
        if (neglect_projections != self.neglect_projections):
            self.neglect_projections = neglect_projections
            for i in neglect_projections:
                r = requests.post(url = self.url + "neglectProjections", json= {
                    "name": i
                })
                res = r.json()
                if "response" not in res or res["response"] != 200:
                    msg = "Setting neglectProjections = {} failed".format(neglect_projections)
                    self.logger.warning(msg)
        
        if (use_direct_sentence_state != self.use_direct_sentence_state):
            self.use_direct_sentence_state = use_direct_sentence_state
            r = requests.post(url = self.url + "toggleDirectSentenceState", json= {
                    "directSentenceState": use_direct_sentence_state
            })
            res = r.json()
            if "response" not in res or res["response"] != 200:
                msg = "Setting use_direct_sentence_state = {} failed".format(use_direct_sentence_state)
                self.logger.warning(msg)
        
        if (use_existing_ds):
            params = {'q': query}
            r = requests.get(url = self.url + "query", params = params)
            res = r.json()
        else:
            if dialog_state is None:
                params = {'q': query, "aux": aux}
            else:
                params = {'q': query, 'ds': dialog_state, "aux": aux}
            
            r = requests.post(url = self.url + "queryContext", json = params)
            res = r.json()
            
        return res


    def quit(self):
        """
        ### Description:
        
        Shut down this Genie engine.

        ### Returns:
        
        JSON:
        ```
        {
            'response': 200 for success and 404 for failure
        }
        ```
        """
        r = requests.post(url = self.url + "quit")
        return r.json()


    def clean(self):
        """
        ### Description:
        
        Erase and flush the current contextual state of Genie.
        Genie keeps an internal formal conversational state. This method erases conversation history stored by Genie.

        ### Returns:
        
        JSON:
        ```
        {
            'response': 200 for success and 404 for failure
        }
        ```
        """
        r = requests.post(url = self.url + "clean")
        return r.json()

        
    def download_or_find_model(self, model_name : str, force_update = False) -> str:
        """
        ### Description:
        
        Given a model_name, do:
        
        (1) if model_name is a valid nlu directory, return it directly
        
        (2) if model_name corresponds to available models (e.g. yelp), download/find it
        
        (3) raise error otherwise

        ### Args:
        
        `model_name` (str): path to nlu model or model name.
        `force_update` (bool, optional): force to update the model (if download from huggingface). Defaults to False.

        ### Raises:
            
        `ValueError`: in case model name is neither a valid path nor an available model

        ### Returns:
        
        (str): path to model
        """
        if "localhost" in model_name:
            return self.__retrieve_localhost()
        
        if "http" in model_name:
            return model_name
        
        if (os.path.exists(os.path.join(model_name, 'config.json'))):
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
        """
        ### Description:
        
        Given a manifest name, do:
        
        (1) if manifest_name is a valid directory, return it directly
        
        (2) otherwise, downlaod the latest `wip/geniescript` branch of `thingpedia-common-devices`

        ### Args:
        
        `manifest_name` (str): path to thingpedia directory.
            
        `force_update` (bool, optional): force to update the manifest (if downloaded from git). Defaults to False.

        ### Returns:
        
        (str): path to manifest
        """
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
    
    
    def __retrieve_localhost(self):
        try:
            with open(os.path.join(current_file_directory, '_local_post_binding.txt'), "r") as fd:
                port_number = fd.read().strip()
            return "http://127.0.0.1:{}".format(port_number)
        except Exception:
            return "http://127.0.0.1:8400"
            
        
    def __install_genie(self):
        self.logger.info("installing genie-toolkit at {}".format(current_file_directory))
        subprocess.call(["npm", "install", "genie-toolkit"], cwd=current_file_directory)
    
    # whether the installed version of genie is outdated
    def __if_outdated_genie(self):
        if (not self.genie_dir):
            return False
        
        # get desired genie version associated with this version of pyGenieScript
        with open(os.path.join(current_file_directory, "package.json"), 'r') as fd:
            genie_desired_ver : str = json.loads(fd.read())['dependencies']['genie-toolkit']
        genie_desired_ver_hash = genie_desired_ver.split("#")[-1]
        
        try:
            res = subprocess.check_output(['npm', 'ls', '--json'], cwd=current_file_directory)
            genie_installed_ver : str = json.loads(res)['dependencies']['genie-toolkit']['resolved']
            genie_installed_ver_hash = genie_installed_ver.split("#")[-1]
            
            if genie_desired_ver_hash == genie_installed_ver_hash:
                return False
        except Exception as e:
            self.logger.debug("__if_outdated_genie produced error {}".format(e))
        
        if 'genie_installed_ver_hash' in locals():
            print("Installed genie-toolkit version: {}".format(genie_installed_ver_hash))
        else:
            print("Installed genie-toolkit version: N/A")
        
        print("Specified genie-toolkit version: {}\nwill reinstall genie-toolkit".format(genie_desired_ver_hash))
        print("You can disregard any npm errors above as long as the new installation is successful")
        return True
    
    def __retrieve_port_number(self, process):
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output and "Server port number at" in output.strip().decode():
                port_number = int(output.strip().decode().split(',')[-1].strip())
                break
            
        return port_number
    
    def __print_process(self, process):
        def subprocess_yield(process):            
            for stdout_line in iter(process.stdout.readline, ""):
                yield stdout_line 
        
        for msg in subprocess_yield(process):
            print(msg)