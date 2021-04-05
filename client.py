import webbrowser
import sys

try:
    ip = sys.argv[1]  # ip of the server
    port = sys.argv[2]  # port where the server wil respond
    file_name= sys.argv[3]  # name of the desired file
    webbrowser.open_new_tab(f"http://{ip}/{file_name}")
except IndexError:
    print("Error: Arguments given are not valid")

"""print("Note: file extension is not required when entering the file's name\n")
print("Welcome")

while True:
    file_name = input('Enter the html file name here: ')
    if file_name.lower() == "exit":
        print("See you next time! Bye!")
        break"""

