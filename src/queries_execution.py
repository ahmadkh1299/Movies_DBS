"""
This file includes the main function and provides user friendly usage of the custom queries in queries_db_script.py
"""

import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd

from queries_db_script import (
    fetch_genres,
    query_1,
    query_2,
    query_3,
    query_4,
    query_5
)
from utilities import connect_mysql_server


def _top_genres_the_last(mysql_connection, years):
    df = query_1(mysql_connection)
    try:
        years = int(years)
        start_year = 2022 - years + 1

        # Filter the DataFrame for the last specified number of years
        df_filtered = df[(df['Year'] >= start_year) & (df['Year'] <= 2022)]

        # Ensure DataFrame is sorted by Year in descending order
        df_filtered = df_filtered.sort_values(by='Year', ascending=False)

        print(df_filtered)
    except ValueError:
        print("Invalid input for years. Please enter a valid number.")


def _plot_by_genre(genre, mysql_connection,years):
    df = query_2(genre, years, mysql_connection)
    # Process the data for plotting
    df['Revenue'] = pd.to_numeric(df['Revenue'])
    df['Rating'] = pd.to_numeric(df['Rating'])

    # Group by year to summarize revenue and rating
    revenue_by_year = df.groupby('Year')['Revenue'].mean()
    rating_by_year = df.groupby('Year')['Rating'].mean()

    # Plotting revenue by year
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    revenue_by_year.plot(kind='bar', color='skyblue')
    plt.title(f'Average Revenue by Year for {genre} (Last {years} Years)')
    plt.xlabel('Year')
    plt.ylabel('Average Revenue')
    plt.grid(True)

    # Plotting average rating by year
    plt.subplot(1, 2, 2)
    rating_by_year.plot(kind='bar', color='lightgreen')
    plt.title(f'Average Rating by Year for {genre} (Last {years} Years)')
    plt.xlabel('Year')
    plt.ylabel('Average Rating')
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def _directors_by_metascore(mysql_connection):
    df = query_3(mysql_connection)
    print(df.iloc[:, 0])
    _director_actor_suitability(df)


def _director_actor_suitability(df):
    director = input("\nPlease enter a director's name: ").strip()  # Trim whitespace for better matching
    if director in df['Director'].values:
        suitable_actors = df.loc[df['Director'] == director, 'Actors_List'].values[0]
        print(f"Director {director} is suitable to work with these actors in this order:\n (according to Average meta score of the movies they worked together on)")
        print(suitable_actors)
    else:
        print(f"No data found for the director named {director}. Please check the spelling or try another name.")


def _readable_print_query4_results(df):
    print("____________________________________________\n")
    for index, row in df.iterrows():
        print(f"TOP {index+1} best-match by metascore")
        print("Movie Title:", row["title"])
        print("Description:", row["description"])
        print("Metascore:", row["metascore"])
        print()


def _readable_print_query5_results(df):
    print("____________________________________________\n")
    for index, row in df.iterrows():
        print(f"TOP {index+1} best-match by metascore")
        print("title:", row["title"])
        print("directors:", row["directors"])
        print("revenue:", row["revenue"])
        print("average_revenue:", row["average_revenue"])
        print()


def _print_menu_options():
    """
    Display menu options to the user
    """
    print("\n-----------------------------------------------")
    print("Select an option:")
    print("1 - Show table of top genres by year by revenue")
    print("2 - Graph revenue and rating by year according to genre")
    print("3 - Display directors ordered by Average meta score of their movies ")
    print("4 - Display the TOP 20 movies containing one of the buzzwords, and their descriptions")
    print("5 - Show metrics on movie that contains the buzzword and has more than average revenue, shows the revenue and director")
    print("exit - exits from the program")
    print("help - shows the options menu")
    print("-----------------------------------------------\n")


def main():
    """
    Usage the Database Queries
    """
    try:
        mysql_connection = connect_mysql_server()
        if mysql_connection.is_connected():
            print("MySQL connection is successful")
            _print_menu_options()
            while True:
                # Get user input
                choice = input("Enter your choice (1, 2, 3, 4, 5, exit, help): ")

                # Handle user's choice
                if choice == '1':
                    years = input("Please enter how many years of data you want to see : ")
                    _top_genres_the_last(mysql_connection, years)
                elif choice == '2':
                    genres = fetch_genres(mysql_connection)
                    if not genres:
                        print("No genres available. Please check your database.")
                        return

                    print("Available Genres:")
                    for genre in genres:
                        print(genre)

                    genre = input("Please enter a genre from the list above: ")
                    while genre not in genres:
                        print("Invalid genre. Please enter a valid genre from the list above.")
                        genre = input("Please enter a genre from the list above: ")
                    years = input("Please enter how many years of data you want to see : ")
                    _plot_by_genre(genre, mysql_connection, years)
                elif choice == '3':
                    _directors_by_metascore(mysql_connection)
                elif choice == '4':
                    buzzwords = []
                    while True:
                        buzzword = input("Please enter a buzzword. Type 'N' to stop: ")
                        if buzzword == "N":
                            break
                        else:
                            buzzwords.append(buzzword)
                    df = query_4(buzzwords, mysql_connection)
                    _readable_print_query4_results(df)

                elif choice == "5":
                    buzzword = input("Please enter the buzzword: ")
                    df = query_5(buzzword, mysql_connection)
                    _readable_print_query5_results(df)
                elif choice == 'exit':
                    break
                elif choice == 'help':
                    _print_menu_options()
                else:
                    print("Invalid choice.")

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)
    finally:
        if mysql_connection.is_connected():
            mysql_connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    main()
