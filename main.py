import logging
import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime, time
import sqlite3
import atexit

from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackContext, MessageHandler
from datetime import datetime

#logging.basicConfig(
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#    level=logging.INFO
#)
logger = logging.getLogger(__name__)

#Goodreads scraping functions here
def scrape_book_details(book_name, update: Update, context):
    # Define headers to mimic a web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }

    try:
        book_info = {}
        # Construct the search URL for Goodreads based on the book name
        url = f'https://www.goodreads.com/search?q={book_name}'
        
        print('inside function')
        # Send a GET request to fetch the search results page
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'lxml')

        # Find the container that holds the search results
        container = soup.find('div', class_='leftContainer')
        
        if container:
            # Extract the first search result details
            row = container.table.tr
            title = row.find('a', class_='bookTitle').text.strip()
            author = row.find('a', class_='authorName').text.strip()
            book_url = 'https://www.goodreads.com/' + row.find('a', class_='bookTitle')['href']
            rating = row.find('span', class_='minirating').text.strip()

            book_info['Title'] = title
            book_info['Author'] = author
            book_info['Rating'] = rating
            book_info['Link'] = book_url

            return book_info
        else:
            update.message.reply_text("No results found for the given book name.")

    except requests.exceptions.RequestException as e:
        # Handle connection errors or invalid URLs
        update.message.reply_text(f"Error: {e}")

    except Exception as e:
        # Handle other exceptions
        update.message.reply_text(f"An error occurred: {e}")

    return None  # Return None if book details retrieval fails

async def scrape_book_quotes(book_name, bot, chat_id):
    # Define headers to mimic a web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }

    try:
        # Construct the search URL for Goodreads based on the book name
        url = f'https://www.goodreads.com/quotes/search?q={book_name}'
        
        # Send a GET request to fetch the search results page
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'lxml')

        # Find the container that holds the search results
        container = soup.find('div', class_='leftContainer')
        
        if container:
            # Extract all the quotes from the search results
            quotes = container.find_all('div', 'quote mediumText')
            
            # Remove all blank spaces from the quote text and store them in a list
            cleaned_quotes = [' '.join(quote.text.strip().split()[:-3]) for quote in quotes]

            # Randomly select a quote from the top 100 quotes in cleaned_quotes
            if len(cleaned_quotes) > 100:
                top_100_quotes = cleaned_quotes[:100]  # Take the first 100 quotes
                random_quote = random.choice(top_100_quotes)
            else:
                random_quote = random.choice(cleaned_quotes)

            # Send the random quote to the user
            await bot.send_message(chat_id=chat_id, text=random_quote)
 
        else:
            print("No results found for the given book name.")
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")


# Telegram Bot Token (replace 'YOUR_TOKEN' with your actual bot token)
#TOKEN = '7088427087:AAGbXtNdWjdwhbNXxkOzcQMq8gjLzbrRpgw'
TOKEN = '6747878340:AAFp_L5-PNdpnY8Nae5ZcuggqdlpAYi4_7E'

# Initialize SQLite database connection
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS UserBooks
                  (chat_id INTEGER, book_name TEXT)''')
conn.commit()


# Dictionary to store user's read books {chat_id: [books]}
user_books = {}
print('Starting a bot....')
     

# Command handler for /start command
async def start_command(update: Update, context):
    await update.message.reply_text('''Welcome! I'm designed to help you search for books on Goodreads, mark them as read, and receive daily random quotes from their list of read books.

To Search Book - /s book_name
To Mark Book(s) as 'Read' - /m book1, book2
To Remove a book from your list - /unmark book_name
To Get Quotes from Your Reading List - /q
To Start Automatic Quotes - /auto
To Stop Automatic Quotes - /stop
''')


# Message handler for search conversation
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    book_name = ' '.join(context.args)
    #book_name = update.message.text
    book_info = scrape_book_details(book_name, update, context)
    if book_info:
        message_text = (
            f"Title: {book_info['Title']}\n"
            f"Author: {book_info['Author']}\n"
            f"Rating: {book_info['Rating']}\n"
            f"Link: {book_info['Link']}\n"
        )
        await update.message.reply_text(message_text)
    else:
        await update.message.reply_text("No results found for the given book name.")


# Command handler for marking books as read and saving to the database
# Command handler for marking books as read and saving to the database
async def markread_command(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide book names after the /m command.")
        return
    
    # Join the arguments into a single string
    book_names = ' '.join(context.args).strip().lower()
    book_names = [name.strip() for name in book_names.split(",")]

    chat_id = update.message.chat_id
    for book_name in book_names:
        # Check if the book is already marked as read for this chat_id
        cursor.execute("SELECT * FROM UserBooks WHERE chat_id = ? AND book_name = ?", (chat_id, book_name))
        existing_book = cursor.fetchone()
        if existing_book:
            await update.message.reply_text(f"Book '{book_name}' already marked as read.")
        else:
            # Insert the new book into the database for this chat_id
            cursor.execute("INSERT INTO UserBooks (chat_id, book_name) VALUES (?, ?)", (chat_id, book_name))
            conn.commit()
            await update.message.reply_text(f"{book_name} marked as read.")
            #await update.message.reply_text(f"Marked as read.")


    # Send the user their updated list of books from the database
    cursor.execute("SELECT book_name FROM UserBooks WHERE chat_id = ?", (chat_id,))
    user_books = cursor.fetchall()
    updated_books = ', '.join(book[0] for book in user_books)
    await update.message.reply_text(f"Your updated list of books: {updated_books}")

# Command handler for removing a book from the reading list
async def unmark_command(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide the name of the book you want to unmark after the /unmark command.")
        return

    # Join the arguments into a single string
    book_name = ' '.join(context.args).strip().lower()

    chat_id = update.message.chat_id

    # Check if the book is in the user's reading list
    cursor.execute("SELECT * FROM UserBooks WHERE chat_id = ? AND book_name = ?", (chat_id, book_name))
    existing_book = cursor.fetchone()
    if existing_book:
        # Remove the book from the reading list
        cursor.execute("DELETE FROM UserBooks WHERE chat_id = ? AND book_name = ?", (chat_id, book_name))
        conn.commit()
        await update.message.reply_text(f"Book '{book_name}' removed from your reading list.")
    else:
        await update.message.reply_text(f"Book '{book_name}' is not in your reading list.")
    # Send the user their updated list of books from the database
    cursor.execute("SELECT book_name FROM UserBooks WHERE chat_id = ?", (chat_id,))
    user_books = cursor.fetchall()
    updated_books = ', '.join(book[0] for book in user_books)
    await update.message.reply_text(f"Your book list: {updated_books}")


# Command handler for daily random quotes
async def send_random_quotes_command(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    # Retrieve the user's reading list from the database
    cursor.execute('SELECT book_name FROM UserBooks WHERE chat_id = ?', (chat_id,))
    user_books = [row[0] for row in cursor.fetchall()]

    if not user_books:
        await update.message.reply_text("Your reading list is empty. Add some books with (/m book_name) to receive quotes!")
        return

    # Select three random books from the user's read books
    random_books = random.sample(user_books, min(3, len(user_books)))

    # Iterate over each random book to fetch and send quotes
    for book_name in random_books:
        # Fetch quotes for the current book
        await scrape_book_quotes(book_name, context.bot, chat_id)

# Modify send_periodic_quotes to use user_books from the database
async def send_periodic_quotes(context: CallbackContext):
    chat_id = context.job.data.get("chat_id")

    # Retrieve the user's reading list from the database
    cursor.execute('SELECT book_name FROM UserBooks WHERE chat_id = ?', (chat_id,))
    user_books = [row[0] for row in cursor.fetchall()]

    if not user_books:
        await update.message.reply_text("Your reading list is empty. Add some books with (/m book_name) to receive quotes!")
        return
    
    # Select three random books from the user's read books
    random_books = random.sample(user_books, min(3, len(user_books)))

    # Iterate over each random book to fetch and send quotes
    for book_name in random_books:
        # Fetch quotes for the current book
        try:
            await scrape_book_quotes(book_name, context.bot, chat_id=chat_id)
        except Exception as e:
            logger.error(f"Error sending quote for book '{book_name}' to chat ID {chat_id}: {e}")

# Modify start_auto_command to use send_periodic_quotes
async def start_auto_command(update: Update, context: CallbackContext):
    job = context.chat_data.get('quote_job')
    if job:
        await update.message.reply_text('Automatic quotes are already running!')
    else:
        chat_id = update.message.chat_id

        # Retrieve the user's reading list from the database
        cursor.execute('SELECT book_name FROM UserBooks WHERE chat_id = ?', (chat_id,))
        user_books = [row[0] for row in cursor.fetchall()]

        if not user_books:
            await update.message.reply_text("Your reading list is empty. Add some books with (/m book_name) to receive quotes!")
            return

        await update.message.reply_text(f"You will now receive quotes from your booklist every day at this time.")
        await update.message.reply_text("TO STOP - send /stop")
        
        # Schedule the repeating job for sending periodic quotes
        job = context.job_queue.run_repeating(
            send_periodic_quotes, 
            interval=86400,  # 24 hrs
            first=10, 
            data={"chat_id": chat_id}
        )
        context.chat_data['quote_job'] = job

async def stop_quotes(update: Update, context: CallbackContext):
    job = context.chat_data.get('quote_job')
    if job:
        job.schedule_removal()  # remove the repeating job from the job queue
        del context.chat_data['quote_job']  # remove the job from the context
        await update.message.reply_text('Automatic Quotes Stopped.')  # send a message to confirm the polling job has stopped
    else:
        await update.message.reply_text('No automatic quotes were scheduled.')  # send a message indicating that there is no active job

# Add code to close the database connection when the script exits
atexit.register(lambda: (cursor.close(), conn.close()))

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    
    # Commands
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler("s", search_command))
    application.add_handler(CommandHandler("m", markread_command))
    application.add_handler(CommandHandler("unmark", unmark_command))
    application.add_handler(CommandHandler("q", send_random_quotes_command))
    application.add_handler(CommandHandler("auto", start_auto_command))
    application.add_handler(CommandHandler("stop", stop_quotes))


    application.run_polling()