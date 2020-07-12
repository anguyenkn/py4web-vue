# Component installer / packager for py4web

Luca de Alfaro, 2020. BSD License.

## Usage:

    ./component_manager.py --help

    usage: component_manager.py [-h] [-z ZIPFILE] [-f] mode component app_folder
    
    positional arguments:
      mode                  install / pack / remove
      component             name of the component in the app
      app_folder            folder of py4web app
    
    optional arguments:
      -h, --help            show this help message and exit
      -z ZIPFILE, --zipfile ZIPFILE
                            zip file for component (otherwise, the component name,
                            with .zip added is used in the current directory).
      -f, --force           Force installation over old version of package
      
## Examples

### Installing a component in an app:

    ./component_manager.py install starrater ~/path/to/py4web/apps/myapp
    
This uses `starrater.zip` in the current directory.  If the zip file is 
elsewhere: 

    ./component_manager.py install starrater -z ~/path/to/starrater.zip ~/path/to/py4web/apps/myapp

If the component already exists: 

    ./component_manager.py install --force starrater ~/path/to/py4web/apps/myapp

### Packing a component from an app:

    ./component_manager.py pack starrater ~/path/to/py4web/apps/myapp
    
To put the zip file elsewhere: 

    /component_manager.py pack starrater -z ~/other/path/to/zipfile.zip ~/path/to/py4web/apps/myapp
    
### Removing a component from an app:

    /component_manager.py remove starrater ~/path/to/py4web/apps/myapp
