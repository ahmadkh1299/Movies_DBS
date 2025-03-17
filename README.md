# 🎬 Movie Database Application

## 📌 Overview

Understanding industry trends, analyzing successful films, and identifying key contributors are crucial aspects of filmmaking. This application provides aspiring filmmakers, researchers, and movie enthusiasts with a powerful tool to explore movie data in a structured and insightful way.

With access to a **movie database** sourced from IMDb, containing **10,000 movies**, users can gain valuable insights into genres, revenue trends, and director collaborations. The system includes advanced queries to help users uncover patterns in movie success, analyze industry dynamics, and make informed creative and business decisions. Whether studying the evolution of film genres, identifying high-performing actors and directors, or analyzing buzzword trends in movie descriptions, this application serves as a valuable resource.

## 🚀 Features

- 📊 **Top Genres Analysis**: Displays the most successful genres by revenue over time.
- 📉 **Revenue & Rating Trends**: Generates graphs showing revenue and IMDb rating trends for a selected genre.
- 🎭 **Director Collaboration Insights**: Lists actors who have worked with a selected director, ranked by the success of their films.
- 🎞 **Buzzword-Based Movie Search**: Retrieves up to 20 movies containing specific buzzwords in their descriptions.
- 💰 **Revenue-Based Analysis**: Identifies movies with above-average revenue that match the user's buzzword search, along with their directors.

## 🛠 Technologies Used

- **Database**: MySQL (optimized with indexing, normalization, and efficient querying).
- **Backend**: Python (using `mysql.connector` for direct MySQL interaction).
- **Frontend**: Command-line interface (with potential future expansion to a web-based UI).
- **Data Source**: IMDb Movie Dataset.

## 📂 Project Structure

```
├── documentation/
│   ├── mysql_and_user_password.txt   # Database credentials.
│   ├── name_and_id.txt               # Stores project owner details.
│   ├── system_docs.pdf               # System architecture and database schema.
│   ├── user_manual.pdf               # User guide and application instructions.
│
├── src/
│   ├── __init__.py                   # Marks the directory as a Python package.
│   ├── api_data_retrieve.py          # Fetches and populates movie data.
│   ├── create_db_script.py           # Creates database schema and indexes.
│   ├── imdb_movies_dataset_10K.csv   # The dataset containing 10,000 movies.
│   ├── queries_db_script.py          # Executes database queries.
│   ├── queries_execution.py          # Runs queries based on user input.
│   ├── utilities.py                  # Utility functions for database operations.
│
├── README.md                         # Project documentation.
├── requirements.txt                   # Python dependencies.
```

## 🔧 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ahmadkh1299/Movies_DBS.git
   cd Movies_DBS
   ```
2. **Set up the database:**
   ```bash
   python src/create_db_script.py
   ```
3. **Populate the database:**
   ```bash
   python src/api_data_retrieve.py
   ```
4. **Run the application:**
   ```bash
   python src/queries_execution.py
   ```

## 🎮 Usage

Upon running `queries_execution.py`, users can interact with a menu-driven interface to execute available queries. The options include:

- `help` - Displays available query options.
- `exit` - Exits the application.
- Query-specific selections (e.g., genre revenue trends, top directors, etc.).

## 🏆 Optimization Strategies

- **Indexing**: Custom indexes (B-Tree, Hash, and Full-Text) to optimize query performance.
- **Normalization**: Efficient table structure using **one-to-many** and **many-to-many** relationships.
- **Query Optimization**: Reduced temporary tables, optimized SELECT statements, and improved JOIN conditions.

## 📖 Additional Documentation

For more details, refer to the **System Documentation** (`documentation/system_docs.pdf`) and **User Manual** (`documentation/user_manual.pdf`).

