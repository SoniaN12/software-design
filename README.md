# CLEANY
<img width="923" height="497" alt="Screen Shot 2025-09-20 at 1 54 45 PM" src="https://github.com/user-attachments/assets/70f4194f-53fe-4f5f-a428-2147b9ae441f" />


A tool to manage, clean, and optimize your file storage.

#Requirement 
python  + 3.8.0 (install a version 3.8 or higher)
install Pillow >8.0.0 (library for compression)
Go to terminal(macos/linux) / command line(windows)
 pip install .   #( to be able to install a copy of my library to your computer and will make storage manager command available in your terminal )

 To use the features run commands:
 1. python3 client.py path/to/directory/folder --clean-old  #to remove old files according to a configurable number of days
 2. python3 client.py path/to/directory/folder --remove-duplicates # to remove duplicates
 3. python3 client.py path/to/directory/folder --compress  #to compress image
 4. python3 client.py path/to/directory/folder  --history #to check edit history of files
 5. python3 client.py path/to/directory/folder  --stats   # to check storage  statistics
 6. python3 client.py path/to/directory/folder  --all  # to run all features at same time
 
 
