#!/usr/bin/env python3
# coding: utf-8
import sys
import os
import subprocess
import configparser
import datetime


def main(file_name):
    ret = subprocess.run(["ffmpeg", "-i", file_name, "-f", "ffmetadata", "-"],
                         capture_output=True,
                         text=True, encoding='utf-8')
    if ret.returncode != 0:
        print("Error !!!!!")
        print("-------------------------")
        print(ret.stderr)
        print("-------------------------")
        return

    chapter_info = "[META]"
    chapter_cnt = 1
    for line in ret.stdout.split("\n"):
        if line == "[CHAPTER]":
            line = f"[CHAPTER{chapter_cnt}]"
            chapter_cnt += 1
        chapter_info += line + os.linesep

    time_info = []
    need_hour = False
    config = configparser.ConfigParser()
    config.read_string(chapter_info)
    for section in config.sections():
        if section.startswith("CHAPTER"):
            if not "timebase" in config[section]:
                print(f"{section}: timebase key not found")
                continue
            if not "start" in config[section]:
                print(f"{section}: start key not found")
                continue
            if not "title" in config[section]:
                print(f"{section}: title key not found")
                continue
            if config[section]["timebase"] != "1/1000":
                print(
                    f"{section}: timebase({config[section]['timebase']}) is not supported")
                continue
            if not config[section]["start"].isdecimal():
                print(
                    f"{section}: invalid start time {config[section]['start']}")
                continue
            start_time_ms = int(config[section]["start"])
            time_info.append({"time_stamp_ms": start_time_ms,
                             "title": config[section]["title"]})
            if 1000 * 60 * 60 < start_time_ms:
                need_hour = True

    for item in time_info:
        date = datetime.datetime(
            2000, 1, 1) + datetime.timedelta(milliseconds=item["time_stamp_ms"])
        if need_hour:
            print(f'{date.strftime("%H:%M:%S")} {item["title"]}')
        else:
            print(f'{date.strftime("%M:%S")} {item["title"]}')


if __name__ == "__main__":
    args = sys.argv
    if 2 <= len(args):
        main(args[1])
