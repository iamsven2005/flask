from website.models import warranty
import shelve

db_shelve = shelve.open('databases/warranty/warranty.db', 'c')
db_shelve_uniqueID = shelve.open('databases/warranty/warranty_uniqueID.db', 'c')
warranty = {}
ids = 0
try:
    if "warrantyinfo" in db_shelve:
        warranty = db_shelve['warrantyinfo']
    else:
        db_shelve['warrantyinfo'] = warranty
    if 'Id_info' in db_shelve_uniqueID:
        ids = db_shelve_uniqueID['Id_info']
    else:
        db_shelve_uniqueID['Id_info'] = ids

except IOError:
    print("Error trying to read file")

except Exception as e:
    print(f"An unknown error has occurred,{e}")

else:
    while True:
        choice = input("Create warranty(1), Check warranty database(2), Delete warranty(3), Save Changes & Exit(4): ")
        if choice == '1':
            ids += 1
            name = input("Enter warranty Name: ")
            warranty = warranty(name)
            warranty.set_id(ids)
            warranty[ids] = warranty
            print("warranty database")
            for i in warranty:
                print(f"{warranty[i]}")


        elif choice == '2':
            for i in warranty:
                print(f"{warranty[i]}")
        elif choice == '3':
            print("warranty Database:")
            for i in warranty:
                print(f"{i}, {warranty[i]}")
            try:
                choice = int(input("Enter an ID to delete"))
            except ValueError:
                print("Invalid Value")
            if choice in warranty:
                del warranty[choice]


        elif choice == '4':
            db_shelve['warrantyinfo'] = warranty
            db_shelve.close()
            db_shelve_uniqueID['Id_info'] = ids
            db_shelve_uniqueID.close()
            exit()

