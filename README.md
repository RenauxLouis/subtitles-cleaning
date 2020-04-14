# Description
This script removes all [] parts on subtitles located within .mkv files as well as in the same directory (provided the basename of the .mkv is contained in the .srt file).

# Setup
1. Requirements listed in the requirements.txt file 

2. The script also requires the software MKVToolNix that can be downloaded there: 
https://mkvtoolnix.download/downloads.html

3. Once it is downloaded, you might have to change the 3 following files of the repo:
- mkvextract.bat
- mkvinfo.bat
- mkvmerge.bat
In each of them, you will find a path to where the MKVToolNix got installed. If it is located in a different place in you computer, change the paths in those files.
# Run
Simply run the script with python. 2 flags are available:
--languages: list of languages you want to keep and clean (as ISO 639-1 Format of Language Name, eg. "French")
--folder: folder where the .mkv files are located

Command example:
python clean_subtitles --folder movies_folder --languages English Spanish French

Expected logs:
![Image of logs](https://ibb.co/vzCNPZ7)
