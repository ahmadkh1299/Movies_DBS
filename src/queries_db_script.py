"""
Queries database Script implmentation
"""

import mysql.connector
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # or another backend that works on your system


def query_1(mysql_connection):
    """
    Fetch top genre by year.
    Show table of top genres by year by revenue.
    """
    query = """
    SELECT 
        yearly_revenue.release_year AS 'Year',
        G.name AS 'Top Genre',
        yearly_revenue.max_revenue AS 'Max Revenue'
    FROM
        (
            SELECT 
                M.release_year,
                MGA.genre_id,
                MAX(total_revenue) AS max_revenue
            FROM 
                Movie M
            JOIN MovieMetrics MM ON M.metrics_id = MM.metrics_id
            JOIN MovieGenreAssociation MGA ON M.movie_id = MGA.movie_id
            JOIN (
                SELECT 
                    M2.movie_id,
                    SUM(MM2.revenue) AS total_revenue
                FROM 
                    Movie M2
                JOIN MovieMetrics MM2 ON M2.metrics_id = MM2.metrics_id
                GROUP BY M2.movie_id
            ) AS yearly_totals ON M.movie_id = yearly_totals.movie_id
            GROUP BY M.release_year, MGA.genre_id
        ) AS yearly_revenue
    JOIN Genre G ON yearly_revenue.genre_id = G.genre_id
    WHERE EXISTS (
        SELECT 1
        FROM
            (
                SELECT 
                    M.release_year,
                    MAX(total_revenue) AS max_revenue
                FROM 
                    Movie M
                JOIN MovieMetrics MM ON M.metrics_id = MM.metrics_id
                JOIN MovieGenreAssociation MGA ON M.movie_id = MGA.movie_id
                JOIN (
                    SELECT 
                        M2.movie_id,
                        SUM(MM2.revenue) AS total_revenue
                    FROM 
                        Movie M2
                    JOIN MovieMetrics MM2 ON M2.metrics_id = MM2.metrics_id
                    GROUP BY M2.movie_id
                ) AS yearly_totals ON M.movie_id = yearly_totals.movie_id
                GROUP BY M.release_year
            ) AS max_revenue_per_year
        WHERE
            yearly_revenue.release_year = max_revenue_per_year.release_year AND
            yearly_revenue.max_revenue = max_revenue_per_year.max_revenue
    )
    ORDER BY yearly_revenue.release_year DESC;
    """

    try:
        cursor = mysql_connection.cursor()
        cursor.execute(query)

        # Fetch the results
        rows = cursor.fetchall()

        # Get column names
        columns = [i[0] for i in cursor.description]

        # Create DataFrame from the fetched data
        df = pd.DataFrame(rows, columns=columns)

        # Print the DataFrame
        return df
    except mysql.connector.Error as error:
        print("Error while executing SQL query:", error)


def fetch_genres(mysql_connection):
    """
    Fetch the Genres names
    """
    query = "SELECT name FROM Genre ORDER BY name;"
    try:
        cursor = mysql_connection.cursor()
        cursor.execute(query)
        genres = [item[0] for item in cursor.fetchall()]
        cursor.close()
        return genres
    except mysql.connector.Error as error:
        print("Error fetching genres:", error)
        return []


def query_2(genre, years, mysql_connection):
    """
    Revenue and rating by year according to genre
    """
    cursor = mysql_connection.cursor()
    current_year = 2023
    years = int(years)
    start_year = current_year - years

    query = f"""
    SELECT 
        M.release_year AS 'Year',
        MM.revenue AS 'Revenue',
        MM.rating AS 'Rating'
    FROM
        Movie M
    JOIN MovieMetrics MM ON M.metrics_id = MM.metrics_id
    JOIN MovieGenreAssociation MGA ON M.movie_id = MGA.movie_id
    JOIN Genre G ON MGA.genre_id = G.genre_id
    WHERE 
        G.name = %s AND
        M.release_year >= {start_year}
    ORDER BY 
        M.release_year;
    """

    try:
        cursor.execute(query, (genre,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        if df.empty:
            print(f"No data found for the specified genre in the last {years} years.")
            return

        return df


    except mysql.connector.Error as error:
        print("Error while executing SQL query:", error)
    except Exception as e:
        print("Error while fetching and plotting data:", e)
    finally:
        if cursor is not None:
            cursor.close()


def query_3(mysql_connection):
    """
    Display directors ordered by Average meta score of their movies
    """
    try:
        cursor = mysql_connection.cursor()
        # Increase the maximum length for GROUP_CONCAT to avoid truncation
        cursor.execute("SET SESSION group_concat_max_len = 55000;")  # Adjust based on your needs

        query = """
        SELECT 
            D.full_name AS Director,
            GROUP_CONCAT(A.full_name ORDER BY SubA.AVG_A_Metascore DESC SEPARATOR ', ') AS Actors_List
        FROM
            Worker D
        JOIN MovieWorkerAssociation MWA_Director ON D.worker_id = MWA_Director.worker_id
        JOIN Role RD ON D.role_id = RD.role_id AND RD.name = 'director'
        JOIN Movie M ON MWA_Director.movie_id = M.movie_id
        JOIN MovieMetrics MM ON M.metrics_id = MM.metrics_id
        JOIN MovieWorkerAssociation MWA_Actor ON M.movie_id = MWA_Actor.movie_id
        JOIN Worker A ON MWA_Actor.worker_id = A.worker_id
        JOIN Role RA ON A.role_id = RA.role_id AND RA.name = 'actor'
        JOIN (
            SELECT 
                M2.movie_id,
                MWA_Actor.worker_id,
                AVG(MM.metascore) AS AVG_A_Metascore
            FROM 
                MovieWorkerAssociation MWA_Actor
            JOIN Movie M2 ON MWA_Actor.movie_id = M2.movie_id
            JOIN MovieMetrics MM ON M2.metrics_id = MM.metrics_id
            GROUP BY M2.movie_id, MWA_Actor.worker_id
        ) SubA ON SubA.movie_id = M.movie_id AND SubA.worker_id = A.worker_id
        GROUP BY D.full_name
        ORDER BY AVG(MM.metascore) DESC;
        """
        cursor.execute(query)

        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]  # Extract column headers for the DataFrame
        df = pd.DataFrame(rows, columns=columns)

        return df
    except mysql.connector.Error as e:
        print("Error executing query:", e)
    finally:
        if cursor is not None:
            cursor.close()  # Ensure the cursor is closed after the operation


def query_4(buzzwords, mysql_connection):
    """
    Display the TOP 20 movies containing any of the buzzwords, and their descriptions
    """
    buzzwords_boolean_query = " | ".join(buzzwords)
    query = """
        SELECT Movie.title as title, Movie.description as description, MovieMetrics.metascore as metascore
        FROM Movie, MovieMetrics
        WHERE MATCH(Movie.description) AGAINST ("%s")
            AND Movie.metrics_id = MovieMetrics.metrics_id
            AND MovieMetrics.metascore IS NOT NULL
        ORDER BY MovieMetrics.metascore desc
        LIMIT 20;
    """

    try:
        cursor = mysql_connection.cursor()
        cursor.execute(query, (buzzwords_boolean_query,))

        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]  # Get column headers

        # Create DataFrame from fetched data
        df = pd.DataFrame(rows, columns=columns)
        cursor.close()
        return df
    except mysql.connector.Error as e:
        print("Error executing query:", e)


def query_5(buzzword, mysql_connection):
    """
    Show metrics on movie that contains the buzzword and has more than average revenue, shows the revenue and director.
    """
    query = """
    WITH RelevantMovies AS (
        SELECT movie_id, metrics_id, title
        From Movie
        WHERE MATCH(description) AGAINST (%s)
    ),
    RelevantMoviesWithRevenue AS (
        Select RelevantMovies.movie_id, RelevantMovies.title, MovieMetrics.revenue,
        AVG(MovieMetrics.revenue) OVER () AS average_revenue
        From RelevantMovies, MovieMetrics
        WHERE RelevantMovies.metrics_id = MovieMetrics.metrics_id
        AND MovieMetrics.revenue IS NOT NULL
    ),
    RelevantRevenueMovies AS (
        Select * from RelevantMoviesWithRevenue
        WHERE RelevantMoviesWithRevenue.revenue > RelevantMoviesWithRevenue.average_revenue
    ),
    RelevantMovieDirectors AS (
        SELECT RRM.movie_id, GROUP_CONCAT(Worker.full_name) AS directors
        FROM RelevantRevenueMovies RRM, MovieWorkerAssociation MWA, Worker
        WHERE RRM.movie_id = MWA.movie_id
        AND	MWA.worker_id = Worker.worker_id
        AND Worker.role_id = 2
        GROUP BY RRM.movie_id
    )
    select RRM.title, RMD.directors, RRM.revenue, RRM.average_revenue
        FROM RelevantRevenueMovies RRM, RelevantMovieDirectors RMD
        WHERE RRM.movie_id = RMD.movie_id
    """

    try:
        cursor = mysql_connection.cursor()
        cursor.execute(query, (buzzword,))

        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]  # Get column headers

        # Create DataFrame from fetched data
        df = pd.DataFrame(rows, columns=columns)
        cursor.close()
        return df
    except mysql.connector.Error as e:
        print("Error executing query:", e)
