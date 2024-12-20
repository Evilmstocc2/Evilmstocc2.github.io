import pandas as pd
import numpy as np
import requests
import tempfile
import os

def myIBCF(w,S, n = 10):      
    # simularity already parsed

    # nan to zero
    S = np.nan_to_num(S, nan=0)
    # where user did not rate
    unrated_indices = np.where(np.isnan(w))[0]
    # where user did rate
    rated_indices = np.where(~np.isnan(w))[0]
    # print(unrated_indices)
    # print(rated_indices)
    recommend = np.zeros_like(w)
    for i in unrated_indices:

        # prediction formula
        num = np.sum(S[i, rated_indices] * w[rated_indices])
        den = np.sum(S[i, rated_indices])

        # no divde by zero please
        if den > 0: recommend[i] = num/den 
        else: recommend[i] = 0
    
    value_recommended = (np.argsort(recommend)[::-1])[:n]   #top n values to recommend movie

    if ~np.isnan(recommend).any():   #return if no nan elements
        return value_recommended
    else: 
        # signaling that something is wrong
        return [-1]

# Define the URL for movie data
myurl = "https://liangfgithub.github.io/MovieData/movies.dat?raw=true"
myurlrating = "https://liangfgithub.github.io/MovieData/ratings.dat?raw=true"
rmaturl = "https://github.com/Evilmstocc2/Evilmstocc2.github.io/raw/refs/heads/main/CS598_PSL_Proj4/single_R_Row.csv?raw=true"


# Read ratings and movies data
ratings = pd.read_csv(myurlrating, sep='::', engine='python',
                    names=['UserID', 'MovieID', 'Rating', 'Timestamp'])

movies = pd.read_csv(myurl, sep='::', engine='python', 
                    names=['MovieID', 'Title', 'Genres'], encoding='ISO-8859-1')

movies["MovieID"] = movies["MovieID"].astype(int)

# because of memory constraints and the fact that I do not want to remake the whole S matrix
# we shall filter here. every. time. because I dont care.
R_onerow = pd.read_csv(rmaturl, index_col=0)
R_col = R_onerow.columns
R_col_num = [eval(i[1:]) for i in R_col]
R_ind = []
for i in range(len(R_col)):
    R_ind.append(np.where(movies['MovieID'] == R_col_num[i])[0][0])
R_sorted_movies = movies.iloc[R_ind].reset_index(drop=True)

# print(R_sorted_movies)

# Step 1: Group by MovieID to calculate average ratings and rating counts
movie_stats = ratings.groupby('MovieID').agg(
    ratings_per_movie=('Rating', 'size'),
    ave_ratings=('Rating', lambda x: round(x.mean(), 3))
).reset_index()

# Step 2: Merge with movies data
movie_stats = movie_stats.merge(movies[['MovieID', 'Title']], on='MovieID')

# Step 3: Filter movies with an average rating over 4 and more than 1300 ratings
filtered_movies = movie_stats[
    (movie_stats['ave_ratings'] > 4) & (movie_stats['ratings_per_movie'] > 1300)
].copy()

# Step 5: Select and arrange columns
filtered_movies = filtered_movies[['Title', 'ave_ratings', 'ratings_per_movie', 'MovieID']].sort_values(
    by=[ 'ratings_per_movie'], ascending=[False]
)

# Step 6: Display only the top 10 rows
top_10_movies = filtered_movies.head(10)

movie_stats = None
filtered_movies = None
ratings = None

genres = list(
    sorted(set([genre for genres in movies.Genres.unique() for genre in genres.split("|")]))
)

# loading parsed S
input_parsed_S_chunks = []

response = None
for i in range(5):
    # forced to use requests and tempfile here
    response = requests.get(f"https://github.com/Evilmstocc2/Evilmstocc2.github.io/raw/refs/heads/main/CS598_PSL_Proj4/S_parsed_chunks/S_{i}.npy")
    if response.status_code == 200:
        temp_file_path = None
        with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as temp_file:
            temp_file.write(response.content) 
            temp_file_path = temp_file.name
        input_parsed_S_chunks.append(np.load(temp_file_path))
        os.remove(temp_file_path)
    else:
        print(f"S_{i} matrix failure")

input_parsed_S = np.vstack(input_parsed_S_chunks)
input_parsed_S = input_parsed_S[:,0:100]
# freeing space in memory just in case
response = None

def get_displayed_movies():
    return R_sorted_movies.head(100)

def get_recommended_movies(new_user_ratings):
    # getting temporary structure.
    wtemp = R_onerow.iloc[0:1].copy()
    wtemp = wtemp.replace(wtemp.values, np.nan)
    for key, value in new_user_ratings.items():
        # print(key, value)
        wtemp.loc["u1", f"m{key}"] = value
    w = wtemp.values[0]
    # print(w)
    # print(len(w))
    results = myIBCF(w,input_parsed_S, n = 10)

    if len(results) > 0 and results[0] == -1:
        return top_10_movies
    
    return R_sorted_movies.iloc[results]

def get_popular_movies(genre: str):
    return top_10_movies