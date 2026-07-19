import json
import os, shutil, sys

# Made by Qunalpha
version = "1.2"

class jsonFileManagment():
    def __init__(self, path: str, tuple_list: list, indent: int=4):
        """Make sure the (name) parameter is a string with .json as file type\n
        for example - 'file.json'"""

        self.path = path
        self.default = dict(tuple_list)
        self.indent = indent

    def load(self):
        if not os.path.exists(self.path):
                with open(self.path, "w") as file:
                    json.dump(self.default, file, indent=self.indent)
                return self.default
        try:
            with open(self.path, "r") as file:
                return json.load(file)
        except json.decoder.JSONDecodeError as Exception:
            with open(self.path, "w") as file:
                json.dump(self.default, file, indent=self.indent)
            print(Exception)
            return self.default
        
    def save(self, value: dict):
        with open(self.ensure_writable_resource(self.path), "w") as file:
            json.dump(value, file, indent=4)

    def reset(self):
        with open(self.path, "w") as file:
            json.dump(self.default, file, indent=self.indent)

    def ensure_writable_resource(self, filename):
        user_path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(user_path):
            bundled_path = self.resource_path(filename)
            shutil.copyfile(bundled_path, user_path)
        return user_path
    
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)
    
class jsonDatabase():
    def __init__(self, path: str, tuple: str | tuple, indent: int=4):
        """Make sure the (name) parameter is a string with .json as file type\n
        for example - 'file.json'\n
        This class is a database type set i.e. You can Dynamically add Dict to a list and read them.\n
        *Also make sure if you're passing only one tuple as parameter don't forget to add one extra comma like- ("Name",).*"""

        self.path = path
        self.indent = indent
        self.field = tuple
        self.default = []
        self.array = self.load()

    def load(self):
        if not os.path.exists(self.path):
                with open(self.path, "w") as file:
                    json.dump(self.default, file, indent=self.indent)
                return self.default
        try:
            with open(self.path, "r") as file:
                return json.load(file)
        except json.decoder.JSONDecodeError as Exception:
            with open(self.path, "w") as file:
                json.dump(self.default, file, indent=self.indent)
            print(Exception)
            return self.default
        
    def add(self, value: tuple):
        local_list = []
        for i in range(len(self.field)):
            local_list.append((self.field[i], value[i]))
        self.array.append(dict(local_list))
        self.save(self.array)

    def remove(self, index: int):
        self.array.pop(index)
        self.save(self.array)
        
    def save(self, value: dict):
        with open(self.ensure_writable_resource(self.path), "w") as file:
            json.dump(value, file, indent=4)

    def reset(self):
        with open(self.path, "w") as file:
            json.dump(self.default, file, indent=self.indent)
        self.array = []

    def ensure_writable_resource(self, filename):
        user_path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(user_path):
            bundled_path = self.resource_path(filename)
            shutil.copyfile(bundled_path, user_path)
        return user_path
    
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)