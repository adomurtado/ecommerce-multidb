import redis

def get_metadata(sku_list):
    mongo_client = pymongo.MongoClient("mongodb://admin:admin123@mongo:27017/", authSource="admin")
    mongo_coll = mongo_client["ecom"]["produk_metadata"]
    docs = mongo_coll.find({"sku": {"$in": sku_list}}, {"_id": 0, "sku": 1, "deskripsi": 1})
    metadata = list(docs)
    metadata_map = {doc["sku"]: doc["deskripsi"] for doc in metadata}
    return metadata, metadata_map  # ✅ PENTING



def set_stok(sku, jumlah):
    r = redis.Redis(host="redis", port=6379, db=0)
    r.set(f"stok:{sku}", jumlah)

def delete_stok(sku):
    r = redis.Redis(host="redis", port=6379, db=0)
    r.delete(f"stok:{sku}")

def get_stok(sku):
    r = redis.Redis(host="redis", port=6379, db=0)
    value = r.get(f"stok:{sku}")
    return int(value) if value else None
