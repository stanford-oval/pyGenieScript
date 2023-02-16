import shutil
import subprocess
import os
import sys
# old_syspath = sys.path
# current_file_directory = os.path.dirname(os.path.abspath(__file__))
# sys.path = [path for path in sys.path if current_file_directory not in path]
import pyGenieScript.geniescript

def test_genienlp():
    if "installgenienlp" in os.environ:
        subprocess.check_call([sys.executable, "-m", "pip", "install", 'genienlp==0.7.0a4'])
    
    if (not shutil.which('genienlp')):
        # genienlp is not succesfully installed
        raise ValueError("genienlp is not correctly installed")
    assert(True)

def test_setup():
    genie = pyGenieScript.geniescript.Genie()
    genie.initialize('yelp', 'yelp')
    response = genie.query("show me a chinese restaurant")
    assert(len(response['results']) >= 1)
    genie.quit()

def test_server():
    import threading
    
    def instantiate_server():
        import pyGenieScript.geniescript
        genie = pyGenieScript.geniescript.Genie()
        genie.nlu_server('yelp')
    
    server_thread = threading.Thread(target=instantiate_server, name="localhost")
    server_thread.start()
    genie = pyGenieScript.geniescript.Genie()
    genie.initialize('yelp', 'yelp')
    response = genie.query("show me a chinese restaurant")
    assert(len(response['results']) >= 1)
    genie.quit()