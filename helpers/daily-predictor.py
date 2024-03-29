'''
daily-predictor - python module to create daily predictions

- needs to define model number from models/ directory
- create neural network model from saved file
- gets prepared input and makes predictions for incoming matches
- publishes results in blog by entering new post to database

usage: python3 daily-predictor.py -m MODEL_NUMBER

'''

# import warnings filter
import warnings
# ignore all future warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
#simplefilter(action='ignore', category=FutureWarning)
from keras.models import model_from_json
import os
import pickle
import csv
import logging
import argparse
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from prettytable import PrettyTable
from io import StringIO
import sys
sys.path.append(os.path.expanduser('~/nba-dl/blog/'))
from blog import db
from blog.models import Post

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", type=str, required=True, help="model to use")
args = parser.parse_args()

date = datetime.now().strftime('%Y-%m-%d')
daily_dataset_path = os.path.expanduser('~/nba-dl/data/realtime/{}.csv'.format(date))
model_path = os.path.expanduser('~/nba-dl/models/model-{}.json'.format(args.model))
weights_path = os.path.expanduser('~/nba-dl/models/model-{}-weights.h5'.format(args.model))
features_path = os.path.expanduser('~/nba-dl/models/model-{}-features.pickle'.format(args.model))
csv_outfile_path = os.path.expanduser('~/nba-dl/data/daily-predictions/{}-predictions.csv'.format(date))

def setup_model(path):
    logger.info("Getting submitted model...")
    with open(path, 'r') as f:
        model_data = f.read()
    model = model_from_json(model_data)
    return model

def load_weights(model, path):
    logger.info("Loading weights...")
    model.load_weights(path)

def load_features(path):
    with open(path, 'rb') as f:
        features = pickle.load(f)
    return features

def get_raw_dataset():
    logger.info("Getting dataset for {}".format(date))
    dataset = pd.read_csv(daily_dataset_path)
    return dataset

def prepare_input(dataset, features):
    logger.info("Preparing input data...")    
    data = dataset[features]
    scaler = StandardScaler()
    scaled_dataset = scaler.fit_transform(data)
    return scaled_dataset

def predict(model, input_data):
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    results = model.predict_classes(input_data)
    percentage_results = model.predict(input_data)
    return results, percentage_results

def map_result(result):
    # 1 means [0, 1] -> home team win
    if result == 1:
        winner = 'W'
    # 0 means [1, 0] -> away team win
    else:
        winner = 'L'
    return winner

def map_winner(series):
    if series['Home Result'] == 'W':
        winner = series['Home']
        odds = round(series['Home Odds'] * 100, 2)
    else:
        winner = series['Away']
        odds = round(series['Away Odds'] * 100, 2)
    return winner, odds

def generate_csv(results, percentage_results, raw_dataset):
    with open(csv_outfile_path, 'w+') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Home", "Away", "Home Odds", "Away Odds", "Home Result"])
        i=0
        for index, series in raw_dataset.iterrows():
            writer.writerow([series["HOME_TEAM_NAME"], series["AWAY_TEAM_NAME"], percentage_results[i][1], percentage_results[i][0], map_result(results[i])])
            i+=1
    logger.info("Successfully written predictions to csv file!")

def generate_table(results, percentage_results, raw_dataset):
    logger.info("Generating predictions...")
    table = PrettyTable()
    table.field_names = ["Home", "Away", "Home Odds", "Away Odds", "Home Result"]
    i=0
    for index, series in raw_dataset.iterrows():
        table.add_row([series["HOME_TEAM_NAME"], series["AWAY_TEAM_NAME"], percentage_results[i][1], percentage_results[i][0], map_result(results[i])])
        i+=1
    print(table)

def add_post():
    logger.info("Adding new post to blog...")
    output = StringIO()
    df = pd.read_csv(csv_outfile_path)
    for index, series in df.iterrows():
        winner, odds = map_winner(series)
        output.write("{} vs {} -> {} ({}%)\n".format(series['Home'], series['Away'], winner, odds))
    content = output.getvalue()
    post = Post(title='Daily bets - matchup and predicted winner', date_posted=datetime.now(), text=content)
    db.session.add(post)
    db.session.commit()

def main():
    model = setup_model(model_path)
    load_weights(model, weights_path)
    features = load_features(features_path)
    raw_data = get_raw_dataset()
    daily_input_data = prepare_input(raw_data, features)
    results, percentage_results = predict(model, daily_input_data)
    generate_table(results, percentage_results, raw_data)
    generate_csv(results, percentage_results, raw_data)
    add_post()

if __name__ == '__main__':
    main()
