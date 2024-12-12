import pandas as pd

# Define the URL for movie data
myurl = "https://liangfgithub.github.io/MovieData/movies.dat?raw=true"
myurlrating = "https://liangfgithub.github.io/MovieData/ratings.dat?raw=true"

# Read ratings and movies data
ratings = pd.read_csv(myurlrating, sep='::', engine='python',
                    names=['UserID', 'MovieID', 'Rating', 'Timestamp'])

movies = pd.read_csv(myurl, sep='::', engine='python', 
                    names=['MovieID', 'Title', 'Genres'], encoding='ISO-8859-1')

movies['MovieID'] = movies['MovieID'].astype(int)


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
filtered_movies = filtered_movies[['Title', 'ave_ratings', 'ratings_per_movie']].sort_values(
    by=[ 'ratings_per_movie'], ascending=[ False]
)

# Step 6: Display only the top 10 rows
top_10_movies = filtered_movies.head(10)

genres = list(
    sorted(set([genre for genres in movies.Genres.unique() for genre in genres.split("|")]))
)

def get_displayed_movies():
    return movies.head(100)

def get_recommended_movies(new_user_ratings):
    return movies.head(10)

def get_popular_movies(genre: str):
    return top_10_movies