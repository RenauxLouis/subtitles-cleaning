Setup for MS Windows

# Description
This script removes all brackets areas (e.g. **[scary music]**) on subtitles located within .mkv files as well as in the same directory (provided the basename of the .mkv is contained in the .srt file). It also selects a set of languages to keep and discards the others.</br>
The input is a folder on your computer, and will clean all .mkv in it (and subfolders as well).
# Setup
1. Requirements listed in the requirements.txt file 

2. The script is built upon **MKVToolNix** that can be downloaded there: 
https://mkvtoolnix.download/downloads.html

3. Once it is downloaded, you might have to change the 3 following files of the repo located in the **batch_files** folder:
- mkvextract.bat
- mkvinfo.bat
- mkvmerge.bat<br/>
In each of them, you will find a path to where the MKVToolNix got installed. If it is located in a different place in your computer, change the paths in those files.
# Run
Simply run the script with python.<br/>3 flags are available:<br/>
--videos_dirpath: folder where the .mkv files are located<br/>
--languages: list of languages you want to keep and clean (as [ISO 639-1 Format](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) of Language Name, e.g. "French")
--overwrite_all_files: bool to overwrite all original files instead of deciding individually

# Expected use:
![Image of logs](https://i.ibb.co/HP6rQpx/logs.png)


# Warning:
MKVToolNix does not allow overwriting files, so make sure you have enough space to run the script (~2x the size of your biggest .mkv file).
