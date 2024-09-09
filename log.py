import logging

# Configure logging for file
logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
    filename='app.log',  
    filemode='w'  
)

# Create a logger
logger = logging.getLogger(__name__)

# Add a console handler to also print to terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set the level for console output

# Create a formatter for the console handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)


