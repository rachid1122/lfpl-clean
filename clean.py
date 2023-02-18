import argparse
import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Clean data in the Louisville Metro KY - Library Collection Inventory
#
# Usage: 
# $ python3 clean.py data/test.csv results/test-clean.csv
#
# where:
#   data/test.csv              = path to the input file
#   results/test-clean.csv     = path to the output file
#
# test input file provided: data/test.csv

def get_file_names() -> tuple:
    """Get the input and output file names from the arguments passed in
    @return a tuple containing (input_file_name, output_file_name)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Name of the original data file.")
    parser.add_argument("output_file", help="Name of the file for cleaned data.")
    args = parser.parse_args()
    return args.input_file, args.output_file


def validate_columns(df: pd.DataFrame) -> None:
    """Validates that the data in the input file has the expected columns. \
    Exits with an error if the expected columns are not present.
    @param df - The DataFrame object with the data from the input file.
    """
    EXPECTED_COLUMNS = ['BibNum', 'Title', 'Author', 'ISBN', 'PublicationYear', 
        'ItemType','ItemCollection', 'ItemLocation', 'ItemPrice', 'ReportDate']
    if not all(item in list(df.columns) for item in EXPECTED_COLUMNS):
       logging.error('Input file does not have the expected columns.')
       exit(1)
    return None


def build_genre_column(df: pd.DataFrame) -> pd.DataFrame:
    """Creates a new column in the DataFrame called Genre that is based on the\
    ItemCollection column.
    @param df - the original DataFrame
    @return a DataFrame with a new column added
    """
    json_path = Path('data/genre.json')
    with open(json_path, 'r') as json_file:
        genre_data = json.load(json_file)
        genre_conditions = [
            (df['ItemCollection'].isin(genre_data['Fiction'])),
            (df['ItemCollection'].isin(genre_data['Non-Fiction'])),
            (df['ItemCollection'].isin(genre_data['Unknown'])),
        ]
        genre_values = ['Fiction', 'Non-Fiction', 'Unknown']
        df['Genre'] = np.select(genre_conditions, genre_values)
        return df


# TODO: define a function to create the audience column here
def build_audience_column(df: pd.DataFrame) -> pd.DataFrame:
    """Creates a new column in the DataFrame called Audience that is based on the\
    ItemCollection column.
    @param df - the original DataFrame
    @return a DataFrame with a new column added
    """
    json_path = Path('data/audience.json')
    with open(json_path, 'r') as json_file:
        audience_data = json.load(json_file)
        audience_conditions = [
            (df['ItemCollection'].isin(audience_data["Adult"])),
            (df['ItemCollection'].isin(audience_data["Teen"])),
            (df['ItemCollection'].isin(audience_data["Children"])),
            (df['ItemCollection'].isin(audience_data["Unknown"])),
        ]
        audience_values = ["Adult", "Teen", "Children", 'Unknown']
        df['Audience'] = np.select(audience_conditions, audience_values)
        return df


def main() -> None:
    """Main cleaning logic
    """
    logging.info('Getting file names from arguments.')
    input_file, output_file = get_file_names()
    logging.info(f'Input file is: {input_file}')
    logging.info(f'Output file is: {output_file}')
 
    logging.info('Loading data from input file.')
    input_path = Path(input_file)
    if not input_path.exists():
        logging.error(f'Input file not found: {input_file}')
        exit(1)
    books_df = pd.read_csv(input_path)

    logging.info('Validating columns in input file.')
    validate_columns(books_df)

    # 1. TODO: Remove unneeded columns (ISBN, ReportDate)
    logging.info('Step 1: Removing unneeded columns.')
    books_df.drop(['ISBN','ReportDate'], axis=1, inplace=True)


    # 2. TODO: Remove records with empty and invalid PuublicationYear or ItemCollection.
    logging.info('Step 2: Removing records with empty and invalid PuublicationYear or ItemCollection.')
    logging.debug(f'before dropping columns {books_df["ItemCollection"]}')
    books_df.dropna(subset=['ItemCollection'], inplace=True)
    logging.debug(f'after dropping columns {books_df["ItemCollection"]}')

    logging.debug(books_df['PublicationYear'] != 0)
    logging.debug(f'before removing0S{books_df["PublicationYear"]}')
    books_df = books_df[books_df['PublicationYear'] != 0]
    books_df = books_df[books_df['PublicationYear'] != 9999]
    logging.debug(f'after removing 0S{books_df["PublicationYear"]}')

    # 3. TODO: Update incorrect values (PublicationYear 2109 -> 2019)
    logging.info('Step 3: Update incorrect values (PublicationYear 2109 -> 2019)')
    books_df.replace(to_replace=2109, value=2019, inplace=True)


    # 4. TODO: Add genre and audience columns
    logging.info('step 4 : Add genre and audience columns')
    books_df = build_genre_column(books_df)
    books_df = build_audience_column(books_df)


    logging.info('Saving output file.')
    output_path = Path(output_file)
    if output_path.suffix == '.csv.gz':
        books_df.to_csv(output_path, index=False, compression="gzip")
    else:
        books_df.to_csv(output_path, index=False)
    
    return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    main()