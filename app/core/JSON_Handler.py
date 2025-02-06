import json
import os

class JsonHandler:
    def __init__(self):
        self.data = {}
    
    def __check_file_exists(self, file_path):
        return os.path.exists(file_path)

    def read_json_file(self, file_path):
        self.data ={}
        try:
            if self.__check_file_exists(file_path):
                with open(file_path, 'r') as file:
                    self.data = json.load(file)
                return True
            else:
                raise FileNotFoundError(f"Le fichier JSON {file_path} n'existe pas.")
        except FileNotFoundError:
            print(f"Le fichier JSON {file_path} n'existe pas.")
            return False
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier JSON : {str(e)}")
            return False
    
    def get_data(self):
        return self.data
    
    def write_json_file(self, file_path, data):
        try:
            cwd = os.getcwd()
            full_path = os.path.join(cwd, file_path)
            with open(full_path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as e:
            print(f"Erreur lors de l'écriture dans le fichier JSON : {str(e)}")
            return False
