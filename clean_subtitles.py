import sys
import argparse
import os
import subprocess
from langdetect import detect
import codecs
import re
import glob
from tqdm import tqdm

CHAR_TUPLES_TO_REMOVE = {
    ("[", "]")
}


def remove_mkv_subs(full_fname_mkv, full_fname_no_sub):
    print("2. Removing subtitles from original .mkv file")
    subprocess.check_output([".\mkvmerge.bat", "-o", full_fname_no_sub, "--no-subtitles", full_fname_mkv],
                            stderr=subprocess.STDOUT)


def extract_mkv_subs(mkv_full_path, srt_track_id, srt_full_path):
    subprocess.check_output([".\mkvextract.bat", "tracks", mkv_full_path,
                             srt_track_id + ":" + srt_full_path],
                                        stderr=subprocess.STDOUT)


def add_subs(full_fname_no_sub, full_fname_with_sub, srt_to_add):
    print("4. Adding subtitles")
    subprocess.check_output([".\mkvmerge.bat", "-o", full_fname_with_sub,
                            full_fname_no_sub] + srt_to_add,
                                        stderr=subprocess.STDOUT)


def get_mkv_track_id(file_path):
    """ Returns the track ID of the SRT subtitles track"""
    raw_info = subprocess.check_output([".\mkvmerge.bat", "-i", file_path],
                                        stderr=subprocess.STDOUT)

    pattern = re.compile(".* (\d+): subtitles \(SubRip/SRT\).*", re.DOTALL)
    m = pattern.match(str(raw_info))
    if m:
        return m.group(1)
    else:
        raise Exception("Extraction of track ID failed")


def clean_and_rename_subs(srt_fpaths, languages, languages_per_iso_code):
    print("3. Opening SRT files to select the languages")
    srt_to_add = []
    lang_code_to_add = []
    for srt_fpath in srt_fpaths:
        with open(str_fpath, "r", encoding="utf-8") as fi:
            lines = fi.read().splitlines()
        random_lines = lines[len(lines)//2:len(lines)//2+40]
        random_lines_alpha = [line for line in random_lines if not any(map(str.isdigit, line))]
        random_lines_alpha_no_empty = [line for line in random_lines_alpha if line]
        join_text = " ".join(random_lines_alpha_no_empty)
        join_text = join_text.replace("</i>", "").replace("<i>", "")
        language_detected_abbrev = detect(join_text)
        if language_detected_abbrev in languages_per_iso_code:
            language_detected = languages_per_iso_code[language_detected_abbrev]
            if language_detected in languages:
                cleaned_lines = clean_sub(lines)
                new_name = str_fpath.replace(os.path.basename(str_fpath), language_detected + ".srt")
                with codecs.open(new_name, "w", "utf-8") as fo:
                    for line in cleaned_lines:
                        fo.write(line + "\n")

                srt_to_add.append(new_name)
                lang_code_to_add.append(language_detected)
    return srt_to_add, lang_code_to_add


def clean_sub(lines):
    for char_tuple in CHAR_TUPLES_TO_REMOVE:
        open_char = char_tuple[0]
        close_char = char_tuple[1]
        cleaned_lines = [re.sub(r"\o[^)]*\c".replace("o", open_char).replace("c", close_char), "", line) for line in lines]

    return cleaned_lines


def add_language_titles(full_fname_with_sub, full_fname_with_sub_and_lang, lang_code_to_add):
    print("5. Adding language titles")
    lang_ids = [str(i+2) + ":" + code for i, code in enumerate(lang_code_to_add)]
    list_languages_parsed = " ".join(["--language " + lang_id for lang_id in lang_ids]).split(" ")
    list_subprocess = [".\mkvmerge.bat", "-o", full_fname_with_sub_and_lang, *list_languages_parsed, full_fname_with_sub]

    subprocess.check_output(list_subprocess, stderr=subprocess.STDOUT)


def get_existing_srt(folder, basename):
    files_in_dir = os.listdir(folder)
    list_str = [os.path.join(folder, file) for file in files_in_dir if os.path.splitext(file)[1] == ".srt" and basename in os.path.splitext(file)[0]]
    return list_str

def get_embedded_str(mkv_full_path, track_id_int):
    srt_full_paths = []
    if track_id_int >= 2:
        track_ids = [str(num) for num in range(2, track_id_int + 1)]

        for srt_track_id in track_ids:
            srt_full_path = os.path.join(root, basename + "_{}_.srt".format(_id))
            extract_mkv_subs(mkv_full_path, srt_track_id, srt_full_path)
            srt_full_paths.append(srt_full_path)

    return srt_full_paths


def get_languages_map():
    raw_info = subprocess.check_output([".\mkvmerge.bat", "--list-languages"],
                                       stderr=subprocess.STDOUT)
    raw_info_str = raw_info.decode("utf-8")
    cleaned_lines = [line.replace(" ", "")for line in raw_info_str.split("\r\n")]
    languages_per_iso_code = {}
    for line in cleaned_lines:
        if "|" in line:
            language_split = line.split("|")
            if len(language_split) == 3:
                languages_per_iso_code[language_split[2]] = language_split[0]
            languages_per_iso_code[language_split[1]] = language_split[0]

    return languages_per_iso_code


def main(folder, languages):

    print("0. Get ISO 639-1 languages codes")
    languages_per_iso_code= get_languages_map()
    for root, dirs, files in os.walk(folder):
        for fname in files:

            basename, ext = os.path.splitext(fname)
            if ext == ".mkv":

                full_fname_mkv = os.path.join(root, fname)
                track_id_int = int(get_mkv_track_id(os.path.join(root, fname)))

                existing_list_srt = get_existing_srt(root, basename)
                embedded_list_srt = get_embedded_str(mkv_full_path, track_id_int)
                srt_fpaths = existing_list_srt + embedded_list_srt

                full_fname_no_sub = full_fname_mkv.replace(".mkv", "_no_sub.mkv")
                full_fname_with_sub = full_fname_mkv.replace(".mkv", "_with_sub.mkv")
                full_fname_with_sub_and_lang = full_fname_mkv.replace(".mkv", "_with_sub_and_lang.mkv")
                # Copies the .mkv files without subtitles in it
                remove_mkv_subs(full_fname_mkv, full_fname_no_sub)
                # Clean all .srt files and rename according to language
                srt_to_add, lang_code_to_add = clean_and_rename_subs(srt_fpaths, languages, languages_per_iso_code)
                # Add .srt files to .mkv
                add_subs(full_fname_no_sub, full_fname_with_sub, srt_to_add)
                # Add language title to .mkv
                add_language_titles(full_fname_with_sub, full_fname_with_sub_and_lang, lang_code_to_add)
                # Remove temp files
                os.remove(full_fname_mkv)
                os.remove(full_fname_no_sub)
                os.remove(full_fname_with_sub)
                for str_fpath in srt_fpaths:
                    os.remove(os.path.join(root, item))
                os.rename(full_fname_with_sub_and_lang, full_fname_mkv)


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
