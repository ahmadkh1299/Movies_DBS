# 🎬 Movie Database Application

## 📌 Overview

Understanding industry trends, analyzing successful films, and identifying key contributors are critical aspects of filmmaking. This application is designed to provide aspiring filmmakers, researchers, and movie enthusiasts with a powerful tool to explore movie data in an insightful and meaningful way.

With access to a **movie database** sourced from IMDb, containing **10,000 movies**, users can retrieve structured insights into genres, revenue trends, and director collaborations. The system includes advanced queries to help users uncover patterns in movie success, explore industry dynamics, and make informed creative and business decisions. Whether you are looking to study the evolution of film genres, identify high-performing actors and directors, or analyze buzzword trends in movie descriptions, this application serves as a valuable resource.

## 🚀 Features

- 📊 **Top Genres Analysis**: Displays the most successful genres by revenue over time.
- 📉 **Revenue & Rating Trends**: Graphs showing the revenue and IMDb rating over time for a selected genre.
- 🎭 **Director Collaboration Insights**: Lists actors who have worked with a selected director, ranked by the success of their films.
- 🎞 **Buzzword-Based Movie Search**: Retrieves up to 20 movies containing specific buzzwords in their descriptions.
- 💰 **Revenue-Based Analysis**: Identifies movies that have above-average revenue and match the user's buzzword search, along with their directors.

## 🛠 Technologies Used

- **Database**: MySQL / PostgreSQL (Optimized with indexing, normalization, and efficient querying)
- **Backend**: Python (with SQLAlchemy for database interaction)
- **Frontend**: Command-line interface (future expansion to web-based UI planned)
- **Data Source**: IMDb Movie Dataset

## 📂 Project Structure

```
├── src/
│   ├── create_db_script.py      # Creates database schema and indexes
│   ├── api_data_retrieve.py     # Fetches and populates movie data
│   ├── queries_execution.py     # Runs queries based on user input
│   ├── requirements.txt         # Dependencies for the project
│   ├── config.py                # Configuration settings
│
├── docs/
│   ├── system_docs.docx         # System architecture and database schema
│   ├── user_manual.docx         # User guide and application instructions
│
├── README.md                    # Project documentation
├── LICENSE                       # License information
```

## 🔧 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/movie-database-app.git
   cd movie-database-app
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Setup the database:**
   ```bash
   python src/create_db_script.py
   ```
4. **Populate the database:**
   ```bash
   python src/api_data_retrieve.py
   ```
5. **Run the application:**
   ```bash
   python src/queries_execution.py
   ```

## 🎮 Usage

Upon running `queries_execution.py`, the user can interact with a menu-driven interface to execute the available queries. The options include:

- `help` - Displays query options
- `exit` - Exits the application
- Query-specific selections (e.g., genre revenue trends, top directors, etc.)

## 🏆 Optimization Strategies

- **Indexing**: Custom indexes (B-Tree, Hash, and Full-Text) to optimize query performance
- **Normalization**: Efficient table structure using **one-to-many** and **many-to-many** relationships
- **Query Optimization**: Reduced temporary tables, optimized SELECT statements, and improved JOIN conditions

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request to improve the application.

---

🔍 For more details, refer to the **System Documentation** (`docs/system_docs.docx`) and **User Manual** (`docs/user_manual.docx`).

