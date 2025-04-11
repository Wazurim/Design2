import json
import os

class JsonHandler:
    """Manage the json file reading and writing
    """
    def __init__(self):
        self.data = {}
    
    def __check_file_exists(self, file_path):
        """Verify if the file exist...

        Args:
            file_path (string): path of the file to check

        Returns:
            bool: Boolean if the file exit
        """
        return os.path.exists(file_path)

    def read_json_file(self, file_path):
        """open and extract data from the specified file (json)

        Args:
            file_path (string): path of the file to read

        Raises:
            FileNotFoundError: Prevent the program from crashing but forcing an error to be caught by parent

        Returns:
            boolean: Boolean if the operation was a success
        """
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
        """Returns the data

        Returns:
            dict: A dictionnary containing the data (python form of a json)
        """
        return self.data
    
    def write_json_file(self, file_path, data):
        """handle the writing of json file

        Args:
            file_path (string): path of the file to write
            data (dict): python dictionnary to write in the json

        Returns:
            _type_: _description_
        """
        try:
            cwd = os.getcwd()
            full_path = os.path.join(cwd, file_path)
            with open(full_path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as e:
            print(f"Erreur lors de l'écriture dans le fichier JSON : {str(e)}")
            return False
