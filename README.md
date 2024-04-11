# Book Assistant Telegram Bot

The Book Assistant Telegram Bot, accessible via `@bookish_thief_bot` on Telegram, is designed to help users search for books on Goodreads, mark them as read, and receive daily random quotes from their list of read books.

## Table of Contents
- [Project Background](#project-background)
- [Thought Process](#thought-process)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Web Scraping Logic](#web-scraping-logic)
- [Automatic Quotes and Job Queue](#automatic-quotes-and-job-queue)
- [Dependencies](#dependencies)
- [Additional Information](#additional-information)
- [Hosting on PythonAnywhere](#hosting-on-pythonanywhere)

## Project Background

The idea for this project originated from the aspiration to develop a tool akin to Readwise, a service that delivers weekly highlights' quotes linked to Kindle and dispatches them via Gmail. Goodreads was selected as the primary data source for book information retrieval due to its vast database and reputation for providing accurate book details. Notably, Readwise is a paid service. Hence, this bot was developed as a free alternative, tailored to personal requirements.

## Thought Process

1. **Conceptualization**:
   - The initial concept was to create a bot that would fetch book details and quotes, similar to Readwise's functionality, but tailored for Telegram users.

2. **Platform Selection**:
   - Goodreads was selected as the platform for book information retrieval due to its popularity and comprehensive database.

3. **Feature Planning**:
   - The features were planned step by step, starting with a search function to fetch book details, followed by a mark as read function to create a reading list, and then integrating quote scraping and Telegram bot functionalities.

## Project Structure

- **main.py**: Contains the main code for the Telegram bot, including command handlers and message handlers.
- **user_data.db**: SQLite database file for storing user data such as the reading list.
- **requirements.txt**: Contains the required Python packages for running the bot (`python-telegram-bot` and `requests`).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/BookAssistantBot.git
   cd BookAssistantBot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update the `TOKEN` variable in `main.py` with your actual Telegram bot token.

4. Run the bot:
   ```bash
   python main.py
   ```

## Usage

Once the bot is running, users can interact with it using the following commands:

- `/start`: Start the bot and get a welcome message with instructions.
- `/s book_name`: Search for a book on Goodreads.
- `/m book1, book2`: Mark one or more books as 'Read'.
- `/unmark book_name`: Remove a book from the reading list.
- `/q`: Get random quotes from your reading list.
- `/auto`: Start receiving automatic daily quotes from your reading list.
- `/stop`: Stop receiving automatic daily quotes.

## Web Scraping Logic

The web scraping logic in the bot includes functions to search for book details and retrieve random quotes from Goodreads.

### Searching Book Details
- The `scrape_book_details` function takes a book name as input and scrapes Goodreads for details such as title, author, rating, and link.
- It mimics a web browser by setting headers in the HTTP request.
- The function returns the book details or notifies the user if no results are found.

### Retrieving Random Quotes
- The `scrape_book_quotes` function fetches random quotes from Goodreads based on a book name.
- It sends the quotes to the user's Telegram chat using the bot.

## Automatic Quotes and Job Queue

The bot provides a feature to receive daily random quotes from the user's reading list automatically. This is achieved using the Telegram job queue.

- The `/auto` command starts the automatic quotes feature by scheduling a job to send quotes daily.
- The `start_auto_command` function schedules a repeating job that calls `send_periodic_quotes` every 24 hours.
- The job queue ensures that quotes are sent automatically at the specified interval.
- The `/stop` command stops the automatic quotes feature by removing the scheduled job from the job queue.

## Dependencies

Ensure you have Python installed on your system. Install the required dependencies using the following command:

```bash
pip install python-telegram-bot python-telegram-bot[job-queue] requests
```
## Hosting on PythonAnywhere

The bot can be hosted on PythonAnywhere for easy deployment and accessibility. Follow these steps to host the bot:

1. Sign up for a PythonAnywhere account.
2. Upload your bot files to your PythonAnywhere account.
3. Set up a virtual environment and install the required dependencies (`python-telegram-bot`, `requests`, etc.).
4. Configure the Telegram bot token and other settings.
5. Start the bot on PythonAnywhere.

## Additional Information

- The bot uses an SQLite database (`user_data.db`) to store user data, including the reading list.
- It provides a convenient way for users to manage their reading lists and receive inspirational quotes daily.
- Customize the bot's behavior or add more features as needed for your project.



