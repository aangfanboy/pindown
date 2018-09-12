import json
import os
import pandas as pd

class infos:
    IMAGE_PATH = 'pins/q/'
    PATH_TO_FOLDER = os.path.join(os.getcwd(), IMAGE_PATH)
    CSV_NAME = f"humans_for_{IMAGE_PATH.replace('/','_').strip('_')}_csv.csv"

def read_json_files(PATH_TO_FOLDER):
    dataframes = []
    for PATH in os.listdir(PATH_TO_FOLDER):
        if PATH.endswith(".json"):
            with open(os.path.join(PATH_TO_FOLDER,PATH),"r") as f:
                data = json.load(f)

            df = json2csv(data)
            dataframes.append(df)

    return dataframes


def json2csv(data):
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']#['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    for i in range(len(data)):
        xml_df = pd.DataFrame(data, columns=column_name)

    try:
        return xml_df
    except:
        xml_df = pd.DataFrame(data, columns=column_name)
        return xml_df



if __name__ == '__main__':
    dataframes = read_json_files(infos.PATH_TO_FOLDER)
    csv_data = pd.concat(dataframes)
    csv_data.to_csv(os.path.join(infos.PATH_TO_FOLDER,infos.CSV_NAME), index=None)
    print(f"Created CSV file for {infos.IMAGE_PATH} to {infos.PATH_TO_FOLDER} as a {infos.CSV_NAME}")