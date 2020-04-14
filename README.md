# Description
This script removes all [] parts on subtitles located within .mkv files as well as in the same directory (provided the basename of the .mkv is contained in the .srt file).

# Setup
1. Requirements listed in the requirements.txt file 

2. The script also requires the software MKVToolNix that can be downloaded there: 
https://mkvtoolnix.download/downloads.html

3. Once it is downloaded, you might have to change the 3 following files of the repo:

# Run
Simply run the script with python. 2 flags are available:
--languages: list of languages you want to keep and clean (as ISO 639-1 Format of Language Name, eg. "French")
--folder: folder where the .mkv files are located

Command example:
python clean_subtitles --folder movies_folder --languages English Spanish French
