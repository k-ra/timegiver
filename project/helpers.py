from flask import redirect, render_template, request, session

# packages for TF-IDF
import nltk
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def keyword():
    # https://www.geeksforgeeks.org/tf-idf-for-bigrams-trigrams/

    # extract description from database
    txt1 = []
    # txt1 = db.execute("SELECT * FROM dataset name WHERE time <= ?", time)

    # Preprocessing
    def remove_string_special_characters(s):
        # removes special characters with ' '
        stripped = re.sub('[^a-zA-z\s]', '', s)
        stripped = re.sub('_', '', stripped)

        # Change any white space to one space
        stripped = re.sub('\s+', ' ', stripped)

        # Remove start and end white spaces
        stripped = stripped.strip()
        if stripped != '':
            return stripped.lower()

    # Stopword removal
    stop_words = set(stopwords.words('english'))
    your_list = ['skills', 'ability', 'job', 'description']
    for i, line in enumerate(txt1):
        txt1[i] = ' '.join([x for
                            x in nltk.word_tokenize(line) if
                            (x not in stop_words) and (x not in your_list)])
    # Getting trigrams
    vectorizer = CountVectorizer(ngram_range=(3, 3))
    X1 = vectorizer.fit_transform(txt1)
    features = (vectorizer.get_feature_names())
    # print("\n\nFeatures : \n", features)

    # Applying TFIDF
    vectorizer = TfidfVectorizer(ngram_range=(3, 3))
    X2 = vectorizer.fit_transform(txt1)

    # Getting top ranking features
    sums = X2.sum(axis=0)
    data1 = []
    for col, term in enumerate(features):
        data1.append((term, sums[0, col]))
    ranking = pd.DataFrame(data1, columns=['term', 'rank'])
    words = (ranking.sort_values('rank', ascending=False))
    print("\n\nWords head : \n", words.head(7))