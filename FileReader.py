import csv
import re
import json
import pandas as pd
from api_db_connection import *
from MySQLConnection import MySQLConnection, get_mysql_connection

class Filereader:
    def __init__(self):
        self.status = 0
        self.db = get_mysql_connection()

# Get Data From Local Files for Testing=======================================================================
    def readReviews(self, csvpath: str, encoding='utf-8', skip=1) -> list:
        reviews = []
        with open(csvpath, mode='r', encoding=encoding) as file:
            reader = csv.reader(file)

            for _ in range(skip):
                next(reader)

            for row in reader:
                reviews.append(row)

        return reviews

    def readBooks(self, path: str, encoding='utf-8') -> list:
        books = []
        with open(path, mode='r', encoding=encoding) as file:
            lines = file.readlines()
            for i in range(0, len(lines), 6):
                title = lines[i].strip()
                reviews = [lines[i + j].strip() for j in range(1, 6)]

                for n, review in enumerate(reviews):
                    filtered_review = re.sub(r'^\d+\.\s*', '', review)
                    reviews[n] = filtered_review

                books.append([title, reviews])
        return books

    def readReviewFromCSV(self, csvpath: str, encoding='utf-8'):
        """
        Review for same book will be returned in different row.
        [t1, r1], [t1, r2]
        :param csvpath: Path of csv file
        :param encoding: encoding type of csv file
        :return: List of review keyword in [ [title, keywords], [title, keywords] ]
        """
        reviews_processed = []
        dataframe = pd.read_csv(csvpath, encoding=encoding)

        for _, row in dataframe.iterrows():
            book = row['title']
            keyword_list = [row[f'keyword{i}'] for i in range(1, 6) if pd.notnull(row[f'keyword{i}'])]
            reviews_processed.append([book, keyword_list])

        return reviews_processed

    def readReviewFromJson(self, jsonpath: str, encoding='utf-8') -> list:
        reviews_processed = []
        with open(jsonpath, 'r', encoding=encoding) as file:
            data = json.load(file)
            for book, reviews in data.items():
                #print(f'book = {book} : {reviews}')
                for keywords in reviews:
                    keyword_list = []
                    for keyword_set in keywords:
                        #print(keyword_set)
                        keyword_list.append(keyword_set[0])
                    reviews_processed.append([book, keyword_list])
        return reviews_processed

# Get Data From API ========================================================================================
    def readReviewFromAPI(self):
        rk = get_review_keywords_all(self.db)
        return rk

    def readInfoFromAPI(self):
        bk = get_book_keywords_all(self.db)
        return bk

    def get_group_vocab(self):
        gv = get_group_vocab(self.db)
        return gv

    def get_book_vocab(self):
        bv = get_book_vocab(self.db)
        return bv

    def get_book_search_by_user(self, user_id: str, num: int = 5):
        bl = get_book_search_by_user(self.db, user_id, num=num)
        return bl

    def get_book_id_and_quotation(self, question_id: str, user_id: str):
        bi, qu = get_book_id_and_quotation(self.db, question_id, user_id)
        return bi, qu

    def get_review_by_id(self, review_id: str):
        """
        :param review_id:
        :return: user_id: str, book_id: str, review_string: str
        """
        user_id, book_id, review_string = get_review_by_id(self.db, review_id)
        return user_id, book_id, review_string

    def update_book_review_keywords(self, book_id: str, review_keyword: list[str]):
        result = update_review_keyword_table(self.db, book_id, review_keyword)
        return result

    def update_review_recommend_table(self, review_id, user_id, review_book_id, book_id_list):
        result = update_review_recommend_table(self.db, review_id, user_id, review_book_id, book_id_list)
        return result

    def update_quot_recommend_table(self, question_id, user_id, book_id_list: list[str]):
        result = update_quot_recommend_table(self.db, question_id, user_id, book_id_list)
        return result

# Others =======================================================================================================
    def exit(self):
        self.db.close()

    def add_book_title_csv(self, csv_path = "data/reco_result.csv"):
        processed_data = []
        columns = ['title', 'keyword1', 'keyword2', 'keyword3', 'keyword4', 'keyword5',
                   'book1', 'book2', 'book3', 'book4', 'book5']
        new_columns = ['bt1', 'bt2', 'bt3', 'bt4', 'bt5']

        data = pd.read_csv(csv_path, encoding='utf-8-sig')
        output_file_path = 'results/booktitle.csv'

        book1 = data['book1'].tolist()
        book2 = data['book2'].tolist()
        book3 = data['book3'].tolist()
        book4 = data['book4'].tolist()
        book5 = data['book5'].tolist()

        books = [book1, book2, book3, book4, book5]
        for i, item_list in enumerate(books):
            data[new_columns[i]] = data[f'book{i+1}'].apply(lambda x: get_book_title(self.db, x))


        data.to_csv(output_file_path, encoding='utf-8-sig')



# reader = Filereader()
# reader.add_book_title_csv()



