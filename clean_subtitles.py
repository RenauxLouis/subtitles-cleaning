import sys
import argparse
import os
import re
import subprocess
from subliminal import save_subtitles, scan_video, region, download_best_subtitles
from babelfish import Language
from langdetect import detect
import codecs


MAP_LANGUAGES = {
    "en": "english",
    "es": "spanish",
    "fr": "french"
}


def remove_mkv_subs(full_fname, full_fname_no_sub):
    print("Removing subtitles from original .mkv file")
    subprocess.check_output([".\mkvmerge.bat", "-o", full_fname_no_sub, "--no-subtitles", full_fname], stderr=subprocess.STDOUT)
    print("Subtitles removed")

def extract_mkv_subs(str_file):
    subprocess.check_output([".\mkvextract.bat", "tracks", str_file["mkv_full_path"],
                    str_file["srt_track_id"] + ":" + str_file["srt_full_path"]],
                                        stderr=subprocess.STDOUT)


def add_subs(full_fname_no_sub, full_fname_with_sub, str_to_add):
    print("Adding subtitles")
    print(full_fname_with_sub)
    print(full_fname_no_sub)
    print(str_to_add[0])
    subprocess.check_output([".\mkvmerge.bat", "-o", full_fname_with_sub,
                            full_fname_no_sub, str_to_add[0]],
                                        stderr=subprocess.STDOUT)
    print("Subtitles added")
    sys.exit()


def extract_subs(str_files):
    print("*****************************")
    print("Directory: {d}".format(d=str_files[0]["root_folder"]))
    print("File: {f}".format(f=str_files[0]["mkv_fname"]))
    for str_file in str_files:
        print(str_file["srt_full_path"])
        if str_file["srt_exists"]:
            print("    Subtitles ready. Nothing to do.")
            continue
        elif not str_file["srt_track_id"]:
            print("    No embedded subtitles found.")
        else:
            print("    Embedded subtitles found.")
            extract_mkv_subs(str_file)


def get_mkv_track_id(file_path):
    """ Returns the track ID of the SRT subtitles track"""
    try:
        raw_info = subprocess.check_output([".\mkvmerge.bat", "-i", file_path],
                                            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as ex:
        print(ex)
        sys.exit(1)
    pattern = re.compile(".* (\d+): subtitles \(SubRip/SRT\).*", re.DOTALL)
    m = pattern.match(str(raw_info))
    if m:
        return raw_info, m.group(1)
    else:
        return raw_info, None


def clean_and_rename_subs(str_file_list, languages):
    print("Opening SRT files to select the languages")
    str_to_add = []
    for str_file in str_file_list:
        str_fpath = str_file["srt_full_path"]
        try:
            with open(str_fpath, "r", encoding="utf-8") as fi:
                lines = fi.read().splitlines()
                random_lines = lines[len(lines)//2:len(lines)//2+40]
                random_lines_alpha = [line for line in random_lines if not any(map(str.isdigit, line))]
                random_lines_alpha_no_empty = [line for line in random_lines_alpha if line]
                join_text = " ".join(random_lines_alpha_no_empty)
                join_text = join_text.replace("</i>", "").replace("<i>", "")
                print(join_text)
                language_detected = detect(join_text)
                print(language_detected)
                if language_detected in MAP_LANGUAGES:
                    cleaned_lines = clean_sub(lines)
                    new_name = str_fpath.replace(os.path.basename(str_fpath), MAP_LANGUAGES[language_detected] + ".srt")
                    with codecs.open(new_name, "w", "utf-8") as fo:
                        for line in cleaned_lines:
                            fo.write(line + "\n")

                    str_to_add.append(new_name)
        except UnicodeDecodeError:
            print("Can't open {} because of UnicodeDecodeError".format(str_fpath))
            continue
    return str_to_add


def clean_sub(lines):
    cleaned_lines = lines
    return cleaned_lines

def main(folder, languages):
    for root, dirs, files in os.walk(folder):
        for fname in files:
            str_file_list = []
            basename, ext = os.path.splitext(fname)
            full_fname = os.path.join(root, fname)
            if ext == ".mkv":
                raw_track_info, track_id = get_mkv_track_id(os.path.join(root, fname))
                track_id_int = int(track_id)
                if track_id_int >= 2:
                    track_ids = [str(num) for num in range(2, track_id_int + 1)]

                for _id in track_ids:
                    srt_full_path = os.path.join(root, basename + "_{}_.srt".format(_id))
                    srt_exists = os.path.isfile(srt_full_path)
                    str_file_list.append({"mkv_fname": fname,
                                        "mkv_basename": basename,
                                        "mkv_extension": ext,
                                        "root_folder": root,
                                        "mkv_full_path": full_fname,
                                        "srt_track_id": _id,
                                        "srt_full_path": srt_full_path,
                                        "srt_exists": srt_exists
                                        })
                # Gets all the subtitles from the .mkv and creates .srt files
                extract_subs(str_file_list)

                full_fname_no_sub = full_fname.replace(".mkv", "_no_sub.mkv")
                full_fname_with_sub = full_fname.replace(".mkv", "_with_sub.mkv")
                # Copies the .mkv files without subtitles in it
                remove_mkv_subs(full_fname, full_fname_no_sub)
                # Clean all .srt files and rename according to language
                str_to_add = clean_and_rename_subs(str_file_list, languages)
                # Add .srt files to .mkv
                add_subs(full_fname_no_sub, full_fname_with_sub, str_to_add)
                """
                os.remove(full_fname)
                os.rename(full_fname_with_sub, full_fname)
                """
            """
            # Remove all .srt
            for item in os.listdir(root):
                if item.endswith(".srt"):
                    os.remove(os.path.join(root, item))
            """


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="subs")
    parser.add_argument("--languages", default=["english", "spanish", "french"])
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    folder = args.folder
    languages = args.languages

    main(folder=folder, languages=languages)

