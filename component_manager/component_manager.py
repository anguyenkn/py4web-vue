#!/usr/bin/env python

# Luca de Alfaro, 2020
# BSD License.

import argparse
import pathlib
import zipfile


def add_to_zip(args, zipf, filename):
    zipf.write(filename, arcname=filename.relative_to(args.apps_dir))

def remove_component(args):
    if args.python_file.exists():
        args.python_file.unlink()
    if args.static_dir.is_file():
        args.static_dir.unlink()
    elif args.static_dir.exists():
        for f in args.static_dir.iterdir():
            f.unlink()
        args.static_dir.rmdir()

def pack_component(args):
    assert args.python_file.is_file(), str(args.python_file) + " does not exist"
    assert args.static_dir.is_dir(), str(args.static_dir) + " does not exist"
    assert (not args.component_zip.exists()) or args.force, "The destination .zip file already exists"
    # Creates the zipfile.
    with zipfile.ZipFile(args.component_zip, 'w') as zipf:
        # Writes the Python file to it.
        add_to_zip(args, zipf, args.python_file)
        # Writes the static files to it.
        for static_file in args.static_dir.iterdir():
            add_to_zip(args, zipf, static_file)

def install_component(args):
    assert (not args.python_file.exists()) or args.force, str(args.python_file) + " exists"
    assert (not args.static_dir.exists()) or args.force, str(args.static_dir) + " exists"
    # Cleans up old files if we are asked.
    if args.force:
        remove_component(args)
    with zipfile.ZipFile(args.component_zip, 'r') as zipf:
        for f in zipf.namelist():
            zipf.extract(f, path=str(args.apps_dir))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-z', '--zipfile', type=str,
                        help='zip file for component '
                        '(otherwise, the component name, with .zip added '
                        'is used in the current directory).', )
    parser.add_argument('-f', '--force', action='store_true', default=False,
                        help='Force installation over old version of package')
    parser.add_argument("mode", help="install / pack / remove")
    parser.add_argument("component", help="name of the component in the app")
    parser.add_argument("app_folder", help="folder of py4web app")
    args = parser.parse_args()
    assert args.mode in ['install', 'pack', 'remove'], 'Invalid mode'
    assert args.zipfile is None or args.zipfile.endswith('.zip'), 'zipfile must end with .zip'
    # Builds useful paths
    args.apps_dir = pathlib.Path(args.app_folder)
    # Python file.
    args.python_path = pathlib.Path("components") / (args.component + ".py")
    args.python_file = args.apps_dir / args.python_path
    # Static dir.
    args.static_path = pathlib.Path("static") / "components" / args.component
    args.static_dir = args.apps_dir / args.static_path
    if args.zipfile is None:
        args.component_zip = pathlib.Path('.') / (args.component + ".zip")
    else:
        args.component_zip = pathlib.Path('.') / args.zipfile
    # Dispatcher.
    if args.mode == 'pack':
        pack_component(args)
    elif args.mode == 'install':
        install_component(args)
    elif args.mode == 'remove':
        remove_component(args)

main()
