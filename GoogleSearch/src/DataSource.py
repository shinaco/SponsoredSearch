import sqlite3
import os
import pandas as pd
import xlsxwriter

class SearchDB:
    def __init__(self, tablename):
        self.conn = sqlite3.connect("../data/googlesearch.db")
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
        self.tablename = tablename

    def __del__(self):
        self.conn.close()

    def create_table(self):
        if self.tablename == "searchresults":
            self.conn.execute('''CREATE TABLE {0}  (
                                    City text,
                                    State text,
                                    Datetime text,
                                    SearchTerm text,
                                    GoogleURL text,
                                    AdURLWebsite text,
                                    WebsiteName text,
                                    Vendor text,
                                    PositionNum text,
                                    Position text,
                                    ResultConsistent text,
                                    PageNumber text,
                                    TypeofResult text,
                                    Comments text,
                                    AdValue text,
                                    StaticFilePath text)'''.format(self.tablename))
        elif self.tablename == "products":
            self.conn.execute('''CREATE TABLE {0} (
                                  ProductID integer,
                                  ProductName text)'''.format(self.tablename))
        self.conn.commit()

    def purge_table(self):
        ''''
        DROP TABLE
        '''
        self.conn.execute('''DROP TABLE IF EXISTS {}'''.format(self.tablename))
        self.conn.commit()

    def add_row(self, row):
        '''
        Add a new row to table
        :param row: a list of formatted row values.
        :return: None
        '''
        if self.tablename == "searchresults":
            self.conn.execute('''INSERT INTO searchresults VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                                                  (row[0],
                                                                   row[1],
                                                                   row[2],
                                                                   row[3],
                                                                   row[4],
                                                                   row[5],
                                                                   row[6],
                                                                   row[7],
                                                                   row[8],
                                                                   row[9],
                                                                   row[10],
                                                                   row[11],
                                                                   row[12],
                                                                   row[13],
                                                                   row[14],
                                                                   row[15]
                                                               ))
        elif self.tablename == "products":
            self.conn.execute('''INSERT INTO products VALUES (?,?)''', (row[0], row[1]))
        self.conn.commit()

    def get_all(self):
        '''
        Return a pandas dataframe of the stored data.
        :return:
        '''
        df = pd.read_sql("SELECT * FROM {}".format(self.tablename), con=self.conn)
        return df

    def save_to_spreadsheet(self):
        df = self.get_all()
        # writer = pd.ExcelWriter("../data/SearchResults.xlsx")
        # df['StaticFilePath'] = df['StaticFilePath'].apply(lambda link :'=HYPERLINK("{0}"; "ScreenShot File")'.format(link))
        # df.to_excel(writer, sheet_name="Result", index=False)
        # writer.save()
        # writer.close()

        row = 0
        col = 0
        datadir = os.path.dirname(os.path.realpath(__file__)) + "/../data/"
        #logger.info("Writing Excelfile to : %s" , datadir)
        workbook = xlsxwriter.Workbook(datadir + "SearchResult.xlsx")
        worksheet = workbook.add_worksheet("ProductDetails")
        for j, t in enumerate(df.columns):
          worksheet.write(row, col + j, t)
        for idx, val in df.iterrows():
          row = row + 1
          row_elements = val
          for i in range(len(row_elements)):
            if (df.columns[i] == "StaticFilePath" or df.columns[i] == "GoogleURL" or df.columns[i] == "AdURLWebsite"):
              worksheet.write_url(row, i, row_elements[i])
            else:
              worksheet.write(row, i, row_elements[i])
        workbook.close()

def setupDB():
    prodDB = SearchDB("products")
    prodDB.purge_table()
    prodDB.create_table()

    searchDB = SearchDB("searchresults")
    searchDB.purge_table()
    searchDB.create_table()

if __name__ == "__main__":
    mydb = SearchDB("searchresults")
    # mydb.purge_table()
    # mydb.create_table()
    # mydb.add_row([1, 'Marmot Tungsten 4P Tent - 4 Person, 3 Season'])
    #mydb.add_row(['Pittsburgh', 'PA', datetime.datetime(2018, 3, 11, 1, 1, 34, 667852), 'Marmot+Tungsten+4P+Tent+-+4+Person%2C+3+Season', 'http://www.google.com/search?q=Marmot+Tungsten+4P+Tent+-+4+Person%2C+3+Season&num=10&hl=en&start=10', 'http://www.outsideoutfitters.com/p-44945-marmot-tungsten-4p-tent.aspx?variantID=183063', 'Outside Outfitters', 'NA', 'NA', 'RHS', 'NA', 1, 'SponsoredAd', 'NA', '$273.93', 'file:///Users/rohansingh/Programming/ResearchProject/GoogleSearch/data/SponsoredAdMarmot_TungstenOutside_Outfitters15556.png'])
    # print(mydb.get_all())
    #mydb.save_to_spreadsheet()
    setupDB()

