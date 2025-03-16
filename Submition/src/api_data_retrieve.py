"""
This file handles data insertion.
"""

import ast
import mysql.connector
import pandas as pd
from pathlib import Path
from ast import literal_eval

from utilities import MYSQL_DATABASE_NAME, connect_mysql_server

MOVIES_DATASET_FILENAME = "imdb_movies_dataset_10K.csv"

def _extract_unique_genres(movies_data_frame):
    genres_set = set()
    for genres_list in movies_data_frame['Genre']:
        # Convert the string list into an actual list if it's not already proper format
        if isinstance(genres_list, str):
            genres_list = literal_eval(genres_list)
        # Add each genre to the set, stripping extra whitespace
        genres_set.update(gen.strip() for gen in genres_list)
    return genres_set


def _insert_genres(mysql_connection, mysql_cursor, genres_set):
    mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME};")
    try:
        mysql_cursor.execute("START TRANSACTION;")
        for genre in genres_set:
            # Check if the genre already exists to avoid duplicates
            mysql_cursor.execute("SELECT genre_id FROM Genre WHERE name = %s;", (genre,))
            result = mysql_cursor.fetchone()
            if result is None:
                mysql_cursor.execute(
                    "INSERT INTO Genre (name) VALUES (%s);",
                    (genre,)
                )
        mysql_connection.commit()
    except mysql.connector.Error as error:
        print("Error inserting genres: ", error)
        mysql_connection.rollback()


def _insert_certificates(mysql_connection, mysql_cursor, certificates):
    mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME};")
    try:
        mysql_cursor.execute("START TRANSACTION;")

        for certificate in certificates:
            # Check if the certificate already exists to avoid duplicates
            mysql_cursor.execute("SELECT certificate_id FROM Certificate WHERE certificate = %s;", (certificate,))
            result = mysql_cursor.fetchone()
            if result is None:
                mysql_cursor.execute(
                    "INSERT INTO Certificate (certificate, description) VALUES (%s, %s);",
                    (certificate, "Description placeholder")  # Assuming you need a placeholder for description
                )
        mysql_connection.commit()  # Use the connection object to commit
    except mysql.connector.Error as error:
        print("Error inserting certificates: ", error)
        mysql_connection.rollback()  # Use the connection object to rollback


def _insert_roles(mysql_connection, mysql_cursor):
    # Define a list of roles
    roles = [
        {'role_id': 2, 'name': 'actor'},
        {'role_id': 1, 'name': 'director'}
    ]

    mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME};")
    try:
        mysql_cursor.execute("START TRANSACTION;")

        # Insert each role into the Role table
        for role in roles:
            # Check if the role already exists to avoid duplicates
            mysql_cursor.execute("SELECT role_id FROM Role WHERE name = %s;", (role['name'],))
            result = mysql_cursor.fetchone()
            if result is None:
                mysql_cursor.execute(
                    "INSERT INTO Role (role_id, name) VALUES (%s, %s);",
                    (role['role_id'], role['name'])
                )
        mysql_connection.commit()
    except mysql.connector.Error as error:
        print("Error inserting roles: ", error)
        mysql_connection.rollback()

def _extract_and_insert_workers(mysql_connection, mysql_cursor, movies_data_frame):
    # Define role_ids based on your database setup
    role_ids = {'actor': 2, 'director': 1}

    # Initialize a set to keep track of unique names to avoid duplicates
    workers = set()

    # Process directors
    for directors in movies_data_frame['Director'].dropna():
        # Convert the string list into an actual list if it's a string representation
        directors_list = literal_eval(directors) if isinstance(directors, str) else directors
        for director in directors_list:
            director = director.strip()
            if (director, role_ids['director']) not in workers:
                workers.add((director, role_ids['director']))

    # Process stars
    for stars in movies_data_frame['Stars'].dropna():
        stars_list = literal_eval(stars) if isinstance(stars, str) else stars
        for star in stars_list:
            star = star.strip()
            if (star, role_ids['actor']) not in workers:
                workers.add((star, role_ids['actor']))

    # Insert workers into the database
    mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME};")
    try:
        mysql_cursor.execute("START TRANSACTION;")
        for worker, role_id in workers:
            # Insert worker into Worker table
            mysql_cursor.execute(
                "INSERT INTO Worker (full_name, role_id) VALUES (%s, %s);",
                (worker, role_id)
            )
        mysql_connection.commit()
    except mysql.connector.Error as error:
        print("Error inserting workers: ", error)
        mysql_connection.rollback()

def _insert_movies_tables(mysql_connection, mysql_cursor, movies_data_frame):
    mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME};")
    try:
        mysql_cursor.execute("START TRANSACTION;")

        for index, row in movies_data_frame.iterrows():
            # Fetch the certificate_id based on the certification name in the CSV.
            if pd.notna(row["Certification"]):  # Check if the Certification field is not NaN
                mysql_cursor.execute("SELECT certificate_id FROM Certificate WHERE certificate = %s;", (row["Certification"],))
                result = mysql_cursor.fetchone()
                certificate_id = result[0] if result else None
            else:
                certificate_id = None

            if pd.notna(row["Description"]):
                try:
                    description = " ".join(ast.literal_eval(row["Description"]))
                except Exception:
                    description = None
            else:
                description = None
            # Insert the movie data into the Movie table.
            mysql_cursor.execute(
                "INSERT INTO Movie (movie_id, title, release_year, duration_minutes, description, certificate_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (index + 1, row["Movie Name"], row["Year of Release"], row["Run Time in minutes"], description, certificate_id)
            )

        mysql_connection.commit()
    except mysql.connector.Error as mysql_connection_error:
        print("Error in statement: ", mysql_connection_error)
        mysql_connection.rollback()


def _insert_movie_metrics(mysql_connection, mysql_cursor, movies_data_frame):
    mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME};")
    try:
        mysql_cursor.execute("START TRANSACTION;")

        for index, row in movies_data_frame.iterrows():
            metascore = row["MetaScore"] if not pd.isnull(row["MetaScore"]) else None
            revenue = row["Gross"] if not pd.isnull(row["Gross"]) else None

            # Insert into MovieMetrics table
            movie_id = index + 1
            mysql_cursor.execute(
                "INSERT INTO MovieMetrics (rating, votes, metascore, revenue, movie_id) VALUES (%s, %s, %s, %s, %s);",
                (row["Movie Rating"], row["Votes"], metascore, revenue, movie_id)
            )

            # Update Movie Foriegn Key
            metrics_id = mysql_cursor.lastrowid
            mysql_cursor.execute(
                "UPDATE Movie SET metrics_id = %s WHERE movie_id = %s;",
                (metrics_id, movie_id)
            )

        mysql_connection.commit()
        print("Movie metrics populated successfully.")
    except mysql.connector.Error as error:
        print("Error inserting movie metrics: ", error)
        mysql_connection.rollback()


def _insert_movie_genre_associations(mysql_connection, mysql_cursor, movies_data_frame):
    mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME};")
    try:
        mysql_cursor.execute("START TRANSACTION;")

        for index, row in movies_data_frame.iterrows():
            genres = literal_eval(row["Genre"]) if isinstance(row["Genre"], str) else row["Genre"]
            for genre in genres:
                genre = genre.strip()
                # Get the genre_id from the Genre table
                mysql_cursor.execute("SELECT genre_id FROM Genre WHERE name = %s;", (genre,))
                genre_id = mysql_cursor.fetchone()[0]

                # Insert into MovieGenreAssociation table
                mysql_cursor.execute(
                    "INSERT INTO MovieGenreAssociation (movie_id, genre_id) VALUES (%s, %s);",
                    (index + 1, genre_id)
                )

        mysql_connection.commit()
        print("Movie-genre associations populated successfully.")
    except mysql.connector.Error as error:
        print("Error inserting movie-genre associations: ", error)
        mysql_connection.rollback()


def _insert_movie_worker_associations(mysql_connection, movies_data_frame):
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME};")
    try:
        mysql_cursor.execute("START TRANSACTION;")

        for index, row in movies_data_frame.iterrows():
            movie_id = index + 1

            if index % 1000 == 0:
                print("Iteration: ", index)
                print("Row: ", row)

            # Handle directors
            if 'Director' in row and pd.notna(row['Director']):
                directors = literal_eval(row['Director'])
                for director in directors:
                    director = director.strip()
                    mysql_cursor.execute(
                        "SELECT worker_id FROM Worker WHERE full_name = %s AND role_id = 1;",
                        (director,))
                    result = mysql_cursor.fetchone()
                    if result:
                        director_id = result[0]
                        mysql_cursor.execute(
                            "INSERT INTO MovieWorkerAssociation (movie_id, worker_id) VALUES (%s, %s);",
                            (movie_id, director_id)
                        )

            # Handle actors
            if 'Stars' in row and pd.notna(row['Stars']):
                actors = literal_eval(row['Stars'])
                for actor in actors:
                    actor = actor.strip()
                    mysql_cursor.execute(
                        "SELECT worker_id FROM Worker WHERE full_name = %s AND role_id = 2;",
                        (actor,))
                    actor_id = mysql_cursor.fetchone()
                    if actor_id:
                        mysql_cursor.execute(
                            "INSERT INTO MovieWorkerAssociation (movie_id, worker_id) VALUES (%s, %s);",
                            (movie_id, actor_id[0])
                        )

        mysql_connection.commit()
    except mysql.connector.Error as error:
        print("Error inserting movie-worker associations: ", error)
        mysql_cursor.rollback()
    finally:
        mysql_cursor.close()


def main():
    """
    handles data insertion
    """
    mysql_connection = None
    mysql_cursor = None

    try:
        mysql_connection = connect_mysql_server()
        mysql_cursor = mysql_connection.cursor()

        # Load the CSV
        script_directory = Path(__file__).resolve().parent
        movies_data_frame = pd.read_csv(script_directory / MOVIES_DATASET_FILENAME)

        # Populate certificates
        unique_certificates = movies_data_frame['Certification'].dropna().unique()
        print("Populating Certificates.")
        _insert_certificates(mysql_connection, mysql_cursor, unique_certificates)
        print("Certificates populated successfully.")

        # Populate Roles
        print("Populating Roles.")
        _insert_roles(mysql_connection, mysql_cursor)
        print("Roles populated successfully.")

        # Populate Genres
        unique_genres = _extract_unique_genres(movies_data_frame)
        print("Populating Genres.")
        _insert_genres(mysql_connection, mysql_cursor, unique_genres)
        print("Genres populated successfully.")

        # Populate Movies
        print("Populating Movies.")
        _insert_movies_tables(mysql_connection, mysql_cursor, movies_data_frame)
        print("Movies populated successfully.")

        # Populate MovieMetrics
        print("Populating MovieMetrics.")
        _insert_movie_metrics(mysql_connection, mysql_cursor, movies_data_frame)
        print("MovieMetrics populated successfully.")

        # Populate Workers
        print("Populating Workers.")
        _extract_and_insert_workers(mysql_connection, mysql_cursor, movies_data_frame)
        print("Workers populated successfully.")
        
        # Populate MovieGenresAssociations
        print("Populating MovieGenresAssociations.")
        _insert_movie_genre_associations(mysql_connection, mysql_cursor, movies_data_frame)
        print("MovieGenresAssociations populated successfully.")

        # Populate MovieWorkerAssociations
        print("Populating MovieWorkerAssociations.")
        _insert_movie_worker_associations(mysql_connection, movies_data_frame)
        print("MovieWorkerAssociations populated successfully.")

    except mysql.connector.Error as mysql_connection_error:
        print("MySQL data retrieve error: ", mysql_connection_error)
    except Exception as err:
        print(err)
    finally:
        if mysql_cursor:
            mysql_cursor.close() 
        if mysql_connection:
            mysql_connection.close()

if __name__ == "__main__":
    main()
