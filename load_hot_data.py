from services.data_service import DataService

if __name__ == "__main__":
    service = DataService()
    #print("Updating ths_hot...")
    #success, msg = service.update_ths_hot()
    #print(f"ths_hot: {msg}")
    print("Updating dc_hot...")
    success, msg = service.update_dc_hot()
    print(f"dc_hot: {msg}")
    service.close()
