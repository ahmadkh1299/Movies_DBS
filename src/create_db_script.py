"""
This file contains code responsible for creating the database
"""

import mysql.connector

from utilities import MYSQL_DATABASE_NAME, connect_mysql_server


def _create_database(mysql_cursor) -> None:
    try:
        mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE_NAME}")
    except mysql.connector.Error as mysql_connection_error:
        print(f"Error while creating database: {MYSQL_DATABASE_NAME}")
        raise Exception(str(mysql_connection_error))


def _get_tables() -> dict[str,str]:
    tables = {}

    tables["Certificate"] = """
    CREATE TABLE IF NOT EXISTS Certificate(
        certificate_id INT NOT NULL AUTO_INCREMENT,
        certificate VARCHAR(255) NOT NULL,
        description VARCHAR(255) NOT NULL,
        PRIMARY KEY(certificate_id)
    );
    """

    tables["Genre"] = """
    CREATE TABLE IF NOT EXISTS Genre(
        genre_id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        PRIMARY KEY(genre_id)
    );
    """

    tables["Movie"] = """
    CREATE TABLE IF NOT EXISTS Movie(
        movie_id INT NOT NULL,
        title VARCHAR(255) NOT NULL,
        release_year SMALLINT UNSIGNED NOT NULL,
        duration_minutes SMALLINT UNSIGNED NOT NULL,
        description TEXT,
        certificate_id INT,
        PRIMARY KEY(movie_id),
        FOREIGN KEY(certificate_id) REFERENCES Certificate(certificate_id)
    );
    """

    tables["MovieMetrics"] = """
    CREATE TABLE IF NOT EXISTS MovieMetrics(
        metrics_id INT NOT NULL AUTO_INCREMENT,
        rating FLOAT CHECK (rating BETWEEN 0 AND 10),
        votes INT UNSIGNED,
        metascore TINYINT UNSIGNED NULL CHECK (metascore BETWEEN 0 AND 100),
        revenue BIGINT UNSIGNED NULL,
        movie_id INT,
        PRIMARY KEY(metrics_id),
        FOREIGN KEY(movie_id) REFERENCES Movie(movie_id)
    );
    """

    tables["Role"] = """
    CREATE TABLE IF NOT EXISTS Role(
        role_id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        PRIMARY KEY(role_id)
    );
    """

    tables["Worker"] = """
    CREATE TABLE IF NOT EXISTS Worker(
        worker_id INT NOT NULL AUTO_INCREMENT,
        full_name VARCHAR(255) NOT NULL,
        role_id INT NOT NULL,
        PRIMARY KEY(worker_id),
        FOREIGN KEY(role_id) REFERENCES Role(role_id)
    );
    """


    tables["MovieWorkerAssociation"] = """
    CREATE TABLE IF NOT EXISTS MovieWorkerAssociation(
        movie_id INT NOT NULL,
        worker_id INT NOT NULL,
        PRIMARY KEY(movie_id, worker_id),
        FOREIGN KEY(movie_id) REFERENCES Movie(movie_id),
        FOREIGN KEY(worker_id) REFERENCES Worker(worker_id)
    );
    """

    tables["MovieGenreAssociation"] = """
    CREATE TABLE IF NOT EXISTS MovieGenreAssociation(
        movie_id INT NOT NULL,
        genre_id INT NOT NULL,
        PRIMARY KEY(movie_id, genre_id),
        FOREIGN KEY(movie_id) REFERENCES Movie(movie_id),
        FOREIGN KEY(genre_id) REFERENCES Genre(genre_id)
    );
    """

    return tables


def _create_tables(mysql_cursor) -> None:
    tables = _get_tables()
    for table_name, table_creation_statement in tables.items():
        try:
            print(f"Creating table: {table_name}")
            mysql_cursor.execute(table_creation_statement)
        except mysql.connector.Error as mysql_connection_error:
            print(f"Error while creating table: {table_name}")
            raise Exception(str(mysql_connection_error))


def _create_indexes(mysql_cursor) -> None:
    add_full_text_index = """
    ALTER TABLE Movie
    ADD FULLTEXT(description)
    """
    add_forgien_key_metrics = """
    ALTER TABLE Movie ADD COLUMN metrics_id INT;
    ALTER TABLE Movie ADD FOREIGN KEY(metrics_id) REFERENCES MovieMetrics(metrics_id)
    """
    indexes_queries = [
        "CREATE INDEX idx_movie_release_year ON Movie(release_year)",
        "CREATE INDEX idx_metascore ON MovieMetrics(metascore)",
        "CREATE INDEX idx_genre_name ON Genre(name) USING HASH",
        "CREATE INDEX idx_role_name ON Role(name) USING HASH",
    ]
    indexes_queries.append(add_full_text_index)
    indexes_queries.append(add_forgien_key_metrics)

    for index_query in indexes_queries:
        try:
            print("Creating index: ", index_query)
            mysql_cursor.execute(index_query)
        except mysql.connector.Error as mysql_connection_error:
            print(f"Error while creating index: {index_query}. {mysql_connection_error}")


def main():
    """
    Create Database Script
    """
    mysql_connection = None
    mysql_cursor = None

    try:
        mysql_connection = connect_mysql_server()
        mysql_cursor = mysql_connection.cursor()
    
        print("Creating Databse")
        _create_database(mysql_cursor)

        mysql_cursor.execute(f"USE {MYSQL_DATABASE_NAME}")

        print("Creating tables")
        _create_tables(mysql_cursor)

        print("Creating database indexes")
        _create_indexes(mysql_cursor)

    except mysql.connector.Error as mysql_connection_error:
        print("MySQL create db error: ", mysql_connection_error)
    except Exception as err:
        print(err)
    finally:
        if mysql_cursor:
            mysql_cursor.close()
        if mysql_connection:
            mysql_connection.close()

if __name__ == "__main__":
    main()
