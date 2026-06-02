import csv
import os

base_file = "Data Sources/Leeds Branch.csv"
transformed_file = "Data Sources/Leeds Transformed.csv"

try:
    with open(base_file, mode="r", encoding="utf-8") as basefile, \
        open(transformed_file, mode="w", newline="", encoding="utf-8") as outfile:

        read=csv.reader(basefile)
        write=csv.writer(outfile)

        rows_processed = 0 
        for row in read:
            raw_date_time = row[0].strip()
            date, time = raw_date_time.split()
            location = row[1].strip().lower()
            product=row[3].strip().lower()
            raw_price=float(row[4].strip())
            transform_price=f"{raw_price:.2f}" #2 decimal points for total price
            payment_method=row[5].strip()

            write.writerow([date, time, location, product, transform_price, payment_method])
            rows_processed += 1

except FileNotFoundError:
    print("Error: Paths incorrect.")



    