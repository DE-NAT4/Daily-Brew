import csv
import json

def export():
    transactions_list = []

    with open('Data Sources/Leeds Branch.csv', mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        for row in reader:
            raw_date_time = row[0].strip()
            date, time = raw_date_time.split(' ') 
            card_id = row[6].strip() if len(row) > 6 and row[6] else "N/A"
            
            transaction_dict = {
                "date": date,                      
                "time": time,                       
                "location": row[1].strip(),       
                "customer_name": row[2].strip(),   
                "items": row[3].strip(),            
                "total_price": float(row[4].strip()),
                "payment_method": row[5].strip(),   
                "card_id": card_id                  
            }
            transactions_list.append(transaction_dict)


    import pprint
    print(f"Total transactions loaded: {len(transactions_list)}")
    pprint.pprint(transactions_list[0])

    #with open('leeds_transactions.json', mode='w', encoding='utf-8') as json_file:
    #    json.dump(transactions_list, json_file, indent=4)

    return (transactions_list)