from idlelib.query import Query
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException,Depends,status
import requests
from MySQLConnection import MySQLConnection, get_mysql_connection

delimiter = ';'

"""
router = APIRouter(
    prefix= "/simtest"
)
"""

# ================================= actual connection to DB ======================================
def get_review_keywords_all(db: MySQLConnection):
    """
    input: [ [book_id, "key1;key2;key3;key4;key5" ]
    output: [ [book_id, [k1, k2, ... ] ]
    :return:
    """
    db.start_transaction()
    try:
        db.execute(f"SELECT * "
                   f"FROM bookReviewKeywordTable")
        response = db.fetchall()
        db.commit()

        review_keyword_list = []

        for title, keyword_string in response:
            key = [item.strip() for item in keyword_string.split(';')]
            review_keyword = [title, key]
            review_keyword_list.append(review_keyword)

        return review_keyword_list

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_review_keywords_all 오류 발생."
        )


def get_book_keywords_all(db: MySQLConnection):
    db.start_transaction()

    try:
        db.execute(f"SELECT * "
                   f"FROM bookKeywordTable")
        response = db.fetchall()
        db.commit()

        book_keywords_list = []

        for title, keyword_string in response:
            key = [item.strip() for item in keyword_string.split(delimiter)]
            book_keyword = [title, key]
            book_keywords_list.append(book_keyword)

        return book_keywords_list

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_book_keywords_all 오류 발생."
        )


def get_group_vocab(db: MySQLConnection, show_id = False):
    db.start_transaction()
    try:
        db.execute(f"SELECT * "
                   f"FROM groupVocabularyTable")
        response = db.fetchall()
        db.commit()

        vocab_list = []

        for id, vocab in response:
            vocab_list.append(vocab)

        #print(f"get_gv complete {vocab_list}")
        return vocab_list

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_review_keywords_all 오류 발생."
        )


def get_book_vocab(db: MySQLConnection):
    db.start_transaction()
    try:
        db.execute(f"SELECT * "
                   f"FROM bookVocabularyTable")
        response = db.fetchall()
        db.commit()
        return response

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_book_vocab 오류 발생."
        )


def get_book_title(db: MySQLConnection, id: str):
    db.start_transaction()
    try:
        db.execute(f"SELECT name "
                   f"FROM bookTable "
                   f"WHERE ID={id}")
        response = db.fetchall()
        db.commit()
        return response[0][0]

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_book_title 오류 발생."
        )


def get_book_search_by_user(db: MySQLConnection, user_id: str, num: int = 5):
    """
    인풋 유저 ID의 상위 num 개의 읽은 책 ID를 리스트 꼴로 반환
    """
    db.start_transaction()
    try:
        db.execute(f"SELECT bookID "
                   f"FROM reviewTable "
                   f"WHERE userID = {user_id} "
                   f"ORDER BY reviewDate DESC "
                   f"LIMIT {num}")
        response = db.fetchall()
        db.commit()

        read_book_list = []
        for item in response:
            read_book_list.append(str(item[0]))

        return read_book_list

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_book_search_by_user 오류 발생."
        )


def get_book_id_and_quotation(db: MySQLConnection, question_id: str, user_id: str):
    db.start_transaction()
    try:
        db.execute(f"SELECT bookID, quotation "
                   f"FROM groupQuestionQuotationTable "
                   f"WHERE userID = {user_id} and questionID = {question_id}")

        response = db.fetchall()
        db.commit()

        data = response[0]
        book_id = str(data[0])
        quotation = data[1]

        return book_id, quotation

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_book_search_by_user 오류 발생."
        )

#================================== Testing API ======================================
# db = get_mysql_connection()
