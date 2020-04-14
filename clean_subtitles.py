import argparse
import codecs
import json
import os
import re
import subprocess

from langdetect import detect
from tqdm import tqdm

CHAR_TUPLES_TO_REMOVE = {
    ("[", "]")
}


def remove_mkv_subs(fpath_mkv, fpath_mkv_no_sub):
    subprocess.check_output([".\mkvmerge.bat", "-o", fpath_mkv_no_sub,
                             "--no-subtitles", fpath_mkv],
                            stderr=subprocess.STDOUT)


def extract_fpath_mkv_subs(mkv_fpath, srt_track_id, srt_full_path):
    subprocess.check_output([".\mkvextract.bat", "tracks", mkv_fpath,
                             srt_track_id + ":" + srt_full_path],
                            stderr=subprocess.STDOUT)


def add_subs(fpath_mkv_no_sub, fpath_mkv_sub, selected_srts):
    subprocess.check_output([".\mkvmerge.bat", "-o", fpath_mkv_sub,
                            fpath_mkv_no_sub] + selected_srts,
                            stderr=subprocess.STDOUT)


def get_mkv_track_id(mkv_fpath):
    """ Returns the track ID of the SRT subtitles track

    Args:
        mkv_fpath (str): filepath of .mkv file

    Returns:
        str: number of track ids found in the .mkv file
    """
    raw_info = subprocess.check_output([".\mkvmerge.bat", "-i", mkv_fpath],
                                       stderr=subprocess.STDOUT)

    pattern = re.compile(".* (\d+): subtitles \(SubRip/SRT\).*", re.DOTALL)
    m = pattern.match(str(raw_info))
    if m:
        return m.group(1)
    else:
        raise Exception("Extraction of track ID failed")


def clean_and_rename_subs(srt_fpaths, languages, languages_per_iso_code):
    """ Removes [] areas and saves cleaned subtitle files

    Args:
        srt_fpaths (list[str]): list of filepaths of .srt files
        languages (list[str]): list of requested languages to keep
        languages_per_iso_code (dict[str:str]): map of languages per iso code

    Returns:
        list[str]: list of filepath of cleaned .srt file
        list[str]: list of languages found to keep
        list[str]: list of all filepath of .srt files
    """

    selected_srts = []
    selected_lang = []
    for srt_fpath in tqdm(srt_fpaths):
        with open(srt_fpath, "r", encoding="utf-8") as fi:
            lines = fi.read().splitlines()
        random_lines = lines[len(lines)//2:len(lines)//2+40]
        random_lines_alpha = [line for line in random_lines if (
            not any(map(str.isdigit, line)))]
        random_lines_alpha_no_empty = [
            line for line in random_lines_alpha if line]
        join_text = " ".join(random_lines_alpha_no_empty)
        join_text = join_text.replace("</i>", "").replace("<i>", "")
        language_detected_639_1 = detect(join_text)
        if language_detected_639_1 in languages_per_iso_code:
            language_name = languages_per_iso_code[
                language_detected_639_1]["name"]
            if language_name in languages:
                new_name = clean_and_save_sub(lines, srt_fpath, language_name)
                selected_srts.append(new_name)
                selected_lang.append(language_name)

    all_srt = srt_fpaths + selected_srts

    return selected_srts, selected_lang, all_srt


def clean_and_save_sub(lines, srt_fpath, language_name):
    """ Removes [] areas and saves cleaned subtitle files

    Args:
        lines (list[str]): content of the .srt file
        srt_fpath (str): filepath of .srt file
        language_name (str): language of .srt file

    Returns:
        str: filepath of cleaned .srt file
    """

    for char_tuple in CHAR_TUPLES_TO_REMOVE:
        open_char = char_tuple[0]
        close_char = char_tuple[1]
        cleaned_lines = [re.sub(r"\o[^)]*\c".replace("o", open_char).replace(
            "c", close_char), "", line) for line in lines]

    new_name = srt_fpath.replace(os.path.basename(srt_fpath),
                                 language_name + ".srt")
    with codecs.open(new_name, "w", "utf-8") as fo:
        for line in cleaned_lines:
            fo.write(line + "\n")

    return new_name


def add_language_titles(fpath_mkv_sub, fpath_mkv_sub_lang, selected_lang,
                        iso_codes_per_language):
    """ Adds the languages description to the subtitles on the output .mkv file

    Args:
        fpath_mkv_sub (str): filepath of .mkv file with subtitles
        fpath_mkv_sub_lang (str): filepath of output .mkv file with subtitles
            and language titles
        selected_lang (list[str]): list languages names to add
        iso_codes_per_language (list[str]): list of languages iso codes to add
    """
    lang_ids = [iso_codes_per_language[lang] for lang in selected_lang]
    lang_ids = [str(i+2) + ":" + lang_id for i, lang_id in enumerate(lang_ids)]
    list_languages_parsed = " ".join([
        "--language " + lang_id for lang_id in lang_ids]).split(" ")
    list_subprocess = [".\mkvmerge.bat", "-o", fpath_mkv_sub_lang,
                       *list_languages_parsed, fpath_mkv_sub]
    subprocess.check_output(list_subprocess, stderr=subprocess.STDOUT)


def get_existing_srt(dirpath, basename):
    """ Get the list of .srt files containing the .mkv basename

    Args:
        dirpath (str): dirpath containing the .mkv file
        basename (str): basename of the .mkv file

    Returns:
        list[str]: list existing filepaths of .srt files
    """

    files_in_dir = os.listdir(dirpath)
    fpaths_srt = [os.path.join(dirpath, file) for file in files_in_dir if (
        os.path.splitext(file)[1] == ".srt" and basename in os.path.splitext(
            file)[0])]
    return fpaths_srt


def get_embedded_srt(dirpath, mkv_fpath, track_ids_as_int):
    """ Extracts .srt from .mkv and saves them in the same dir

    Args:
        dirpath (str): dirpath containing the .mkv file
        mkv_fpath (str): filepath to .mkv file
        track_ids_as_int (list[int]): list of track ids in the .mkv file

    Returns:
        list[str]: list of filepaths of all .srt files
    """
    srt_full_paths = []
    if track_ids_as_int >= 2:
        track_ids = [str(num) for num in range(2, track_ids_as_int + 1)]

        for srt_track_id in tqdm(track_ids):
            srt_full_path = os.path.join(dirpath, os.path.basename(
                mkv_fpath) + "_{}_.srt".format(srt_track_id))
            extract_fpath_mkv_subs(mkv_fpath, srt_track_id, srt_full_path)
            srt_full_paths.append(srt_full_path)

    return srt_full_paths


def main(movies_dirpath, languages):
    """ Main script

    Args:
        movies_dirpath (str): dirpath containing all movies
        languages (list[str]): subs languages to keep
    """

    with open("iso_map.json", encoding="utf-8") as fi:
        languages_per_iso_code = json.load(fi)
    iso_codes_per_language = {lang["name"]: lang[
        "639-2"] for _, lang in languages_per_iso_code.items()}

    for root, dirs, files in os.walk(movies_dirpath):
        for fname in files:

            basename, ext = os.path.splitext(fname)
            if ext == ".mkv":

                fpath_mkv = os.path.join(root, fname)
                track_ids_as_int = int(get_mkv_track_id(os.path.join(root,
                                                                     fname)))

                print("1. Extract srt files")
                existing_srts = get_existing_srt(root, basename)
                embedded_srts = get_embedded_srt(root, fpath_mkv,
                                                 track_ids_as_int)
                srt_fpaths = existing_srts + embedded_srts
                if srt_fpaths:
                    fpath_mkv_no_sub = fpath_mkv.replace(".mkv", "_no_sub.mkv")
                    fpath_mkv_sub = fpath_mkv.replace(".mkv", "_sub.mkv")
                    fpath_mkv_sub_lang = fpath_mkv.replace(".mkv",
                                                           "_sub_lang.mkv")
                    print("2. Removing subtitles from original .mkv file")
                    remove_mkv_subs(fpath_mkv, fpath_mkv_no_sub)
                    print("3. Opening SRT files to select the languages")
                    selected_srts, selected_lang, all_srt = (
                        clean_and_rename_subs(srt_fpaths, languages,
                                              languages_per_iso_code))
                    print("4. Adding subtitles")
                    add_subs(fpath_mkv_no_sub, fpath_mkv_sub, selected_srts)
                    print("5. Adding language titles")
                    add_language_titles(fpath_mkv_sub, fpath_mkv_sub_lang,
                                        selected_lang, iso_codes_per_language)
                    print("6. Remove temp files")
                    os.remove(fpath_mkv)
                    os.remove(fpath_mkv_no_sub)
                    os.remove(fpath_mkv_sub)
                    for str_fpath in all_srt:
                        os.remove(str_fpath)
                    os.rename(fpath_mkv_sub_lang, fpath_mkv)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--movies_dirpath", default="subs")
    parser.add_argument(
        "--languages", default=["English", "Spanish", "French"],
        help="The ISO 639 language names are capitalized")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    movies_dirpath = args.movies_dirpath
    languages = args.languages

    main(movies_dirpath=movies_dirpath, languages=languages)
