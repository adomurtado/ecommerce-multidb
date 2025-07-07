# db/mongo.py
import pymongo

def get_metadata(sku_list):
    mongo_client = pymongo.MongoClient("mongodb://admin:admin123@mongo:27017/", authSource="admin")
    mongo_coll = mongo_client["ecom"]["produk_metadata"]
    docs = mongo_coll.find({"sku": {"$in": sku_list}}, {"_id": 0, "sku": 1, "deskripsi": 1})
    metadata = list(docs)
    metadata_map = {doc["sku"]: doc["deskripsi"] for doc in metadata}
    return metadata, metadata_map
