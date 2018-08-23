import os
import sys
import zipfile
import shutil


INPUT_EXT = ".zipx"
ZIP_EXT = ".zip"
TXT_EXT = ".txt"
CSV_EXT = ".csv"

KEY_NCOA = "_NCOA"
KEY_ERROR = "Errors"
KEY_CORRECTIONS = "Corrections"
KEY_ENOTIFY = ".ebill"

DST_FOLDER_NCOA = "NCOA"
DST_FOLDER_ERRORS = "Errors"
DST_FOLDER_CORRECTIONS = "Corrections"
DST_FOLDER_ENOTIFY = "eNotify"


def check_extensions(src_dir):
    paths = [os.path.join(src_dir, fn) for fn in os.listdir(src_dir) if os.path.splitext(fn)[1].lower() == INPUT_EXT]

    return paths


def renaming(paths):
    # renaming
    zip_paths = []
    for path in paths:
        if not os.path.exists(path):
            continue

        new_path = os.path.splitext(path)[0] + ZIP_EXT
        os.rename(path, new_path)
        zip_paths.append(new_path)

    return zip_paths


def unzip2(zip_path, extract_dir):
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(extract_dir)
    zip_ref.close()


def unzip3(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)


def extracting(zip_path):
    tail, fn = os.path.split(zip_path)
    base, ext = os.path.splitext(fn)

    # create new directory to extract the files
    extract_dir = os.path.join(tail, base)
    if not os.path.isdir(extract_dir):
        extract_dir = os.path.join(tail, "temp")

    # if already exist then remove all contents of this dir
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir, ignore_errors=True)
    else:
        os.mkdir(extract_dir)

    if sys.version_info[0] == 2:
        unzip2(zip_path, extract_dir)
    else:
        unzip3(zip_path, extract_dir)

    return extract_dir


def move(extract_dir, dst_dir):
    # check the contents on extracted folder
    paths = [os.path.join(extract_dir, name) for name in os.listdir(extract_dir)]
    for path in paths:
        try:
            if os.path.isfile(path):
                sys.stdout.write("file {}\n".format(path))

                tail, fn = os.path.split(path)
                base, ext = os.path.splitext(fn)

                if ext == TXT_EXT and base.find(KEY_NCOA) != -1:
                    sys.stdout.write("\t {} -> {}\n".format(fn, KEY_NCOA))

                    new_path = os.path.join(dst_dir, DST_FOLDER_NCOA, fn)
                    os.rename(path, new_path)

                elif ext == CSV_EXT and base.find(KEY_ERROR) != -1:
                    sys.stdout.write("\t {} -> {}\n".format(fn, KEY_ERROR))

                    new_path = os.path.join(dst_dir, DST_FOLDER_ERRORS, fn)
                    os.rename(path, new_path)

                elif ext == CSV_EXT and base.find(KEY_CORRECTIONS) != -1:
                    sys.stdout.write("\t {} -> {}\n".format(fn, KEY_CORRECTIONS))

                    new_path = os.path.join(dst_dir, DST_FOLDER_CORRECTIONS, fn)
                    os.rename(path, new_path)

            else:  # folder
                sys.stdout.write("folder {}\n".format(path))

                if path.endswith(KEY_ENOTIFY):
                    content_paths = [os.path.join(path, fn) for fn in os.listdir(path)]
                    for content_path in content_paths:
                        fn = os.path.split(content_path)[1]
                        ext = os.path.splitext(fn)[1].lower()
                        if ext in [CSV_EXT, TXT_EXT]:
                            sys.stdout.write("\t {} -> {}\n".format(fn, KEY_ENOTIFY))

                            new_path = os.path.join(dst_dir, DST_FOLDER_ENOTIFY, fn)
                            os.rename(content_path, new_path)
                else:
                    move(extract_dir=path, dst_dir=dst_dir)

        except Exception as e:
            print(e)

    # remove all remaining contents on extract dir
    shutil.rmtree(extract_dir, ignore_errors=True)


def removing(zip_paths):
    for zip_path in zip_paths:
        os.remove(zip_path)


if __name__ == '__main__':
    cur_dir = os.path.dirname(os.path.realpath(__file__))

    _src_dir = cur_dir
    _dst_dir = cur_dir

    # check the existence of the destination folders

    for key in [DST_FOLDER_ENOTIFY, DST_FOLDER_CORRECTIONS, DST_FOLDER_ERRORS, DST_FOLDER_NCOA]:
        dst = os.path.join(_dst_dir, key)
        if not os.path.exists(dst) or not os.path.isdir(dst):
            os.mkdir(dst)

    # step 1
    sys.stdout.write("### check the extensions on source directory {}\n".format(_src_dir))
    zipx_paths = check_extensions(src_dir=_src_dir)
    sys.stdout.write("\t number of zipx files {}\n".format(len(zipx_paths)))

    # step 2
    sys.stdout.write("### rename zipx to zip\n")
    zip_paths = renaming(paths=zipx_paths)
    sys.stdout.write("\t number of zip files {}\n".format(len(zip_paths)))

    sys.stdout.write("### extracting...\n")
    for zip_path in zip_paths:
        # step 3
        extract_dir = extracting(zip_path=zip_path)
        move(extract_dir=extract_dir, dst_dir=_dst_dir)

        # step 4
        removing(zip_paths=zip_paths)

    sys.stdout.write("Done!")
