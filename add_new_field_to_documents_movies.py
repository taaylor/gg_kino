import json
import time

PATH_TO_DOCUMENTS = "backup/elastic_dump/dump/movies_data.json"
PATH_TO_NEW_DOCUMENTS_WITH_DATES = "backup/elastic_dump/dump/movies_data_with_dates.json"


def main():
    with (
        open(file=PATH_TO_DOCUMENTS, mode="r", encoding="utf-8") as f_read,
        open(file=PATH_TO_NEW_DOCUMENTS_WITH_DATES, mode="w", encoding="utf-8") as f_write,
    ):
        fims_in_str = f_read.readlines()
        fims_in_dict = [json.loads(film) for film in fims_in_str]
        # future_timestamp - на один день вперёд
        # future_timestamp = int(time.time() * 1000) + 100000000
        # 10_000_000_000 - на 115 дней вперёд
        future_timestamp = int(time.time() * 1000) + 10_000_000_000
        for film in fims_in_dict:
            film["_source"]["created_at"] = future_timestamp
            film["_source"]["updated_at"] = future_timestamp
            f_write.write(json.dumps(film, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
