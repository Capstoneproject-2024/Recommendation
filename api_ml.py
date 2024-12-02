from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
from RequestFormat import *
from Extractor import *
from SimilarityMatcher import *
from api_db_connection import *

# Type "uvicorn [file name]:app --reload" to start server
#   -> ex) "uvicorn api_test:app --reload"


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

"""
router = APIRouter(
    prefix="/sim"
)
"""

extractor = Extractor()
matcher = Matcher()


# Request Body Pydantic Models ======================================================================================

@app.post("/submit")
# For testing
async def submit_message(request: Request):
    sample_str = 'hello'
    print(f"Received message: {sample_str}")  # 콘솔에 메시지 출력
    return {"message": f"Received: {sample_str}"}


@app.post("/match/basic")
async def match_basic(request: MatchBody):
    """
    get title & review
    return matched book list (book)
    :param request:
    :return:
    """
    update_keyword_table = False
    update_review_recommend = True

    # title = request.title
    review_id = request.review_id

    # 추출
    user_id, book_id, review = matcher.reader.get_review_by_id(review_id)
    extracted_keywords = extractor.extract_keyword_string(review, show_similarity=False, pos=True)
    keyword_string = ';'.join(extracted_keywords)

    # Table Update
    if update_keyword_table:
        matcher.reader.update_book_review_keywords(book_id, extracted_keywords)

    # 추천 알고리즘
    book_recommend = matcher.match_both(book_id, extracted_keywords, recommend_number=3)

    # Recommend table update
    if update_review_recommend:
        matcher.reader.update_review_recommend_table(review_id, user_id, book_id, book_recommend)

    return {"result": book_recommend}


@app.post("/match/quotation")
async def match_quotation(request: QuotBody):
    update_quot_recommend = True

    user_id = request.user_id
    question_id = request.question_id
    past_data_num = request.past_data_num

    quot_book_id, quotation = matcher.reader.get_book_id_and_quotation(question_id, user_id)

    # 추출
    quot_keyword = extractor.extract_keyword_string(quotation, show_similarity=False)

    # 추천
    book_recommend = matcher.match_quot(user_id, quot_book_id, quot_keyword, num=past_data_num,
                                        only_quot=False)
    if update_quot_recommend:
        matcher.reader.update_quot_recommend_table(question_id, user_id, book_recommend)

    return {"result": book_recommend}


@app.post("/extract")
async def extract_keyword(request: ExtractBody):
    review = request.review
    keywords = extractor.extract_keyword_string(review, show_similarity=False, pos=True)
    # print(f"Received review: {review}")
    # print(f"Extracted Keywords: {keywords}")

    return {"result": keywords}


@app.get('/extractVocab')
async def extract_vocab(keywords_string: str):
    """
    :param keywords_string: Should be formed 'k1;k2;k3;k4;k5'
    :return: groupVocabulary
    """
    keywords_string = [key.strip() for key in keywords_string.split(';')]
    group_vocab = matcher.match_group_vocab(keywords_string)

    return {"result": group_vocab}

# DB CHECK PART =====================================================================================================
