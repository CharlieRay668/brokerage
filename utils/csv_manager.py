import pandas as pd

class CSVHandler():

    def __init__(self, database_location, indexer_col):
        self.database = database_location
        self.indexer_col = indexer_col
        self.columns = pd.read_csv(self.database, index_col=0).columns

    def exists(self, index):
        df = self.get_db()
        row = df[df[self.indexer_col] == index]
        return len(row) > 0

    def get_db(self):
        return pd.read_csv(self.database, index_col = 0)

    def get_value(self, index, col):
        df = self.get_db()
        row = df[df[self.indexer_col] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            return_value = df.loc[true_index, col]
            return 200, return_value
        except KeyError:
            return 403, 'Unable to find specified column'
        return 500, 'Something went wrong'
    
    def get_rows(self, index):
        df = self.get_db()
        rows = df[df[self.indexer_col] == index]
        return rows

    def edit_value(self, index, col, value):
        df = self.get_db()
        row = df[df[self.indexer_col] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            df.loc[true_index, col] = value
            df.to_csv(self.database)
            return 200, 'Success'
        except KeyError:
            return 403, 'Unable to find specified column'
        return 500, 'Something went wrong'

    def edit_row(self, index, new_row, expected_len=None):
        if expected_len == None:
            expected_len = self.columns
        if len(new_row) < expected_len:
            return 400, 'Not enough values provided'
        while expected_len < self.columns:
            new_row.append(None)
            expected_len += 1
        df = self.get_db()
        row = df[df[self.indexer_col] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            df.loc[true_index] = new_row
            df.to_csv(self.database)
            return 200, 'Success'
        except KeyError:
            return 403, 'Unable to find specified column'
        return 500, 'Something went wrong'

    def add_row(self, row):
        df = self.get_db()
        new_df = pd.DataFrame([row], columns = df.columns)
        df = df.append(new_df, ignore_index = True)
        df.to_csv(self.database)
        return 200, 'Success'
    
    def add_rows(self, new_df):
        df = self.get_db()
        df = df.append(new_df, ignore_index = True)
        df.to_csv(self.database)
        return 200, 'Success'
        
    def remove_row(self, index):
        df = self.get_db()
        row = df[df[self.indexer_col] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            df.drop([true_index], inplace=True)
            df.to_csv(self.database)
            return 200, 'Success'
        except:
            return 500, 'Something went wrong'
        return 500, 'Something went wrong'
