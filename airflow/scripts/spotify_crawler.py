import kaggle

path = "./data"

data = kaggle.api.dataset_download_files(dataset="maharshipandya/-spotify-tracks-dataset",path=path,unzip=True)